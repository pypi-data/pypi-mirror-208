# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _


class cs_task(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'

    related_carsharing_update_data_id = fields.Many2one(
        'sm_partago_user.carsharing_update_data', string=_("Update data - Registration"))
    related_carsharing_user_request_id = fields.Many2one(
        'sm_partago_user.carsharing_user_request', string=_("CSUserRequest"))
