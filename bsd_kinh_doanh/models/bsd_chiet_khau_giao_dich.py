# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdChietKhauGiaoDich(models.Model):
    _name = 'bsd.ps_gd_ck'
    _rec_name = 'bsd_ten'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Ghi nhận chiết khấu giao dịch'

    bsd_ma = fields.Char(string="Mã", help="Mã chiết khấu giao dịch", required=True, readonly=True, copy=False,
                         default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã  đã tồn tại !')]
    bsd_ten = fields.Char(string="Tên", required=True, help="Tên chiết khấu giao dịch")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Tên đặt cọc")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True)
    bsd_loai_ps = fields.Selection([('chung', 'Chung'),
                                    ('noi_bo', 'Nội bộ'),
                                    ('mua_si', 'Mua sỉ'),
                                    ('ltt', 'Lịch thanh toán'),
                                    ('ttth', 'Thanh toán trước hạn'),
                                    ('ttn', 'Thanh toán nhanh'),
                                    ('dac_biet', 'Đặc biệt'),
                                    ('pl_ck', 'Phụ lục thay đổi CKTM')], string="Loại phát sinh",
                                   default='chung', required=True, help="Loại phát sinh")
    bsd_ltt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", help="Đợt thanh toán")
    bsd_sn_th = fields.Integer(string="Số ngày trước hạn", help="Số ngày dùng để tính thanh toán trước hạn")
    bsd_tien_dot_tt = fields.Monetary(string="Số tiền thanh toán", help="Số tiền thanh toán của đợt thanh toán")
    bsd_tl_ck = fields.Float(string="Tỷ lệ CK", help="Tỷ lệ chiết khấu")
    bsd_tien = fields.Monetary(string="Tiền CK", help="Tiền")
    bsd_tien_ck = fields.Monetary(string="Tổng tiền", help="Tổng tiền chiết khấu")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('xac_nhan', 'Xác nhận'),
                              ('huy', 'Hủy')], string="Trạng thái",
                             default='xac_nhan', tracking=1, help="Trạng thái", required=True)

    # TC.15.03 Hủy chiết khấu
    def action_huy(self):
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
            raise UserError(_('Dự án chưa có mã chiết khấu giao dịch.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdChietKhauGiaoDich, self).create(vals)