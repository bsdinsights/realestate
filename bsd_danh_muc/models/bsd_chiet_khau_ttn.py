# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdChietKhauTTN(models.Model):
    _name = 'bsd.ck_ttn'
    _rec_name = 'bsd_ten_ck_ttn'
    _description = "Thông tin chiết khấu thanh toán nhanh"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_ttn = fields.Char(string="Mã chiết khấu", help="Mã chiết khấu thanh toán nhanh", required=True,
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_ck_ttn_unique', 'unique (bsd_ma_ck_ttn)',
         'Mã chiết khấu thanh toán nhanh đã tồn tại !'),
    ]
    bsd_ten_ck_ttn = fields.Char(string="Tên chiết khấu", help="Mã chiết khấu thanh toán nhanh", required=True,
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu chung",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu chung",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})

    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', readonly=1, required=True, tracking=1,
                             help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.ck_ttn_ct', 'bsd_ck_ttn_id', string="Chi tiết")
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    # DM.17.01 Xác nhận chiết khấu
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan'
        })

    # DM.17.02 Duyệt chiết khấu
    def action_duyet(self):
        self.write({
            'state': 'duyet',
        })

    # DM.17.04 Không duyệt chiết khấu
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_ck_ttn_action').read()[0]
        return action

    # DM.17.03 Hủy chiết khấu
    def action_huy(self):
        self.write({
            'state': 'huy',
        })


class BsdChietKhauTTNChiTiet(models.Model):
    _name = 'bsd.ck_ttn_ct'
    _description = "Thông tin chiết khấu thanh toán nhanh chi tiết"
    _rec_name = 'bsd_chiet_khau_id'

    bsd_ck_ttn_id = fields.Many2one('bsd.ck_ttn', string="Chiết khấu TTN")
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu", required=True,
                                        domain=[('bsd_loai_ck', '=', 'ttn'), ('state', '=', 'duyet')])
    bsd_ma_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ma_ck")
    bsd_tu_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_tu_ngay")
    bsd_den_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_den_ngay")
    bsd_ngay_tt = fields.Date(related="bsd_chiet_khau_id.bsd_ngay_tt")
    bsd_tl_tt = fields.Float(related="bsd_chiet_khau_id.bsd_tl_tt")
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh")
    bsd_tien_ck = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck")
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
