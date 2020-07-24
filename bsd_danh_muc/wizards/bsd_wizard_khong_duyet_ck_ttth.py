# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardCKTTTH(models.TransientModel):
    _name = 'bsd.wizard.ck_ttth'
    _description = 'Ghi nhận lý do từ chối'

    def _get_ck_ttth(self):
        ck_ttth = self.env['bsd.ck_ttth'].browse(self._context.get('active_ids', []))
        return ck_ttth

    bsd_ck_ttth_id = fields.Many2one('bsd.ck_ttth', string="Chiết khấu", default=_get_ck_ttth, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_ck_ttth_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })