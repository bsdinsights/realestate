# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán",
                                    help="Đợt mở bán hiện tại của Sản phẩm",
                                    readonly=True)
    bsd_giu_cho_ids = fields.One2many('bsd.giu_cho', 'bsd_product_tmpl_id', string="DS giữ chỗ",
                                      readonly=True)
    bsd_quan_tam_ids = fields.One2many('bsd.quan_tam', 'bsd_product_tmpl_id', domain=[('state', '=', 'xac_nhan')],
                                       string="DS quan tâm")
    bsd_so_qt = fields.Integer(string="# Số quan tâm", compute="_compute_so_qt", store=True)

    @api.depends('bsd_quan_tam_ids')
    def _compute_so_qt(self):
        for each in self:
            each.bsd_so_qt = len(each.bsd_quan_tam_ids)

    # Tạo giữ chỗ từ sản phẩm
    def action_tao_gc(self):
        product_id = self.env['product.product'].search([('product_tmpl_id', '=', self.id)], limit=1)
        action = self.env.ref('bsd_kinh_doanh.bsd_giu_cho_action_popup').read()[0]
        action['context'] = {'default_bsd_du_an_id': self.bsd_du_an_id.id,
                             'default_bsd_unit_id': product_id.id}
        return action


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Tạo giữ chỗ từ sản phẩm
    def action_tao_gc(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_giu_cho_action_popup').read()[0]
        action['context'] = {'default_bsd_du_an_id': self.bsd_du_an_id.id,
                             'default_bsd_unit_id': self.id}
        return action
