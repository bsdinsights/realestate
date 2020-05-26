# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class BsdHuyGC(models.Model):
    _name = 'bsd.huy_gc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_huy_gc'
    _description = 'Phiếu đề nghị hủy giữ chỗ'

    bsd_ma_huy_gc = fields.Char(string="Mã", help="Mã phiếu hủy", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_huy_gc = fields.Date(string="Ngày", help="Ngày hủy", required=True,
                                  default=lambda self: fields.Date.today(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án",required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_loai_gc = fields.Selection([('gc_tc', 'Giữ chỗ thiện chí'), ('giu_cho', 'Giữ chỗ')],
                                   string="Loại", required=True, default='gc_tc', help="Loại phiếu hủy",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Căn hộ",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí bị hủy",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_tien = fields.Monetary(string="Số tiền", help="Số tiền", compute='_compute_tien', store=True)
    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Số tiền đã thanh toán",
                                     compute='_compute_tien', store=True)
    bsd_hoan_tien = fields.Boolean(string="Hoàn tiền", help="Hoàn tiền",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             tracking=1, default="nhap", required=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.depends('bsd_gc_tc_id', 'bsd_giu_cho_id', 'bsd_loai_gc')
    def _compute_tien(self):
        for each in self:
            if each.bsd_loai_gc == 'gc_tc':
                each.bsd_tien = each.bsd_gc_tc_id.bsd_tien_gc
                each.bsd_tien_da_tt = each.bsd_gc_tc_id.bsd_tien_da_tt
            elif each.bsd_loai_gc == 'giu_cho':
                each.bsd_tien = each.bsd_giu_cho_id.bsd_tien_gc
                each.bsd_tien_da_tt = each.bsd_giu_cho_id.bsd_tien_da_tt

    # KD.14.01 Xác nhận hủy giữ chỗ
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    # KD.14.02 Duyệt hủy giữ chỗ
    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
            })
        if self.bsd_loai_gc == 'giu_cho':
            # Cập nhật trạng thái giữ chỗ, mã hủy giữ chỗ
            if self.bsd_giu_cho_id.state == 'huy':
                raise UserError("Giữ chỗ đã bị hủy. Vui lòng kiểm tra lại.")
            else:
                self.bsd_giu_cho_id.write({
                    'state': 'dong',
                    'bsd_huy_gc_id': self.id
                })

    # KD.14.03 Không duyệt Hủy giữ chỗ
    def action_khong_duyet(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_huy_gc_action').read()[0]
        return action

    # KD.14.04 Hủy hủy giữ chỗ
    def action_huy(self):
        if self.state == 'xac_nhan':
            self.write({'state': 'huy'})

