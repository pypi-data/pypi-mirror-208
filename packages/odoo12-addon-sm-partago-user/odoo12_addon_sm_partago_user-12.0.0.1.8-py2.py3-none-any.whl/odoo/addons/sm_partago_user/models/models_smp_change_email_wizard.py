# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.addons.sm_connect.models.models_sm_carsharing_db_utils import sm_carsharing_db_utils


class sm_change_email_wizard(models.TransientModel):
    _name = "sm_partago_user.sm_change_email_wizard"

    current_member = fields.Many2one('res.partner', string=_("Member"))
    new_email = fields.Char(string=_("New email"))
    change_in_odoo = fields.Boolean(
        string=_("Change email in Odoo"), default=True)

    @api.multi
    def change_email_action(self):
        self.ensure_one()
        member = self.current_member
        db_utils = sm_carsharing_db_utils.get_instance(self)
        if member.cs_firebase_uid:
            db_utils.delete_user_from_auth(member.cs_firebase_uid)
            db_utils.firebase_delete('users', member.cs_firebase_uid)
        db_utils.firebase_update('persons', member.cs_person_index, {
                                 'email': self.new_email})
        if self.change_in_odoo:
            member.email = self.new_email
        member.recompute_cs_registration_info()
        member.recompute_send_app_registration_email()
        return True
