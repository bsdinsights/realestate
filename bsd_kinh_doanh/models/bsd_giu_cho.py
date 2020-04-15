# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdRapCan(models.Model):
    _name = 'bsd.giu_cho'
    _description = "Thông tin giữ chỗ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_gc'

    bsd_ma_gc = fields.Char(string="Mã giữ chỗ", required=True,
                            readonly=True, help="Mã giữ chỗ",
                            states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_gc_unique', 'unique (bsd_ma_gc)',
         'Mã giữ chỗ đã tồn tại !'),
    ]
    bsd_ngay_gc = fields.Datetime(string="Ngày giữ chỗ", required=True, default=datetime.datetime.now(),
                                  readonly=True, help='Ngày giữ chỗ',
                                  states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True,
                                        readonly=True, help="Tên khách hàng",
                                        states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True, help="Tên dự án",
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", required=True,
                                  readonly=True, help="Tên căn hộ",
                                  states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True, help="Diễn giải",
                                states={'nhap': [('readonly', False)]})
    bsd_truoc_mb = fields.Boolean(string="Trước mở bán", default=False,
                                  help="Thông tin xác định Giữ chỗ được tạo trước hay sau khi unit có đợt mở bán",
                                  readonly=True, required=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', related="bsd_unit_id.bsd_dot_mb_id",
                                    help="Đợt mở bán",
                                    string="Đợt mở bán", store=True)
    bsd_bang_gia_id = fields.Many2one('product.pricelist', related="bsd_dot_mb_id.bsd_bang_gia_id", store=True,
                                      string="Bảng giá", help="Bảng giá bán")
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", required=True,
                                  readonly=True, help="Tiền giữ chỗ",
                                  states={'nhap': [('readonly', False)]})
    bsd_nvbh_id = fields.Many2one('hr.employee', string="Nhân viên BH",
                                  readonly=True, help="Nhân viên bán háng",
                                  states={'nhap': [('readonly', False)]})
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch",domain=[('is_company', '=', True)],
                                    readonly=True, help="Sàn giao dịch",
                                    states={'nhap': [('readonly', False)]})
    bsd_ctv_id = fields.Many2one('res.partner', string="Công tác viên", domain=[('is_company', '=', False)],
                                 readonly=True, help="Cộng tác viên",
                                 states={'nhap': [('readonly', False)]})
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu",help="Cá nhân hoặc đơn vị giới thiệu",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_hh_gc = fields.Datetime(string="Hạn giữ chỗ", help="Hiệu lực của giữ chỗ", compute='_compute_hl_gc', store=True)
    bsd_gc_da = fields.Boolean(string="Giữ chỗ dự án", help="""Thông tin ghi nhận Giữ chỗ được tự động tạo từ 
                                                                giữ chỗ thiện chí hay không""", readonly=True)
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", readonly=True,
                                   help="Phiếu giữ chỗ thiện chí",)
    bsd_rap_can_id = fields.Many2one('bsd.rap_can', string="Ráp căn", help="Phiếu ráp căn", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('dat_cho', 'Đặt chỗ'),
                              ('giu_cho', 'Giữ chỗ'),
                              ('bao_gia', 'Báo giá'),
                              ('huy', 'Hủy')], default='nhap', string="Trạng thái", tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_thanh_toan = fields.Selection([('chua_tt', 'Chưa thanh toán'),
                                       ('dang_tt', 'Đang thanh toán'),
                                       ('da_tt', 'Đã thanh toán')], string="Thanh toán", default="chua_tt",
                                      help="Thanh toán",
                                      required=True)
    bsd_ngay_tt = fields.Datetime(string="Ngày thanh toán", help="Ngày (kế toán xác nhận) thanh toán giữ chỗ",
                                  readonly=True)
    bsd_stt_bg = fields.Integer(string="STT báo giá", readonly=True, help="Số thứ tự ưu tiên làm báo giá")
    bsd_ngay_hh_bg = fields.Datetime(string="Hạn báo giá", help="Hiệu lực được làm báo giá", readonly=True)
    bsd_het_han_bg = fields.Boolean(string="Hết hạn báo giá", readonly=True, default=False,
                                    help="Thông tin ghi nhận thời gian làm báo giá có bok hết hiệu lực hay chưa")

    @api.onchange('bsd_du_an_id')
    def _onchange_unit(self):
        self.bsd_unit_id = False

    # KD.07.02 Ràng buộc số giữ chỗ theo căn hộ/ NVBH
    @api.constrains('bsd_nvbh_id', 'bsd_unit_id')
    def _constrain_unit_nv(self):
        _logger.debug(" Ràng buộc số giữ chỗ theo căn hộ/ NVBH")
        gc_in_unit = self.env['bsd.giu_cho'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                     ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                     ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                     ('state', 'in', ['nhap', 'giu_cho', 'dat_cho'])])
        if len(gc_in_unit) > self.bsd_du_an_id.bsd_gc_unit_nv:
            raise UserError("Tổng số giữ chỗ trên Căn hộ của bạn đã vượt quá quy định!")

    # KD.07.03 Ràng buộc số giữ chỗ theo căn hộ
    @api.constrains('bsd_unit_id')
    def _constrain_unit(self):

        gc_in_unit = self.env['bsd.giu_cho'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                     ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                     ('state', 'in', ['nhap', 'giu_cho', 'dat_cho'])])
        if len(gc_in_unit) > self.bsd_du_an_id.bsd_gc_unit:
            raise UserError("Tổng số giữ chỗ trên Căn hộ đã vượt quá quy định!")

    # KD.07.04 Ràng buộc số giữ chỗ theo NVBH/ngày
    @api.constrains('bsd_nvbh_id', 'bsd_ngay_gc')
    def _constrain_nv_bh(self):
        min_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        max_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
        gc_in_day = self.env['bsd.giu_cho'].search([('bsd_ngay_gc', '<', max_time),
                                                   ('bsd_ngay_gc', '>', min_time),
                                                   ('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                   ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                   ('state', 'in', ['nhap', 'giu_cho', 'dat_cho'])])
        if len(gc_in_day) >= self.bsd_du_an_id.bsd_gc_nv_ngay:
            raise UserError("Tổng số Giữ chỗ trên một ngày của bạn đã vượt quá quy định")

    # KD.07.05 Ràng buộc số giữ chỗ theo căn hộ/NVBH/ngày
    @api.constrains('bsd_nvbh_id', 'bsd_unit_id', 'bsd_ngay_gc')
    def _constrain_unit_nv_ngay(self):
        min_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        max_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
        gc_in_day = self.env['bsd.giu_cho'].search([('bsd_ngay_gc', '<', max_time),
                                                   ('bsd_ngay_gc', '>', min_time),
                                                   ('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                   ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                   ('bsd_nvbh_id', '=', self.bsd_nvbh_id.id),
                                                   ('state', 'in', ['nhap', 'giu_cho', 'dat_cho'])])
        if len(gc_in_day) >= self.bsd_du_an_id.bsd_gc_unit_nv_ngay:
            raise UserError("Tổng số Giữ chỗ trong ngày theo căn hộ của bạn đã vượt quá quy định")

    @api.onchange('bsd_unit_id', 'bsd_du_an_id')
    def _onchange_tien_gc(self):
        if self.bsd_unit_id:
            tien_gc = self.bsd_unit_id.bsd_tien_gc
            if tien_gc != 0:
                self.bsd_tien_gc = tien_gc
            else:
                self.bsd_tien_gc = self.bsd_du_an_id.bsd_tien_gc

    # R.05 Tính hạn hiệu lực giữ chỗ
    @api.depends('bsd_ngay_gc', 'bsd_du_an_id')
    def _compute_hl_gc(self):
        for each in self:
            if each.bsd_ngay_gc:
                if not each.bsd_dot_mb_id:
                    days = each.bsd_du_an_id.bsd_gc_tmb or 0 if each.bsd_du_an_id else 0
                    each.bsd_ngay_hh_gc = each.bsd_ngay_gc + datetime.timedelta(days=days)
                else:
                    hours = each.bsd_du_an_id.bsd_gc_smb or 0 if each.bsd_du_an_id else 0
                    each.bsd_ngay_hh_gc = each.bsd_ngay_gc + datetime.timedelta(hours=hours)

    # KD07.01 Xác nhận giữ chỗ
    def action_xac_nhan(self):
        if not self.bsd_dot_mb_id:
            self.write({
                'state': 'dat_cho',
                'bsd_ngay_gc': datetime.datetime.now(),
            })
            # Cập nhật lại trạng thái unit
            self.bsd_unit_id.write({
                'state': 'dat_cho',
            })
        else:
            giu_cho_unit = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                           ('bsd_stt_bg', '>', 0)])
            stt = 1
            time_gc = self.bsd_du_an_id.bsd_gc_smb
            ngay_hh_bg = datetime.datetime.now() + datetime.timedelta(hours=time_gc)
            if giu_cho_unit:
                stt = max(filter(None, giu_cho_unit.mapped('bsd_stt_bg'))) + 1
                ngay_hh_bg = max(filter(None, giu_cho_unit.mapped('bsd_ngay_hh_bg'))) + datetime.timedelta(hours=time_gc)
            self.write({
                'state': 'giu_cho',
                'bsd_ngay_gc': datetime.datetime.now(),
                'bsd_stt_bg': stt,
                'bsd_ngay_hh_bg': ngay_hh_bg,
            })
            # Cập nhật lại trạng thái unit
            self.bsd_unit_id.write({
                'state': 'giu_cho',
            })

    # KD.07.07 Tự động hủy giữ chỗ quá hạn thanh toán
    def auto_huy_gc(self):
        self.write({
            'state': 'huy',
        })

    # R7 Ghi nhận thông tin trước mở bán
    @api.model
    def create(self, vals):
        res = super(BsdRapCan, self).create(vals)
        if res.bsd_unit_id.bsd_dot_mb_id:
            res.write({
                'bsd_truoc_mb': False,
            })
        else:
            res.write({
                'bsd_truoc_mb': True,
            })
        return res

    def write(self, vals):
        if 'bsd_unit_id' in vals:
            _logger.debug("Chạy ở đây")
            if self.env['product.product'].browse(vals['bsd_unit_id']).bsd_dot_mb_id:
                vals.update({
                    'bsd_truoc_mb': False,
                })
            else:
                vals.update({
                    'bsd_truoc_mb': True,
                })
            _logger.debug(vals)
        res = super(BsdRapCan, self).write(vals)
        return res
