# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdLoaiSanPham(models.Model):
    _name = "bsd.loai_sp"
    _rec_name = 'bsd_ma_nhom'
    _description = 'Thông tin loại sản phẩm'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten_nhom = fields.Char(string="Tên nhóm", required=True, help="Tên nhóm sản phẩm")
    bsd_ma_nhom = fields.Char(string="Mã nhóm", required=True, help="Mã nhóm sản phẩm")
    _sql_constraints = [
        ('bsd_ma_nhom_unique', 'unique (bsd_ma_nhom)',
         'Mã loại sản phẩm đã tồn tại !'),
    ]
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True, help="Tên dự án")
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", help="Tên tòa nhà")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")

    def name_get(self):
        res = []
        for loai in self:
            res.append((loai.id, loai.bsd_ten_nhom))
        return res
