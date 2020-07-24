# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardCKCSTT(models.TransientModel):
    _name = 'bsd.wizard.ck_cstt'
    _description = 'Ghi nhận lý do từ chối'

    def _get_ck_cstt(self):
        ck_cstt = self.env['bsd.ck_cstt'].browse(self._context.get('active_ids', []))
        return ck_cstt

    bsd_ck_cstt_id = fields.Many2one('bsd.ck_cstt', string="Chiết khấu", default=_get_ck_cstt, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_ck_cstt_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })