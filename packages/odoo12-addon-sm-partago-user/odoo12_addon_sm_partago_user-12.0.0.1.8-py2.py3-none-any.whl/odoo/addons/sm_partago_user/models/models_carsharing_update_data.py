# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.addons.sm_maintenance.models.models_sm_utils import sm_utils
from odoo.addons.sm_maintenance.models.models_sm_resources import sm_resources


class carsharing_update_data(models.Model):
    _name = 'sm_partago_user.carsharing_update_data'

    related_member_id = fields.Many2one(
        'res.partner', string=_("Related member"))
    parent_id = fields.Many2one('res.partner', string=_("Related company"))
    form_id = fields.Char(string=_("wp entry ID"))
    cs_update_type = fields.Char(string=_("Registration type"))
    cs_update_name = fields.Char(string=_("Firstname"))
    cs_update_first_surname = fields.Char(string=_("First surname"))
    cs_update_second_surname = fields.Char(string=_("Second surname"))
    cs_update_dni = fields.Char(string=_("DNI/NIF"))
    cs_update_dni_image = fields.Char(string=_("DNI/NIF Image"))
    cs_update_email = fields.Char(string=_("Email"))
    cs_update_mobile = fields.Char(string=_("Phone"))
    cs_update_birthday = fields.Date(string=_("Birthdate"))
    cs_update_driving_license_expiration_date = fields.Date(
        string=_("Driving license. Expiricy date"))
    cs_update_image_driving_license = fields.Char(
        string=_("Driving license. Image"))
    cs_update_comments = fields.Char(string=_("Comments"))
    cs_update_cif = fields.Char(string=_("CIF"))
    cs_update_group = fields.Char(string=_("Group"))
    cs_update_group_secondary = fields.Char(string=_("Group (secondary"))
    cs_complete_date = fields.Date(string=_("Completed Date"))
    state = fields.Selection([
        ('new', 'New'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='new')
    final_state = fields.Selection([
        ('not_completed', 'Not completed'),
        ('cs_company_member', 'CS company member created & registration request'),
        ('soci_not_found', 'Soci not found'),
        ('error', 'Error.'),
        ('data_updated', 'Data updated & registration request'),
        ('cancelled', 'Cancelled')
    ], default='not_completed')
    cs_registration_request_ids = fields.One2many(
        comodel_name='sm_partago_user.carsharing_registration_request',
        inverse_name='related_cs_update_data_id',
        string=_("Registration request:")
    )
    cron_executed = fields.Boolean(string=_("Cron executed"))

    _order = "id desc"

    @api.multi
    def complete_cron(self):
        if self.final_state == 'not_completed':
            func_ret_data = self.complete_request(True)
            self._set_completed(
                func_ret_data['final_state'],
                func_ret_data['mail_template']
            )
            self.write({
                'cron_executed': True
            })

    def complete_action(self):
        resources = sm_resources.getInstance()
        if self.final_state == 'not_completed':
            func_ret_data = self.complete_request()
            if func_ret_data['error_msg']:
                return resources.get_successful_action_message(
                    self,
                    func_ret_data['error_msg'],
                    self._name
                )
            else:
                self._set_completed(
                    func_ret_data['final_state'],
                    func_ret_data['mail_template']
                )
                return resources.get_successful_action_message(
                    self,
                    _("Completed successfully"),
                    self._name
                )
        else:
            return resources.get_successful_action_message(
                self,
                _("Can't complete an already completed request."),
                self._name
            )

    def cancel_action(self):
        self._set_cancelled()

    def complete_request(self, notify_admin_or_user=False):
        final_state = 'not_completed'
        mail_template = False
        error_msg = False
        error_subject = _("Update data / registration error.")
        overwrite_project_id = 9
        # COMPANY REGISTRATION
        if self.cs_update_type == "company":
            error_msg = self._complete_company_request()
            if error_msg:
                final_state = 'error'
                if notify_admin_or_user:
                    sm_utils.create_system_task_csupdatedata(
                        self,
                        error_subject,
                        error_msg,
                        self.id,
                        overwrite_project_id
                    )
            else:
                final_state = 'cs_company_member'
        # MEMBER UPDATE / CS REGISTRATION
        else:
            success = self._fetch_related_member()
            if success:
                error_msg = self._complete_cs_user_request()
                if error_msg:
                    final_state = 'error'
                    if notify_admin_or_user:
                        sm_utils.create_system_task_csupdatedata(
                            self,
                            error_subject,
                            error_msg,
                            self.id,
                            overwrite_project_id
                        )
                else:
                    final_state = 'data_updated'
            else:
                final_state = 'soci_not_found'
                error_msg = _("Contact not found on the system")
                if notify_admin_or_user:
                    mail_template = 'cs_complete_data_soci_not_found_email_template_id'
        return {
            'final_state': final_state,
            'mail_template': mail_template,
            'error_msg': error_msg
        }

    # returns error if exists
    def _complete_company_request(self):
        success = self._create_company_user()
        if success:
            return self._validate_and_create_postpayment_registration_requests()
        else:
            return _("Cannot create company member. Company not found.")

    # return an error if exists
    def _complete_cs_user_request(self):
        # Get carsharing groups and carsharing status
        self.related_member_id.set_carsharing_groups()
        # Recompute carsharing status
        self.related_member_id.recompute_cs_registration_info()
        # Update personal data
        self._update_cs_data()
        # Registrations
        # prepayment user
        if self.related_member_id.is_prepayment:
            return self._validate_and_create_prepayment_registration_requests()
        # user without memberships (new)
        elif not self.related_member_id.has_memberships():
            return self._validate_and_create_postpayment_registration_requests()
        # postpayment
        else:
            return self._validate_and_create_postpayment_registration_requests()

    def _validate_and_create_prepayment_registration_requests(self):
        valid = self._validate_prepayment_registration_request()
        if valid:
            self._create_prepayment_registration_request()
            return False
        else:
            return _("Prepayment group configuration not valid")

    def _validate_and_create_postpayment_registration_requests(self):
        valid = self._validate_postpayment_registration_request()
        if valid:
            self._create_postpayment_registration_request()
            return False
        else:
            return _("Postpayment group configuration not valid")

    def _validate_prepayment_registration_request(self):
        if self.cs_update_group:
            rel_group = self._get_db_group_by_index(self.cs_update_group)
            if rel_group:
                if not rel_group.is_prepayment:
                    return False
            else:
                return False
        if self.cs_update_group_secondary:
            rel_group = self._get_db_group_by_index(
                self.cs_update_group_secondary)
            if rel_group:
                if not rel_group.is_prepayment:
                    return False
            else:
                return False
        return True

    def _validate_postpayment_registration_request(self):
        if self.cs_update_group:
            rel_group = self._get_db_group_by_index(self.cs_update_group)
            if rel_group:
                if rel_group.is_prepayment:
                    return False
            else:
                return False
        if self.cs_update_group_secondary:
            rel_group = self._get_db_group_by_index(
                self.cs_update_group_secondary)
            if rel_group:
                if rel_group.is_prepayment:
                    return False
            else:
                return False
        return True

    def _create_postpayment_registration_request(self):
        if self.cs_update_group:
            self._create_registration_request(
                self.cs_update_group,
                'no_ba'
            )
        else:
            company = self.env.user.company_id
            self._create_registration_request(
                company.sm_user_person_group,
                'no_ba'
            )
        if self.cs_update_group_secondary:
            self._create_registration_request(
                self.cs_update_group_secondary,
                'no_ba'
            )

    def _create_prepayment_registration_request(self):
        if self.cs_update_group:
            self._create_registration_request(
                self.cs_update_group,
                'update_ba'
            )
        else:
            company = self.env.user.company_id
            self._create_registration_request(
                company.sm_user_person_group_general_prepayment,
                'update_ba'
            )
        if self.cs_update_group_secondary:
            self._create_registration_request(
                self.cs_update_group_secondary,
                'update_ba'
            )

    def _create_registration_request(self, group_index, ba_behaviour):
        self.env['sm_partago_user.carsharing_registration_request'].create({
            'related_member_id': self.related_member_id.id,
            'force_registration': False,
            'group_index': group_index,
            'ba_behaviour': ba_behaviour,
            'related_cs_update_data_id': self.id
        })

    def _fetch_related_member(self):
        update_dni = str(self.cs_update_dni).replace(
            "-", "").replace(" ", "").upper()
        query = [('vat', '=', update_dni),
                 ('cs_user_type', '!=', 'organisation')]
        related_members = self.env['res.partner'].search(query, order="id asc")
        if related_members.exists():
            # return first related member having same email
            for rmember in related_members:
                if rmember.email == self.cs_update_email:
                    self.write({'related_member_id': rmember.id})
                    return True
            # return first related member for query
            self.write({'related_member_id': related_members[0].id})
            return True
        return False

    def _set_completed(self, final_state=False, mail_template=False):
        if final_state != 'not_completed':
            u_data = {
                'state': 'completed',
                'cs_complete_date': datetime.today(),
                'final_state': final_state
            }
            if mail_template:
                if mail_template == 'cs_complete_data_soci_not_found_email_template_id':
                    sm_utils.send_email_from_template(self, mail_template)
                else:
                    sm_utils.send_email_from_template(
                        self.related_member_id, mail_template)
            self.write(u_data)

    def _set_cancelled(self):
        self.write({
            'state': 'cancelled',
            'cs_complete_date': datetime.today(),
            'final_state': 'cancelled'
        })

    def _get_db_group_by_index(self, group_index):
        rel_groups = self.env['smp.sm_group'].search([
            ('name', '=', group_index)
        ])
        if rel_groups.exists():
            return rel_groups[0]
        return False

    #
    # CS USERS: UPDATE
    #
    def _update_cs_data(self):
        if self.related_member_id:
            self.related_member_id.write(self._get_update_data())

    def _get_update_data(self):
        cs_member_dict = {}
        if self.cs_update_name:
            cs_member_dict["firstname"] = self.cs_update_name
        lastname = ''
        if self.cs_update_first_surname:
            lastname += self.cs_update_first_surname
        if self.cs_update_second_surname:
            lastname += " "+self.cs_update_second_surname
        if lastname != '':
            cs_member_dict["lastname"] = lastname
        if self.cs_update_dni:
            cs_member_dict["vat"] = self.cs_update_dni
        if self.cs_update_email:
            cs_member_dict["email"] = self.cs_update_email
        if self.cs_update_mobile:
            cs_member_dict["mobile"] = self.cs_update_mobile
        if self.cs_update_birthday:
            cs_member_dict["birthdate_date"] = self.cs_update_birthday
        if self.parent_id and self.cs_update_type == "company":
            cs_member_dict["parent_id"] = self.parent_id.id
        if self.cs_update_driving_license_expiration_date:
            cs_member_dict["driving_license_expiration_date"] = self.cs_update_driving_license_expiration_date
        if self.cs_update_image_driving_license:
            cs_member_dict["image_driving_license"] = self.cs_update_image_driving_license
        if self.cs_update_dni_image:
            cs_member_dict["image_dni"] = self.cs_update_dni_image

        return cs_member_dict

    #
    # COMPANY USERS
    #
    def _compute_related_company(self):
        related_company = self.env['res.partner'].search([
            ('vat', '=', str(self.cs_update_cif).replace(" ", "").upper()),
            ('is_company', '=', True)
        ], order="id desc")
        if related_company.exists():
            self.write({'parent_id': related_company[0].id})
            return True
        return False

    def _create_company_user(self):
        success = self._compute_related_company()
        if success:
            self._create_member({
                'cs_user_type': 'organisation',
                'is_company': False,
                'company_type': 'person',
                'lang': 'ca_ES'
            })
            return True
        return False

    def _create_member(self, extra_data={}):
        u_data = self._get_update_data()
        u_data.update(extra_data)
        new_member = self.env['res.partner'].create(u_data)
        self.write({'related_member_id': new_member.id})
        return True
