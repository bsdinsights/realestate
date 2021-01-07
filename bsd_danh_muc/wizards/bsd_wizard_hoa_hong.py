# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardHoaHong(models.TransientModel):
    _name = 'bsd.wizard.hoa_hong'
    _description = 'Ghi nhận lý do từ chối'

    def _get_hoa_hong(self):
        hoa_hong = self.env['bsd.hoa_hong'].browse(self._context.get('active_ids', []))
        return hoa_hong

    bsd_hoa_hong_id = fields.Many2one('bsd.hoa_hong', string="Hoa hồng", default=_get_hoa_hong, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_hoa_hong_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })
        self.bsd_hoa_hong_id.message_post(body='Lý do không duyệt: ' + self.bsd_ly_do)
