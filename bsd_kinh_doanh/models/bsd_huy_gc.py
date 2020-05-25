# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdHuyGC(models.Model):
    _name = 'bsd.huy_gc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_huy_gc'
    _description = 'Phiếu đề nghị hủy giữ chỗ'

    bsd_ma_huy_gc = fields.Char(string="Mã", help="Mã phiếu hủy", required=True)
    bsd_ngay_huy_gc = fields.Date(string="Ngày", help="Ngày hủy", required=True,
                                  default=lambda self: fields.Date.today())
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án",required=True)
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True)
    bsd_loai_gc = fields.Selection([('gc_tc', 'Giữ chỗ thiện chí'), ('giu_cho', 'Giữ chỗ')],
                                string="Loại", required=True, default='gc_tc', help="Loại phiếu hủy")
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Căn hộ")
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí bị hủy")
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ")
    bsd_tien = fields.Monetary(string="Số tiền", help="Số tiền")
    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Số tiền đã thanh toán")
    bsd_hoan_tien = fields.Boolean(string="Hoàn tiền", help="Hoàn tiền")
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             tracking=1, default="nhap", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    # KD.14.01 Xác nhận hủy giữ chỗ
    def action_xac_nhan(self):
        pass

    # KD.14.02 Duyệt hủy giữ chỗ
    def action_duyet(self):
        pass

    # KD.14.04