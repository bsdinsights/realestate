# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


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
                              ('het_han', 'Hết hạn'),
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

    @api.constrains('bsd_loai_ck', 'bsd_tu_ngay', 'bsd_den_ngay', 'bsd_sl_tu', 'bsd_sl_den')
    def constrains_ck(self):
        # DM.13.07 Kiểm tra điều kiện trùng chiếu khấu mua sỉ
        if self.bsd_loai_ck == 'mua_si':
            mua_si = self.env['bsd.chiet_khau'].search([('bsd_loai_ck', '=', 'mua_si'),
                                                        ('id', '!=', self.id),
                                                        ('state', '!=', 'huy')])
            mua_si_time = mua_si.filtered(lambda m: not (m.bsd_sl_den < self.bsd_sl_tu < self.bsd_sl_den
                                                         or self.bsd_sl_tu < self.bsd_sl_den < m.bsd_sl_tu))
            if mua_si_time:
                khoang_time = [(t.bsd_tu_ngay, t.bsd_den_ngay) for t in mua_si_time.sorted('bsd_tu_ngay')]
                flag_time = True
                if self.bsd_tu_ngay < self.bsd_den_ngay < khoang_time[0][0]:
                    flag_time = False
                elif khoang_time[-1][1] < self.bsd_tu_ngay < self.bsd_den_ngay:
                    flag_time = False
                else:
                    le = len(khoang_time)
                    for i in range(0, le - 1):
                        t_first = khoang_time[i][1]
                        t_last = khoang_time[i + 1][0]
                        if t_first < self.bsd_tu_ngay < self.bsd_den_ngay < t_last:
                            _logger.debug("Nằm trong khoảng cho phep")
                            flag_time = False
                if flag_time:
                    raise UserError("Đã tồn tại chiết khấu này. Vui lòng kiểm tra lại")
            mua_si_sl = mua_si.filtered(lambda m: not (m.bsd_den_ngay < self.bsd_tu_ngay < self.bsd_den_ngay
                                                       or self.bsd_tu_ngay < self.bsd_den_ngay < m.bsd_tu_ngay))
            if mua_si_sl:
                so_luong = [(t.bsd_sl_tu, t.bsd_sl_den) for t in mua_si_sl.sorted('bsd_sl_tu')]
                flag_sl = True
                if self.bsd_sl_tu < self.bsd_sl_den < so_luong[0][0]:
                    flag_sl = False
                elif so_luong[-1][1] < self.bsd_sl_tu < self.bsd_sl_den:
                    flag_sl = False
                else:
                    le = len(so_luong)
                    for i in range(0, le - 1):
                        t_first = so_luong[i][1]
                        t_last = so_luong[i + 1][0]
                        if t_first < self.bsd_sl_tu < self.bsd_sl_den < t_last:
                            _logger.debug("Nằm trong khoảng cho phep")
                            flag_sl = False
                if flag_sl:
                    raise UserError("Đã tồn tại chiết khấu mua sỉ. Vui lòng kiểm tra lại")

        # DM.13.08 Kiểm tra điều kiện trùng lịch thanh toán
        if self.bsd_loai_ck == 'ltt':
            lich_tt = self.env['bsd.chiet_khau'].search([('bsd_loai_ck', '=', 'ltt'),
                                                         ('id', '!=', self.id),
                                                         ('state', '!=', 'huy')])
            if lich_tt:
                raise UserError("Chính sách thanh toán đã có chiết khấu")

        # DM.13.09 Kiểm tra điều kiện trùng chiết khấu thanh toán trước hạn
        if self.bsd_loai_ck == 'ttth':
            ttth = self.env['bsd.chiet_khau'].search([('bsd_loai_ck', '=', 'ttth'),
                                                      ('id', '!=', self.id),
                                                      ('state', '!=', 'huy')])
            if ttth:
                khoang_time = [(t.bsd_tu_ngay, t.bsd_den_ngay) for t in ttth.sorted('bsd_tu_ngay')]
                flag_time = True
                if self.bsd_tu_ngay < self.bsd_den_ngay < khoang_time[0][0]:
                    flag_time = False
                elif khoang_time[-1][1] < self.bsd_tu_ngay < self.bsd_den_ngay:
                    flag_time = False
                else:
                    le = len(khoang_time)
                    for i in range(0, le - 1):
                        t_first = khoang_time[i][1]
                        t_last = khoang_time[i + 1][0]
                        if t_first < self.bsd_tu_ngay < self.bsd_den_ngay < t_last:
                            _logger.debug("Nằm trong khoảng cho phep")
                            flag_time = False
                if flag_time:
                    raise UserError("Đã tồn tại chiết khấu này. Vui lòng kiểm tra lại")
        # DM.13.10 Kiểm tra điều kiện trùng chiết khấu thanh toán nhanh
        if self.bsd_loai_ck == 'ttn':
            ttn = self.env['bsd.chiet_khau'].search([('bsd_loai_ck', '=', 'ttn'),
                                                     ('id', '!=', self.id)])
            if ttn:
                khoang_time = [(t.bsd_tu_ngay, t.bsd_den_ngay) for t in ttn.sorted('bsd_tu_ngay')]
                flag_time = True
                if self.bsd_tu_ngay < self.bsd_den_ngay < khoang_time[0][0]:
                    flag_time = False
                elif khoang_time[-1][1] < self.bsd_tu_ngay < self.bsd_den_ngay:
                    flag_time = False
                else:
                    le = len(khoang_time)
                    for i in range(0, le - 1):
                        t_first = khoang_time[i][1]
                        t_last = khoang_time[i + 1][0]
                        if t_first < self.bsd_tu_ngay < self.bsd_den_ngay < t_last:
                            _logger.debug("Nằm trong khoảng cho phep")
                            flag_time = False
                if flag_time:
                    raise UserError("Đã tồn tại chiết khấu này. Vui lòng kiểm tra lại")
