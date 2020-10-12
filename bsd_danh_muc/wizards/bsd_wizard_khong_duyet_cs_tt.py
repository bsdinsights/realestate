# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardCSTT(models.TransientModel):
    _name = 'bsd.wizard.cs_tt'
    _description = 'Ghi nhận lý do từ chối'

    def _get_cs_tt(self):
        cs_tt = self.env['bsd.cs_tt'].browse(self._context.get('active_ids', []))
        return cs_tt

    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="Chiết khấu", default=_get_cs_tt, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_cs_tt_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })