# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdChietKhau(models.Model):
    _name = 'bsd.chiet_khau'
    _rec_name = 'bsd_ten_ck'
    _description = "Thông tin chiết khấu"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck = fields.Char(string="Mã chiết khấu", required=True, help="Mã chiết khấu")
    _sql_constraints = [
        ('bsd_ma_ck_unique', 'unique (bsd_ma_ck)',
         'Mã chiết khấu đã tồn tại !'),
    ]
    bsd_ten_ck = fields.Char(string="Tên chiết khấu", required=True, help="Tên chiết khấu")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_loai_ck = fields.Selection([('chung', 'Chung'),
                                    ('noi_bo', 'Nội bộ'),
                                    ('mua_si', 'Mua sỉ'),
                                    ('ltt', 'Lịch thanh toán'),
                                    ('ttth', 'Thanh toán trước hạn'),
                                    ('ttn', 'Thanh toán nhanh')], string="Loại chiết khấu",
                                   default='chung', required=True, help="Loại chiết khấu")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án")
    bsd_cach_tinh = fields.Selection([('phan_tram', 'Phần trăm'), ('tien', 'Tiền')],
                                     help='Hình thức trả chiết khấu theo tiền hoăc theo phần trăm số tiền',
                                     string="Cách tính", required=True, default='phan_tram')
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu")
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu")
    bsd_cung_tang = fields.Boolean(string="Mua cùng tầng",
                                   help="Điều kiện xét chiết khấu mua sỉ số lượng mua có cùng chung một tầng hay không")
    bsd_sl_tu = fields.Integer(string="Số lượng từ", help="Điều kiện xét chiết khấu theo số lượng từ")
    bsd_sl_den = fields.Integer(string="Số lượng đến", help="Điều kiện xét chiết theo số lượng đến")
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="Chính sách thanh toán", help="Chính sách thanh toán")
    bsd_ngay_tt = fields.Date(string="Ngày thanh toán",
                              help="Mốc (ngày) thanh toán được sử dụng để xét thanh toán nhanh")
    bsd_tl_tt = fields.Float(string="Tỷ lệ thanh toán", help="Tỷ lệ thanh toán để được xét chiết khấu thanh toán nhanh")
    bsd_tien_ck = fields.Monetary(string="Tiền chiết khấu", help="Tiền chiết khấu được hưởng")
    bsd_tl_ck = fields.Float(string="Tỷ lệ chiết khấu", help="Tỷ lệ chiết khấu được hưởng")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)