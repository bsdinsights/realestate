# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdDieukienBanGiao(models.Model):
    _inherit = 'bsd.dk_bg'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", readonly=True,
                                    states={'nhap': [('readonly', False)]})
