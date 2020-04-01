# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdDkbg(models.Model):
    _name = 'bsd.dk_bg'
    _rec_name = 'bsd_ma_dkbg'
    _description = "Điều kiện bàn giao"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_dkbg = fields.Char(string="Mã", help="Mã điều kiện bàn giao", required=True)
    _sql_constraints = [
        ('bsd_ma_dkbg_unique', 'unique (bsd_ma_dkbg)',
         'Mã điều kiện bàn giao đã tồn tại !'),
    ]
    bsd_ten_dkbg = fields.Char(string="Tên", help="Tên điều kiện bàn giao", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True)
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu hiệu lực của điều kiện bàn giao", required=True)
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc hiệu lực của điều kiện bàn giao", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_loai_bg = fields.Selection([('hoan_thien', 'Bàn giao hoàn thiện'),
                                    ('tho', 'Bàn giao thô'),
                                    ('co_ban', 'Bàn giao cơ bản'),
                                    ('noi_that', 'Bàn giao có nội thất'),
                                    ('khac', 'Bàn giao khác'),
                                    ('tuy_chon', 'Bàn giao tùy chọn')], string="Loại bàn giao",
                                   help="Tình trạng của căn hộ khi bàn giao")
    bsd_dk_tt = fields.Selection([('m2', 'Giá/m2'),
                                  ('tien', 'Tiền'),
                                  ('ty_le', 'Tỷ lệ')
                                  ], string="Điều kiện thanh toán", default="m2", required=True,
                                 help="Điều kiện thanh toán để được nhận bàn giao")
    bsd_theo_ch = fields.Selection([('1', 'Có'), ('0', 'Không')], string="Theo căn hộ", default="0",
                                   help="Thông tin quy định điều kiện bàn giao sẽ được áp dụng cho căn hộ hay cả dự án")
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Tên căn hộ được áp dụng điều kiện bàn giao")
    bsd_gia_m2 = fields.Monetary(string="Giá/m2", help="Giá/m2 theo đợt bàn giao")
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền thanh toán theo đợt bàn giao")
    bsd_ty_le = fields.Float(string="Tỷ lệ (%)", help="Tỷ lệ thanh toán theo đợt bàn giao")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)


