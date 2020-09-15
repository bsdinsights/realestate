# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán",
                                    help="Đợt mở bán hiện tại của Sản phẩm",
                                    readonly=True)
    bsd_giu_cho_ids = fields.One2many('bsd.giu_cho', 'bsd_product_tmpl_id', string="Danh sách giữ chỗ",
                                      domain=[('state', 'in', ['giu_cho', 'dat_cho'])],
                                      readonly=True)

    # Tạo giữ chỗ từ sản phẩm
    def action_tao_gc(self):
        product_id = self.env['product.product'].search([('product_tmpl_id', '=', self.id)], limit=1)
        action = self.env.ref('bsd_kinh_doanh.bsd_giu_cho_action_popup').read()[0]
        action['context'] = {'default_bsd_du_an_id': self.bsd_du_an_id.id,
                             'default_bsd_unit_id': product_id.id}
        return action
