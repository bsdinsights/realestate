# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardCKChung(models.TransientModel):
    _name = 'bsd.wizard.ck_ch'
    _description = 'Ghi nhận lý do từ chối'

    def _get_ck_ch(self):
        ck_ch = self.env['bsd.ck_ch'].browse(self._context.get('active_ids', []))
        return ck_ch

    bsd_ck_ch_id = fields.Many2one('bsd.ck_ch', string="Chiết khấu", default=_get_ck_ch, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_ck_ch_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })