# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdPhatSinhGiaoDichChietKhau(models.Model):
    _name = 'bsd.ps_gd_ck'
    _rec_name = 'bsd_ten_ck'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Ghi nhận phát sinh chiết khấu giao dịch'

    bsd_ma_ck = fields.Char(string="Mã chiết khấu", required=True, help="Mã chiết khấu")
    _sql_constraints = [
        ('bsd_ma_ck_unique', 'unique (bsd_ma_ck)',
         'Mã chiết khấu đã tồn tại !'),
    ]
    bsd_ten_ck = fields.Char(string="Tên chiết khấu", required=True, help="Tên chiết khấu")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng")
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ")
    bsd_loai_ck = fields.Selection([('chung', 'Chung'),
                                    ('noi_bo', 'Nội bộ'),
                                    ('mua_si', 'Mua sỉ'),
                                    ('ltt', 'Lịch thanh toán'),
                                    ('ttth', 'Thanh toán trước hạn'),
                                    ('ttn', 'Thanh toán nhanh')], string="Loại chiết khấu",
                                   default='chung', required=True, help="Loại chiết khấu")
    bsd_ltt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", help="Đợt thanh toán")
    bsd_sn_th = fields.Integer(string="Số ngày trước hạn", help="Số ngày dùng để tính thanh toán trước hạn")
    bsd_tien_dot_tt = fields.Monetary(string="Số tiền thanh toán", help="Số tiền thanh toán của đợt thanh toán")
    bsd_tl_ck = fields.Float(string="Tỷ lệ chiết khấu", help="Tỷ lệ chiết khấu")
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền")
    bsd_tien_ck = fields.Monetary(string="Tiền chiết khấu", help="Tiền chiết khấu")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)