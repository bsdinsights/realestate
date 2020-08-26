# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdBanGiaoSanPham(models.Model):
    _name = 'bsd.bg_sp'
    _description = "Bàn giao sản phẩm"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_bg'

    bsd_ma_bg = fields.Char(string="Mã", help="Mã bàn giao sản phẩm", required=True, readonly=True,
                            copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_bg_unique', 'unique (bsd_ma_bg)',
         'Mã bàn giao sản phẩm đã tồn tại !')
    ]
    bsd_ngay_tao_bg = fields.Datetime(string="Ngày", help="Ngày tạo bàn giao sản phẩm",
                                      required=True, default=lambda self: fields.Datetime.now(),
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_ten_bg = fields.Char(string="Tiêu đề", required=True,
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_duyet_bgdb = fields.Boolean(related="bsd_hd_ban_id.bsd_duyet_bgdb")
    bsd_tien_tt_hd = fields.Monetary(related="bsd_hd_ban_id.bsd_tien_tt_hd",
                                     help="Tổng tiền khách hàng thanh toán(Không bao gồm phí bảo trì, phí quản lý")
    bsd_tl_tt_hd = fields.Float(related="bsd_hd_ban_id.bsd_tl_tt_hd")
    bsd_dt_tt = fields.Float(related="bsd_unit_id.bsd_dt_tt")
    bsd_ngay_dkbg = fields.Date(related="bsd_hd_ban_id.bsd_ngay_dkbg", string="Ngày DKBG theo hợp đồng",
                                help="Ngày dự kiến bàn giao trên hợp đồng")
    bsd_ngay_in = fields.Datetime(string="Ngày in", help="Ngày in biên bản bàn giao sản phẩm", readonly=True)
    bsd_nguoi_in_id = fields.Many2one('res.users', string="Người in", help="Người in biên bản bàn giao sản phẩm",
                                      readonly=True)
    bsd_ngay_bg_tt = fields.Datetime(string="Ngày BG thực tế", help="Ngày bàn giao sản phẩm thực tế", readonly=True)
    bsd_nguoi_bg_tt_id = fields.Many2one('hr.employee', string="Người BG thực tế",
                                         help="Người bàn giao sản phẩm thực tế", readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('ban_giao', 'Bàn giao'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Char(string="Lý do hủy", readonly=True, tracking=2)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
        self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id

    # DV.11.01 Xác nhận bàn giao sản phẩm
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    # DV.11.02 In biên bản bàn giao sản phẩm
    def action_in(self):
        action = self.env.ref('bsd_dich_vu.bsd_bg_sp_report_action').read()[0]
        return action

    # DV.11.03 Ký biên bản bàn giao sản phẩm
    def action_ky(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_bg_sp_action').read()[0]
        return action

    # DV.11.04 Hủy bàn giao sản phẩm
    def action_huy(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_huy_bg_sp_action').read()[0]
        return action

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã bàn giao sản phẩm'))
        vals['bsd_ma_bg'] = sequence.next_by_id()
        return super(BsdBanGiaoSanPham, self).create(vals)
