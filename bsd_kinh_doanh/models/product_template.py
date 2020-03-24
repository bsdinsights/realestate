# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán",
                                    help="Đợt mở bán hiện tại của căn hộ")