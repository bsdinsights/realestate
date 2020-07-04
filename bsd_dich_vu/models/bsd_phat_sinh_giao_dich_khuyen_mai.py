# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdPSGDKM(models.Model):
    _name = 'bsd.ps_gd_km'
    _description = 'Thông tin phát sinh giao dịch chiết khấu'
    _rec_name = 'bsd_ma_ht'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_ht = fields.Char(string="Mã hệ thống", help="Mã hệ thống", required=True, readonly=True, copy=False,
                                   default='/')
    _sql_constraints = [
        ('bsd_ma_ht_unique', 'unique (bsd_ma_ht)',
         'Mã hệ thống đã tồn tại !'),
    ]
    bsd_khuyen_mai_id = fields.Many2one('bsd.khuyen_mai', string="Tên khuyến mãi", required=True, help="Tên khuyến mãi")
    bsd_ma_km = fields.Char(related='bsd_khuyen_mai_id.bsd_ma_km')
    bsd_loai = fields.Selection(related='bsd_khuyen_mai_id.bsd_loai')
    bsd_dot_mb_id = fields.Many2one(related='bsd_hd_ban_id.bsd_dot_mb_id')
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng bán", required=True)
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True)
    bsd_gia_tri = fields.Monetary(related='bsd_khuyen_mai_id.bsd_gia_tri')
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_tu_ngay = fields.Date(related='bsd_khuyen_mai_id.bsd_tu_ngay')
    bsd_den_ngay = fields.Date(related='bsd_khuyen_mai_id.bsd_den_ngay')
    bsd_tong_tt = fields.Monetary(related='bsd_khuyen_mai_id.bsd_tong_tt')
    bsd_tl_tt = fields.Float(related='bsd_khuyen_mai_id.bsd_tl_tt')
    bsd_ngay_tt = fields.Date(string="Ngày thanh toán", help="Ngày tạo giao dịch khuyến mãi")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('huy', 'Hủy')], string="Trạng thái",
                             default='nhap', tracking=1, help="Trạng thái", required=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)

    # KD.15.01 Xác nhận giao dịch khuyến mãi
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    # KD.15.02 Duyệt giao dịch khuyến mãi
    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
            })

    # KD.15.03 Không duyệt giao dịch khuyến mãi
    def action_khong_duyet(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_ps_gd_km_action').read()[0]
        return action

    # KD.15.04 Hủy giao dịch khuyến mãi
    def action_huy(self):
        if self.state == 'xac_nhan':
            self.write({'state': 'huy'})

    @api.model
    def create(self, vals):
        sequence = False
        if vals.get('bsd_ma_ht', '/') == '/':
            sequence = self.env['bsd.ma_bo_cn'].search([('bsd_loai_cn', '=', 'bsd.ps_gd_km')], limit=1).bsd_ma_tt_id
            vals['bsd_ma_ht'] = self.env['ir.sequence'].next_by_code('bsd.ps_gd_km') or '/'
        if not sequence:
            raise UserError(_('Danh mục mã chưa khai báo mã giao dịch khuyến mãi'))
        vals['bsd_ma_ht'] = sequence.next_by_id()
        return super(BsdPSGDKM, self).create(vals)