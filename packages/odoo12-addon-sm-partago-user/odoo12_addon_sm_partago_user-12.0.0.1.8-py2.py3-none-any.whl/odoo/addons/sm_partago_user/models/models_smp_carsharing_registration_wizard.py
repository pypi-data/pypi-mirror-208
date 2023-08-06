# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.addons.sm_partago_user.models.models_smp_user_utils import smp_user_utils


class sm_carsharing_registration_wizard(models.TransientModel):
    _name = "partago_user.sm_carsharing_registration_wizard"

    current_member = fields.Many2one('res.partner', string=_("Member"))
    force_registration = fields.Boolean(
        string=_("Force Registration"), default=False)
    registration_billing_account = fields.Boolean(
        string=_("Create billing account"), default=False)
    billing_account_minutes = fields.Integer(
        string=_("Billing account minutes"), default=300)
    group = fields.Many2one('smp.sm_group', string=_("Group"))

    @api.multi
    def register_member_action(self):
        for record in self:
            member = record.current_member
            cs_group = False
            ba_credits = 0
            ba_behaviour = 'no_ba'
            if record.group:
                cs_group = record.group.name
            if record.registration_billing_account:
                ba_credits = record.billing_account_minutes
                ba_behaviour = 'update_ba'
            record.env['sm_partago_user.carsharing_registration_request'].create({
                'related_member_id': member.id,
                'force_registration': self.force_registration,
                'group_index': cs_group,
                'ba_behaviour': ba_behaviour,
                'ba_credits': ba_credits
            })
        return True

    @api.multi
    def check_completion_action(self):
        app_user_utils = smp_user_utils.get_instance()
        app_user_utils.update_members_carsharing_registration_status(self)
