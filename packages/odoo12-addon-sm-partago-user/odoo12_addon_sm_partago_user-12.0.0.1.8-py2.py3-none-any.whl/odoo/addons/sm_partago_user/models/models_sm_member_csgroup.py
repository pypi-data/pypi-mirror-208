# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _


class carsharing_member_group(models.Model):
    _name = 'sm_partago_user.carsharing_member_group'

    related_member_id = fields.Many2one(
        'res.partner',
        string=_("Related member")
    )
    related_group_id = fields.Many2one(
        'smp.sm_group',
        string=_("Cs group")
    )
    related_billingaccount_id = fields.Many2one(
        'smp.sm_billing_account',
        string=_("Cs billingAccount")
    )
    role = fields.Char(string=_("Role in this group"))
    admin_role = fields.Char(string=_("Admin Role in this group"))
    related_billingaccount_minutesleft = fields.Float(
        string=_("Minutes left (BillingAccount)"),
        compute="_get_billingaccount_minutesleft",
        store=False
    )
    default_billingaccount_id = fields.Many2one(
        'smp.sm_billing_account',
        string=_("default billingAccount"),
        compute="_get_default_billingaccount_id",
        store=True
    )
    default_billingaccount_minutesleft = fields.Float(
        compute="_get_default_billingaccount_minutesleft",
        string=_("minutes Left (default billingAccount)"),
        store=False
    )
    is_prepayment = fields.Boolean(
        string=_("Prepayment"),
        compute="_get_is_prepayment",
        store=False
    )

    @api.depends('related_billingaccount_id')
    def _get_billingaccount_minutesleft(self):
        for record in self:
            if record.related_billingaccount_id:
                record.related_billingaccount_minutesleft = record.related_billingaccount_id.minutesLeft

    @api.depends('related_group_id')
    def _get_default_billingaccount_id(self):
        for record in self:
            if record.related_group_id:
                if record.related_group_id.related_billingaccount_id:
                    record.default_billingaccount_id = record.related_group_id.related_billingaccount_id

    @api.depends('default_billingaccount_id')
    def _get_default_billingaccount_minutesleft(self):
        for record in self:
            if record.default_billingaccount_id:
                record.default_billingaccount_minutesleft = record.default_billingaccount_id.minutesLeft

    @api.depends('related_group_id')
    def _get_is_prepayment(self):
        for record in self:
            if record.related_group_id.is_prepayment:
                record.is_prepayment = True
