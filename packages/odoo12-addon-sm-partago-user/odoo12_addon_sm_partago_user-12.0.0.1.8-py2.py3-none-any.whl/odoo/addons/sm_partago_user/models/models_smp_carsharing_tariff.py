# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _

class smp_carsharing_tariff_carsharing_user_request(models.Model):
  _name = 'smp.sm_carsharing_tariff'
  _inherit = 'smp.sm_carsharing_tariff'
  related_carsharing_user_request_id = fields.Many2one('sm_partago_user.carsharing_user_request', string=_("Related Carsharing user request"))