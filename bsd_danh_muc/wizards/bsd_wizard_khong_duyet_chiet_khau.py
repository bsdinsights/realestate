# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardChietKhau(models.TransientModel):
    _name = 'bsd.wizard.chiet_khau'
    _description = 'Ghi nhận lý do từ chối'

    def _get_chiet_khau(self):
        chiet_khau = self.env['bsd.chiet_khau'].browse(self._context.get('active_ids', []))
        return chiet_khau

    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu", default=_get_chiet_khau, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_chiet_khau_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })