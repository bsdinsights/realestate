# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class BsdBaoGia(models.Model):
    _name = 'bsd.bao_gia'
    _description = "Bảng tính giá căn hộ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_bao_gia'

    bsd_ma_bao_gia = fields.Char(string="Mã bảng giá", help="Mã bảng tính giá", required=True)
    _sql_constraints = [
        ('bsd_ma_bao_gia_unique', 'unique (bsd_ma_bao_gia)',
         'Mã bảng giá đã tồn tại !'),
    ]
    bsd_ten_bao_gia = fields.Char(string="Tên bảng giá", help="Tên bảng tính giá", required=True)
    bsd_ngay_bao_gia = fields.Datetime(string="Ngày", help="Ngày bảng tính giá", required=True,
                                       default=fields.Datetime.now())
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True)
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Tên giữ chỗ", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án",
                                   related="bsd_giu_cho_id.bsd_du_an_id", store=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Tên đợt mở bán",
                                    related="bsd_giu_cho_id.bsd_dot_mb_id", store=True)
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá", help="Bảng giá bán",
                                      related="bsd_dot_mb_id.bsd_bang_gia_id", store=True)
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ",
                                  related="bsd_giu_cho_id.bsd_tien_gc")
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc", compute='_compute_tien_dc', store=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Tên căn hộ",
                                  related="bsd_giu_cho_id.bsd_unit_id", store=True)
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng", help="Diện tích tim tường",
                             related="bsd_unit_id.bsd_dt_xd", store=True)
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế",
                             related="bsd_unit_id.bsd_dt_sd", store=True)
    bsd_thue_id = fields.Many2one('account.tax', string="Mã thuế", help="Mã thuế", required=True)
    bsd_qsdd_m2 = fields.Monetary(string="QSDĐ/ m2", help="Giá trị quyền sử dụng đất trên m2",
                                  related="bsd_unit_id.bsd_qsdd_m2", store=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", related="bsd_thue_id.amount", store=True)
    bsd_tl_pbt = fields.Float(string="% phí bảo trì", help="Tỷ lệ phí bảo trì", compute='_compute_tl_pbt', store=True)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán", required=True)
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán", compute="_compute_gia_ban", store=True)
    bsd_tien_ck = fields.Monetary(string="Chiết khấu", help="Tổng tiền chiết khấu")
    bsd_tien_bg = fields.Monetary(string="Tiền bàn giao", help="Tổng tiền bàn giao",
                                  compute='_compute_tien_bg', store=True)
    bsd_gia_truoc_thue = fields.Monetary(string="Giá bán trước thuế",
                                         help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ chiết khấu""",
                                         compute='_compute_gia_truoc_thue')
    bsd_tien_qsdd = fields.Monetary(string="Giá trị QSDĐ",
                                    help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""",
                                    related="bsd_unit_id.bsd_tien_gsdd", store=True)
    bsd_tien_thue = fields.Monetary(string="Tiền thuế",
                                    help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""",
                                    compute='_compute_tien_thue', store=True)
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán",
                                   related="bsd_unit_id.bsd_tien_pbt")
    bsd_tong_gia = fields.Monetary(string="Tổng giá bán",
                                   help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                   compute="_compute_tong_gia", store=True)
    bsd_thang_pql = fields.Integer(string="Số tháng đóng phí quản lý",
                                   help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức")
    bsd_tien_pql = fields.Monetary(string="Phí quản lý/ tháng", help="Số tiền phí quản lý cần đóng mỗi tháng")

    state = fields.Selection([('nhap', 'Nháp')], string="Trạng thái", default="nhap", help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_dk_bg_ids = fields.One2many('bsd.bao_gia_bg', 'bsd_bao_gia_id', string="Bàn giao")
    bsd_ltt_ids = fields.One2many('bsd.bao_gia_ltt', 'bsd_bao_gia_id', string="Lịch thanh toán")

    @api.depends('bsd_unit_id')
    def _compute_tien_dc(self):
        for each in self:
            if each.bsd_unit_id.bsd_tien_dc != 0:
                each.bsd_tien_dc = each.bsd_unit_id.bsd_tien_dc
            else:
                each.bsd_tien_dc = each.bsd_unit_id.bsd_du_an_id.bsd_tien_dc

    @api.depends('bsd_unit_id')
    def _compute_tl_pbt(self):
        for each in self:
            if each.bsd_unit_id.bsd_tien_dc != 0:
                each.bsd_tl_pbt = each.bsd_unit_id.bsd_tl_pbt
            else:
                each.bsd_tl_pbt = each.bsd_unit_id.bsd_du_an_id.bsd_tl_pbt

    @api.depends('bsd_unit_id', 'bsd_bang_gia_id')
    def _compute_gia_ban(self):
        for each in self:
            item = each.bsd_bang_gia_id.item_ids.filtered(
                    lambda x: x.product_tmpl_id == each.bsd_unit_id.product_tmpl_id)
            each.bsd_gia_ban = item.fixed_price

    @api.depends('bsd_dk_bg_ids.bsd_tien_bg')
    def _compute_tien_bg(self):
        for each in self:
            each.bsd_tien_bg = sum(each.bsd_dk_bg_ids.mapped('bsd_tien_bg'))

    @api.depends('bsd_gia_ban', 'bsd_tien_ck', 'bsd_tien_bg')
    def _compute_gia_truoc_thue(self):
        for each in self:
            each.bsd_gia_truoc_thue = each.bsd_gia_ban - each.bsd_tien_ck + each.bsd_tien_bg

    @api.depends('bsd_thue_suat', 'bsd_gia_truoc_thue', 'bsd_tien_qsdd')
    def _compute_tien_thue(self):
        for each in self:
            each.bsd_tien_thue = (each.bsd_gia_truoc_thue - each.bsd_tien_qsdd) * each.bsd_thue_suat / 100

    @api.onchange('bsd_unit_id')
    def _onchange_phi(self):
        for each in self:
            if each.bsd_unit_id.bsd_thang_pql != 0:
                each.bsd_tl_pbt = each.bsd_unit_id.bsd_thang_pql
            else:
                each.bsd_tl_pbt = each.bsd_unit_id.bsd_du_an_id.bsd_thang_pql

            if each.bsd_unit_id.bsd_thang_pql != 0:
                each.bsd_tl_pbt = each.bsd_unit_id.bsd_thang_pql
            else:
                each.bsd_tl_pbt = each.bsd_unit_id.bsd_du_an_id.bsd_thang_pql

    @api.depends('bsd_gia_truoc_thue', 'bsd_tien_thue','bsd_tien_pbt')
    def _compute_tong_gia(self):
        for each in self:
            each.bsd_tong_gia = each.bsd_gia_truoc_thue + each.bsd_tien_thue + each.bsd_tien_pbt

    def action_xac_nhan(self):
        pass

    def action_duyet(self):
        pass

    def action_in_bg(self):
        pass

    def action_in_gc(self):
        pass

    def action_lich_tt(self):
        pass

    def action_huy(self):
        pass

    def action_ky_bg(self):
        pass

    def action_ky_gc(self):
        pass


class BsdBaoGiaDKBG(models.Model):
    _name = 'bsd.bao_gia_bg'
    _description = 'Thông tin điều kiện bàn giao cho báo giá'
    _rec_name = 'bsd_dk_bg_id'

    bsd_dk_bg_id = fields.Many2one('bsd.dk_bg', string="Mã ĐKBG", help="Mã điều kiện bàn giao", required=True)
    bsd_ten_dkbg = fields.Char(related='bsd_dk_bg_id.bsd_ten_dkbg', store=True)
    bsd_dk_tt = fields.Selection(related='bsd_dk_bg_id.bsd_dk_tt', store=True)
    bsd_gia_m2 = fields.Monetary(related='bsd_dk_bg_id.bsd_gia_m2', store=True)
    bsd_tien = fields.Monetary(related='bsd_dk_bg_id.bsd_tien', store=True)
    bsd_ty_le = fields.Float(related="bsd_dk_bg_id.bsd_ty_le", store=True)
    bsd_tien_bg = fields.Monetary(string="Tiền bàn giao ", help="Tiền thanh toán theo điều kiện bàn giao ",
                                  compute="_compute_tien_bg", store=True)
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", help="Tên báo giá", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.constrains('bsd_tien_bg')
    def _check_tien_bg(self):
        for record in self:
            if record.bsd_tien_bg <= 0:
                raise ValidationError("Kiểm tra lại trường tiền bàn giao")

    @api.depends('bsd_dk_tt', 'bsd_gia_m2', 'bsd_tien', 'bsd_ty_le')
    def _compute_tien_bg(self):
        for each in self:
            if each.bsd_dk_tt == 'm2':
                each.bsd_tien_bg = each.bsd_gia_m2 * each.bsd_bao_gia_id.bsd_dt_sd
            elif each.bsd_dk_tt == 'tien':
                each.bsd_tien_bg = each.bsd_tien
            else:
                each.bsd_tien_bg = each.bsd_ty_le * each.bsd_bao_gia_id.bsd_gia_ban / 100


class BsdBaoGiaLTT(models.Model):
    _name = 'bsd.bao_gia_ltt'
    _description = "Lịch thanh toán cho báo giá"

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá", help="Bảng tính giá", required=True)
    bsd_stt = fields.Integer(string='Số thứ tự', help="Số thứ tự đợt thanh toán")
    bsd_ngay_tt = fields.Datetime(string="Ngày thanh toán")
