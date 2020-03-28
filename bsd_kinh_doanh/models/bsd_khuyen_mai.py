# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdKhuyenMai(models.Model):
    _inherit = 'bsd.khuyen_mai'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", required=True)
