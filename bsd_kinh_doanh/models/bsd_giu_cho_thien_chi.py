# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdGiuChoThienChi(models.Model):
    _name = 'bsd.gc_tc'
    _description = 'Giữ chỗ thiện chí'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_gctc'

    bsd_ma_gctc = fields.Char(string="Mã giữ chỗ", required=True, help="Mã giữ chỗ thiện chí",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_gctc_unique', 'unique (bsd_ma_gctc)',
         'Mã giữ chỗ thiện chí đã tồn tại !'),
    ]
    bsd_ngay_gctc = fields.Datetime(string="Ngày giữ chỗ", required=True, help="Ngày giữ chỗ thiện chí",
                                    readonly=True, default=datetime.datetime.now(),
                                    states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True,
                                        readonly=True, help="Khách hàng",
                                        states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True, help="Tên dự án",
                                   states={'nhap': [('readonly', False)]})
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ thiện chí",
                                  related='bsd_du_an_id.bsd_tien_gc', store=True)
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True, help="Diễn giải",
                                states={'nhap': [('readonly', False)]})
    bsd_nvbh_id = fields.Many2one('hr.employee', string="Nhân viên BH", help="Nhân viên bán hàng",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch", domain=[('is_company', '=', True)],
                                    readonly=True, help='Sàn giao dịch',
                                    states={'nhap': [('readonly', False)]})
    bsd_ctv_id = fields.Many2one('res.partner', string="Cộng tác viên", domain=[('is_company', '=', False)],
                                 readonly=True, help="Cộng tác viên",
                                 states={'nhap': [('readonly', False)]})
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu", help="Cá nhân hoặc đơn vị giới thiệu",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_hh_gctc = fields.Datetime(string="Hạn giữ chỗ", help="Hiệu lực của giữ chỗ",
                                readonly=True, compute='_compute_htgc', store=True)
    bsd_ngay_tt = fields.Datetime(string="Ngày thanh toán", help="Ngày (kế toán xác nhận) thanh toán giữ chỗ")
    bsd_ngay_ut = fields.Datetime(string="Ưu tiên ráp căn",
                                  help="Thời gian được sử dụng để xét ưu tiên khi làm phiếu ráp căn",
                                  readonly=True, compute="_compute_ngay_ut", store=True)
    bsd_het_han = fields.Boolean(string="Hết hạn", help="Giữ chỗ bị hết hạn sau khi thanh toán đủ",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_ngay_rc = fields.Datetime(string="Ngày ráp căn", help="Ngày thực tế ráp căn", readonly=True)
    bsd_ngay_huy_rc = fields.Datetime(string="Hủy ráp căn", help="Ngày hủy ráp căn", readonly=True)
    bsd_rap_can_id = fields.Many2one('bsd.rap_can', string="Ráp căn", help="Phiếu ráp căn", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('giu_cho', 'Giữ chỗ'),
                              ('huy', 'Hủy')], string="Trạng thái", default="nhap", tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_thanh_toan = fields.Selection([('chua_tt', 'Chưa thanh toán'),
                                       ('dang_tt', 'Đang thanh toán'),
                                       ('da_tt', 'Đã thanh toán')], string="Thanh toán", default="chua_tt",
                                      required=True)

    @api.depends('bsd_ngay_gctc')
    def _compute_htgc(self):
        for each in self:
            each.bsd_ngay_hh_gctc = each.bsd_ngay_gctc + datetime.timedelta(each.bsd_du_an_id.bsd_gc_tmb) + \
                             datetime.timedelta(minutes=1)

    @api.depends('bsd_ngay_tt')
    def _compute_ngay_ut(self):
        for each in self:
            if each.bsd_ngay_tt:
                each.bsd_ngay_ut = each.bsd_ngay_tt + datetime.timedelta(each.bsd_du_an_id.bsd_gc_tmb) + \
                                   datetime.timedelta(minutes=1)
            else:
                each.bsd_ngay_ut = False

    # KD.05.06 Quản lý số lượng giữ chỗ theo nhân viên bán hàng
    @api.constrains('bsd_nvbh_id')
    def _constrain_nv_bh(self):
        min_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        max_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
        gc_in_day = self.env['bsd.gc_tc'].search([('create_date', '<', max_time),
                                                  ('create_date', '>', min_time),
                                                  ('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                  ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                  ('state', '=', 'xac_nhan')])
        if len(gc_in_day) >= self.bsd_du_an_id.bsd_gc_nv_ngay:
            raise UserError("Số lượng giữ chỗ tối đa trên một ngày của bạn đã vượt mức.\n Vui lòng kiểm tra lại")

    # KD.05.01 Xác nhận giữ chỗ thiện chí
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
            'bsd_ngay_gctc': datetime.datetime.now(),
        })

    # KD.05.02 Hủy giữ chỗ thiện chí
    def action_huy(self):
        self.write({
            'state': 'huy',
        })

    # KD.05.03 Tự động hủy giữ chỗ
    def auto_huy_giu_cho(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'huy'
            })

    # KD.05.04 Tự động đánh dấu hết hạn giữ chỗ
    def auto_danh_dau_hh_gc(self):
        if self.state == 'thanh_toan':
            self.write({
                'bsd_het_han': True
            })