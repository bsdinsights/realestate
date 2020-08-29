# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdPSGDKM(models.TransientModel):
    _name = 'bsd.wizard.ps_gd_km'
    _description = 'Ghi nhận lý do từ chối'

    def _get_ps_gd_km(self):
        ps_gd_km = self.env['bsd.ps_gd_km'].browse(self._context.get('active_ids', []))
        return ps_gd_km

    bsd_ps_gd_km_id = fields.Many2one('bsd.ps_gd_km', string="Giao dịch khuyến mãi", default=_get_ps_gd_km, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_ps_gd_km_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'huy',
        })

