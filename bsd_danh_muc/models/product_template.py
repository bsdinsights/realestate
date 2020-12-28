# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bsd_pricelist_ids = fields.One2many('product.pricelist.item', 'product_tmpl_id',
                                        string="Chi tiết giá", readonly=True,
                                        domain=[('bsd_state', '=', 'duyet')])

    def action_view_gia(self):
        action = self.env.ref('bsd_danh_muc.bsd_chi_tiet_gia_action').read()[0]
        action['domain'] = [('id', 'in', self.bsd_pricelist_ids.ids)]
        return action


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_view_gia(self):
        action = self.env.ref('bsd_danh_muc.bsd_chi_tiet_gia_action').read()[0]
        action['domain'] = [('id', 'in', self.bsd_pricelist_ids.ids)]
        return action
