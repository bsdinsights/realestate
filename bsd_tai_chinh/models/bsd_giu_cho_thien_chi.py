# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdGiuChoThienChi(models.Model):
    _inherit = 'bsd.gc_tc'

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_gc_tc_id', string="Công nợ chứng tự",
                                 domain=[('bsd_loai', '=', 'pt_gctc')],
                                 readonly=True)

    bsd_ngay_tt = fields.Datetime(compute='_compute_tien_tt', store=True)
    bsd_thanh_toan = fields.Selection(compute='_compute_tien_tt', store=True)
    bsd_sequence_gc_tc_id = fields.Many2one('ir.sequence', string="STT giữ chỗ thiện chí")

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien_gc')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tien_gc - each.bsd_tien_da_tt

            if each.bsd_tien_phai_tt == 0:
                each.bsd_thanh_toan = 'da_tt'
            elif 0 < each.bsd_tien_phai_tt < each.bsd_tien_gc:
                each.bsd_thanh_toan = 'dang_tt'
            else:
                each.bsd_thanh_toan = 'chua_tt'

            if each.bsd_ct_ids:
                each.bsd_ngay_tt = max(each.bsd_ct_ids.mapped('bsd_ngay_pb'))
            else:
                each.bsd_ngay_tt = None

    # Tạo thanh toán
    def action_thanh_toan(self):
        context = {
            'default_bsd_loai_pt': 'gc_tc',
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_gc_tc_id': self.id,
        }
        action = self.env.ref('bsd_tai_chinh.bsd_phieu_thu_action_popup').read()[0]
        action['context'] = context
        return action

    # Sinh số thứ tự cho phiếu
    def create_stt(self):
        stt = self.bsd_du_an_id.bsd_sequence_gc_tc_id.next_by_code(self.bsd_du_an_id.bsd_ma_da)
        self.write({
            'bsd_stt': stt,
        })