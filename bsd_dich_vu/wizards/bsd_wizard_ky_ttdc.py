# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyttdc(models.TransientModel):
    _name = 'bsd.wizard.ky_ttdc'
    _description = 'Xác nhận ngày ký thỏa thuận đặt cọc'

    def _get_ttdc(self):
        ttdc = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return ttdc

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng bán", default=_get_ttdc, readonly=True)
    bsd_ngay_ky_ttdc = fields.Datetime(string="Ngày ký ", required=True)
    bsd_so_ttdc = fields.Char(string="Số TTĐC", required=True)

    def action_xac_nhan(self):
        self.bsd_hd_ban_id.write({
            'bsd_ngay_ky_ttdc': self.bsd_ngay_ky_ttdc,
            'bsd_so_ttdc': self.bsd_so_ttdc,
            'state': 'da_ky_ttdc'
        })

