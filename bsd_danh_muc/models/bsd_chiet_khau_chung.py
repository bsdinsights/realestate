# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdChietKhauChung(models.Model):
    _name = 'bsd.ck_ch'
    _rec_name = 'bsd_ten_ck_ch'
    _description = "Thông tin chiết khấu chung"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_ch = fields.Char(string="Mã", help="Mã chiết khấu chung", required=True, readonly=True, copy=False,
                               default='/')
    _sql_constraints = [
        ('bsd_ma_ck_ch_unique', 'unique (bsd_ma_ck_ch)',
         'Mã chiết khấu chung đã tồn tại !'),
    ]
    bsd_ten_ck_ch = fields.Char(string="Tên", required=True, help="Tên chiết khấu chung",
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
    bsd_ct_ids = fields.One2many('bsd.ck_ch_ct', 'bsd_ck_ch_id', string="Chi tiết",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    # DM.14.01 Xác nhận chiết khấu
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan'
        })

    # DM.14.02 Duyệt chiết khấu
    def action_duyet(self):
        self.write({
            'state': 'duyet',
        })

    # DM.14.04 Không duyệt chiết khấu
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_ck_ch_action').read()[0]
        return action

    # DM.14.03 Hủy chiết khấu
    def action_huy(self):
        self.write({
            'state': 'huy',
        })

    @api.model
    def create(self, vals):
        sequence = False
        if vals.get('bsd_ma_ck_ch', '/') == '/':
            sequence = self.env['bsd.ma_bo_cn'].search([('bsd_loai_cn', '=', 'bsd.ck_ch')], limit=1).bsd_ma_tt_id
            vals['bsd_ma_ck_ch'] = self.env['ir.sequence'].next_by_code('bsd.ck_ch') or '/'
        if not sequence:
            raise UserError(_('Danh mục mã chưa khai báo mã danh sách chiết khấu'))
        vals['bsd_ma_ck_ch'] = sequence.next_by_id()
        return super(BsdChietKhauChung, self).create(vals)


class BsdChietKhauChungChiTiet(models.Model):
    _name = 'bsd.ck_ch_ct'
    _description = "Thông tin chiết khấu chung chi tiết"
    _rec_name = 'bsd_chiet_khau_id'

    bsd_ck_ch_id = fields.Many2one('bsd.ck_ch', string="Chiết khấu chung")
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu", required=True,
                                        domain=[('bsd_loai_ck', '=', 'chung'), ('state', '=', 'duyet')])
    bsd_ma_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ma_ck")
    bsd_tu_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_tu_ngay")
    bsd_den_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_den_ngay")
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh")
    bsd_tien_ck = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck")
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
