# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKhongDuyetCapNhatDKBG(models.TransientModel):
    _name = 'bsd.wizard.cn_dkbg'
    _description = 'Ghi nhận lý do từ chối'

    def _get_cn_dkbg(self):
        cn_dkbg = self.env['bsd.cn_dkbg'].browse(self._context.get('active_ids', []))
        return cn_dkbg

    bsd_cn_dkbg_id = fields.Many2one('bsd.cn_dkbg', string="Cập nhật DKBG", default=_get_cn_dkbg, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_cn_dkbg_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })
        self.bsd_cn_dkbg_id.message_post(body='Lý do không duyệt: ' + self.bsd_ly_do)
        for ct in self.bsd_cn_dkbg_id.bsd_ct_ids.filtered(lambda c: c.state == 'xac_nhan'):
            ct.write({"state": "nhap"})

