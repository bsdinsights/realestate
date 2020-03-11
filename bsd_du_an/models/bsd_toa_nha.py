# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdBlock(models.Model):
    _name = "bsd.toa_nha"
    _rec_name = 'bsd_ten'
    _description = 'Thông tin tòa nhà'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten = fields.Char(string="Tên tòa nhà", required=True)
    bsd_ma = fields.Char(string="Mã tòa nhà", required=True)
    bsd_so_thu_tu = fields.Char(string="Số thứ tự sắp xếp")
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                help="Thông tin chi tiết về tòa nhà",
                                required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    bsd_so_tang = fields.Integer(string="Số tầng")
    bsd_so_can_ho = fields.Integer(string="Số căn hộ")
    bsd_dia_chi = fields.Text(string="Địa chỉ", help="Địa chỉ tòa nhà")
    bsd_postal = fields.Char(string="Block Postal Code", help="Mã Postal")
