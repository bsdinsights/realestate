# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdWizardNghiemThu(models.TransientModel):
    _name = 'bsd.wizard.nghiem_thu'
    _description = "Chọn đợt thanh toán gắn phí phát sinh"

    def _get_nghiem_thu(self):
        nghiem_thu = self.env['bsd.nghiem_thu'].browse(self._context.get('active_ids', []))
        return nghiem_thu

    bsd_nghiem_thu_id = fields.Many2one('bsd.nghiem_thu', string="Nghiệm thu sản phẩm", default=_get_nghiem_thu,
                                        readonly=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", readonly=True)
    bsd_dot_tt_ids = fields.Many2many('bsd.lich_thanh_toan', string="Đợt thanh toán")

    @api.onchange('bsd_nghiem_thu_id')
    def _onchange_nghiem_thu(self):
        self.bsd_hd_ban_id = self.bsd_nghiem_thu_id.bsd_hd_ban_id

    def action_xac_nhan(self):
        if len(self.bsd_dot_tt_ids) != 1:
            raise UserError(_("vui lòng kiểm tra lại đợt thanh toán"))
        self.bsd_nghiem_thu_id.write({
            'bsd_dot_tt_id': self.bsd_dot_tt_ids.id,
            'bsd_ngay_kt_xn': fields.Datetime.now(),
            'state': 'xac_nhan',
        })


class BsdHuyNghiemThu(models.TransientModel):
    _name = 'bsd.wizard.huy_nt'
    _description = 'Ghi nhận lý do hủy nghiệm thu'

    def _get_nghiem_thu(self):
        nghiem_thu = self.env['bsd.nghiem_thu'].browse(self._context.get('active_ids', []))
        return nghiem_thu

    bsd_nghiem_thu_id = fields.Many2one('bsd.nghiem_thu', string="Nghiệm thu sản phẩm", default=_get_nghiem_thu,
                                        readonly=True)
    bsd_ly_do = fields.Char(string="Lý do hủy", required=True)

    def action_xac_nhan(self):
        self.bsd_nghiem_thu_id.write({
            'bsd_ly_do_huy': self.bsd_ly_do,
            'state': 'huy',
        })
