# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdChietKhauMuaSi(models.Model):
    _name = 'bsd.ck_ms'
    _rec_name = 'bsd_ten_ck_ms'
    _description = "Thông tin chiết khấu mua sỉ"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ck_ms = fields.Char(string="Mã", help="Mã danh sách chiết khấu mua sỉ", required=True, readonly=True, copy=False,
                               default='/')
    _sql_constraints = [
        ('bsd_ma_ck_ms_unique', 'unique (bsd_ma_ck_ms)',
         'Mã chiết khấu mua sỉ đã tồn tại !'),
    ]
    bsd_ten_ck_ms = fields.Char(string="Tên", help="Tên chiết khấu mua sỉ", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chiết khấu mua sỉ",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chiết khấu mua sỉ",
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
    bsd_ct_ids = fields.One2many('bsd.ck_ms_ct', 'bsd_ck_ms_id', string="Chi tiết")
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
        action = self.env.ref('bsd_danh_muc.bsd_wizard_ck_ms_action').read()[0]
        return action

    # DM.15.03 Hủy chiết khấu
    def action_huy(self):
        self.write({
            'state': 'huy',
        })

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã chiết khấu mua sỉ'))
        vals['bsd_ma_ck_ms'] = sequence.next_by_id()
        return super(BsdChietKhauMuaSi, self).create(vals)


class BsdChietKhauMuaSiChiTiet(models.Model):
    _name = 'bsd.ck_ms_ct'
    _description = "Thông tin chiết khấu mua sỉ chi tiết"
    _rec_name = 'bsd_chiet_khau_id'

    bsd_ck_ms_id = fields.Many2one('bsd.ck_ms', string="Chiết khấu mua sỉ")
    bsd_chiet_khau_id = fields.Many2one('bsd.chiet_khau', string="Chiết khấu", required=True,
                                        domain=[('bsd_loai_ck', '=', 'mua_si'), ('state', '=', 'duyet')])
    bsd_ma_ck = fields.Char(related="bsd_chiet_khau_id.bsd_ma_ck")
    bsd_tu_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_tu_ngay")
    bsd_den_ngay = fields.Date(related="bsd_chiet_khau_id.bsd_den_ngay")
    bsd_cung_tang = fields.Boolean(related="bsd_chiet_khau_id.bsd_cung_tang")
    bsd_sl_tu = fields.Integer(related="bsd_chiet_khau_id.bsd_sl_tu")
    bsd_sl_den = fields.Integer(related="bsd_chiet_khau_id.bsd_sl_den")
    bsd_cach_tinh = fields.Selection(related="bsd_chiet_khau_id.bsd_cach_tinh")
    bsd_tien_ck = fields.Monetary(related="bsd_chiet_khau_id.bsd_tien_ck")
    bsd_tl_ck = fields.Float(related="bsd_chiet_khau_id.bsd_tl_ck")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

