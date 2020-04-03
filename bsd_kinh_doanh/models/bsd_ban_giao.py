# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BsdBanGiao(models.Model):
    _name = 'bsd.ban_giao'
    _description = 'Thông tin bàn giao cho báo giá'
    _rec_name = 'bsd_dk_bg_id'

    bsd_dk_bg_id = fields.Many2one('bsd.dk_bg', string="Mã ĐKBG", help="Mã điều kiện bàn giao", required=True)
    bsd_ten_dkbg = fields.Char(related='bsd_dk_bg_id.bsd_ten_dkbg', store=True)
    bsd_dk_tt = fields.Selection(related='bsd_dk_bg_id.bsd_dk_tt', store=True)
    bsd_gia_m2 = fields.Monetary(related='bsd_dk_bg_id.bsd_gia_m2', store=True)
    bsd_tien = fields.Monetary(related='bsd_dk_bg_id.bsd_tien', store=True)
    bsd_ty_le = fields.Float(related="bsd_dk_bg_id.bsd_ty_le", store=True)
    bsd_tien_bg = fields.Monetary(string="Tiền bàn giao ", help="Tiền thanh toán theo điều kiện bàn giao ",
                                  compute="_compute_tien_bg", store=True)
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", help="Tên báo giá", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.constrains('bsd_tien_bg')
    def _check_tien_bg(self):
        for record in self:
            if record.bsd_tien_bg <= 0:
                raise ValidationError("Kiểm tra lại trường tiền bàn giao")

    @api.depends('bsd_dk_tt', 'bsd_gia_m2', 'bsd_tien', 'bsd_ty_le')
    def _compute_tien_bg(self):
        for each in self:
            if each.bsd_dk_tt == 'm2':
                each.bsd_tien_bg = each.bsd_gia_m2 * each.bsd_bao_gia_id.bsd_dt_sd
            elif each.bsd_dk_tt == 'tien':
                each.bsd_tien_bg = each.bsd_tien
            else:
                each.bsd_tien_bg = each.bsd_ty_le * each.bsd_bao_gia_id.bsd_gia_ban / 100
