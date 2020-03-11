# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdTinhThanh(models.Model):
    _name = 'bsd.tinh_thanh'
    _rec_name = 'bsd_ten'
    _description = 'Danh mục tỉnh thành'

    bsd_quoc_gia_id = fields.Many2one('bsd.quoc_gia', string="Quốc gia")
    bsd_ten = fields.Char(string="Tên tỉnh thành", required=True)
    bsd_ma = fields.Char(string="Mã tỉnh thành", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_trang_thai = fields.Selection([('active', "Đang sử dụng"),
                                       ('inactive', "Không sử dụng")], string='Trạng thái', default='active')
