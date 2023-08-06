# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.addons.sm_connect.models.models_sm_carsharing_api_utils import sm_carsharing_api_utils
from odoo.addons.sm_connect.models.models_sm_carsharing_db_utils import sm_carsharing_db_utils
from odoo.addons.sm_connect.models.models_sm_wordpress_db_utils import sm_wordpress_db_utils
from odoo.addons.sm_partago_db.models.models_smp_db_utils import smp_db_utils
from odoo.addons.sm_maintenance.models.models_sm_utils import sm_utils
from odoo.addons.sm_maintenance.models.models_sm_resources import sm_resources


class partago_user(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    _resources = sm_resources.getInstance()

    cs_person_index = fields.Char(string=_("Carsharing person index"))

    cs_registration_completed_date = fields.Date(
        string=_("Carsharing registration completed date")
    )
    cs_firebase_uid = fields.Char(string=_("UID"))
    cs_data_ok = fields.Boolean(
        string=_("CS registration attemp user data ok"),
        compute="_get_cs_data_ok",
        store=False
    )
    cs_registration_info_ok = fields.Boolean(
        string=_("CS registration complete info ok"),
        compute="_get_cs_registration_info_ok",
        store=True
    )
    cs_registration_coupon = fields.Char(
        string=_("Registration coupon for team members")
    )

    cs_state = fields.Selection([
        ('only_exists_on_db', 'Person created on APP (nothing more)'),
        ('requested_access', 'Access request sent'),
        ('active', 'Active'),
        ('blocked_banned', 'Manually Blocked'),
        ('no_access', 'No access')
    ], default='no_access', string=_("Carsharing user status"))

    cs_user_type = fields.Selection([
        ('none', 'None'),
        ('user', 'Regular user'),
        ('promo', 'Promo user'),
        ('maintenance', 'Maintenance user'),
        ('organisation', 'Organisation user')
    ], default='none', string=_("Carsharing user type"))

    registration_link = fields.Char(string=_("Registration link"))

    cs_member_group_ids = fields.One2many(
        comodel_name='sm_partago_user.carsharing_member_group',
        inverse_name='related_member_id',
        string=_("CS Groups")
    )

    cs_registration_request_ids = fields.One2many(
        comodel_name='sm_partago_user.carsharing_registration_request',
        inverse_name='related_member_id',
        string=_("CS registration requests")
    )

    #
    # CS REGISTRATION
    #
    def exists_on_app_db(self):
        if (
            self.cs_state == 'requested_access' or
            self.cs_state == 'active' or
            self.cs_state == 'only_exists_on_db'
        ):
            return True
        return False

    # Sends the registration email trough the APP
    # This methods returns an error if occurs
    def compute_send_app_registration_email(
        self,
        registration_api_endpoint_overwrite=False
    ):
        if self.cs_person_index and self.cs_person_index != '':
            api_utils = sm_carsharing_api_utils.get_instance(self)
            r = api_utils.post_persons_send_registration_email(
                self,
                self.cs_person_index,
                self.get_cs_lang(),
                registration_api_endpoint_overwrite
            )
            if r.status_code != 200:
                return (
                    """API ERROR:
                Send APP registration email returned != 200.
                Member id: %s""") % (str(self.id))
            else:
                self._compute_registration_link()
                return False
        else:
            return (
                """USER DATA ERROR:
            Send APP registration email cannot be sent if user has no cs_index
            Member id: %s""") % (str(self.id))

    def recompute_send_app_registration_email(self):
        error = self.compute_send_app_registration_email()
        if error:
            return error
        else:
            self.write({
                'cs_state': 'requested_access'
            })
            return False

        # TODO: API must return regKey so we can do this via API

    def _compute_registration_link(self):
        cs_url = self.env.user.company_id.sm_carsharing_api_credentials_cs_url
        db_utils = sm_carsharing_db_utils.get_instance(self)
        existing_person = db_utils.firebase_get(
            'persons', self.cs_person_index)
        try:
            registration_key = existing_person['registrationKey']
        except:
            registration_key = False
        if registration_key:
            computed_link = cs_url + "/#/?regkey=" + registration_key
            self.write({
                'registration_link': computed_link
            })

    #
    # CS STATUS
    @api.depends('cs_state')
    def _get_cs_data_ok(self):
        for record in self:
            record.cs_data_ok = record.verify_cs_data_fields()

    @api.depends('cs_state', 'cs_registration_completed_date', 'cs_person_index', 'cs_firebase_uid')
    def _get_cs_registration_info_ok(self):
        for record in self:
            if record.exists_on_app_db() and record.cs_registration_completed_date and record.cs_firebase_uid \
                    and record.cs_person_index:
                record.cs_registration_info_ok = True
            else:
                record.cs_registration_info_ok = False

    def verify_cs_data_fields(self):
        if not self.firstname:
            return False
        if not self.vat:
            return False
        if not self.image_dni:
            return False
        if not self.email:
            return False
        if not self.mobile:
            return False
        if not self.birthdate_date:
            return False
        if not self.driving_license_expiration_date:
            return False
        if not self.image_driving_license:
            return False
        return True

    def is_cs_person_requested(self):
        if self.cs_state == 'requested_access' or self.cs_state == 'requested_access_second_notification':
            return True
        return False

    def recompute_cs_registration_info(self):
        db_utils = sm_carsharing_db_utils.get_instance(self)
        firebase_uid = db_utils.get_uid_from_email(self.email)
        if firebase_uid:
            self.write({'cs_firebase_uid': firebase_uid})
            if self.cs_state in ['only_exists_on_db', 'requested_access']:
                self.write({
                    'cs_registration_completed_date': datetime.now(),
                    'cs_state': 'active'
                })
        else:
            if self.cs_firebase_uid:
                udata = {
                    'cs_firebase_uid': None,
                    'cs_registration_completed_date': None
                }
                if self.cs_state == 'active' and self.cs_person_index:
                    udata['cs_state'] = 'only_exists_on_db'
                self.write(udata)

    #
    # GETTERS
    #
    def get_app_person_details(self):
        app_db_utils = smp_db_utils.get_instance(self)
        return app_db_utils.get_app_person_details(self.cs_person_index)

    def get_app_person_groups(self):
        app_db_utils = smp_db_utils.get_instance(self)
        return app_db_utils.get_app_person_groups(self.cs_person_index)

    def get_member_data_for_app(self):
        member_data = {}
        if self.company_type == 'person':
            firstname = self.firstname
            lastname = self.lastname
        else:
            firstname = self.name
            lastname = ""
        if not firstname:
            firstname = ""
        if not lastname:
            lastname = ""
        member_data["firstname"] = firstname
        member_data["lastname"] = lastname
        # email
        member_data["email"] = self.email
        if not member_data["email"]:
            member_data["email"] = ""
        # address
        city = self.city
        if not city:
            city = ""
        postalCode = self.zip
        if not postalCode:
            postalCode = ""
        street = self.street
        if not street:
            street = ""
        member_data["address"] = {
            'city': city,
            'postalCode': postalCode,
            'street': street
        }
        # phone
        main_phone = self.mobile
        if not main_phone:
            main_phone = ""
        member_data["phones"] = {"main": main_phone}
        # DNI
        member_data["nationalIdentificationNumber"] = self.vat
        if not member_data["nationalIdentificationNumber"]:
            member_data["nationalIdentificationNumber"] = ""
        # lang
        member_data["preferredLanguage"] = self.get_cs_lang()
        if not member_data["preferredLanguage"]:
            member_data["preferredLanguage"] = "ca"
        return member_data

    @api.model
    def get_registration_view(self):
        view_ref = self.env['ir.ui.view'].sudo().search(
            [('name', '=', 'partago_user.carsharing_registration_wizard.form')])
        return view_ref.id

    @api.model
    def get_change_email_view(self):
        view_ref = self.env['ir.ui.view'].sudo().search(
            [('name', '=', 'sm_partago_user.sm_change_email_wizard.form')])
        return view_ref.id

    def get_cs_lang(self):
        company = self.env.user.company_id

        if self.lang:
            languages = [company.sm_user_allowed_user_langs_es,
                         company.sm_user_allowed_user_langs_ca]
            member_language = self.lang.split("_")
            if member_language in languages:
                return member_language
        return company.sm_user_person_default_language
        # return "ca"

    #
    # REGISTRATION COUPON (COMPANIES)
    #
    def set_registration_coupon(self):
        db_utils = sm_wordpress_db_utils.get_instance(self)
        if not self.is_company:
            return
        mcargs = {
            'post_type': 'sm_coupon',
            'orderby': 'ID',
            'order': 'DESC'
        }
        # get pages in batches of 20
        offset = 0
        increment = 100
        coupon_found = False
        while coupon_found is False:
            mcargs['number'] = increment
            mcargs['offset'] = offset
            member_coupons = db_utils.get_posts(mcargs)
            if len(member_coupons) == 0:
                break  # no more posts returned
            for coupon in member_coupons:
                for custom_field in coupon.custom_fields:
                    if custom_field['key'] == 'coupon_related_company_cif':
                        if custom_field['value']:
                            if custom_field['value'].upper().strip() == self.vat.upper().strip():
                                self.write({'cs_registration_coupon': coupon})
                                coupon_found = True
                                break
            offset = offset + increment
        return coupon_found

    #
    # CS GROUPS
    #
    def has_memberships(self):
        memberships = self.env[
            'sm_partago_user.carsharing_member_group'
        ].search([
            ('related_member_id', '=', self.id)
        ])
        return memberships.exists()

    def has_general_postpayment_membership(self):
        company = self.env.user.company_id
        general_postpayment_group = self.env['smp.sm_group'].search([
            ('name', '=', company.sm_user_person_group)
        ])
        if general_postpayment_group.exists():
            general_postpayment_user_group = self.env[
                'sm_partago_user.carsharing_member_group'
            ].search([
                ('related_member_id', '=', self.id),
                ('related_group_id', '=', general_postpayment_group[0].id)
            ])
            return general_postpayment_user_group.exists()
        return False

    def has_general_prepayment_membership(self):
        company = self.env.user.company_id
        general_prepayment_group = self.env['smp.sm_group'].search([
            ('name', '=', company.sm_user_person_group_general_prepayment)
        ])
        if general_prepayment_group.exists():
            general_prepayment_user_group = self.env[
                'sm_partago_user.carsharing_member_group'
            ].search([
                ('related_member_id', '=', self.id),
                ('related_group_id', '=', general_prepayment_group[0].id)
            ])
            return general_prepayment_user_group.exists()
        return False

    def set_carsharing_groups(self):
        cs_person_groups = self.get_app_person_groups()
        if cs_person_groups:
            self._set_carsharing_groups_from_data(cs_person_groups)
        else:
            self._remove_all_carsharing_groups()
        self._get_is_prepayment()

    def _set_carsharing_groups_from_data(self, current_cs_groups):
        self._create_update_current_cs_groups(current_cs_groups)
        self._clean_non_existing_cs_groups(current_cs_groups)

    def _create_update_current_cs_groups(self, current_cs_groups):
        for group_name in current_cs_groups.keys():
            db_group = self.env['smp.sm_group'].search(
                [('name', '=', group_name)])
            if db_group.exists():
                update_data = self._prepare_cs_group_data(
                    db_group[0], current_cs_groups[group_name])
                cs_member_group = self.env['sm_partago_user.carsharing_member_group'].search([
                    ('related_member_id', '=', self.id),
                    ('related_group_id', '=', db_group[0].id)
                ])
                if cs_member_group.exists():
                    cs_member_group[0].write(update_data)  # update
                else:
                    new_cs_group = self.env['sm_partago_user.carsharing_member_group'].create(
                        update_data)

    def _clean_non_existing_cs_groups(self, current_cs_groups):
        if self.cs_member_group_ids:
            for cs_member_group in self.cs_member_group_ids:
                delete_group = True
                if cs_member_group.related_group_id:
                    if cs_member_group.related_group_id.name in current_cs_groups.keys():
                        delete_group = False
                if delete_group:
                    cs_member_group.unlink()

    def _remove_all_carsharing_groups(self):
        if self.cs_member_group_ids:
            for cs_member_group in self.cs_member_group_ids:
                cs_member_group.unlink()

    def _prepare_cs_group_data(self, db_group, current_cs_group):
        app_db_utils = smp_db_utils.get_instance(self)
        data = {
            'related_member_id': self.id,
            'related_group_id': db_group.id
        }

        data['role'] = ''
        if 'role' in current_cs_group.keys():
            if current_cs_group['role'] is not None:
                data['role'] = current_cs_group['role']

        data['admin_role'] = ''
        if 'adminRole' in current_cs_group.keys():
            if current_cs_group['adminRole'] is not None:
                data['admin_role'] = current_cs_group['adminRole']

        data['related_billingaccount_id'] = False
        if 'billingAccountId' in current_cs_group.keys():
            if current_cs_group['billingAccountId']:
                app_db_utils.update_system_ba_from_app_ba(
                    self, current_cs_group['billingAccountId'])
            db_ba = self.env['smp.sm_billing_account'].search(
                [('name', '=', current_cs_group['billingAccountId'])])
            if db_ba.exists():
                data['related_billingaccount_id'] = db_ba[0].id

        return data

    #
    # UI ACTIONS
    #
    @api.model
    def recompute_member_cs_registration_info_action(self):
        if self.env.context:
            if 'active_ids' in self.env.context:
                members = self.env['res.partner'].browse(
                    self.env.context['active_ids'])
                if members.exists():
                    for member in members:
                        member.recompute_cs_registration_info()

    @api.multi
    def set_registration_coupon_from_action(self):
        if self.env.context:
            if 'active_ids' in self.env.context:
                members = self.env['res.partner'].browse(
                    self.env.context['active_ids'])
                if members.exists():
                    for member in members:
                        if member.vat:
                            member.set_registration_coupon()
        return

    @api.model
    def get_carsharing_groups_action(self):
        app_db_utils = smp_db_utils.get_instance(self)
        app_db_utils.update_all_system_db_data_from_app_db(self)
        if self.env.context:
            if 'active_ids' in self.env.context:
                members = self.env['res.partner'].browse(
                    self.env.context['active_ids'])
                if members.exists():
                    for member in members:
                        member.set_carsharing_groups()

    @api.model
    def recompute_registration_emaillink_action(self):
        if self.env.context:
            if 'active_ids' in self.env.context:
                members = self.env['res.partner'].browse(
                    self.env.context['active_ids'])
                if members.exists():
                    for member in members:
                        error = member.recompute_send_app_registration_email()
                        if error:
                            return self._resources.get_successful_action_message(self, error, self._name)
                        else:
                            return self._resources.get_successful_action_message(self, _("Action: OK"), self._name)

    @api.model
    def complete_registration_requests_action(self):
        if self.env.context:
            if 'active_ids' in self.env.context:
                members = self.env['res.partner'].browse(
                    self.env.context['active_ids'])
                if members.exists():
                    for member in members:
                        if member.cs_registration_request_ids:
                            for registration_request in member.cs_registration_request_ids:
                                if registration_request.completed_behaviour == 'not_computed':
                                    registration_request.compute_request()

    @api.model
    def block_user_action(self):
        if self.env.context:
            if 'active_ids' in self.env.context:
                member = self.env['res.partner'].browse(
                    self.env.context['active_ids'])
            if member:
                member.ensure_one()
                groups = member.get_app_person_groups()
                app_db_utils = smp_db_utils.get_instance(self)
                for group in groups.keys():
                    app_db_utils.delete_app_person_from_groups(
                        member.cs_person_index, group)
                self.get_carsharing_groups_action()
                member.cs_state = 'blocked_banned'

    @api.model
    def get_register_in_carsharing_view_action(self):
        if self.env.context:
            if 'active_ids' in self.env.context:
                members = self.env['res.partner'].browse(
                    self.env.context['active_ids'])
                if members.exists():
                    for member in members:
                        data = {'current_member': member.id}
                        return {
                            'type': 'ir.actions.act_window',
                            'name': "Register in carsharings",
                            'res_model': 'partago_user.sm_carsharing_registration_wizard',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_id': self.env['partago_user.sm_carsharing_registration_wizard'].create(data).id,
                            'view_id': self.get_registration_view(),
                            'target': 'new'
                        }

    @api.model
    def change_app_email_action(self):
        if self.env.context:
            if 'active_ids' in self.env.context:
                member = self.env['res.partner'].browse(
                    self.env.context['active_ids'])
                if member:
                    member.ensure_one()
                    data = {'current_member': member.id}
                    return {
                        'type': 'ir.actions.act_window',
                        'name': "Change APP Email",
                        'res_model': 'sm_partago_user.sm_change_email_wizard',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_id': self.env['sm_partago_user.sm_change_email_wizard'].create(data).id,
                        'view_id': self.get_change_email_view(),
                        'target': 'new'
                    }

    def view_on_app_action(self):
        company = self.env.user.company_id
        return {
            'type': 'ir.actions.act_url',
            'url': '%s/admin/#/persons/%s' % (company.sm_carsharing_api_credentials_cs_url, self.cs_person_index),
            'target': 'blank'
        }
