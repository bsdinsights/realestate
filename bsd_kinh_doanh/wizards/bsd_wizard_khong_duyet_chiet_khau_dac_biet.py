# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardChietKhauDacBiet(models.TransientModel):
    _name = 'bsd.wizard.ck_db'
    _description = 'Ghi nhận lý do từ chối'

    def _get_chiet_khau(self):
        chiet_khau = self.env['bsd.ck_db'].browse(self._context.get('active_ids', []))
        return chiet_khau

    bsd_ck_db_id = fields.Many2one('bsd.ck_db', string="Chiết khấu đặc biệt", default=_get_chiet_khau, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_ck_db_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })