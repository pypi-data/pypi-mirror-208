# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.addons.sm_partago_db.models.models_smp_db_utils import smp_db_utils
from odoo.addons.sm_maintenance.models.models_sm_utils import sm_utils


class carsharing_registration_request(models.Model):
    _name = 'sm_partago_user.carsharing_registration_request'
    _order = "create_date asc"

    active = fields.Boolean(string=_("Active"), default=True)
    related_member_id = fields.Many2one(
        'res.partner', string=_("Related member"))
    force_registration = fields.Boolean(string=_("Force registration"))
    group_index = fields.Char(string=_("CS Group index"))
    group_id = fields.Many2one(
        'smp.sm_group',
        string=_("Cs group"),
        compute="_get_group_id", store=False)
    ba_behaviour = fields.Selection([
        ('no_ba', 'No billingAccount'),
        ('dedicated_ba', 'Create dedicated billingAccount'),
        ('update_ba', 'Update personal billingAccount')],
        string=_("billingAccount behaviour"), default="no_ba")
    ba_credits = fields.Float(string=_("billingAccount credits"))
    # TODO: this must be moved to reward module
    related_coupon_index = fields.Char(string=_("Coupon index"))
    related_cs_update_data_id = fields.Many2one(
        'sm_partago_user.carsharing_update_data',
        string=_("Related CS Update data request"))
    related_carsharing_user_request_id = fields.Many2one(
        'sm_partago_user.carsharing_user_request',
        string=_("Related Carsharing user request"))
    completed = fields.Boolean(string=_("Completed"))
    completed_date = fields.Date(string=_("Completed date"))
    completed_behaviour = fields.Selection([
        ('not_computed', 'Not computed'),
        ('user_created', 'User created'),
        ('user_created_membership', 'User created + Membership'),
        ('user_created_membership_ba', 'User created + billingAccount Membership'),
        ('user_created_membership_ba_transaction',
         'User created + billingAccount Membership + Transaction'),
        ('membership', 'Membership'),
        ('membership_ba', 'billingAccount Membership'),
        ('membership_ba_transaction', 'billingAccount Membership + Transaction'),
        ('ba_transaction', 'Transaction created'),
        ('nothing_done', 'Nothing done (registration email if must)'),
        ('error', 'Error')],
        string=_("Completed behaviour"), default="not_computed", required=True)
    completed_behaviour_before_error = fields.Selection([
        ('not_computed', 'Not computed'),
        ('user_created', 'User created'),
        ('user_created_membership', 'User created + Membership'),
        ('user_created_membership_ba', 'User created + billingAccount Membership'),
        ('user_created_membership_ba_transaction',
         'User created + billingAccount Membership + Transaction'),
        ('membership', 'Membership'),
        ('membership_ba', 'billingAccount Membership'),
        ('membership_ba_transaction', 'billingAccount Membership + Transaction'),
        ('ba_transaction', 'Transaction created'),
        ('nothing_done', 'Nothing done (registration email if must)'),
        ('error', 'Error'),
        ('not_relevant', 'Not relevant')],
        string=_("Completed behaviour (before error)"), default="not_computed", required=True)
    completed_error_description = fields.Char(string="Resolution description")
    registration_api_endpoint_overwrite = fields.Char(
        string="Registration API endpoint overwrite")

    @api.depends("group_index")
    def _get_group_id(self):
        for record in self:
            if record.group_index:
                existing_db_groups = self.env['smp.sm_group'].search(
                    [('name', '=', record.group_index)])
                if existing_db_groups.exists():
                    record.group_id = existing_db_groups[0]

    def compute_request(self, task_creation=False):
        # Once first registration request gets executed member has cs_user_type defined at least as user
        if self.related_member_id.cs_user_type == 'none':
            self.related_member_id.write({
                'cs_user_type': 'user'
            })

        app_db_utils = smp_db_utils.get_instance(self)
        _completed_behaviour = 'not_computed'
        company = self.env.user.company_id

        # 1.-SYSTEMDB UPDATE
        # update systemdb: system group
        if self.group_index:
            app_db_utils.update_system_group_from_app_group(
                self, self.group_index)
        else:
            app_db_utils.update_system_group_from_app_group(
                self, company.sm_user_person_group)
            app_db_utils.update_system_group_from_app_group(
                self, company.sm_user_person_group_prepayment)
        # update systemdb: person groups
        self.related_member_id.set_carsharing_groups()

        # 2.-GROUP COMPUTATION & VALIDATION
        computed_group_data = self._compute_registration_group()
        # errors on registration group computation
        if computed_group_data['error']:

            # User has already active membership. Send some emails to make him remember.
            if computed_group_data['completed_behaviour'] == 'nothing_done':
                success = self._compute_send_app_registration_email_if_must(
                    computed_group_data['completed_behaviour'], task_creation)
                if not success:
                    return False
                # On "nothing done" behaviour we don't need to create a error task
                task_creation = False

            self._complete_request(
                computed_group_data['completed_behaviour'],
                _completed_behaviour,
                computed_group_data['error'],
                task_creation
            )
            return False

        # 3.-PERSON CREATION: if needed (TEST) (OK)
        if self.related_member_id.exists_on_app_db() == False:
            # if self.force_registration or self.related_member_id.verify_cs_data_fields():
            res_data = app_db_utils.create_app_person(
                self.related_member_id.get_member_data_for_app())
            if res_data is False:
                error_msg = _(
                    """ADD TO APP DB FAIL: PERSON API Call.
          Couldn't create person. Call returned != 200.
          Registration request id: %s""") % (str(self.id))
                self._complete_request(
                    'error', _completed_behaviour, error_msg, task_creation)
                return False
            else:
                # system behaviour
                _completed_behaviour = 'user_created'
                self.related_member_id.write({
                    "cs_state": "only_exists_on_db",
                    "cs_person_index": res_data['id']
                })

        # 4.-MEMBERSHIP CREATION: check registration behaviour and act accordingly
        # 4.1.-NO BA (TEST) (OK)
        if self.ba_behaviour == 'no_ba':
            membership_error = self._create_membership(
                computed_group_data['computed_group_id'].name)
            if membership_error:
                self._complete_request(
                    'error', _completed_behaviour, membership_error, task_creation)
                return False
            else:
                # system behaviour
                if _completed_behaviour == 'user_created':
                    _completed_behaviour = 'user_created_membership'
                else:
                    _completed_behaviour = 'membership'

        # 4.2.-DEDICATED BA / UPDATE BA (TEST) (OK)
        if self.ba_behaviour == 'dedicated_ba' or self.ba_behaviour == 'update_ba':
            # 4.2.1.-MEMBERSHIP EXISTS (only update BA) (TEST) (OK)
            if computed_group_data['existing_system_membership']:
                if self.ba_credits > 0:
                    transaction_error = self._create_ba_transaction(
                        computed_group_data['existing_system_membership'].related_billingaccount_id.name, self.ba_credits)
                    if transaction_error:
                        self._complete_request(
                            'error', _completed_behaviour, transaction_error, task_creation)
                        return False
                    else:
                        # system behaviour
                        _completed_behaviour = 'ba_transaction'
                else:
                    _completed_behaviour = 'membership_ba'

            # 4.2.2 .-NO MEMBERSHIP
            else:
                if self.ba_behaviour == 'dedicated_ba':
                    # dedicated ba (create dedicate BA membership)
                    membership_ba_data = self._create_membership_ba_transaction(
                        computed_group_data['computed_group_id'].name,
                        False,
                        self.ba_credits,
                        _completed_behaviour
                    )
                if self.ba_behaviour == 'update_ba':
                    # update ba (update BA if exists or create id personal_billing_account_index is FALSE)
                    membership_ba_data = self._create_membership_ba_transaction(
                        computed_group_data['computed_group_id'].name,
                        self.related_member_id.personal_billing_account_index,
                        self.ba_credits,
                        _completed_behaviour
                    )
                if membership_ba_data['error']:
                    self._complete_request(
                        'error', membership_ba_data['completed_behaviour'], membership_ba_data['error'], task_creation)
                    return False
                else:
                    _completed_behaviour = membership_ba_data['completed_behaviour']
                    # new membership: if update BA we write the personal_billing_account_index
                    if self.ba_behaviour == 'update_ba':
                        self.related_member_id.write({
                            "personal_billing_account_index": membership_ba_data["billing_account"]
                        })

        # 5.-EVERYTING OK on DB
        self.related_member_id.set_carsharing_groups()

        # 5.1 CONTROL AUTO CREATE BA WHEN ONLY MEMBERSHIP DESIRED (no_ba)
        # when we create no_ba membership on group without fallback ba it creates ba for the membership
        if self.ba_behaviour == 'no_ba':
            if not self.related_member_id.personal_billing_account_index:
                member_cs_groups = self.env['sm_partago_user.carsharing_member_group'].search([
                    ('related_member_id', '=', self.related_member_id.id),
                    ('related_group_id', '=',
                        computed_group_data['computed_group_id'].id)
                ])
                if member_cs_groups.exists():
                    member_cs_group = member_cs_groups[0]
                    if member_cs_group.related_billingaccount_id:
                        self.related_member_id.write({
                            "personal_billing_account_index": member_cs_group.related_billingaccount_id.name
                        })

        # 6.-SEND REGISTRATION EMAIL
        success = self._compute_send_app_registration_email_if_must(
            _completed_behaviour, task_creation)
        if success:
            self._complete_request(_completed_behaviour, 'not_relevant')
            return True
        return False

    def _compute_registration_group(self):
        app_db_utils = smp_db_utils.get_instance(self)
        company = self.env.user.company_id
        # Check which group we want to work
        if self.group_index:
            computed_group_index = self.group_index
        else:
            if self.ba_behaviour == 'no_ba':
                computed_group_index = company.sm_user_person_group
            else:
                computed_group_index = company.sm_user_person_group_prepayment

        # get related system group object
        computed_group_id = app_db_utils.get_system_db_group(
            self, computed_group_index)
        if computed_group_id is False:
            error_msg = _(
                """SYSTEM FAIL:
          Group index has no related system group entry.
          Registration request id: %s""") % (str(self.id))
            return {
                'completed_behaviour': 'error',
                'error': error_msg
            }

        # get related member system membership
        existing_cs_groups = self.env['sm_partago_user.carsharing_member_group'].search([
            ('related_member_id', '=', self.related_member_id.id),
            ('related_group_id', '=', computed_group_id.id)
        ])

        # Existing membership
        if existing_cs_groups.exists():

            # update data on existing membership only sends registration email if must
            if self.related_cs_update_data_id:
                error_msg = _(
                    """GROUP COMPUTATION no action needed:
          Registration request (update data) on existing membership.
          Registration request id: %s""") % (str(self.id))
                return {
                    'completed_behaviour': 'nothing_done',
                    'error': error_msg
                }

            existing_cs_group = existing_cs_groups[0]
            # no BA membership
            if self.ba_behaviour == 'no_ba':
                error_msg = _(
                    """GROUP COMPUTATION no action needed:
          Membership (no billingAccount) already exists.
          Registration request id: %s""") % (str(self.id))
                return {
                    'completed_behaviour': 'nothing_done',
                    'error': error_msg
                }
            # dedicated BA membership
            if self.ba_behaviour == 'dedicated_ba':
                if existing_cs_group.related_billingaccount_id:
                    # if membership exists and BA defined is not default for the user we can update this one
                    if existing_cs_group.related_billingaccount_id.name != self.related_member_id.personal_billing_account_index:
                        return {
                            'computed_group_id': computed_group_id,
                            'existing_system_membership': existing_cs_group,
                            'error': False
                        }
                error_msg = _(
                    """GROUP COMPUTATION misconfiguration:
          Membership (dedicated billingAccount). Already active membership.
          Registration request id: %s""") % (str(self.id))
                return {
                    'completed_behaviour': 'error',
                    'error': error_msg
                }
            # update BA for this membership
            if self.ba_behaviour == 'update_ba':
                if not existing_cs_group.related_billingaccount_id:
                    error_msg = _(
                        """GROUP COMPUTATION misconfiguration:
            Membership (update billingAccount) Membership has no dedicated BA to update.
            Registration request id: %s""") % (str(self.id))
                    return {
                        'completed_behaviour': 'error',
                        'error': error_msg
                    }
                else:
                    # update_ba
                    return {
                        'computed_group_id': computed_group_id,
                        'existing_system_membership': existing_cs_group,
                        'error': False
                    }
        # Must create membership
        else:
            # update data don't create membership for promo users / only sends emails if must
            if self.related_cs_update_data_id:
                if self.related_member_id.cs_user_type == 'promo':
                    error_msg = _(
                        """GROUP COMPUTATION no action needed:
          Registration request (update data) on promo user must only send email.
          Registration request id: %s""") % (str(self.id))
                    return {
                        'completed_behaviour': 'nothing_done',
                        'error': error_msg
                    }

            if self.ba_behaviour != 'no_ba':
                if computed_group_id.related_billingaccount_index:
                    error_msg = _(
                        """GROUP COMPUTATION misconfiguration:
            Membership (billingAccount) Cannot create membership on group with fallback BA.
            Registration request id: %s""") % (str(self.id))
                    return {
                        'completed_behaviour': 'error',
                        'error': error_msg
                    }

            # no_ba, dedicated_ba, update_ba
            return {
                'computed_group_id': computed_group_id,
                'existing_system_membership': False,
                'error': False
            }

    # returns error
    def _create_membership(self, group_index):
        app_db_utils = smp_db_utils.get_instance(self)
        membership_success = app_db_utils.add_app_person_to_group(
            self.related_member_id.cs_person_index,
            group_index,
            "false"
        )
        if membership_success is False:
            error_msg = _(
                """ADD TO APP DB FAIL: MEMBERSHIP API Call.
        Couldn't create person membership. Call returned != 200.
        Registration request id: %s""") % (str(self.id))
            return error_msg
        return False

    # returns error
    def _create_membership_ba(self, group_index, ba_index):
        app_db_utils = smp_db_utils.get_instance(self)
        # create membership
        if ba_index:
            membership_success = app_db_utils.add_app_person_to_group_with_defined_ba(
                self.related_member_id.cs_person_index,
                group_index,
                ba_index
            )
        else:
            membership_success = app_db_utils.add_app_person_to_group(
                self.related_member_id.cs_person_index,
                group_index,
                "true"
            )
        if membership_success is False:
            error_msg = _(
                """ADD TO APP DB FAIL: MEMBERSHIP API Call.
        Couldn't create person membership. Call returned != 200.
        Registration request id: %s""") % (str(self.id))
            return error_msg
        return False

    # returns error
    def _create_ba_transaction(self, ba_index, ba_credits):
        app_db_utils = smp_db_utils.get_instance(self)
        transaction_success = app_db_utils.create_app_ba_transaction(
            ba_index,
            "other",
            "registration request: "+str(self.id),
            ba_credits
        )
        if transaction_success is False:
            error_msg = _(
                """ADD TO APP DB FAIL: Add transaccion API Call.
        Adding a transaction failed for BA.
        Registration request id: %s""") % (str(self.id))
            return error_msg
        # update system billing account with transaction
        app_db_utils.update_system_ba_from_app_ba(self, ba_index)
        return False

    # returns dict: error,completed_behaviour,billing_account
    def _create_membership_ba_transaction(self, group_index, ba_index, ba_credits, previous_completed_behaviour):
        _completed_behaviour = previous_completed_behaviour
        app_db_utils = smp_db_utils.get_instance(self)
        membership_error = self._create_membership_ba(group_index, ba_index)
        if membership_error:
            return {
                'error': membership_error,
                'completed_behaviour': _completed_behaviour
            }
        else:
            # system behaviour
            if _completed_behaviour == 'user_created':
                _completed_behaviour = 'user_created_membership_ba'
            else:
                _completed_behaviour = 'membership_ba'

        app_person_groups = app_db_utils.get_app_person_groups(
            self.related_member_id.cs_person_index)
        if app_person_groups is False:
            error_msg = _(
                """ADD TO APP DB FAIL: Get Groups API Call (BA transaction).
                Couldn't get person groups after membership successful. Call returned != 200.
                Registration request id: %s""") % (str(self.id))
            return {
                'error': error_msg,
                'completed_behaviour': _completed_behaviour
            }
        else:
            group_data = app_person_groups[group_index]
        # create transaction
        if ba_credits > 0:
            transaction_error = self._create_ba_transaction(
                group_data["billingAccountId"], ba_credits)
            if transaction_error:
                return {
                    'error': transaction_error,
                    'completed_behaviour': _completed_behaviour
                }
            else:
                # system behaviour
                if _completed_behaviour == 'user_created_membership_ba':
                    _completed_behaviour = 'user_created_membership_ba_transaction'
                else:
                    _completed_behaviour = 'membership_ba_transaction'
        return {
            'error': False,
            'completed_behaviour': _completed_behaviour,
            'billing_account': group_data["billingAccountId"]
        }

    def _compute_send_app_registration_email_if_must(self, _completed_behaviour, task_creation):
        if self.related_member_id.cs_state not in ['blocked_banned', 'active']:
            # 6.1.-MEMBER DATA VALIDATON
            # Missing necessary data for register
            if self.force_registration is False \
                    and self.related_member_id.verify_cs_data_fields() is False:
                sm_utils.send_email_from_template(
                    self.related_member_id, 'cs_missing_data_email_template_id')
                error_msg = _(
                    """USER DATA FAIL:
          Member has not all necessary data for registration.
          Registration request id: %s""") % (str(self.id))
                self._complete_request(
                    'error', _completed_behaviour, error_msg)
                return False
            error = self._compute_send_app_registration_email()
            if error:
                self._complete_request(
                    'error', _completed_behaviour, error, task_creation)
                return False
            else:
                self.related_member_id.write({
                    'cs_state': 'requested_access'
                })
        return True

    # Sends the registration email trough the APP
    # This methods returns an error if occurs
    def _compute_send_app_registration_email(self):
        return self.related_member_id.compute_send_app_registration_email(self.registration_api_endpoint_overwrite)

    def _complete_request(self, completed_behaviour, completed_behaviour_before_error=False, completed_error_description=False, task_creation=False):
        self.write({
            'completed': True,
            'completed_date': datetime.now(),
            'completed_behaviour': completed_behaviour,
            'completed_behaviour_before_error': completed_behaviour_before_error,
            'completed_error_description': completed_error_description
        })
        if task_creation:
            sm_utils.create_system_task(
                self, "CS Registration error.", completed_error_description)

    @api.model
    def complete_registration_request_action(self):
        if self.env.context:
            if 'active_ids' in self.env.context:
                registration_requests = self.env['sm_partago_user.carsharing_registration_request'].browse(
                    self.env.context['active_ids'])
                if registration_requests.exists():
                    for registration_request in registration_requests:
                        registration_request.compute_request()
