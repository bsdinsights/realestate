# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardDKBG(models.TransientModel):
    _name = 'bsd.wizard.dk_bg'
    _description = 'Ghi nhận lý do từ chối'

    def _get_dk_bg(self):
        dk_bg = self.env['product.pricelist'].browse(self._context.get('active_ids', []))
        return dk_bg

    bsd_dk_bg_id = fields.Many2one('bsd.dk_bg', string="Điều kiện bàn giao", default=_get_dk_bg, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_dk_bg_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })