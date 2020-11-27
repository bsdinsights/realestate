# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdTBNT(models.TransientModel):
    _name = 'bsd.wizard.tb_nt'
    _description = 'Ghi nhận ngày thông báo nghiệm thu'

    def _get_tb_nt(self):
        tb_nt = self.env['bsd.tb_nt'].browse(self._context.get('active_ids', []))
        return tb_nt

    def _get_loai(self):
        return self._context.get('loai_ngay')

    bsd_tb_nt_id = fields.Many2one('bsd.tb_nt', string="Thông báo nghiệm thu", default=_get_tb_nt, readonly=True)
    bsd_ngay = fields.Date(string="Ngày", required=True, default=lambda self: fields.Date.today())
    bsd_loai_ngay = fields.Selection([('ngay_gui', 'Ngày gửi thông báo'), ('ngay_dong', 'Ngày đóng thông báo')],
                                     string="Loại",
                                     default=_get_loai, readonly=True)

    def action_xac_nhan(self):
        if self.bsd_tb_nt_id:
            if self.bsd_loai_ngay == 'ngay_gui':
                self.bsd_tb_nt_id.write({
                    'bsd_ngay_gui': self.bsd_ngay,
                })
            if self.bsd_loai_ngay == 'ngay_dong':
                self.bsd_tb_nt_id.write({
                    'bsd_ngay_dong': self.bsd_ngay,
                    'state': 'hoan_thanh'
                })
                self.bsd_tb_nt_id.tao_nt_sp()

