# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdChietKhauMuaSi(models.Model):
    _name = 'bsd.ck_ms'
    _rec_name = 'bsd_ten_ck_ms'
    _description = "Thông tin chiết khấu mua sỉ"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_ms = fields.Char(string="Mã chiết khấu mua sỉ", required=True)
    bsd_ten_ck_ms = fields.Char(string="Tên chiết khấu mua sỉ", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu mua sỉ")
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu mua sỉ")

    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.ck_ch_ct', 'bsd_ck_ch_id', string="Chi tiết")


class BsdChietKhauMuaSiChiTiet(models.Model):
    _name = 'bsd.ck_ms_ct'
    _description = "Thông tin chiết khấu mua sỉ chi tiết"
    _rec_name = 'bsd_chiet_khau_id'

    bsd_ck_ms_id = fields.Many2one('bsd.ck_ms', string="Chiết khấu mua sỉ")
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu", required=True,
                                        domain=[('bsd_loai_ck', '=', 'mua_si')])
    bsd_ma_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ma_ck")
    bsd_tu_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_tu_ngay")
    bsd_den_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_den_ngay")
    bsd_cung_tang = fields.Boolean(related="bsd_chiet_khau_id.bsd_cung_tang")
    bsd_sl_tu = fields.Integer(related="bsd_chiet_khau_id.bsd_sl_tu")
    bsd_sl_den = fields.Integer(related="bsd_chiet_khau_id.bsd_sl_den")
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh")
    bsd_tien_ck = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck")
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

