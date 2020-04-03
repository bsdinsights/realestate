# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import datetime, calendar
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
                                  related="bsd_giu_cho_id.bsd_tien_gc", store=True)
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
                                         compute='_compute_gia_truoc_thue', store=True)
    bsd_tien_qsdd = fields.Monetary(string="Giá trị QSDĐ",
                                    help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""",
                                    related="bsd_unit_id.bsd_tien_qsdd", store=True)
    bsd_tien_thue = fields.Monetary(string="Tiền thuế",
                                    help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""",
                                    compute='_compute_tien_thue', store=True)
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán",
                                   related="bsd_unit_id.bsd_tien_pbt", store=True)
    bsd_tong_gia = fields.Monetary(string="Tổng giá bán",
                                   help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                   compute="_compute_tong_gia", store=True)
    bsd_thang_pql = fields.Integer(string="Số tháng đóng phí quản lý",
                                   help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức")
    bsd_tien_pql = fields.Monetary(string="Phí quản lý/ tháng", help="Số tiền phí quản lý cần đóng mỗi tháng")

    state = fields.Selection([('nhap', 'Nháp')], string="Trạng thái", default="nhap", help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_dk_bg_ids = fields.One2many('bsd.ban_giao', 'bsd_bao_gia_id', string="Bàn giao")
    bsd_ltt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_bao_gia_id', string="Lịch thanh toán")

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

    @api.depends('bsd_gia_truoc_thue', 'bsd_tien_thue', 'bsd_tien_pbt')
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

    def _cb_du_lieu_dtt(self, stt, ma_dtt, dot_tt, lai_phat, ngay_hh_tt, cs_tt):
        res = {}
        if ngay_hh_tt:
            ngay_ah_cd = ngay_hh_tt + datetime.timedelta(days=lai_phat.bsd_an_han)
        else:
            ngay_ah_cd = False
        res.update({
            'bsd_stt': stt,
            'bsd_ma_dtt': ma_dtt,
            'bsd_ten_dtt': dot_tt.bsd_dot_tt,
            'bsd_ngay_hh_tt': ngay_hh_tt,
            'bsd_tien_dot_tt': dot_tt.bsd_tl_tt * (self.bsd_tong_gia - self.bsd_tien_pbt) / 100,
            'bsd_tinh_pql': dot_tt.bsd_tinh_pql,
            'bsd_tinh_pbt': dot_tt.bsd_tinh_pbt,
            'bsd_ngay_ah': ngay_ah_cd,
            'bsd_tinh_phat': lai_phat.bsd_tinh_phat,
            'bsd_lai_phat': lai_phat.bsd_lai_phat,
            'bsd_tien_td': lai_phat.bsd_tien_td,
            'bsd_tl_td': lai_phat.bsd_tl_td,
            'bsd_phat_thd': cs_tt.bsd_phat_thd,
            'bsd_phat_shd': cs_tt.bsd_phat_shd,
            'bsd_cs_tt_id': cs_tt.id,
            'bsd_cs_tt_ct_id': dot_tt.id,
            'bsd_bao_gia_id': self.id,
        })
        return res

    def action_lich_tt(self):
        _logger.debug("Tao tu dong lich thanh toan")

        # hàm cộng tháng
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year, month, day)

        # tạo biến cục bộ
        stt = 0  # Đánh số thứ tự record đợt thanh toán
        cs_tt = self.bsd_cs_tt_id
        dot_tt_ids = cs_tt.bsd_ct_ids
        lai_phat = cs_tt.bsd_lai_phat_tt_id

        dot_cd = dot_tt_ids.filtered(lambda x: x.bsd_cach_tinh == 'cd' and not x.bsd_dot_cuoi)

        if len(dot_cd) > 1:
            raise UserError("Kiểm tra lại dữ liệu chính sách thanh toán")
        if dot_cd:
            stt += 1
            ngay_hh_tt_cd = dot_cd.bsd_ngay_cd
            self.bsd_ltt_ids.create(self._cb_du_lieu_dtt(stt, 'CD', dot_cd, lai_phat, ngay_hh_tt_cd, cs_tt))
        # Tạo dữ liệu đợt tự động
        dot_td = dot_tt_ids.filtered(lambda x: x.bsd_cach_tinh == 'td' and not x.bsd_dot_cuoi)
        ngay_hh_tt_td = ngay_hh_tt_cd
        if len(dot_td) > 1:
            raise UserError("Kiểm tra lại dữ liệu chính sách thanh toán")
        if dot_td:
            list_ngay_hh_tt = []
            if dot_td.bsd_lap_lai:
                for dot in range(0, dot_td.bsd_so_dot):
                    if dot_td.bsd_tiep_theo == 'ngay':
                        ngay_hh_tt_td += datetime.timedelta(days=dot_td.bsd_so_ngay)
                    else:
                        ngay_hh_tt_td = add_months(ngay_hh_tt_td, dot_td.bsd_so_thang)
                    list_ngay_hh_tt.append(ngay_hh_tt_td)
            else:
                if dot_td.bsd_tiep_theo == 'ngay':
                    ngay_hh_tt_td += datetime.timedelta(days=dot_td.bsd_so_ngay)
                else:
                    ngay_hh_tt_td = add_months(ngay_hh_tt_td, dot_td.bsd_so_thang)
                list_ngay_hh_tt.append(ngay_hh_tt_td)
            for ngay_hh_tt in list_ngay_hh_tt:
                stt += 1
                self.bsd_ltt_ids.create(self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay_hh_tt, cs_tt))

        # Tạo đợt thanh toán theo dự kiến bàn giao
        dot_dkbg = dot_tt_ids.filtered(lambda x: x.bsd_cach_tinh == 'dkbg' and not x.bsd_dot_cuoi)
        if len(dot_dkbg) > 1:
            raise UserError("Kiểm tra lại dữ liệu chính sách thanh toán")
        if dot_dkbg:
            ngay_hh_tt_dkbg = self.bsd_unit_id.bsd_ngay_dkbg or self.bsd_unit_id.bsd_du_an_id.bsd_ngay_dkbg or False
            stt += 1
            self.bsd_ltt_ids.create(self._cb_du_lieu_dtt(stt, 'DKBG', dot_dkbg, lai_phat,ngay_hh_tt_dkbg, cs_tt))

        # Tạo đợt bàn giao cuối
        dot_cuoi = dot_tt_ids.filtered(lambda x: x.bsd_dot_cuoi)
        if len(dot_cuoi) > 1:
            raise UserError("Kiểm tra lại dữ liệu chính sách thanh toán")
        if dot_cuoi:
            stt += 1
            self.bsd_ltt_ids.create(self._cb_du_lieu_dtt(stt, 'DBGC', dot_cuoi, lai_phat, False, cs_tt))

    def action_huy(self):
        pass

    def action_ky_bg(self):
        pass

    def action_ky_gc(self):
        pass



