# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyBG(models.TransientModel):
    _name = 'bsd.wizard.them_unit'
    _description = 'Ghi nhận lý do từ chối'

    def _get_them_unit(self):
        them_unit = self.env['bsd.them_unit'].browse(self._context.get('active_ids', []))
        return them_unit

    bsd_them_unit_id = fields.Many2one('bsd.them_unit', string="Thêm unit", default=_get_them_unit, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_them_unit_id.write({
            'bsd_ly_do_khong_duyet': self.bsd_ly_do,
            'state': 'huy',
        })

