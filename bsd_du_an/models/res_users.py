# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    bsd_kh_ids = fields.Many2many('res.partner', string="Khách hàng",
                                  relation="bsd_kh_rel", column1="nvkd_id", column2="kh_id")