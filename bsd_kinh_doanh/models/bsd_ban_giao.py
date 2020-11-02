# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BsdBanGiao(models.Model):
    _name = 'bsd.ban_giao'
    _description = 'Thông tin điều kiện bàn giao cho báo giá'
    _rec_name = 'bsd_dk_bg_id'

    bsd_dk_bg_id = fields.Many2one('bsd.dk_bg', string="Tên ĐKBG", help="Tên điều kiện bàn giao", required=True)
    bsd_ma_dkbg = fields.Char(related='bsd_dk_bg_id.bsd_ma_dkbg', store=True)
    bsd_dk_tt = fields.Selection([('tien', 'Số tiền'),
                                  ('ty_le', 'Phần trăm'),
                                  ('m2', 'Đơn giá/m2'),
                                  ], string="Phương thức tính", default="m2", required=True,
                                 help="Điều kiện thanh toán để được nhận bàn giao", readonly=True)
    bsd_loai_bg = fields.Selection(related='bsd_dk_bg_id.bsd_loai_bg', store=True)
    bsd_loai_sp_id = fields.Many2one(related='bsd_dk_bg_id.bsd_loai_sp_id', store=True)
    bsd_tu_ngay = fields.Date(related='bsd_dk_bg_id.bsd_tu_ngay', store=True)
    bsd_den_ngay = fields.Date(related='bsd_dk_bg_id.bsd_den_ngay', store=True)
    bsd_gia_m2 = fields.Monetary(string="Đơn giá/ m2", help="Đơn giá/ m2 theo điều kiện bàn giao", readonly=True)
    bsd_tien = fields.Monetary(string="Số tiền", help="Số tiền thanh toán theo điều kiện bàn giao", readonly=True)
    bsd_ty_le = fields.Float(string="Phần trăm", help="Tỷ lệ thanh toán theo điều kiện bàn giao", readonly=True)
    bsd_tien_bg = fields.Monetary(string="Tiền bàn giao ", help="Tiền thanh toán theo điều kiện bàn giao ",
                                  compute="_compute_tien_bg", store=True)
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", help="Tên báo giá", required=True)
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="'Đặt cọc", help="Phiếu đặt cọc", readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_bao_gia_id')
    def _onchange_dk_bg(self):
        res = {}
        list_id = []
        if self.bsd_bao_gia_id.bsd_dot_mb_id:
            # Lấy các điều kiện bàn giao trong đợt mở bán
            dk_bg = self.bsd_bao_gia_id.bsd_dot_mb_id.bsd_dkbg_ids
            # Lọc các điều kiện bàn giao có nhóm sản phẩm trùng với unit trong bảng tính giá
            list_id = dk_bg.filtered(
                lambda d: d.bsd_loai_sp_id == self.bsd_bao_gia_id.bsd_unit_id.bsd_loai_sp_id or not d.bsd_loai_sp_id).ids
        res.update({
            'domain': {
                'bsd_dk_bg_id': [('id', 'in', list_id)]
            }
        })
        return res

    @api.onchange('bsd_dk_bg_id')
    def _onchange_dkbg(self):
        self.bsd_dk_tt = self.bsd_dk_bg_id.bsd_dk_tt
        self.bsd_gia_m2 = self.bsd_dk_bg_id.bsd_gia_m2
        self.bsd_tien = self.bsd_dk_bg_id.bsd_tien
        self.bsd_ty_le = self.bsd_dk_bg_id.bsd_ty_le

    @api.depends('bsd_dk_tt', 'bsd_gia_m2', 'bsd_tien', 'bsd_ty_le')
    def _compute_tien_bg(self):
        for each in self:
            if each.bsd_dk_tt == 'm2':
                each.bsd_tien_bg = each.bsd_gia_m2 * each.bsd_bao_gia_id.bsd_dt_sd
            elif each.bsd_dk_tt == 'tien':
                each.bsd_tien_bg = each.bsd_tien
            else:
                each.bsd_tien_bg = each.bsd_ty_le * each.bsd_bao_gia_id.bsd_gia_ban / 100
