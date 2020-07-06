# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyDC(models.TransientModel):
    _name = 'bsd.wizard.ky_dc'
    _description = 'Xác nhận ngày ký đặt cọc'

    def _get_dc(self):
        dc = self.env['bsd.dat_coc'].browse(self._context.get('active_ids', []))
        return dc

    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", default=_get_dc, readonly=True)
    bsd_ngay_ky_dc = fields.Datetime(string="Ngày ký đặt cọc", required=True)

    def action_xac_nhan(self):
        self.bsd_dat_coc_id.write({
            'bsd_ngay_ky_dc': self.bsd_ngay_ky_dc
        })
        self.bsd_dat_coc_id.tao_cong_no_dot_tt()
        # tính lại ngày hạn thanh toán
        self.bsd_dat_coc_id.tinh_lai_han_tt()
        # Ghi nhận giao dịch chiết khấu
        # self.bsd_dat_coc_id.tao_gd_chiet_khau()