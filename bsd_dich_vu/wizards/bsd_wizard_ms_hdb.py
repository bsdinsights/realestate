# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdMsHDB(models.TransientModel):
    _name = 'bsd.wizard.ms_hdb'
    _description = 'Chiết khấu mua sỉ cho hợp đồng'

    def _get_hdb(self):
        hdb = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", default=_get_hdb, readonly=True)
    bsd_khach_hang_id = fields.Many2one(related='bsd_hd_ban_id.bsd_khach_hang_id', store=True)
    bsd_tong_gia = fields.Monetary(related='bsd_hd_ban_id.bsd_tong_gia', store=True)
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu mua sỉ")
    bsd_tien_ck = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck", store=True)
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck", store=True)
    bsd_hd_ban_ids = fields.Many2many('bsd.hd_ban', string="Hợp đồng")
    bsd_tong_ck = fields.Monetary(string="Tổng chiết khấu")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        list_ck_ms = self.bsd_hd_ban_id.bsd_dot_mb_id.bsd_ck_ms_id.bsd_ct_ids.mapped('bsd_chiet_khau_id').ids
        res = {}
        res.update({
            'domain': {
                'bsd_chiet_khau_id': [('id', 'in', list_ck_ms)]
            }
        })
        _logger.debug(res)
        return res

    def action_xac_nhan(self):
        self.bsd_hd_ban_id.tao_ck_ms(self.bsd_chiet_khau_id)

