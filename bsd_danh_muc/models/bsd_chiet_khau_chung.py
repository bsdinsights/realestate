# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdChietKhauChung(models.Model):
    _name = 'bsd.ck_ch'
    _rec_name = 'bsd_ten_ck_ch'
    _description = "Thông tin chiết khấu chung"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_ch = fields.Char(string="Mã chiết khấu chung", required=True)
    bsd_ten_ck_ch = fields.Char(string="Tên chiết khấu chung", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu chung")
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu chung")

    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.ck_ch_ct', 'bsd_ck_ch_id', string="Chi tiết")


class BsdChietKhauChungChiTiet(models.Model):
    _name = 'bsd.ck_ch_ct'
    _description = "Thông tin chiết khấu chung chi tiết"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = ''

    bsd_ck_ch_id = fields.Many2one('bsd.ck_ch', string="Chiết khấu chung")
    bsd_ma_ck = fields.Char(related="bsd_ck_ch_id.bsd_ma_ck")
    bsd_tu_ngay = fields.Date(related="bsd_ck_ch_id.bsd_tu_ngay")
    bsd_den_ngay = fields.Date(related="bsd_ck_ch_id.bsd_den_ngay")
    bsd_cach_tinh = fields.Selection(related="bsd_ck_ch_id.bsd_cach_tinh")
    bsd_tien_ck = fields.Monetary(related="bsd_ck_ch_id.bsd_tien_ck")
    bsd_tl_ck = fields.Float(related="bsd_ck_ch_id.bsd_tl_ck")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
