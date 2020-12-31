# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdKhuyenMai(models.Model):
    _name = 'bsd.khuyen_mai'
    _description = "Bảng chương trình khuyến mãi"
    _rec_name = 'bsd_ten_km'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_km = fields.Char(string="Mã", help="Mã khuyến mãi", required=True, readonly=True, copy=False,
                            default='/')

    _sql_constraints = [
        ('bsd_ma_km_unique', 'unique (bsd_ma_km)',
         'Mã khuyến mãi đã tồn tại !'),
    ]
    bsd_ten_km = fields.Char(string="Tên", help="Tên khuyến mãi", required=True,
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True, readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_gia_tri = fields.Monetary(string="Giá trị", help="Giá trị (tiền) được hưởng khuyến mãi", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_loai_km = fields.Selection([('tien_mat', 'Tiền mặt'), ('qua_tang', 'Quà tặng')],
                                   default='tien_mat',
                                   string="Loại khuyến mãi",
                                   required=True, readonly=True, states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection([('khong', 'Không'), ('ty_le', 'Tỷ lệ'), ('tien', 'Tiền'),
                                 ('ty_le_tien', 'Tỷ lệ hoặc tiền')],
                                string="Điều kiện", help="Điều kiện xét khuyến mãi", required=True, default='khong',
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tong_tt = fields.Monetary(string="Tổng thanh toán", help="Tổng giá trị thanh toán",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tl_tt = fields.Float(string="Tỷ lệ thanh toán", help="Tổng tỷ lệ thanh toán",
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", required=True, help="Ngày bắt đầu áp dụng khuyến mãi",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", required=True, help="Ngày kết thúc áp dụng khuyến mãi",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_ngay_hldc = fields.Date(string="Ngày đặt cọc", help="Ngày hiệu lực của đặt cọc",
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
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True)

    # Kiểm tra dữ liệu ngày hiệu lực
    @api.constrains('bsd_tu_ngay', 'bsd_den_ngay')
    def _constrains_ngay(self):
        for each in self:
            if each.bsd_tu_ngay:
                if not each.bsd_den_ngay:
                    raise UserError(_("Sai thông tin ngày kết thúc.\nVui lòng kiểm tra lại thông tin."))
                elif each.bsd_den_ngay < each.bsd_tu_ngay:
                    raise UserError(_("Ngày kết thúc không thể nhỏ hơn ngày bắt đầu.\nVui lòng kiểm tra lại thông tin."))

    # DM.12.01 Xác nhận khuyến mãi
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # DM.12.02 Duyệt khuyến mãi
    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ngay_duyet': fields.Datetime.now()
            })

    # DM.12.04 Không duyệt khuyến mãi
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_khuyen_mai_action').read()[0]
        return action

    # DM.12.03 Hủy khuyến mãi
    def action_huy(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'huy',
            })

    def auto_kt_km(self):
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
            raise UserError(_('Dự án chưa có mã khuyến mãi.'))
        vals['bsd_ma_km'] = sequence.next_by_id()
        return super(BsdKhuyenMai, self).create(vals)
