# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng")
    bsd_ngay_ky_hdb = fields.Datetime(related='bsd_hd_ban_id.bsd_ngay_ky_hdb')
    bsd_lan_tl = fields.Integer(string="Lần thanh lý",
                                help="Số lần căn hộ bị thanh lý hợp đồng")
    bsd_tt_vay = fields.Selection([('0', 'Không'),
                                   ('1', 'Có')], string="Tình trạng vay", default='0',
                                  help="Tình trạng vay ngân hàng của căn hộ")
