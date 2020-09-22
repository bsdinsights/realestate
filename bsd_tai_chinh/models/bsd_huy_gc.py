# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdHuyGC(models.Model):
    _inherit = 'bsd.huy_gc'

    bsd_hoan_tien_id = fields.Many2one('bsd.hoan_tien', string="Hoàn tiền", readonly=True)