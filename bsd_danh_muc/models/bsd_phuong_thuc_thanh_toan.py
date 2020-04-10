# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdPttt(models.Model):
    _name = 'bsd.pt_tt'
    _rec_name = 'bsd_ten'
    _description = 'Phương thức thanh toán'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten = fields.Char(string="Tên", required=True, help="Tên phương thức thanh toán")
    bsd_ma = fields.Char(string="Mã", required=True, help="Mã phương thức thanh toán")
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phương thức thanh toán đã tồn tại !'),
    ]
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    state = fields.Selection([('active', "Đang sử dụng"),
                              ('inactive', "Không sử dụng")], string='Trạng thái',
                             default='active', tracking=1, help="Trạng thái")
