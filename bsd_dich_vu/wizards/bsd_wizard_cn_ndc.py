# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKhongDuyetCapNhatNDC(models.TransientModel):
    _name = 'bsd.wizard.cn_ndc'
    _description = 'Ghi nhận lý do từ chối'

    def _get_cn_ndc(self):
        cn_ndc = self.env['bsd.cn_ndc'].browse(self._context.get('active_ids', []))
        return cn_ndc

    bsd_cn_ndc_id = fields.Many2one('bsd.cn_ndc', string="Cập nhật ĐHTT", default=_get_cn_ndc, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_cn_ndc_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'huy',
        })

