# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán",
                                    help="Đợt mở bán hiện tại của Sản phẩm")
    bsd_giu_cho_ids = fields.One2many('bsd.giu_cho', 'bsd_product_tmpl_id', string="Danh sách giữ chỗ",
                                      domain=[('state', 'in', ['giu_cho', 'dat_cho'])],
                                      readonly=True)
