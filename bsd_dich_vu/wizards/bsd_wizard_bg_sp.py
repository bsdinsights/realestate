# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdKyBGSP(models.TransientModel):
    _name = 'bsd.wizard.ky_bg_sp'
    _description = 'Cập nhật ngày ký bàn giao sản phẩm'

    def _get_bao_giao(self):
        bg_sp = self.env['bsd.bg_sp'].browse(self._context.get('active_ids', []))
        return bg_sp

    bsd_bg_sp_id = fields.Many2one('bsd.bg_sp', string="Bàn giao sản phẩm", default=_get_bao_giao,
                                   readonly=True)
    bsd_ngay_bg_tt = fields.Date(string="Ngày BG thực tế", required=True)
    bsd_nguoi_bg_tt_id = fields.Many2one('hr.employee', required=True, string="Người BG thực tế")

    def action_xac_nhan(self):
        self.bsd_bg_sp_id.write({
            'bsd_ngay_bg_tt': self.bsd_ngay_bg_tt,
            'bsd_nguoi_bg_tt_id': self.bsd_nguoi_bg_tt_id.id,
            'state': 'ban_giao'
        })
        self.bsd_bg_sp_id.bsd_hd_ban_id.write({
            'state': '08_da_bg',
        })
        self.bsd_bg_sp_id.bsd_unit_id.sudo().write({
            'bsd_ngay_bg': self.bsd_ngay_bg_tt,
            'bsd_bg_sp_id': self.bsd_bg_sp_id.id,
        })


class BsdHuyBGSP(models.TransientModel):
    _name = 'bsd.wizard.huy_bg_sp'
    _description = 'Ghi nhận lý do hủy bàn giao sản phẩm'

    def _get_bao_giao(self):
        bg_sp = self.env['bsd.bg_sp'].browse(self._context.get('active_ids', []))
        return bg_sp

    bsd_bg_sp_id = fields.Many2one('bsd.bg_sp', string="Bàn giao sản phẩm", default=_get_bao_giao,
                                   readonly=True)
    bsd_ly_do = fields.Char(string="Lý do hủy", required=True)

    def action_xac_nhan(self):
        self.bsd_bg_sp_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'huy',
        })