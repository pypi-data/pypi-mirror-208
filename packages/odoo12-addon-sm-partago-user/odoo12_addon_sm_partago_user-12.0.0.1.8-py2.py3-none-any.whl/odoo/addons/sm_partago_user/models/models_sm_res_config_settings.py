# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cs_missing_data_email_template_id = fields.Many2one(
        related='company_id.cs_missing_data_email_template_id',
        string=_("CS missing data email"),
        readonly=False)

    cs_complete_data_soci_not_found_email_template_id = fields.Many2one(
        related='company_id.cs_complete_data_soci_not_found_email_template_id',
        string=_("CS complete data soci not found"),
        readonly=False)

    elprat_ok_mail_template_id = fields.Many2one(
        related='company_id.elprat_ok_mail_template_id',
        string=_("El Prat request successful email template"),
        readonly=False)

    elprat_notok_mail_template_id = fields.Many2one(
        related='company_id.elprat_notok_mail_template_id',
        string=_("El Prat request NOT successful email template"),
        readonly=False)
