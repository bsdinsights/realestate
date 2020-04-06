# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductPriceList(models.Model):
    _inherit = 'product.pricelist'

    bsd_ma_bg = fields.Char(string="Mã bảng giá", required=True)
    _sql_constraints = [
        ('bsd_ma_bg_unique', 'unique (bsd_ma_bg)',
         'Mã bảng giá đã tồn tại !'),
    ]
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_ngay_bd = fields.Date(string="Ngày bắt đầu", help="Ngày bắt đầu áp dụng bảng giá", required=True)
    bsd_ngay_kt = fields.Date(string="Ngày kết thúc", help="Ngày kết thúc áp dụng bảng giá", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True)


class ProductPriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    applied_on = fields.Selection([
        ('3_global', 'All Products'),
        ('2_product_category', ' Product Category'),
        ('1_product', 'Product'),
        ('0_product_variant', 'Product Variant')], "Apply On",
        default='1_product', required=True, readonly=True,
        help='Pricelist Item applicable on selected option')
    compute_price = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('percentage', 'Percentage (discount)'),
        ('formula', 'Formula')], index=True, default='fixed', required=True, readonly=True)