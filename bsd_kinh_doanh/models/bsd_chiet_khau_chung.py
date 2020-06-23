# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdChietKhauChung(models.Model):
    _inherit = 'bsd.ck_ch'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", compute='_compute_dot_mb', store=True)
    bsd_dot_mb_ids = fields.One2many('bsd.dot_mb', 'bsd_ck_ch_id')

    @api.depends('bsd_dot_mb_ids')
    def _compute_dot_mb(self):
        for each in self:
            if len(each.bsd_dot_mb_ids) > 0:
                each.bsd_dot_mb_id = each.bsd_dot_mb_ids[0]