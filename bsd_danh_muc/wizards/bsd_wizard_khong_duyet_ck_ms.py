# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardCKMuaSi(models.TransientModel):
    _name = 'bsd.wizard.ck_ms'
    _description = 'Ghi nhận lý do từ chối'

    def _get_ck_ms(self):
        ck_ms = self.env['bsd.ck_ms'].browse(self._context.get('active_ids', []))
        return ck_ms

    bsd_ck_ms_id = fields.Many2one('bsd.ck_ms', string="Chiết khấu", default=_get_ck_ms, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_ck_ms_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })