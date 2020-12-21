# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKhongDuyetCapNhatDTTT(models.TransientModel):
    _name = 'bsd.wizard.cn_dttt'
    _description = 'Ghi nhận lý do từ chối'

    def _get_cn_DTTT(self):
        cn_dttt = self.env['bsd.cn_dttt'].browse(self._context.get('active_ids', []))
        return cn_dttt

    bsd_cn_dttt_id = fields.Many2one('bsd.cn_dttt', string="Cập nhật DTTT", default=_get_cn_DTTT, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_cn_dttt_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })
        self.bsd_cn_dttt_id.message_post(body='Lý do không duyệt: ' + self.bsd_ly_do)
        for ct in self.bsd_cn_dttt_id.bsd_ct_ids.filtered(lambda c: c.state == 'xac_nhan'):
            ct.write({"state": "nhap"})

