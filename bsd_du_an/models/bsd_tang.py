# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdFloor(models.Model):
    _name = "bsd.tang"
    _rec_name = 'bsd_ma_tang'
    _description = 'Thông tin tầng'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten_tang = fields.Char(string="Tên tầng", required=True)
    bsd_ma_tang = fields.Char(string="Mã tầng", required=True)
    bsd_stt = fields.Integer(string="Số thứ tự", help="Số thứ tự sắp xếp của tầng", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                help="Thông tin chi tiết về tòa nhà")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True)
    state = fields.Selection([('active', 'Đang sử dụng'),
                                       ('inactive', 'Ngưng sử dụng')],
                                      string="Trạng thái", default='active', required=True)

