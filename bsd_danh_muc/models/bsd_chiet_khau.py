# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class BsdChietKhau(models.Model):
    _name = 'bsd.chiet_khau'
    _rec_name = 'bsd_ma_ck'
    _description = "Thông tin chiết khấu"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck = fields.Char(string="Mã chiết khấu", required=True, help="Mã chiết khấu",
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_ck_unique', 'unique (bsd_ma_ck)',
         'Mã chiết khấu đã tồn tại !'),
    ]
    bsd_ten_ck = fields.Char(string="Tên chiết khấu", required=True, help="Tên chiết khấu",
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_loai_ck = fields.Selection([('chung', 'Chung'),
                                    ('noi_bo', 'Nội bộ'),
                                    ('mua_si', 'Mua sỉ'),
                                    ('ltt', 'Lịch thanh toán'),
                                    ('ttth', 'Thanh toán trước hạn'),
                                    ('ttn', 'Thanh toán nhanh')], string="Loại chiết khấu",
                                   default='chung', required=True, help="Loại chiết khấu",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_cach_tinh = fields.Selection([('phan_tram', 'Phần trăm'), ('tien', 'Tiền')],
                                     help='Hình thức trả chiết khấu theo tiền hoăc theo phần trăm số tiền',
                                     string="Cách tính", required=True, default='phan_tram',
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_cung_tang = fields.Boolean(string="Mua cùng tầng",
                                   help="Điều kiện xét chiết khấu mua sỉ số lượng mua có cùng chung một tầng hay không",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_sl_tu = fields.Integer(string="Số lượng từ", help="Điều kiện xét chiết khấu theo số lượng từ",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_sl_den = fields.Integer(string="Số lượng đến", help="Điều kiện xét chiết theo số lượng đến",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="Chính sách thanh toán", help="Chính sách thanh toán",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngay_tt = fields.Date(string="Ngày thanh toán",
                              help="Mốc (ngày) thanh toán được sử dụng để xét thanh toán nhanh",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_tl_tt = fields.Float(string="Tỷ lệ thanh toán", help="Tỷ lệ thanh toán để được xét chiết khấu thanh toán nhanh",
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_tien_ck = fields.Monetary(string="Tiền chiết khấu", help="Tiền chiết khấu được hưởng",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tl_ck = fields.Float(string="Tỷ lệ chiết khấu", help="Tỷ lệ chiết khấu được hưởng",
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', readonly=1, required=True, tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

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
        action = self.env.ref('bsd_danh_muc.bsd_wizard_chiet_khau_action').read()[0]
        return action

    # DM.13.03 Hủy chiết khấu
    def action_huy(self):
        self.write({
            'state': 'huy',
        })

    @api.model
    def create(self, vals):
        domain = []
        if 'bsd_loai_ck' in vals:
            domain.append(('bsd_loai_ck', '=', vals['bsd_loai_ck']))
        if 'bsd_du_an_id' in vals:
            domain.append(('bsd_du_an_id', '=', vals['bsd_du_an_id']))
        if 'bsd_cach_tinh' in vals:
            domain.append(('bsd_cach_tinh', '=', vals['bsd_cach_tinh']))
        if 'bsd_tien_ck' in vals:
            domain.append(('bsd_tien_ck', '=', vals['bsd_tien_ck']))
        if 'bsd_tl_ck' in vals:
            domain.append(('bsd_tl_ck', '=', vals['bsd_tl_ck']))
        if 'bsd_tu_ngay' in vals:
            domain.append(('bsd_tu_ngay', '=', vals['bsd_tu_ngay']))
        if 'bsd_den_ngay' in vals:
            domain.append(('bsd_den_ngay', '=', vals['bsd_den_ngay']))
        if 'bsd_cung_tang' in vals:
            domain.append(('bsd_cung_tang', '=', vals['bsd_cung_tang']))
        if 'bsd_sl_tu' in vals:
            domain.append(('bsd_sl_tu', '=', vals['bsd_sl_tu']))
        if 'bsd_sl_den' in vals:
            domain.append(('bsd_sl_den', '=', vals['bsd_sl_den']))
        if 'bsd_cs_tt_id' in vals:
            domain.append(('bsd_cs_tt_id', '=', vals['bsd_cs_tt_id']))
        if 'bsd_ngay_tt' in vals:
            domain.append(('bsd_ngay_tt', '=', vals['bsd_ngay_tt']))
        if 'bsd_tl_tt' in vals:
            domain.append(('bsd_tl_tt', '=', vals['bsd_tl_tt']))

        chiet_khau = self.env['bsd.chiet_khau'].search(domain)
        if chiet_khau:
            raise UserError("Đã tồn tại chiết khấu. Vui lòng kiểm tra lại!")

        return super(BsdChietKhau, self).create(vals)
