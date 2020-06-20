# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardCKTTN(models.TransientModel):
    _name = 'bsd.wizard.ck_ttn'
    _description = 'Ghi nhận lý do từ chối'

    def _get_ck_ttn(self):
        ck_ttn = self.env['bsd.ck_ttn'].browse(self._context.get('active_ids', []))
        return ck_ttn

    bsd_ck_ttn_id = fields.Many2one('bsd.ck_ttn', string="Chiết khấu", default=_get_ck_ttn, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_ck_ttn_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })