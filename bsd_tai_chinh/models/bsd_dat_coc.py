# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdDatCoc(models.Model):
    _inherit = 'bsd.dat_coc'

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_dat_coc_id', string="Công nợ chứng tự",
                                 domain=[('bsd_loai', '=', 'pt_dc')],
                                 readonly=True)
    bsd_ngay_tt = fields.Datetime(compute='_compute_tien_tt', store=True)
    # bsd_tien_ttd = fields.Monetary(compute="_compute_tien_ttd")
    bsd_thanh_toan = fields.Selection(compute='_compute_tien_tt', store=True)

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien_dc')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.filtered(lambda x: not x.bsd_dot_tt_id).mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tien_dc - each.bsd_tien_da_tt

            if each.bsd_tien_phai_tt == 0:
                each.bsd_thanh_toan = 'da_tt'
            elif 0 < each.bsd_tien_phai_tt < each.bsd_tien_dc:
                each.bsd_thanh_toan = 'dang_tt'
            else:
                each.bsd_thanh_toan = 'chua_tt'

            if each.bsd_ct_ids:
                each.bsd_ngay_tt = max(each.bsd_ct_ids.mapped('bsd_ngay_pb'))
            else:
                each.bsd_ngay_tt = None

    # R.14 Đã thanh toán đợt
    # def _compute_tien_ttd(self):
    #     for each in self:
    #         ltt_dc = each.bsd_ltt_ids.filtered(lambda l: l.bsd_gd_tt == 'dat_coc')
    #         each.bsd_tien_ttd = sum(ltt_dc.mapped('bsd_tien_da_tt'))
