# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdPhatSinhGiaoDichChietKhau(models.Model):
    _name = 'bsd.ps_gd_ck'
    _rec_name = 'bsd_ten_ck'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Ghi nhận phát sinh chiết khấu giao dịch'

    bsd_ma_ht = fields.Char(string="Mã hệ thống", help="Mã hệ thống", required=True, readonly=True, copy=False,
                                   default='/')
    _sql_constraints = [
        ('bsd_ma_ht_unique', 'unique (bsd_ma_ht)',
         'Mã hệ thống đã tồn tại !'),
    ]
    bsd_ma_ck = fields.Char(string="Mã chiết khấu", required=True, help="Mã chiết khấu")
    _sql_constraints = [
        ('bsd_ma_ck_unique', 'check(1=1)',
         'Mã chiết khấu đã tồn tại !'),
    ]
    bsd_ten_ck = fields.Char(string="Tên chiết khấu", required=True, help="Tên chiết khấu")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng")
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ")
    bsd_loai_ck = fields.Selection([('chung', 'Chung'),
                                    ('noi_bo', 'Nội bộ'),
                                    ('mua_si', 'Mua sỉ'),
                                    ('ltt', 'Lịch thanh toán'),
                                    ('ttth', 'Thanh toán trước hạn'),
                                    ('ttn', 'Thanh toán nhanh'),
                                    ('dac_biet', 'Đặc biệt')], string="Loại chiết khấu",
                                   default='chung', required=True, help="Loại chiết khấu")
    bsd_ltt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", help="Đợt thanh toán")
    bsd_sn_th = fields.Integer(string="Số ngày trước hạn", help="Số ngày dùng để tính thanh toán trước hạn")
    bsd_tien_dot_tt = fields.Monetary(string="Số tiền thanh toán", help="Số tiền thanh toán của đợt thanh toán")
    bsd_tl_ck = fields.Float(string="Tỷ lệ chiết khấu", help="Tỷ lệ chiết khấu")
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền")
    bsd_tien_ck = fields.Monetary(string="Tiền chiết khấu", help="Tiền chiết khấu")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('xac_nhan', 'Xác nhận'),
                              ('hoan_tien', 'Hoàn tiền'),
                              ('dc_giam', 'Điều chỉnh giảm'),
                              ('huy', 'Hủy')], string="Trạng thái",
                             default='xac_nhan', tracking=1, help="Trạng thái", required=True)

    # TC.15.01 Hoàn tiền chiết khấu
    def action_hoan_tien(self):
        loai_ck = ""
        if self.bsd_loai_ck == 'ttth':
            loai_ck = "thanh toán trước hạn"
        elif self.bsd_loai_ck == 'ttn':
            loai_ck = "thanh toán nhanh"
        self.env['bsd.hoan_tien'].create({
            'bsd_ngay_ct': fields.Datetime.now(),
            'bsd_khach_hang_id': self.bsd_hd_ban_id.bsd_khach_hang_id.id,
            'bsd_du_an_id': self.bsd_hd_ban_id.bsd_du_an_id.id,
            'bsd_loai': 'gd_ck',
            'bsd_ps_gd_ck_id': self.id,
            'bsd_tien': self.bsd_tien_ck,
            'bsd_dien_giai': "Chiết khấu" + " " + loai_ck
        })
        self.write({
            'state': 'hoan_tien'
        })

    # TC.15.02 Điều chỉnh giảm công nợ chiết khấu
    def action_dc_giam(self):
        loai_ck = ""
        if self.bsd_loai_ck == 'ttth':
            loai_ck = "thanh toán trước hạn"
        elif self.bsd_loai_ck == 'ttn':
            loai_ck = "thanh toán nhanh"
        self.env['bsd.giam_no'].create({
            'bsd_ngay_ct': fields.Datetime.now(),
            'bsd_khach_hang_id': self.bsd_hd_ban_id.bsd_khach_hang_id.id,
            'bsd_du_an_id': self.bsd_hd_ban_id.bsd_du_an_id.id,
            'bsd_loai_dc': 'gd_ck',
            'bsd_tien': self.bsd_tien_ck,
            'bsd_dien_giai': "Chiết khấu" + " " + loai_ck + " " + self.bsd_ma_ht
        })
        self.write({
            'state': 'dc_giam'
        })

    # TC.15.03 Hủy chiết khấu
    def action_huy(self):
        self.write({
            'state': 'huy'
        })

    @api.model
    def create(self, vals):
        sequence = False
        if vals.get('bsd_ma_ht', '/') == '/':
            sequence = self.env['bsd.ma_bo_cn'].search([('bsd_loai_cn', '=', 'bsd.ps_gd_ck')], limit=1).bsd_ma_tt_id
            vals['bsd_ma_ht'] = self.env['ir.sequence'].next_by_code('bsd.ps_gd_ck') or '/'
        if not sequence:
            raise UserError(_('Danh mục mã chưa khai báo mã phát sinh giao dịch chiết khấu'))
        vals['bsd_ma_ht'] = sequence.next_by_id()
        return super(BsdPhatSinhGiaoDichChietKhau, self).create(vals)