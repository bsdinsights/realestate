# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyPLTTI(models.TransientModel):
    _name = 'bsd.wizard.ky_pl_tti'
    _description = 'Xác nhận ngày ký phụ lục thay đổi thông tin'

    def _get_pl_tti(self):
        tti = self.env['bsd.pl_tti'].browse(self._context.get('active_ids', []))
        return tti

    bsd_pl_tti_id = fields.Many2one('bsd.pl_tti', string="Phụ lục HĐ", default=_get_pl_tti, readonly=True)
    bsd_ngay_ky_pl = fields.Datetime(string="Ngày ký phụ lục", required=True)

    def action_xac_nhan(self):
        self.bsd_pl_tti_id.write({
            'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
            'state': 'dk_pl'
        })
        # self.bsd_pl_tti_id.update_tti()
