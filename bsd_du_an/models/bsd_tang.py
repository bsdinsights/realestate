# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdFloor(models.Model):
    _name = "bsd.tang"
    _rec_name = 'bsd_ten'
    _description = 'Thông tin tầng'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten = fields.Char(string="Tên tầng", required=True)
    bsd_ma = fields.Char(string="Mã tầng", required=True)
    bsd_so_thu_tu = fields.Char(string="Số thứ tự sắp xếp")
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                help="Thông tin chi tiết về tòa nhà",
                                required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà")
    bsd_trang_thai = fields.Selection([('active', 'Đang sử dụng'),
                                       ('inactive', 'Ngưng sử dụng')],
                                      string="Trạng thái", default='active')

