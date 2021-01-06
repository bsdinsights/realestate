# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdHoaHong(models.Model):
    _name = 'bsd.hoa_hong'
    _rec_name = 'bsd_ten'
    _description = "Thông tin hoa hồng"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma = fields.Char(string="Mã", help="Mã hoa hồng", required=True, readonly=True, copy=False,
                         default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã hoa hồng đã tồn tại !'),
    ]
    bsd_ten = fields.Char(string="Tiêu đề", required=True, help="Tên hoa hồng",
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection([('dat_coc', 'Đặt cọc'),
                                 ('ky_ttdc', 'Ký TTĐC/ HDĐC'),
                                 ('ky_hd', 'Ký HĐMB'),
                                 ('dot_tt', 'Đợt thanh toán')],
                                string="Loại", help="Loại hoa hồng", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng hoa hồng",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng hoa hồng",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_phuong_thuc = fields.Selection([('gia_tri', 'Giá trị'),
                                        ('phan_tram', 'Phần trăm')],
                                       string="Phương thức", help="Phương thức", required=True,
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_cach_tinh = fields.Selection([('so_luong', 'Số lượng'),
                                      ('so_tien', 'Số tiền')],
                                     string="Cách tính", help="Cách tính", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_sl_tu = fields.Integer(string="Số lượng (từ)", help="Số lượng từ",
                               readonly=True, states={'nhap': [('readonly', False)]})
    bsd_sl_den = fields.Integer(string="Số lượng (đến)", help="Số lượng đến",
                                readonly=True, states={'nhap': [('readonly', False)]})
    bsd_tien_tu = fields.Monetary(string="Số tiền (từ)", help="Số tiền từ",
                                  readonly=True, states={'nhap': [('readonly', False)]})
    bsd_tien_den = fields.Monetary(string="Số tiền (đến)", help="Số tiền đến",
                                   readonly=True, states={'nhap': [('readonly', False)]})
    bsd_tl_dc = fields.Float(string="Tỷ lệ đặt cọc", help="Tỷ lệ đặt cọc", readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc", readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tl_ttdc = fields.Float(string="Tỷ lệ ký TTĐC", help="Tỷ lệ ký TTĐC", readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_tien_ttdc = fields.Monetary(string="Tiền ký TTĐC", help="Tiền ký TTĐC", readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tl_hd = fields.Float(string="Tỷ lệ ký HĐMB", help="Tỷ lệ ký HĐMB", readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_tien_hd = fields.Monetary(string="Tiền ký HĐMB", help="Tiền ký HĐMB", readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tl_dtt = fields.Float(string="Tỷ lệ đợt TT", help="Tỷ lệ đợt thanh toán", readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_tien_dtt = fields.Monetary(string="Tiền đợt TT", help="Tiền đợt thanh toán", readonly=True,
                                   states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', readonly=1, required=True, tracking=1,
                             help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.ck_ch_ct', 'bsd_ck_ch_id', string="Chi tiết",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True)

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã hoa hồng.'))
        vals['bsd_ma_ck_ch'] = sequence.next_by_id()
        return super(BsdHoaHong, self).create(vals)
