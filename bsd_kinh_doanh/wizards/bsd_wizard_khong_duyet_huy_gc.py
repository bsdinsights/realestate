# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdHuyGC(models.TransientModel):
    _name = 'bsd.wizard.huy_gc'
    _description = 'Ghi nhận lý do từ chối'

    def _get_huy_gc(self):
        huy_gc = self.env['bsd.huy_gc'].browse(self._context.get('active_ids', []))
        return huy_gc

    bsd_huy_gc_id = fields.Many2one('bsd.huy_gc', string="Hủy giữ chỗ", default=_get_huy_gc, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_huy_gc_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'huy',
        })

