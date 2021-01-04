# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdViPhamHopDong(models.Model):
    _name = 'bsd.vp_hd'
    _description = "Vi phạm hợp đồng"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten'

    bsd_ma = fields.Char(string="Mã", help="Mã vi phạm hợp đồng", required=True, readonly=True,
                         copy=False, default='/')

    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã vi phạm hợp đồng đã tồn tại !')
    ]
    bsd_ten = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày", required=True, default=lambda self: fields.Date.today(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", readonly=True, required=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one("res.partner", string="Khách hàng", reaonly=True,
                                        required=True, help="Khách hàng",
                                        states={'nhap': [('readonly', False)]})
    bsd_ben_vp = fields.Selection([('khach_hang', 'Khách hàng'),
                                   ('chu_dt', 'Chủ đầu tư')], string="Bên vi phạm", required=True,
                                  default='khach_hang',
                                  readonly=True, states={'nhap': [('readonly', False)]})
    bsd_chu_dt_id = fields.Many2one("res.partner", string="Chủ đầu tư", help="Chủ đầu tư dự án", readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_ngay_bd = fields.Date(string="Ngày bắt đầu", help="Ngày bắt đầu", readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_kt = fields.Date(string="Ngày kết thúc", help="Ngày kết thúc", readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_so_tp = fields.Monetary(string="Số tiền phạt", help="Số tiền phạt", required=True,
                                readonly=True, states={'nhap': [('readonly', False)]})
    bsd_so_tp_tt = fields.Monetary(string="Số tiền phạt tt",
                                   help="Số tiền phạt thực tế sau khi đã thương lượng với khách hàng", readonly=True,
                                   states={'nhap': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default='nhap', required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", help="Người xác nhận", readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", help="Ngày xác nhận", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", help="Ngày duyệt", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_in = fields.Date(string="Ngày in", help="Ngày in", readonly=True)
    bsd_nguoi_in_id = fields.Many2one('res.users', string="Người in", readonly=True)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd(self):
        self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id

    @api.onchange('bsd_du_an_id')
    def _onchange_du_an(self):
        self.bsd_chu_dt_id = self.bsd_du_an_id.bsd_chu_dt_id

    # DV.09.01 Xác nhận
    def action_xac_nhan(self):
        # Kiểm tra hợp đông đã bị thanh lý thì hủy , ghi nhận lý do hủy
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            self.write({
                'state': 'huy',
                'bsd_ly_do': 'Hợp đồng đã bị thanh lý',
            })
            message_id = self.env['message.wizard'].create(
                {'message': _('Tình trạng hợp đồng là đã thanh lý và Vi phạm này sẽ bị hủy tự động')})
            return {
                'name': _('Thông báo'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                'res_id': message_id.id,
                'target': 'new'
            }
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
                'bsd_ngay_xn': fields.Date.today(),
                'bsd_nguoi_xn_id': self.env.uid,
            })

    def action_duyet(self):
        # Kiểm tra hợp đông đã bị thanh lý thì hủy , ghi nhận lý do hủy
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            self.write({
                'state': 'huy',
                'bsd_ly_do': 'Hợp đồng đã bị thanh lý',
            })
            message_id = self.env['message.wizard'].create(
                {'message': _('Tình trạng hợp đồng là đã thanh lý và Vi phạm này sẽ bị hủy tự động')})
            return {
                'name': _('Thông báo'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                'res_id': message_id.id,
                'target': 'new'
            }
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
                'bsd_ngay_duyet': fields.Date.today(),
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ly_do': '',
            })

    def action_in_cn(self):
        return self.env.ref('bsd_dich_vu.bsd_vp_hd_report_action').read()[0]

    def action_ky(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_vp_hd_action').read()[0]
        return action

    # DV.09.06 Không duyệt chuyển nhượng
    def action_khong_duyet(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_khong_duyet_vp_hd_action').read()[0]
        return action

    # DV.09.07 Hủy chuyển nhượng
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy'
            })

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã vi phạm hợp đồng.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdViPhamHopDong, self).create(vals)
