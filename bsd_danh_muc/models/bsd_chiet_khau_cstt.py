# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdChietKhauCSTT(models.Model):
    _name = 'bsd.ck_cstt'
    _rec_name = 'bsd_ten_ck_cstt'
    _description = "Thông tin chiết khấu chính sách thanh toán"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_cstt = fields.Char(string="Mã chiết khấu",
                                 help="Mã chiết khấu theo chính sách thanh toán", required=True,
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_ck_cstt', 'unique (bsd_ma_ck_cstt)',
         'Mã chiết khấu theo chính sách thanh toán đã tồn tại !'),
    ]
    bsd_ten_ck_cstt = fields.Char(string="Tên chiết khấu",
                                  help="Mã chiết khấu theo chính sách thanh toán", required=True,
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
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', readonly=1, required=True, tracking=1,
                             help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.ck_cstt_ct', 'bsd_ck_cstt_id', string="Chi tiết")
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    # DM.15.01 Xác nhận chiết khấu
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan'
        })

    # DM.15.02 Duyệt chiết khấu
    def action_duyet(self):
        self.write({
            'state': 'duyet',
        })

    # DM.15.04 Không duyệt chiết khấu
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_ck_cstt_action').read()[0]
        return action

    # DM.15.03 Hủy chiết khấu
    def action_huy(self):
        self.write({
            'state': 'huy',
        })


class BsdChietKhauCSTTChiTiet(models.Model):
    _name = 'bsd.ck_cstt_ct'
    _description = "Thông tin chiết khấu chính sách thanh toán chi tiết"
    _rec_name = 'bsd_chiet_khau_id'

    bsd_ck_cstt_id = fields.Many2one('bsd.ck_cstt', string="Chiết khấu CSTT")
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu", required=True, help="Chiết khấu",
                                        domain=[('bsd_loai_ck', '=', 'ltt'), ('state', '=', 'duyet')])
    bsd_ma_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ma_ck")
    bsd_tu_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_tu_ngay")
    bsd_den_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_den_ngay")
    bsd_cs_tt_id = fields.Many2one(related="bsd_chiet_khau_id.bsd_cs_tt_id")
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh")
    bsd_tien_ck = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck")
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
