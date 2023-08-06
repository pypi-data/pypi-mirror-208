# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class sm_company(models.Model):
    _inherit = 'res.company'

    cs_missing_data_email_template_id = fields.Many2one(
        'mail.template',
        string=_("CS missing data email"))
    cs_complete_data_soci_not_found_email_template_id = fields.Many2one(
        'mail.template',
        string=_("CS complete data soci not found"))
    elprat_ok_mail_template_id = fields.Many2one(
        'mail.template',
        string=_("El Prat request successful email template"))
    elprat_notok_mail_template_id = fields.Many2one(
        'mail.template',
        string=_("El Prat request NOT successful email template"))
