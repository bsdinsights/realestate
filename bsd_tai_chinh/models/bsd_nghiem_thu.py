# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdNghiemThu(models.Model):
    _inherit = 'bsd.nghiem_thu'

    bsd_phi_ps_id = fields.Many2one('bsd.phi_ps', string="Phí phát sinh", readonly=True,
                                    help="Phí phát sinh từ lần nghiệm thu trước")
    bsd_tt_thanh_toan = fields.Selection(related="bsd_phi_ps_id.bsd_thanh_toan", store=True, string="TT thanh toán")
