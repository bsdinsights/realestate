# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdChietKhauNoiBo(models.Model):
    _name = 'bsd.ck_nb'
    _rec_name = 'bsd_ten_ck_nb'
    _description = "Thông tin chiết khấu nội bộ"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_nb = fields.Char(string="Mã", help="Mã danh sách chiết khấu nội bộ", required=True, readonly=True, copy=False,
                               default='/')

    _sql_constraints = [
        ('bsd_ma_ck_nb_unique', 'unique (bsd_ma_ck_nb)',
         'Mã chiết khấu nội bộ đã tồn tại !'),
    ]
    bsd_ten_ck_nb = fields.Char(string="Tên", help="Tên danh sách chiết khấu nội bộ", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu nội bộ",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu nội bộ",
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
    bsd_ct_ids = fields.One2many('bsd.ck_nb_ct', 'bsd_ck_nb_id', string="Chi tiết")
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    # DM.16.01 Xác nhận chiết khấu
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan'
        })

    # DM.16.02 Duyệt chiết khấu
    def action_duyet(self):
        self.write({
            'state': 'duyet',
        })

    # DM.16.04 Không duyệt chiết khấu
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_ck_nb_action').read()[0]
        return action

    # DM.16.03 Hủy chiết khấu
    def action_huy(self):
        self.write({
            'state': 'huy',
        })

    @api.model
    def create(self, vals):
        sequence = False
        if vals.get('bsd_ma_ck_nb', '/') == '/':
            sequence = self.env['bsd.ma_bo_cn'].search([('bsd_loai_cn', '=', 'bsd.ck_nb')], limit=1).bsd_ma_tt_id
            vals['bsd_ma_ck_nb'] = self.env['ir.sequence'].next_by_code('bsd.ck_nb') or '/'
        if not sequence:
            raise UserError(_('Danh mục mã chưa khai báo mã danh sách chiết khấu nội bộ'))
        vals['bsd_ma_ck_nb'] = sequence.next_by_id()
        return super(BsdChietKhauNoiBo, self).create(vals)


class BsdChietKhauNoiBoChiTiet(models.Model):
    _name = 'bsd.ck_nb_ct'
    _description = "Thông tin chiết khấu nội bộ chi tiết"
    _rec_name = 'bsd_chiet_khau_id'

    bsd_ck_nb_id = fields.Many2one('bsd.ck_nb', string="Chiết khấu nội bộ")
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu", required=True,
                                        domain=[('bsd_loai_ck', '=', 'noi_bo'), ('state', '=', 'duyet')])
    bsd_ma_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ma_ck")
    bsd_tu_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_tu_ngay")
    bsd_den_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_den_ngay")
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh")
    bsd_tien_ck = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck")
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
