# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyBG(models.TransientModel):
    _name = 'bsd.wizard.chuyen_gc'
    _description = 'Ghi nhận lý do từ chối'

    def _get_chuyen_gc(self):
        chuyen_gc = self.env['bsd.chuyen_gc'].browse(self._context.get('active_ids', []))
        return chuyen_gc

    bsd_chuyen_gc_id = fields.Many2one('bsd.chuyen_gc', string="Chuyển giữ chỗ", default=_get_chuyen_gc, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_chuyen_gc_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'huy',
        })

