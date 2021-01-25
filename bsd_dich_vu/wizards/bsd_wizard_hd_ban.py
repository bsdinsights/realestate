# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdXacNhanInTTDC(models.TransientModel):
    _name = 'bsd.wizard.xn_in_ttdc'
    _description = 'Xác nhận ngày in hợp đồng'

    def _get_ttdc(self):
        ttdc = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return ttdc

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", default=_get_ttdc, readonly=True)
    bsd_ngay_in_ttdc = fields.Date(string="Ngày in TTĐC/HĐĐC", required=True)
    bsd_ma_ttdc = fields.Char(string="Mã số TTĐC/HĐĐC", required=True)

    def action_xac_nhan(self):
        # Cập nhật ngày in và mã số thỏa thuận đặt cọc , hợp đồng đặt cọc
        self.bsd_hd_ban_id.write({
            'bsd_ngay_in_ttdc': self.bsd_ngay_in_ttdc,
            'bsd_ngay_hh_ttdc': self.bsd_ngay_in_ttdc + datetime.timedelta(days=self.bsd_hd_ban_id.bsd_du_an_id.bsd_hh_hd),
            'bsd_so_ttdc': self.bsd_ma_ttdc,
        })


class BsdXacNhanInHDB(models.TransientModel):
    _name = 'bsd.wizard.xn_in_hdb'
    _description = 'Xác nhận ngày in hợp đồng'

    def _get_hdb(self):
        hdb = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng bán", default=_get_hdb, readonly=True)
    bsd_ngay_in_hdb = fields.Date(string="Ngày in HĐMB", required=True)
    bsd_ma_so_hd = fields.Char(string="Mã số HĐMB", required=True)

    def action_xac_nhan(self):
        # Cập nhật ngày in và mã số hợp đồng mua bán
        self.bsd_hd_ban_id.write({
            'bsd_ngay_in_hdb': self.bsd_ngay_in_hdb,
            'bsd_ngay_hh_khdb': self.bsd_ngay_in_hdb + datetime.timedelta(days=self.bsd_hd_ban_id.bsd_du_an_id.bsd_hh_hd),
            'bsd_ma_so_hd': self.bsd_ma_so_hd,
        })


class BsdKyHDB(models.TransientModel):
    _name = 'bsd.wizard.ky_hdb'
    _description = 'Xác nhận ngày ký hợp đồng'

    def _get_hdb(self):
        hdb = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        return hdb

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng bán", default=_get_hdb, readonly=True)
    bsd_ngay_ky_hdb = fields.Date(string="Ngày ký hợp đồng", required=True)

    def action_xac_nhan(self):
        # Cập nhật trạng thái hợp đồng
        self.bsd_hd_ban_id.write({
            'bsd_ngay_ky_hdb': self.bsd_ngay_ky_hdb,
            'state': '05_da_ky'
        })
        # Cập nhật field hợp đồng trên unit , chuyển trạng thái đã bán
        self.bsd_hd_ban_id.bsd_unit_id.sudo().write({
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'state': 'da_ban',
        })
        self.bsd_hd_ban_id.tao_cong_no_dot_tt()

