# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdRapCan(models.Model):
    _name = 'bsd.rap_can'
    _description = "Thông tin ráp căn"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_rc'

    bsd_ma_rc = fields.Char(string="Mã ráp căn")
