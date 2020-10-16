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
    bsd_gia_tri = fields.Monetary(string="Giá trị", help="Giá trị (tiền) được hưởng khuyến mãi", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
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
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', readonly=1, required=True, tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

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

    @api.model
    def create(self, vals):
        sequence = False
        if vals.get('bsd_ma_km', '/') == '/':
            sequence = self.env['bsd.ma_bo_cn'].search([('bsd_loai_cn', '=', 'bsd.khuyen_mai')], limit=1).bsd_ma_tt_id
            vals['bsd_ma_km'] = self.env['ir.sequence'].next_by_code('bsd.khuyen_mai') or '/'
        if not sequence:
            raise UserError(_('Danh mục mã chưa khai báo mã chương trình khuyến mãi'))
        vals['bsd_ma_km'] = sequence.next_by_id()
        return super(BsdKhuyenMai, self).create(vals)
