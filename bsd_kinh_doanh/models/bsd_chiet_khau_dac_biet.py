# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BsdChietKhauDacBiet(models.Model):
    _name = 'bsd.ck_db'
    _rec_name = 'bsd_ma_ck_db'
    _description = "Thông tin chiết khấu đặt biệt"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_db = fields.Char(string="Mã chiết khấu", help="Mã chiết khấu đặt biệt", required=True,
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_ck_db_unique', 'unique (bsd_ma_ck_db)',
         'Mã chiết khấu đặt biệt đã tồn tại !'),
    ]
    bsd_ten_ck_db = fields.Char(string="Tên chiết khấu", required=True, help="Tên chiết khấu đặt biệt",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_cach_tinh = fields.Selection([('phan_tram', 'Phần trăm'), ('tien', 'Tiền')],
                                     help='Hình thức trả chiết khấu theo tiền hoăc theo phần trăm số tiền',
                                     string="Cách tính", required=True, default='phan_tram',
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền chiết khấu được hưởng",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_tien_ck = fields.Monetary(string="Tiền chiết khấu",
                                  compute="_compute_tien_ck", store=True,
                                  help="Tiền bàn giao theo chiết khấu")
    bsd_tl_ck = fields.Float(string="Tỷ lệ chiết khấu", help="Tỷ lệ chiết khấu được hưởng",
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Nội dung về yêu cầu chiết khấu đặc biệt")
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá", required=True)
    bsd_khach_hang_id = fields.Many2one(related="bsd_bao_gia_id.bsd_khach_hang_id", store=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án",
                                   related="bsd_bao_gia_id.bsd_du_an_id", store=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Tên căn hộ",
                                  related="bsd_bao_gia_id.bsd_unit_id", store=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Tên đợt mở bán",
                                    related="bsd_bao_gia_id.bsd_dot_mb_id", store=True)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán",
                                   related="bsd_bao_gia_id.bsd_cs_tt_id", store=True)
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ",
                                  related="bsd_bao_gia_id.bsd_tien_gc", store=True)
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc",
                                  related="bsd_bao_gia_id.bsd_tien_dc", store=True)
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', readonly=1, required=True, tracking=1,
                             help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    @api.depends('bsd_cach_tinh', 'bsd_tien', 'bsd_tl_ck', 'bsd_bao_gia_id.bsd_gia_ban')
    def _compute_tien_ck(self):
        for each in self:
            if each.bsd_cach_tinh == 'phan_tram':
                each.bsd_tien_ck = each.bsd_tl_ck * each.bsd_bao_gia_id.bsd_gia_ban / 100
            else:
                each.bsd_tien_ck = each.bsd_tien

    # DM.13.01 Xác nhận chiết khấu
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan'
        })

    # DM.13.02 Duyệt chiết khấu
    def action_duyet(self):
        self.write({
            'state': 'duyet',
        })

    # DM.13.04 Không duyệt chiết khấu
    def action_khong_duyet(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_ck_db_action').read()[0]
        return action

    # DM.13.03 Hủy chiết khấu
    def action_huy(self):
        self.write({
            'state': 'huy',
        })