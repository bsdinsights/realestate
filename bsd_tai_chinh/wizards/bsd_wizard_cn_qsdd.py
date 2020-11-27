# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdWizardKhongDuyetCNQSDD(models.TransientModel):
    _name = 'bsd.wizard.khong_duyet.cn_qsdd'
    _description = 'Ghi nhận lý do từ chối'

    def _get_cn_qsdd(self):
        cn_qsdd = self.env['bsd.cn_qsdd'].browse(self._context.get('active_ids', []))
        return cn_qsdd

    bsd_cn_qsdd_id = fields.Many2one('bsd.cn_qsdd', string="Cập nhật QSDĐ", default=_get_cn_qsdd, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_cn_qsdd_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })
        self.bsd_cn_qsdd_id.message_post(body='Lý do không duyệt: ' + self.bsd_ly_do)
        for ct in self.bsd_cn_qsdd_id.bsd_ct_ids.filtered(lambda c: c.state == 'xac_nhan'):
            ct.write({"state": "nhap"})
