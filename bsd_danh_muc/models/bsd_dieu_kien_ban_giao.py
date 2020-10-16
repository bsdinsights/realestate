# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdDkbg(models.Model):
    _name = 'bsd.dk_bg'
    _rec_name = 'bsd_ten_dkbg'
    _description = "Điều kiện bàn giao"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_dkbg = fields.Char(string="Mã", help="Mã điều kiện bàn giao", required=True, readonly=True, copy=False,
                              default='/')
    _sql_constraints = [
        ('bsd_ma_dkbg_unique', 'unique (bsd_ma_dkbg)',
         'Mã điều kiện bàn giao đã tồn tại !'),
    ]
    bsd_ten_dkbg = fields.Char(string="Tên", help="Tên điều kiện bàn giao", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True)
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu hiệu lực của điều kiện bàn giao", required=True)
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc hiệu lực của điều kiện bàn giao", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_loai_bg = fields.Selection([('tho', 'Bàn giao thô'),
                                    ('co_ban', 'Bàn giao hoàn thiện cơ bản'),
                                    ('hoan_thien', 'Bàn giao hoàn thiện'),
                                    ('noi_that', 'Bàn giao hoàn thiện mặt ngoài và thô bên trong'),
                                    ('bo_sung', 'Bàn giao bổ sung')], string="Loại bàn giao",
                                   help="Tình trạng của căn hộ khi bàn giao")
    bsd_dk_tt = fields.Selection([('tien', 'Giá trị'),
                                  ('ty_le', 'Phần trăm'),
                                  ('m2', 'Đơn giá'),
                                  ], string="Điều kiện thanh toán", default="m2", required=True,
                                 help="Điều kiện thanh toán để được nhận bàn giao")
    bsd_loai_sp_id = fields.Many2one('bsd.loai_sp', string="Theo loại sản phẩm", help="Theo loại sản phẩm")
    bsd_gia_m2 = fields.Monetary(string="Giá/m2", help="Giá/m2 theo đợt bàn giao")
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền thanh toán theo đợt bàn giao")
    bsd_ty_le = fields.Float(string="Tỷ lệ (%)", help="Tỷ lệ thanh toán theo đợt bàn giao")
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('het_han', 'Hết hạn'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', readonly=1, required=True, tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True)
    
    def _get_name(self):
        dk_bg = self
        name = dk_bg.bsd_ten_dkbg or ''
        if self._context.get('show_info'):
            if dk_bg.bsd_dk_tt == 'tien':
                name = "%s - %s - %s đ" % (dk_bg.bsd_ten_dkbg, "Tiền", dk_bg.bsd_tien)
            elif dk_bg.bsd_dk_tt == 'ty_le':
                name = "%s - %s - %s %s" % (dk_bg.bsd_ten_dkbg, "Phần trăm", dk_bg.bsd_ty_le, "%")
            else:
                name = "%s - %s - %s đ" % (dk_bg.bsd_ten_dkbg, "Đơn giá", dk_bg.bsd_gia_m2)
        return name

    def name_get(self):
        res = []
        for dk_bg in self:
            name = dk_bg._get_name()
            res.append((dk_bg.id, name))
        return res

    # DM.13.01 Xác nhận chiết khấu
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # DM.13.02 Duyệt chiết khấu
    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
            })

    # DM.13.04 Không duyệt chiết khấu
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_dk_bg_action').read()[0]
        return action

    # DM.13.03 Hủy chiết khấu
    def action_huy(self):
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
            raise UserError(_('Dự án chưa có mã điều kiện bàn giao.'))
        vals['bsd_ma_ck'] = sequence.next_by_id()
        return super(BsdDkbg, self).create(vals)
