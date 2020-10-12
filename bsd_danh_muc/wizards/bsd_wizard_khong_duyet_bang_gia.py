# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardBangGia(models.TransientModel):
    _name = 'bsd.wizard.bang_gia'
    _description = 'Ghi nhận lý do từ chối'

    def _get_bang_gia(self):
        bang_gia = self.env['product.pricelist'].browse(self._context.get('active_ids', []))
        return bang_gia

    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá", default=_get_bang_gia, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_bang_gia_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })