# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdHdBan(models.Model):
    _inherit = 'bsd.hd_ban'

    bsd_tl_tt_hd = fields.Float(string="Tỷ lệ thanh toán HĐ", help="Tỷ lệ thanh toán hợp đồng", compute='_compute_tl_tt',
                                store=True, digits=(10, 1))

    @api.depends('bsd_ltt_ids.bsd_tien_da_tt', 'bsd_tong_gia')
    def _compute_tl_tt(self):
        for each in self:
            if each.bsd_tong_gia > 0:
                each.bsd_tl_tt_hd = sum(each.bsd_ltt_ids.mapped('bsd_tien_da_tt')) / each.bsd_tong_gia * 100