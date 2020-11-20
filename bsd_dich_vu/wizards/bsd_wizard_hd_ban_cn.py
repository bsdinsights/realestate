# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKhongDuyetChuyenNhuong(models.TransientModel):
    _name = 'bsd.wizard.hd_ban_cn'
    _description = 'Ghi nhận lý do từ chối'

    def _get_hd_ban_cn(self):
        hd_ban_cn = self.env['bsd.hd_ban_cn'].browse(self._context.get('active_ids', []))
        return hd_ban_cn

    bsd_hd_ban_cn_id = fields.Many2one('bsd.hd_ban_cn', string="Chuyển nhượng", default=_get_hd_ban_cn, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_hd_ban_cn_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })

