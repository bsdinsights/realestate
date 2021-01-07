# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


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
                                readonly=True, default='dat_coc',
                                states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng hoa hồng",
                              readonly=True, required=True,
                              states={'nhap': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng hoa hồng",
                               readonly=True, required=True,
                               states={'nhap': [('readonly', False)]})
    bsd_phuong_thuc = fields.Selection([('gia_tri', 'Giá trị'),
                                        ('phan_tram', 'Phần trăm')],
                                       string="Phương thức", help="Phương thức", required=True,
                                       readonly=True, default='gia_tri',
                                       states={'nhap': [('readonly', False)]})
    bsd_cach_tinh = fields.Selection([('so_luong', 'Số lượng'),
                                      ('so_tien', 'Số tiền')],
                                     string="Cách tính", help="Cách tính", required=True,
                                     readonly=True, default='so_luong',
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
                              ('het_han', 'Hết hạn'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', readonly=1, required=True,
                             tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True)

    # Kiểm tra số lượng
    @api.constrains("bsd_sl_tu", "bsd_sl_den", "bsd_tien_tu", "bsd_tien_den", "bsd_cach_tinh")
    def _constraint_sl(self):
        if self.bsd_cach_tinh == 'so_luong':
            if not 0 <= self.bsd_sl_tu <= 100:
                raise UserError(_("Nhập sai giá trị số lượng từ. Vui lòng kiểm tra lại thông tin."))
            if not 0 <= self.bsd_sl_den <= 100:
                raise UserError(_("Nhập sai giá trị số lượng đến. Vui lòng kiểm tra lại thông tin."))
            if self.bsd_sl_tu >= self.bsd_sl_den:
                raise UserError(_("Số lường từ phải nhỏ hơn số lượng đến. Vui lòng kiểm tra lại thông tin."))
        else:
            if not 0 <= self.bsd_tien_tu:
                raise UserError(_("Nhập sai giá trị số tiền từ. Vui lòng kiểm tra lại thông tin."))
            if not 0 <= self.bsd_tien_tu:
                raise UserError(_("Nhập sai giá trị số tiền đến. Vui lòng kiểm tra lại thông tin."))
            if self.bsd_tien_tu >= self.bsd_tien_den:
                raise UserError(_("Số tiền từ phải nhỏ hơn số tiền đến. Vui lòng kiểm tra lại thông tin."))

    # Kiểm tra giá trị còn lại
    @api.constrains("bsd_tl_dc", "bsd_tien_dc", "bsd_tl_ttdc", "bsd_tien_ttdc",
                    "bsd_tl_hd", "bsd_tien_hd", "bsd_tl_dtt", "bsd_tien_dtt", "bsd_loai")
    def _constraint_gia_tri(self):
        if self.bsd_loai == 'dat_coc':
            if not 0 <= self.bsd_tl_dc <= 100:
                raise UserError(_("Nhập sai giá trị tỷ lệ đặt cọc. Vui lòng kiểm tra lại thông tin."))
            if not 0 <= self.bsd_tien_dc:
                raise UserError(_("Nhập sai giá trị tiền đặt cọc. Vui lòng kiểm tra lại thông tin."))
        elif self.bsd_loai == 'ky_ttdc':
            if not 0 <= self.bsd_tl_ttdc <= 100:
                raise UserError(_("Nhập sai giá trị tỷ lệ thỏa thuận đặt cọc. Vui lòng kiểm tra lại thông tin."))
            if not 0 <= self.bsd_tien_ttdc:
                raise UserError(_("Nhập sai giá trị tiền thỏa thuận đặt cọc. Vui lòng kiểm tra lại thông tin."))
        elif self.bsd_loai == 'ky_hd':
            if not 0 <= self.bsd_tl_hd <= 100:
                raise UserError(_("Nhập sai giá trị tỷ lệ hợp đồng mua bán. Vui lòng kiểm tra lại thông tin."))
            if not 0 <= self.bsd_tien_hd:
                raise UserError(_("Nhập sai giá trị tiền hợp đồng mua bán. Vui lòng kiểm tra lại thông tin."))
        elif self.bsd_loai == 'dot_tt':
            if not 0 <= self.bsd_tl_dtt <= 100:
                raise UserError(_("Nhập sai giá trị tỷ lệ đợt thanh toán. Vui lòng kiểm tra lại thông tin."))
            if not 0 <= self.bsd_tien_dtt:
                raise UserError(_("Nhập sai giá trị tiền đợt thanh toán. Vui lòng kiểm tra lại thông tin."))

    # Kiểm tra trùng dữ liệu hoa hồng
    @api.constrains('bsd_loai', 'bsd_phuong_thuc', 'bsd_cach_tinh', 'bsd_tu_ngay', 'bsd_den_ngay')
    def _constraint_record(self):
        # Lấy tất cả hoa hồng cùng loại
        hoa_hong = self.env['bsd.hoa_hong'].search([('bsd_loai', '=', self.bsd_loai),
                                                    ('bsd_phuong_thuc', '=', self.bsd_phuong_thuc),
                                                    ('bsd_cach_tinh', '=', self.bsd_cach_tinh),
                                                    ('id', '!=', self.id),
                                                    ('state', '!=', 'huy'),
                                                    ('bsd_du_an_id', '=', self.bsd_du_an_id.id)])
        if self.bsd_cach_tinh == 'so_luong':
            hoa_hong_time = hoa_hong.filtered(lambda m: not (m.bsd_sl_den < self.bsd_sl_tu < self.bsd_sl_den
                                                         or self.bsd_sl_tu < self.bsd_sl_den < m.bsd_sl_tu))
            if hoa_hong_time:
                khoang_time = [(t.bsd_tu_ngay, t.bsd_den_ngay) for t in hoa_hong_time.sorted('bsd_tu_ngay')]
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
                    raise UserError("Đã tồn tại hoa hồng này.\nVui lòng kiểm tra lại thông tin.")
            hoa_hong_sl = hoa_hong.filtered(lambda m: not (m.bsd_den_ngay < self.bsd_tu_ngay < self.bsd_den_ngay
                                                       or self.bsd_tu_ngay < self.bsd_den_ngay < m.bsd_tu_ngay))
            if hoa_hong_sl:
                so_luong = [(t.bsd_sl_tu, t.bsd_sl_den) for t in hoa_hong_sl.sorted('bsd_sl_tu')]
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
                    raise UserError("Đã tồn tại hoa hồng này.\nVui lòng kiểm tra lại thông tin.")
        else:
            hoa_hong_time = hoa_hong.filtered(lambda m: not (m.bsd_tien_den < self.bsd_tien_tu < self.bsd_tien_den
                                                         or self.bsd_tien_tu < self.bsd_tien_den < m.bsd_tien_tu))
            if hoa_hong_time:
                khoang_time = [(t.bsd_tu_ngay, t.bsd_den_ngay) for t in hoa_hong_time.sorted('bsd_tu_ngay')]
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
                    raise UserError("Đã tồn tại hoa hồng này.\nVui lòng kiểm tra lại thông tin.")
            hoa_hong_tien = hoa_hong.filtered(lambda m: not (m.bsd_den_ngay < self.bsd_tu_ngay < self.bsd_den_ngay
                                                       or self.bsd_tu_ngay < self.bsd_den_ngay < m.bsd_tu_ngay))
            if hoa_hong_tien:
                so_tien = [(t.bsd_tien_tu, t.bsd_tien_den) for t in hoa_hong_tien.sorted('bsd_tien_tu')]
                flag_tien = True
                if self.bsd_tien_tu < self.bsd_sl_den < so_tien[0][0]:
                    flag_tien = False
                elif so_tien[-1][1] < self.bsd_tien_tu < self.bsd_tien_den:
                    flag_tien = False
                else:
                    le = len(so_tien)
                    for i in range(0, le - 1):
                        t_first = so_tien[i][1]
                        t_last = so_tien[i + 1][0]
                        if t_first < self.bsd_tien_tu < self.bsd_tien_den < t_last:
                            _logger.debug("Nằm trong khoảng cho phep")
                            flag_tien = False
                if flag_tien:
                    raise UserError("Đã tồn tại hoa hồng này.\nVui lòng kiểm tra lại thông tin.")

    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ngay_duyet': fields.Date.today(),
                'bsd_ly_do': '',
            })

    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_hoa_hong_action').read()[0]
        return action

    # DM.12.03 Hủy khuyến mãi
    def action_huy(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'huy',
            })

    def auto_kt_hh(self):
        if self.state == 'duyet':
            self.write({
                'state': 'het_han'
            })

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã hoa hồng.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdHoaHong, self).create(vals)
