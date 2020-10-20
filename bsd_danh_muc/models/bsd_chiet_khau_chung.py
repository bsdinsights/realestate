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
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True,
                               readonly=True,
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

    # Kiểm tra dữ liệu ngày hiệu lực
    @api.constrains('bsd_tu_ngay', 'bsd_den_ngay')
    def _constrains_ngay(self):
        for each in self:
            if each.bsd_tu_ngay:
                if not each.bsd_den_ngay:
                    raise UserError(_("Sai thông tin ngày kết thúc.\n Vui lòng kiểm tra lại thông tin."))
                elif each.bsd_den_ngay < each.bsd_tu_ngay:
                    raise UserError(_("Ngày kết thúc không thể nhỏ hơn ngày bắt đầu.\n Vui lòng kiểm tra lại thông tin."))

    # DM.14.01 Xác nhận chiết khấu
    def action_xac_nhan(self):
        # Kiểm tra đã có chi tiết chưa
        if not self.bsd_ct_ids:
            raise UserError(_("Chưa nhập chi tiết chiết khấu.\n Vui lòng kiểm tra lại thông tin."))
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    # DM.14.02 Duyệt chiết khấu
    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
                'bsd_ngay_duyet': fields.Date.today(),
                'bsd_nguoi_duyet_id': self.env.uid,
            })

    # DM.14.04 Không duyệt chiết khấu
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_ck_ch_action').read()[0]
        return action

    # DM.14.03 Hủy chiết khấu
    def action_huy(self):
        dot_mb_dang_ph = self.env['bsd.dot_mb'].search([('state', '=', 'ph'),
                                                        ('bsd_ck_ch_id', '=', self.id)])
        if self.state == 'duyet' and dot_mb_dang_ph:
            raise UserError(_("Danh sách chiết khấu chung đang nằm trong đợt mở bán đã phát hành."))
        if self.state == 'xac_nhan':
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
            raise UserError(_('Dự án chưa có mã chiết khấu chung.'))
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
