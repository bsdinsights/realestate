# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardKhuyenMai(models.TransientModel):
    _name = 'bsd.wizard.khuyen_mai'
    _description = 'Ghi nhận lý do từ chối'

    def _get_khuyen_mai(self):
        khuyen_mai = self.env['bsd.khuyen_mai'].browse(self._context.get('active_ids', []))
        return khuyen_mai

    bsd_khuyen_mai_id = fields.Many2one('bsd.khuyen_mai', string="Khuyến mãi", default=_get_khuyen_mai, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_khuyen_mai_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })

