# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdKhuyenMai(models.Model):
    _name = 'bsd.khuyen_mai'
    _description = "Bảng chương trình khuyến mãi"
    _rec_name = 'bsd_ten_km'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_km = fields.Char(string="Mã khuyến mãi", help="Mã khuyến mãi", required=True)
    _sql_constraints = [
        ('bsd_ma_km_unique', 'unique (bsd_ma_km)',
         'Mã khuyến mãi đã tồn tại !'),
    ]
    bsd_ten_km = fields.Char(string="Tên khuyến mãi", help="Tên khuyến mãi", required=True)
    bsd_gia_tri = fields.Monetary(string="Giá trị", help="Giá trị (tiền) được hưởng khuyến mãi", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_loai = fields.Boolean(string="Điều kiện", help="Điều kiện xét khuyến mãi", required=True, defaule=False)
    bsd_tong_tt = fields.Monetary(string="Tổng thanh toán", help="Tổng giá trị thanh toán")
    bsd_tl_tt = fields.Float(string="Tỷ lệ thanh toán", help="Tổng tỷ lệ thanh toán")
    bsd_tu_ngay = fields.Date(string="Từ ngày", required=True, help="Ngày bắt đầu áp dụng khuyến mãi")
    bsd_den_ngay = fields.Date(string="Đến ngày", required=True, help="Ngày kết thúc áp dụng khuyến mãi")
    bsd_ngay_hldc = fields.Date(string="Ngày đặt cọc", help="Ngày hiệu lực của đặt cọc")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)