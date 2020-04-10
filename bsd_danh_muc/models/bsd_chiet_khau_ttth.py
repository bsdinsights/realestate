# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdChietKhauTTTH(models.Model):
    _name = 'bsd.ck_ttth'
    _rec_name = 'bsd_ten_ck_ttth'
    _description = "Thông tin chiết khấu thanh toán trước hạn"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_ttth = fields.Char(string="Mã chiết khấu", help="Mã chiết khấu thanh toán trước hạn",  required=True)
    _sql_constraints = [
        ('bsd_ma_ck_ttth_unique', 'unique (bsd_ma_ck_ttth)',
         'Mã chiết khấu thanh toán trước hạn đã tồn tại !'),
    ]
    bsd_ten_ck_ttth = fields.Char(string="Tên chiết khấu", help="Tên chiết khấu thanh toán trước hạn", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu thanh toán trước hạn")
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu thanh toán trước hạn")

    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.ck_ttth_ct', 'bsd_ck_ttth_id', string="Chi tiết")


class BsdChietKhauTTTHChiTiet(models.Model):
    _name = 'bsd.ck_ttth_ct'
    _description = "Thông tin chiết khấu chung chi tiết"
    _rec_name = 'bsd_chiet_khau_id'

    bsd_ck_ttth_id = fields.Many2one('bsd.ck_ttth', string="Chiết khấu TTTH")
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu", required=True,
                                        domain=[('bsd_loai_ck', '=', 'ttth'), ('state', '=', 'active')])
    bsd_ma_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ma_ck")
    bsd_tu_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_tu_ngay")
    bsd_den_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_den_ngay")
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh")
    bsd_tien_ck = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck")
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
