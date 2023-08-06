# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.addons.sm_maintenance.models.models_sm_resources import sm_resources
from odoo.addons.sm_maintenance.models.models_sm_utils import sm_utils
from odoo.addons.sm_partago_db.models.models_smp_db_utils import smp_db_utils


class carsharing_user_request(models.Model):
    _name = 'sm_partago_user.carsharing_user_request'
    _inherit = ['mail.thread']
    _description = "CS User request"
    _order = "create_date desc"

    # FIELDS: GENERAL
    name = fields.Char(string=_("Name"))
    type = fields.Selection([
        ('elprat_request', _("El Prat")),
    ], default='elprat_request', string=_("Provision type"), required=True)
    # FIELDS: MEMBER
    force_partner_creation = fields.Boolean(string=_("Force partner creation"))
    member_computation_type = fields.Selection([
        ('not_computed', _("Not computed")),
        ('partner_found', _("Partner found")),
        ('partner_new', _("Partner new"))],
        default='not_computed',
        string=_("Partner computation type"),
        required=True)
    cs_user_status = fields.Selection([
        ('only_exists_on_db', 'Person created on APP (nothing more)'),
        ('requested_access', 'Access request sent'),
        ('active', 'Active'),
        ('blocked_banned', 'Manually Blocked'),
        ('no_access', 'No access')],
        string=_("Carsharing user status"),
        compute="_get_cs_user_status",
        store=False)
    cs_user_type = fields.Selection([
        ('none', 'None'),
        ('user', 'Regular user'),
        ('promo', 'Promo user'),
        ('maintenance', 'Maintenance user'),
        ('organisation', 'Organisation user')],
        string=_("Carsharing user type"),
        compute="_get_cs_user_type",
        store=False)
    related_member_id = fields.Many2one(
        'res.partner', string=_("Related partner"))
    # FIELDS: STATUS INDICATORS
    completed_date = fields.Date(string=_("Completed Date"))
    completion_status = fields.Selection([
        ('not_executed', 'Not executed'),
        ('error', 'Error'),
        ('completed', 'Completed')],
        default='not_executed')
    workflow_status = fields.Selection([
        ('new', 'New'),
        ('member_computed', 'Member computed'),
        ('computed', 'Computed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')],
        default='new')
    cron_executed = fields.Boolean(string=_("Auto completion executed (cron)"))
    # FIELDS: PARTNER CSDATA_IBAN
    data_partner_firstname = fields.Char(string=_("Firstname"))
    data_partner_lastname = fields.Char(string=_("Lastname"))
    data_partner_vat = fields.Char(string=_("VAT"))
    data_partner_email = fields.Char(string=_("Email"))
    data_partner_mobile = fields.Char(string=_("Mobile"))
    data_partner_phone = fields.Char(string=_("Phone"))
    data_partner_gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
        string=_("Gender"),
    )
    data_partner_birthdate_date = fields.Date(string=_("Birthdate"))
    data_partner_street = fields.Char(string=_("Street"))
    data_partner_zip = fields.Char(string=_("ZIP"))
    data_partner_state_id = fields.Many2one(
        'res.country.state', string=_("State"))
    data_partner_city = fields.Char(string=_("City"))
    data_partner_iban = fields.Char(string=_("IBAN"))
    data_partner_driving_license_expiration_date = fields.Char(
        string=_("Driving license expiration date"))
    data_partner_image_dni = fields.Char(string=_("DNI image"))
    data_partner_image_driving_license = fields.Char(
        string=_("Driving license image"))
    # FIELDS: COMPLETION
    cs_registration_request_ids = fields.One2many(
        comodel_name='sm_partago_user.carsharing_registration_request',
        inverse_name='related_carsharing_user_request_id',
        string=_("CS registration requests"))

    # COMPUTED FIELDS
    @api.depends('related_member_id')
    def _get_cs_user_type(self):
        for record in self:
            if record.related_member_id:
                record.cs_user_type = record.related_member_id.cs_user_type

    @api.depends('related_member_id')
    def _get_cs_user_status(self):
        for record in self:
            if record.related_member_id:
                record.cs_user_status = record.related_member_id.cs_state

    # CRON EXECUTION
    @api.multi
    def complete_workflow_cron(self):
        if self.completion_status == 'not_executed':
            error_subject = "CsUserRequest (%s) error" % self.type
            overwrite_project_id = 9  # "Carsharing Helpdesk" project
            # MEMBER COMPUTE WORKFLOW ACTION
            error = self._compute_member_progressbar_cron()
            if error:
                sm_utils.send_email_from_template(
                    self, 'elprat_notok_mail_template_id')
                sm_utils.create_system_task_csuserrequest(
                    self,
                    error_subject,
                    error,
                    self.id,
                    overwrite_project_id
                )
            else:
                # COMPUTE WORKFLOW ACTION
                error = self._compute_progressbar_cron()
                if error:
                    sm_utils.send_email_from_template(
                        self, 'elprat_notok_mail_template_id')
                    sm_utils.create_system_task_csuserrequest(
                        self,
                        error_subject,
                        error,
                        self.id,
                        overwrite_project_id
                    )
                else:
                    # COMPLETE WORKFLOW ACTION (end of process)
                    # (email sent inside method)
                    error = self._complete_progressbar_cron()
                    if error:
                        sm_utils.send_email_from_template(
                            self, 'elprat_notok_mail_template_id')
                        sm_utils.create_system_task_csuserrequest(
                            self,
                            error_subject,
                            error,
                            self.id,
                            overwrite_project_id
                        )
            self.write({
                'cron_executed': True
            })

    # WORKFLOW ACTIONS:
    def _set_workflow_status_to(self, workflow_status):
        self.write({
            'workflow_status': workflow_status
        })

    # RESET WORKFLOW ACTION
    @api.multi
    def reset_progressbar_action(self):
        self.write({
            'member_computation_type': 'not_computed',
            'completion_status': 'not_executed',
            'workflow_status': 'new',
            'completed_date': False
        })

    # MEMBER COMPUTE WORKFLOW ACTION
    # return error ui message or advance
    @api.multi
    def compute_member_progressbar_action(self):
        resources = sm_resources.getInstance()
        if self.workflow_status == 'new':
            error = self._compute_member()
            if error:
                return resources.get_successful_action_message(self, error, self._name)
            self._set_workflow_status_to('member_computed')
        else:
            return resources.get_successful_action_message(self, _('Cannot execute. Status must be "New"'), self._name)

    # returns error
    @api.multi
    def _compute_member_progressbar_cron(self):
        error = self._compute_member()
        if error:
            return error
        self._set_workflow_status_to('member_computed')
        return False

    # returns error
    def _compute_member(self):
        # Only execute if no related_member defined. Otherwise advance state.
        if not self.related_member_id:
            # Forcing creation. Must not exists a partner with same email.
            if self.force_partner_creation:
                if self._find_existing_partner_with_same_email():
                    return _("Force partner creation not possible. It exists already a partner with same email.")
                else:
                    validation_error_response = self._validate_fields_for_partner_creation()
                    if not validation_error_response:
                        self._create_cs_user_partner_and_link_it_to_request()
                        return False
                    else:
                        return validation_error_response
            if self._valid_fields_for_partner_existing():
                existing_partner = self._find_existing_partner()
                # Not forced. Find existing.
                if existing_partner:
                    self.write({
                        'related_member_id': existing_partner.id,
                        'member_computation_type': 'partner_found'
                    })
                    return False
                # Not existing. Try create one.
                else:
                    validation_error_response = self._validate_fields_for_partner_creation()
                    if not validation_error_response:
                        self._create_cs_user_partner_and_link_it_to_request()
                        return False
                    else:
                        return validation_error_response
            else:
                return _("Need at least VAT and Email for member computation")
        # partner already defined setup member_computation_type
        else:
            self.write({
                'member_computation_type': 'partner_found'
            })
        return False

    def _validate_fields_for_partner_creation(self):
        if not self._valid_fields_for_partner_creation():
            return _("No related partner found. Need all contact fields for creating a partner.")
        if not sm_utils.validate_iban(self, self.data_partner_iban):
            return _("No related partner found. Need valid iban for creating a partner.")
        return False

    def _valid_fields_for_partner_existing(self):
        if(
            not self.data_partner_vat or
            not self.data_partner_email
        ):
            return False
        return True

    def _valid_fields_for_partner_creation(self):
        if(
            not self.data_partner_firstname or
            not self.data_partner_lastname or
            not self.data_partner_vat or
            not self.data_partner_email or
            not self.data_partner_mobile or
            not self.data_partner_birthdate_date or
            not self.data_partner_street or
            not self.data_partner_zip or
            not self.data_partner_state_id or
            not self.data_partner_city or
            not self.data_partner_iban or
            not self.data_partner_driving_license_expiration_date or
            not self.data_partner_image_dni or
            not self.data_partner_image_driving_license
        ):
            return False
        return True

    def _find_existing_partner(self):
        q = str(self.data_partner_vat).replace(
            "-", "").replace(" ", "").upper()
        rel_member_q = self.env['res.partner'].sudo().search([('vat', '=', q)])
        if rel_member_q.exists():
            for rmember in rel_member_q:
                if rmember.email == self.data_partner_email:
                    return rmember
            return rel_member_q[0]
        return False

    def _find_existing_partner_with_same_email(self):
        q = str(self.data_partner_email).replace(" ", "")
        rel_member_q = self.env['res.partner'].sudo().search(
            [('email', '=', q)])
        if rel_member_q.exists():
            return rel_member_q[0]
        return False

    def _create_cs_user_partner_and_link_it_to_request(self):
        creation_partner = self._create_cs_user_partner()
        self.write({
            'related_member_id': creation_partner.id,
            'member_computation_type': 'partner_new'
        })

    def _create_cs_user_partner(self):
        partner_creation_data = {
            'firstname': self.data_partner_firstname,
            'lastname': self.data_partner_lastname,
            'vat': self.data_partner_vat,
            'email': self.data_partner_email,
            'mobile': self.data_partner_mobile,
            'phone': self.data_partner_phone,
            'gender': self.data_partner_gender,
            'birthdate_date': self.data_partner_birthdate_date,
            'street': self.data_partner_street,
            'zip': self.data_partner_zip,
            'state_id': self.data_partner_state_id.id,
            'city': self.data_partner_city,
            'driving_license_expiration_date': self.data_partner_driving_license_expiration_date,
            'image_dni': self.data_partner_image_dni,
            'image_driving_license': self.data_partner_image_driving_license
        }
        partner = self.env['res.partner'].create(partner_creation_data)
        partner_bank_creation_data = {
            "acc_number": self.data_partner_iban,
            "acc_type": 'iban',
            "partner_id": partner.id,
        }
        partner_bank = self.env['res.partner.bank'].create(
            partner_bank_creation_data)
        self.write({
            'related_member_id': partner.id
        })
        return partner

    # COMPUTE WORKFLOW ACTION
    # return error ui message or advance
    @api.multi
    def compute_progressbar_action(self):
        resources = sm_resources.getInstance()
        if self.workflow_status == 'member_computed':
            error = self._compute()
            if error:
                return resources.get_successful_action_message(self, error, self._name)
            self._set_workflow_status_to('computed')
        else:
            return resources.get_successful_action_message(self, _('Cannot execute. Status must be "Member computed"'), self._name)

    # returns error
    @api.multi
    def _compute_progressbar_cron(self):
        error = self._compute()
        if error:
            return error
        self._set_workflow_status_to('computed')
        return False

    # return error
    def _compute(self):
        # Get carsharing groups and carsharing status
        self.related_member_id.set_carsharing_groups()
        # Recompute carsharing status
        self.related_member_id.recompute_cs_registration_info()
        if self.type == 'elprat_request':
            # validation
            if not self._valid_cs_user_type():
                return _('Can only compute request if member "Carsharing user type" is "None" or "Regular user"')
            if not self._valid_cs_user_status():
                return _('Can not compute request if member "Carsharing user status" if "Manually Blocked"')
            # add related member to follower
            self.message_subscribe([self.related_member_id.id])
            # computation
            if (
                self.related_member_id.is_prepayment or
                not self.related_member_id.has_memberships()
            ):
                return self._compute_elprat_prepayment()
            else:
                return self._compute_elprat_postpayment()
        return _("Request type must be defined.")

    # return error if happens
    def _compute_elprat_prepayment(self):
        company = self.env.user.company_id
        app_db_utils = smp_db_utils.get_instance(self)
        if self.related_member_id.has_general_prepayment_membership():
            # validation
            if not self.related_member_id.personal_billing_account_index:
                return _('Error on member. Prepayment user without personal billingAccount.')

            # switch from general prepayment group to el prat prepayment
            success = app_db_utils.delete_app_person_from_groups(
                self.related_member_id.cs_person_index,
                company.sm_user_person_group_general_prepayment
            )
            # if not success:
            #    return _('There was a problem removing user from general prepayment group')
            # elprat general prepayment group (for price calculation)
            success = app_db_utils.add_app_person_to_group_with_defined_ba(
                self.related_member_id.cs_person_index,
                '-NI2WrN6P4yf7K9mDGwq',
                self.related_member_id.personal_billing_account_index
            )
            # if not success:
            #    return _('There was a problem adding user to elprat general prepayment group')
            self.related_member_id.set_carsharing_groups()
            if self.cs_user_status != 'active':
                error = self.related_member_id.compute_send_app_registration_email(
                    'https://elprat.sommobilitat.coop'
                )
                if error:
                    return error
        else:
            self.env[
                'sm_partago_user.carsharing_registration_request'
            ].create({
                'related_member_id': self.related_member_id.id,
                'group_index': '-NIqLbwvMiHeG-Aje4yi',
                'ba_behaviour': 'update_ba',
                'related_carsharing_user_request_id': self.id,
                'registration_api_endpoint_overwrite': 'https://elprat.sommobilitat.coop'
            })
        return False

    def _compute_elprat_postpayment(self):
        company = self.env.user.company_id
        # Create tariffs
        self._create_tariffs_elprat()
        # Check if member has access to general SM.
        if self.related_member_id.has_general_postpayment_membership():
            if self.cs_user_status != 'active':
                # Member with general access and not completed -> Resend registration (registration to SM-general)
                registration_request = self.env['sm_partago_user.carsharing_registration_request'].create({
                    'related_member_id': self.related_member_id.id,
                    'group_index': company.sm_user_person_group,
                    'ba_behaviour': 'no_ba',
                    'related_carsharing_user_request_id': self.id,
                    'registration_api_endpoint_overwrite': 'https://elprat.sommobilitat.coop'
                })
        else:
            # Member without access -> Resend registration if must
            # Registering users as postpayment users on "El Prat Users (post)"
            registration_request = self.env['sm_partago_user.carsharing_registration_request'].create({
                'related_member_id': self.related_member_id.id,
                'group_index': '-NIqLSlb4hqINcCCra0g',
                'ba_behaviour': 'no_ba',
                'related_carsharing_user_request_id': self.id,
                'registration_api_endpoint_overwrite': 'https://elprat.sommobilitat.coop'
            })
        return False

    def _valid_cs_user_type(self):
        if self.cs_user_type == 'none' or self.cs_user_type == 'user':
            return True
        return False

    def _valid_cs_user_status(self):
        if self.cs_user_status != 'blocked_banned':
            return True
        return False

    def _create_tariffs_elprat(self):
        # TODO: Here there are some hardcoded params.
        # Warning need to find a better way.
        related_tariffs = []
        existing_tariffs = self.env['smp.sm_carsharing_tariff'].search([
            ('tariff_type', '=', 'rel_car_group'),
            ('related_tariff_group_id', '=', 1),
            ('related_member_id', '=', self.related_member_id.id)
        ])
        if not existing_tariffs:
            tariff = sm_utils.get_create_existing_model(
                self.env['smp.sm_carsharing_tariff'],
                [
                    ('tariff_type', '=', 'rel_car_group'),
                    ('related_tariff_group_id', '=', 1),
                    ('related_carsharing_user_request_id', '=', self.id)
                ],
                {
                    'name': 'El Prat Reduced',
                    'reason': 'El Prat registration',
                    'date': str(datetime.now()),
                    'date_active': str(datetime.now()),
                    'tariff_model_id': 21,
                    'related_tariff_group_id': 1,
                    'description': '<p>El Prat (-30% de la Tarifa Base actual de Som Mobilitat)</p>',
                    'tariff_type': 'rel_car_group',
                    'related_carsharing_user_request_id': self.id
                }
            )
            related_tariffs.append(tariff)
        return related_tariffs

    def _create_tariffs_elprat_relcar_startegy(self):
        tariff_carconfig_refs = [
            "-NEaGmPikt94k4-tVeMf",
            "-NEaH13UfkepEulYY8MF",
            "-NEaHDv7AALG-9aoqdlo",
            "-NEaGUDMAHpRbKICmhUh",
            "-NEaFhhNSV6PTDz0Sf0q",
            "-NEaG86OLlRidau4UnG4",
            "-NEaoXkb_m9L71oKk_h7",
            "-NEaHS7c6RngxaNL054-"
        ]
        related_tariffs = []
        for carconfig_ref in tariff_carconfig_refs:
            db_carconfig_ids = self.env['smp.sm_car_config'].search(
                [('name', '=', carconfig_ref)])
            if db_carconfig_ids.exists():
                tariff = sm_utils.get_create_existing_model(
                    self.env['smp.sm_carsharing_tariff'],
                    [
                        ('tariff_type', '=', 'rel_car'),
                        ('related_carconfig_id', '=', db_carconfig_ids[0].id),
                        ('related_carsharing_user_request_id', '=', self.id)
                    ],
                    {
                        'name': 'El Prat: Reduced for '+carconfig_ref,
                        'reason': 'El Prat registration',
                        'date': str(datetime.now()),
                        'date_active': str(datetime.now()),
                        'tariff_model_id': 21,
                        'related_carconfig_id': db_carconfig_ids[0].id,
                        'description': '<p>El Prat (-30% de la Tarifa Base actual de Som Mobilitat)</p>',
                        'tariff_type': 'rel_car',
                        'related_carsharing_user_request_id': self.id
                    }
                )
                if tariff.related_carsharing_user_request_id:
                    if tariff.related_carsharing_user_request_id.id == self.id:
                        related_tariffs.append(tariff)
        return related_tariffs

    # COMPLETE WORKFLOW ACTION (end of process)
    # return error ui message or success ui message
    @api.multi
    def complete_progressbar_action(self):
        resources = sm_resources.getInstance()
        if self.workflow_status == 'computed':
            # Completion data
            success = self._setup_completion_data()
            if success:
                # Notify contact El Prat went ok
                sm_utils.send_email_from_template(
                    self, 'elprat_ok_mail_template_id')
                # ui msg
                return resources.get_successful_action_message(self, _('Request successfully completed'), self._name)
            else:
                # error ui msg
                return resources.get_successful_action_message(self, _('There was a problem on the registration request. No email was sent to the user.'), self._name)
        else:
            # error ui msg
            return resources.get_successful_action_message(self, _('Cannot execute. Status must be "Computed"'), self._name)

    # return error
    @api.multi
    def _complete_progressbar_cron(self):
        success = self._setup_completion_data()
        if success:
            # Notify contact El Prat went ok
            sm_utils.send_email_from_template(
                self, 'elprat_ok_mail_template_id')
            return False
        else:
            return _('There was a problem on the registration request. No email was sent to the user.')

    # returns boolean if process was successful
    def _setup_completion_data(self):
        completion_data = {
            'completed_date': str(datetime.now()),
            'completion_status': 'completed',
            'workflow_status': 'completed'
        }
        # Apply Tariffs
        if self.tariffs_ids:
            for tariff in self.tariffs_ids:
                tariff.write({
                    'related_member_id': self.related_member_id.id
                })
        # Compute registration requests
        if self.cs_registration_request_ids:
            for registration_request in self.cs_registration_request_ids:
                if not registration_request.completed:
                    registration_request.compute_request()
                    if registration_request.completed_behaviour == 'error':
                        completion_data['completion_status'] = 'error'
        # Write completion data
        self.write(completion_data)
        return completion_data['completion_status'] != 'error'

    @api.multi
    def cancel_progressbar_action(self):
        resources = sm_resources.getInstance()
        if self.workflow_status != 'computed' and self.workflow_status != 'completed':
            completion_data = {
                'completed_date': str(datetime.now()),
                'workflow_status': 'cancelled'
            }
            self.write(completion_data)
        else:
            return resources.get_successful_action_message(self, _('Cannot execute. Status must not be "Computed" or "Cancelled"'), self._name)
