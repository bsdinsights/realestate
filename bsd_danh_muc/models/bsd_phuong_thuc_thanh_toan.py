# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdPttt(models.Model):
    _name = 'bsd.pt_tt'
    _rec_name = 'bsd_ten'
    _description = 'Phương thức thanh toán'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten = fields.Char(string="Tên", required=True)
    bsd_ma = fields.Char(string="Mã", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    state = fields.Selection([('active', "Đang sử dụng"),
                                       ('inactive', "Không sử dụng")], string='Trạng thái', default='active')
