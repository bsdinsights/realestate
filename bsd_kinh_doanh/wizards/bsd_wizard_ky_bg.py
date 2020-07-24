# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyBG(models.TransientModel):
    _name = 'bsd.wizard.ky_bg'
    _description = 'Xác nhận ngày ký báo giá'

    def _get_bg(self):
        bg = self.env['bsd.bao_gia'].browse(self._context.get('active_ids', []))
        return bg

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", default=_get_bg, readonly=True)
    bsd_ngay_ky_bg = fields.Datetime(string="Ngày ký báo giá", required=True)

    def action_xac_nhan(self):
        self.bsd_bao_gia_id.write({
            'bsd_ngay_ky_bg': self.bsd_ngay_ky_bg,
            'state': 'da_ky'
        })

