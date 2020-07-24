# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardCKNoiBo(models.TransientModel):
    _name = 'bsd.wizard.ck_nb'
    _description = 'Ghi nhận lý do từ chối'

    def _get_ck_nb(self):
        ck_nb = self.env['bsd.ck_nb'].browse(self._context.get('active_ids', []))
        return ck_nb

    bsd_ck_nb_id = fields.Many2one('bsd.ck_nb', string="Chiết khấu", default=_get_ck_nb, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_ck_nb_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })