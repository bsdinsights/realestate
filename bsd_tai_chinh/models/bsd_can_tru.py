# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdCanTru(models.Model):
    _name = 'bsd.can_tru'
    _description = 'Cấn trừ công nợ khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_kh'

    bsd_ma_kh = fields.Char(string="Mã khách hàng", help="Mã khách hàng", required=True)
    bsd_khach_hang_id = fields.Many2one("res.partner", string="Tên khách hàng", help="Tên khách hàng", required=True)
    bsd_ngay_can_tru = fields.Datetime(string="Ngày cấn trừ", help="Ngày cấn trừ", required=True)
