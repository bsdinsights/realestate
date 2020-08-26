# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdTBTL(models.TransientModel):
    _name = 'bsd.wizard.tb_tl'
    _description = 'Ghi nhận ngày thông báo thanh lý'

    def _get_tb_tl(self):
        tb_tl = self.env['bsd.tb_tl'].browse(self._context.get('active_ids', []))
        return tb_tl

    bsd_tb_tl_id = fields.Many2one('bsd.tb_tl', string="Thông báo thanh lý", default=_get_tb_tl, readonly=True)
    bsd_ngay = fields.Datetime(string="Ngày gửi", required=True)

    def action_xac_nhan(self):
        if self.bsd_tb_tl_id:
            self.bsd_tb_tl_id.write({
                'bsd_ngay_gui': self.bsd_ngay,
            })

