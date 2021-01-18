# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardKhongDuyetMienGiam(models.TransientModel):
    _name = 'bsd.wizard.khong_duyet.mien_giam'
    _description = 'Ghi nhận lý do từ chối'

    def _get_mien_giam(self):
        mien_giam = self.env['bsd.mien_giam'].browse(self._context.get('active_ids', []))
        return mien_giam

    bsd_mien_giam_id = fields.Many2one('bsd.mien_giam', string="Miễn giảm", default=_get_mien_giam, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_mien_giam_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })
        self.bsd_mien_giam_id.message_post(body='Lý do không duyệt: ' + self.bsd_ly_do)
        for ct in self.bsd_mien_giam_id.bsd_ct_ids.filtered(lambda c: c.state == 'xac_nhan'):
            ct.write({"state": "nhap"})