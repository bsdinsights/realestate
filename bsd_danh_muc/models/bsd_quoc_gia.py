# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdQuocgia(models.Model):
    _name = 'bsd.quoc_gia'
    _rec_name = 'bsd_ten'
    _description = 'Danh mục quốc gia'

    bsd_ten = fields.Char(string="Tên quốc gia", required=True)
    bsd_ma = fields.Char(string="Mã quốc gia", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_trang_thai = fields.Selection([('active', "Đang sử dụng"),
                                       ('inactive', "Không sử dụng")], string='Trạng thái', default='active')
