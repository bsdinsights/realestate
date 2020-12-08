# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
import datetime
import logging

_logger = logging.getLogger(__name__)


class BsdWizardTTGCTC(models.TransientModel):
    _name = 'bsd.wizard.tt_gc_tc'
    _description = 'Thanh toán giữ chỗ thiện chí'
    _rec_name = 'bsd_gc_tc_id'

    bsd_ngay_pt = fields.Date(string="Ngày thanh toán", help="Ngày thanh toán", required=True,
                              default=lambda self: fields.Date.today())
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", required=True)
    bsd_tien_kh = fields.Monetary(string="Tiền khách hàng")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_gc_tc_id')
    def _onchange_gc_tc(self):
        self.bsd_du_an_id = self.bsd_gc_tc_id.bsd_du_an_id.id
        self.bsd_tien_kh = self.bsd_gc_tc_id.bsd_tien_phai_tt

    def action_tao(self):
        # Tạo thanh toán
        now = datetime.datetime.now()
        get_time = now.replace(year=self.bsd_ngay_pt.year,
                               month=self.bsd_ngay_pt.month,
                               day=self.bsd_ngay_pt.day)
        phieu_thu = self.env['bsd.phieu_thu'].create({
            'bsd_ngay_pt': get_time,
            'bsd_loai_pt': 'gc_tc',
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_gc_tc_id': self.bsd_gc_tc_id.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_tien_kh': self.bsd_tien_kh,
        })
        # Kiểm tra số tiền còn phải thu của giữ chỗ thiện chí
        gc_tc = self.env['bsd.cong_no_ct'].search([('bsd_gc_tc_id', '=', self.bsd_gc_tc_id.id),
                                                  ('state', '=', 'hieu_luc')])
        # Kiểm tra số tiền đã thanh toán
        if gc_tc:
            tien_da_tt = sum(gc_tc.mapped('bsd_tien_pb'))
        else:
            tien_da_tt = 0
        # Tính tiền phân bổ
        if self.bsd_gc_tc_id.bsd_tien_gc - tien_da_tt >= self.bsd_tien_kh:
            tien_tt = self.bsd_tien_kh
        else:
            tien_tt = self.bsd_gc_tc_id.bsd_tien_gc - tien_da_tt
        self.env['bsd.cong_no_ct'].create({
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_gc_tc_id': self.bsd_gc_tc_id.id,
            'bsd_phieu_thu_id': phieu_thu.id,
            'bsd_tien_pb': tien_tt,
            'bsd_loai': 'pt_gctc',
            'state': 'nhap',
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Thanh toán',
            'res_model': 'bsd.phieu_thu',
            'res_id': phieu_thu.id,
            'target': 'current',
            'view_mode': 'form'
        }