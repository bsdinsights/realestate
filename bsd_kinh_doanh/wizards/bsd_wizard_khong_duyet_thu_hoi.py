# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyBG(models.TransientModel):
    _name = 'bsd.wizard.thu_hoi'
    _description = 'Ghi nhận lý do từ chối'

    def _get_thu_hoi(self):
        thu_hoi = self.env['bsd.thu_hoi'].browse(self._context.get('active_ids', []))
        return thu_hoi

    bsd_thu_hoi_id = fields.Many2one('bsd.thu_hoi', string="Thu hồi", default=_get_thu_hoi, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_thu_hoi_id.write({
            'bsd_ly_do_khong_duyet': self.bsd_ly_do,
            'state': 'huy',
        })

