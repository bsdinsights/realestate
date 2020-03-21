# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdLoaiSanPham(models.Model):
    _name = "bsd.loai_sp"
    _rec_name = 'bsd_ten_nhom'
    _description = 'Thông tin loại sản phẩm'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten_nhom = fields.Char(string="Tên nhóm", required=True, help="Tên nhóm sản phẩm")
    bsd_ma_nhom = fields.Char(string="Mã nhóm", required=True, help="Mã nhóm sản phẩm")
    bsd_dien_giai = fields.Char(string="Diễn giải",help="Diễn giải")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active')

