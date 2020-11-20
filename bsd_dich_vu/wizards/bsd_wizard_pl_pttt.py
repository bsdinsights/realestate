# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyPLTDPTTT(models.TransientModel):
    _name = 'bsd.wizard.ky_pl_pttt'
    _description = 'Xác nhận ngày ký phụ lục thay đổi phương thức thanh toán'

    def _get_pl_pttt(self):
        pl = self.env['bsd.pl_pttt'].browse(self._context.get('active_ids', []))
        return pl

    bsd_pl_pttt_id = fields.Many2one('bsd.pl_pttt', string="Phụ lục HĐ", default=_get_pl_pttt, readonly=True)
    bsd_ngay_ky_pl = fields.Date(string="Ngày ký phụ lục", required=True)

    def action_xac_nhan(self):
        self.bsd_pl_pttt_id.write({
            'bsd_ngay_ky_pl': self.bsd_ngay_ky_pl,
            'bsd_nguoi_xn_ky_id': self.env.uid,
            'state': 'dk_pl',
        })
        self.bsd_pl_pttt_id.thay_doi_pttt()


class BsdKhongDuyetPLPTTT(models.TransientModel):
    _name = 'bsd.wizard.khong_duyet_pl_pttt'
    _description = 'Ghi nhận lý do từ chối'

    def _get_pl_pttt(self):
        pl_pttt = self.env['bsd.pl_pttt'].browse(self._context.get('active_ids', []))
        return pl_pttt

    bsd_pl_pttt_id = fields.Many2one('bsd.pl_pttt', string="Phụ lục", default=_get_pl_pttt, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_pl_pttt_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })


class BsdHuytPLPTTT(models.TransientModel):
    _name = 'bsd.wizard.huy_pl_pttt'
    _description = 'Ghi nhận lý do hủy phụ lục thay đổi phương thức thanh toán'

    def _get_pl_pttt(self):
        pl_pttt = self.env['bsd.pl_pttt'].browse(self._context.get('active_ids', []))
        return pl_pttt

    bsd_pl_pttt_id = fields.Many2one('bsd.pl_pttt', string="Phụ lục", default=_get_pl_pttt, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_pl_pttt_id.write({
            'bsd_ly_do_huy': self.bsd_ly_do,
            'state': 'huy',
            'bsd_ngay_huy': fields.Date.today(),
            'bsd_nguoi_huy_id': self.env.uid
        })
