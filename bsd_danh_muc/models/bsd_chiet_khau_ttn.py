# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdChietKhauTTN(models.Model):
    _name = 'bsd.ck_ttn'
    _rec_name = 'bsd_ten_ck_ttn'
    _description = "Thông tin chiết khấu thanh toán nhanh"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_ttn = fields.Char(string="Mã chiết khấu", help="Mã chiết khấu thanh toán nhanh", required=True)
    _sql_constraints = [
        ('bsd_ma_ck_ttn_unique', 'unique (bsd_ma_ck_ttn)',
         'Mã chiết khấu thanh toán nhanh đã tồn tại !'),
    ]
    bsd_ten_ck_ttn = fields.Char(string="Tên chiết khấu", help="Mã chiết khấu thanh toán nhanh", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu chung")
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu chung")

    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.ck_ttn_ct', 'bsd_ck_ttn_id', string="Chi tiết")


class BsdChietKhauTTNChiTiet(models.Model):
    _name = 'bsd.ck_ttn_ct'
    _description = "Thông tin chiết khấu thanh toán nhanh chi tiết"
    _rec_name = 'bsd_chiet_khau_id'

    bsd_ck_ttn_id = fields.Many2one('bsd.ck_ttn', string="Chiết khấu TTN")
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu", required=True,
                                        domain=[('bsd_loai_ck', '=', 'ttn'), ('state', '=', 'active')])
    bsd_ma_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ma_ck")
    bsd_tu_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_tu_ngay")
    bsd_den_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_den_ngay")
    bsd_ngay_tt = fields.Date(related="bsd_chiet_khau_id.bsd_ngay_tt")
    bsd_tl_tt = fields.Float(related="bsd_chiet_khau_id.bsd_tl_tt")
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh")
    bsd_tien_ck = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck")
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
