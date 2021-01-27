# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdHuyTT(models.TransientModel):
    _name = 'bsd.wizard.huy_tt.tu_choi'
    _description = 'Ghi nhận lý do từ chối'

    def _get_huy_tt(self):
        huy_tt = self.env['bsd.huy_tt'].browse(self._context.get('active_ids', []))
        return huy_tt

    bsd_huy_tt_id = fields.Many2one('bsd.huy_tt', string="Hủy thanh toán", default=_get_huy_tt, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_huy_tt_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'khong_duyet',
            'bsd_ngay_duyet': fields.Date.today(),
            'bsd_nguoi_duyet_id': self.env.uid
        })
        if self.bsd_huy_tt_id.bsd_loai == 'can_tru':
            self.bsd_huy_tt_id.bsd_can_tru_id.write({"state": 'xac_nhan'})
        elif self.bsd_huy_tt_id.bsd_loai == 'thanh_toan':
            self.bsd_huy_tt_id.bsd_phieu_thu_id.write({"state": 'da_gs'})
            if self.bsd_huy_tt_id.bsd_phieu_thu_id.bsd_tt_id:
                self.bsd_huy_tt_id.bsd_phieu_thu_id.bsd_tt_id.write({"state": 'da_gs'})

