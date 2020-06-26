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

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng bán", default=_get_hdb, readonly=True)
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu mua sỉ")

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

