# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdBaoGiaLTT(models.Model):
    _inherit = 'bsd.lich_thanh_toan'

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_dat_coc_id', string="Công nợ chứng tự", readonly=True)
    bsd_ngay_tt = fields.Datetime(compute='_compute_tien_tt', store=True)

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien_dot_tt')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tien_dot_tt - each.bsd_tien_da_tt - each.bsd_tien_dc
            each.bsd_ngay_tt = max(each.bsd_ct_ids.mapped('bsd_ngay_pb'))