# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdPhuongXa(models.Model):
    _name = 'bsd.phuong_xa'
    _rec_name = 'bsd_ten'
    _description = 'Danh mục phường xã'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_quoc_gia_id = fields.Many2one('bsd.quoc_gia', string="Quốc gia", required=True)
    bsd_tinh_thanh_id = fields.Many2one('bsd.tinh_thanh', string="Tỉnh thành", required=True)
    bsd_quan_huyen_id = fields.Many2one('bsd.quan_huyen', string="Quận huyên", required=True)
    bsd_ten = fields.Char(string="Tên phường xã", required=True)
    bsd_ma = fields.Char(string="Mã phường xã", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_trang_thai = fields.Selection([('active', "Đang sử dụng"),
                                       ('inactive', "Không sử dụng")], string='Trạng thái', default='active')
