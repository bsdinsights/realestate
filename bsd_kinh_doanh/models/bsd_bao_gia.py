# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import datetime
import calendar
import logging

_logger = logging.getLogger(__name__)


class BsdBaoGia(models.Model):
    _name = 'bsd.bao_gia'
    _description = "Bảng tính giá sản phẩm"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_bao_gia'

    bsd_ma_bao_gia = fields.Char(string="Mã", help="Mã bảng tính giá", required=True, readonly=True, copy=False,
                                 default='/')
    _sql_constraints = [
        ('bsd_ma_bao_gia_unique', 'unique (bsd_ma_bao_gia)',
         'Mã bảng giá đã tồn tại !'),
    ]
    bsd_ten_bao_gia = fields.Char(string="Tiêu đề", help="Tên bảng tính giá", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_ngay_bao_gia = fields.Date(string="Ngày", help="Ngày bảng tính giá", required=True,
                                   default=lambda self: fields.Date.today(),
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Tên giữ chỗ",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_giu_cho_id')
    def _onchange_giu_cho(self):
        if self.bsd_giu_cho_id:
            self.bsd_tien_gc = self.bsd_giu_cho_id.bsd_tien_gc

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Tên đợt mở bán")
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá", help="Bảng giá bán",
                                      related="bsd_dot_mb_id.bsd_bang_gia_id", store=True)
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ")
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc")

    def _get_nhan_vien(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)])

    bsd_nvbh_id = fields.Many2one('hr.employee', string="Nhân viên KD", help="Nhân viên kinh doanh",
                                  readonly=True, required=True, default=_get_nhan_vien,
                                  states={'nhap': [('readonly', False)]})
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch", domain=[('is_company', '=', True)],
                                    readonly=True, help="Sàn giao dịch",
                                    states={'nhap': [('readonly', False)]})
    bsd_ctv_id = fields.Many2one('res.partner', string="Công tác viên", domain=[('is_company', '=', False)],
                                 readonly=True, help="Cộng tác viên",
                                 states={'nhap': [('readonly', False)]})
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu", help="Cá nhân hoặc đơn vị giới thiệu",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})

    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Tên Sản phẩm", required=True)
    bsd_ten_sp = fields.Char(related="bsd_unit_id.name", store=True)
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng", help="Diện tích tim tường",
                             related="bsd_unit_id.bsd_dt_xd", store=True)
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế",
                             required=True,
                             readonly=True)

    def _get_thue(self):
        return self.env['bsd.thue_suat'].search([('bsd_ma_ts', '=', 'VAT10')], limit=1)

    bsd_thue_id = fields.Many2one('bsd.thue_suat', string="Thuế", help="Thuế", required=True,
                                  readonly=True, default=_get_thue,
                                  states={'nhap': [('readonly', False)]})
    bsd_qsdd_m2 = fields.Monetary(string="Giá trị QSDĐ/ m2", help="Giá trị quyền sử dụng đất trên m2")
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", required=True, readonly=True,
                                 digits=(12, 2))

    @api.onchange('bsd_thue_id')
    def _onchange_thue(self):
        self.bsd_thue_suat = self.bsd_thue_id.bsd_thue_suat

    bsd_tl_pbt = fields.Float(string="Tỷ lệ phí bảo trì", help="Tỷ lệ phí bảo trì")
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="Phương thức TT", help="Phương thức thanh toán", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán")
    bsd_tien_ck = fields.Monetary(string="Chiết khấu", help="Tổng tiền chiết khấu", compute="_compute_tien_ck", store=True)
    bsd_tien_bg = fields.Monetary(string="Giá trị ĐKBG", help="Tổng tiền bàn giao",
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
                                   compute="_compute_tien_pbt", store=True)
    bsd_tong_gia = fields.Monetary(string="Tổng giá bán",
                                   help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                   compute="_compute_tong_gia", store=True)
    bsd_thang_pql = fields.Integer(string="Số tháng đóng phí quản lý",
                                   help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_tien_pql = fields.Monetary(string="Phí quản lý", help="Số tiền phí quản lý",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_ky', 'Đã ký'),
                              ('hoan_thanh', 'Hoàn thành'),
                              ('huy', 'Hủy')], string="Trạng thái", default="nhap", help="Trạng thái", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_bg_ids = fields.One2many('bsd.ban_giao', 'bsd_bao_gia_id', string="Điều kiện bàn giao",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})

    # Tên hiện thị record
    def name_get(self):
        res = []
        for btg in self:
            res.append((btg.id, "{0} - {1}".format(btg.bsd_ma_bao_gia, btg.bsd_ten_sp)))
        return res

    @api.constrains('bsd_bg_ids')
    def _constrains_dk_bg(self):
        for each in self:
            record = each.bsd_bg_ids
            dk_bg = each.bsd_bg_ids.mapped('bsd_dk_bg_id')
            if len(record) > len(dk_bg):
                raise UserError("Có Điều kiện bàn giao bị trùng.\nVui lòng kiểm tra lại thông tin điều kiện bàn giao.")

    bsd_ltt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_bao_gia_id', string="Lịch thanh toán",
                                  readonly=True, domain=[('bsd_loai', 'in', ['dtt'])])

    bsd_dot_pbt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_bao_gia_id', string="Đợt thu phí bảo trì",
                                      readonly=True, domain=[('bsd_loai', '=', 'pbt')])
    bsd_dot_pql_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_bao_gia_id', string="Đợt thu phí quản lý",
                                      readonly=True, domain=[('bsd_loai', '=', 'pql')])

    bsd_ps_ck_ids = fields.One2many('bsd.ps_ck', 'bsd_bao_gia_id', string="Chiết khấu",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})

    @api.constrains('bsd_ps_ck_ids')
    def _constrains_ck(self):
        for each in self:
            record = each.bsd_ps_ck_ids
            ck = each.bsd_ps_ck_ids.mapped('bsd_chiet_khau_id')
            if len(record) > len(ck):
                raise UserError("Có Chiết khâu bị trùng.\nVui lòng kiểm tra lại thông tin chiết khấu.")

    bsd_ngay_in_bg = fields.Date(string="Ngày in BTG", help="Ngày in báo giá", readonly=True)
    bsd_ngay_hh_kbg = fields.Date(string="Hết hạn ký BTG", help="Ngày hết hiệu lực ký báo giá", readonly=True)
    bsd_ngay_ky_bg = fields.Date(string="Ngày ký BTG", help="Ngày ký báo giá", readonly=True)

    bsd_ngay_hl_bg = fields.Date(string="Hiệu lực BTG", help="Hiệu lực bảng tính giá",
                                     compute="_compute_ngay_hl", store=True)

    bsd_dong_sh_ids = fields.One2many('bsd.dong_so_huu', 'bsd_bao_gia_id', string="Đồng sở hữu",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_so_dat_coc = fields.Integer(string="# Đặt cọc", compute='_compute_dat_coc')

    bsd_km_ids = fields.One2many('bsd.bao_gia_km', 'bsd_bao_gia_id', string="Khuyến mãi",
                                 help="Danh sách khuyến mãi",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})

    @api.constrains('bsd_km_ids')
    def _constrains_km(self):
        for each in self:
            record = each.bsd_km_ids
            km = each.bsd_km_ids.mapped('bsd_khuyen_mai_id')
            if len(record) > len(km):
                raise UserError("Có Khuyến mãi bị trùng.\nVui lòng kiểm tra lại thông tin khuyến mãi.")
    bsd_ck_db_ids = fields.One2many('bsd.ck_db', 'bsd_bao_gia_id', string="Chiết khấu đặc biệt",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_da_co_lich = fields.Boolean(default=False)

    # 3 field ctv , sàn gd, giới thiệu không tồn tại đồng thời
    # Khách hàng không được trùng với mô giới
    @api.constrains('bsd_ctv_id', 'bsd_san_gd_id', 'bsd_gioi_thieu_id', 'bsd_khach_hang_id')
    def _constrains_mo_gioi(self):
        if (self.bsd_ctv_id and self.bsd_san_gd_id) \
            or (self.bsd_ctv_id and self.bsd_gioi_thieu_id) \
               or (self.bsd_san_gd_id and self.bsd_gioi_thieu_id):
            raise UserError("Vui lòng chọn 1 trong 3 giá trị: Sàn giao dịch, Công tác viên, Khách hàng giới thiệu.")
        if self.bsd_khach_hang_id == self.bsd_ctv_id \
            or self.bsd_khach_hang_id == self.bsd_san_gd_id \
                or self.bsd_khach_hang_id == self.bsd_gioi_thieu_id:
            raise UserError("Thông tin môi giới không được trùng với khách hàng.\nVui lòng kiểm tra lại thông tin.")

    @api.onchange('bsd_nvbh_id')
    def _onchange_san_ctv(self):
        res = {}
        self.env.cr.execute("""SELECT bsd_cn_id FROM bsd_loai_cn_rel 
                                WHERE bsd_loai_id = {0}
                            """.format(self.env.ref('bsd_kinh_doanh.bsd_ctv').id))
        list_cn = [cn[0] for cn in self.env.cr.fetchall()]
        self.env.cr.execute("""SELECT bsd_dn_id FROM bsd_loai_dn_rel 
                                WHERE bsd_loai_id = {0}
                            """.format(self.env.ref('bsd_kinh_doanh.bsd_san').id))
        list_dn = [cn[0] for cn in self.env.cr.fetchall()]
        res.update({
            'domain': {
                'bsd_ctv_id': [('id', 'in', list_cn)],
                'bsd_san_gd_id': [('id', 'in', list_dn)]
            }
        })
        return res

    # Kiểm tra sản phẩm đã được ký bảng tính giá hay chưa
    @api.constrains('bsd_unit_id')
    def _constraint_state_unit(self):
        if self.bsd_unit_id.state not in ['chuan_bi', 'san_sang', 'dat_cho', 'giu_cho']:
            raise UserError(_("Sản phẩm đã có giao dịch.\nVui lòng kiểm tra lại thông tin sản phẩm."))

    # R.33 Hiệu lực báo giá
    @api.depends('bsd_ngay_bao_gia')
    def _compute_ngay_hl(self):
        for each in self:
            so_ngay = datetime.timedelta(days=each.bsd_du_an_id.bsd_hh_bg)
            each.bsd_ngay_hl_bg = each.bsd_ngay_bao_gia + so_ngay

    @api.depends('bsd_gia_ban', 'bsd_tl_pbt')
    def _compute_tien_pbt(self):
        for each in self:
            each.bsd_tien_pbt = each.bsd_gia_ban * each.bsd_tl_pbt / 100

    @api.onchange('bsd_unit_id', 'bsd_bang_gia_id')
    def _onchange_gia_ban(self):
        for each in self:
            item = each.bsd_bang_gia_id.item_ids.filtered(
                lambda x: x.product_tmpl_id == each.bsd_unit_id.product_tmpl_id)
            if item:
                each.bsd_gia_ban = item.fixed_price

    @api.constrains('bsd_gia_ban')
    def _constraint_gia_ban(self):
        for each in self:
            if each.bsd_gia_ban == 0:
                raise UserError(_("Vui lòng kiểm tra lại giá bán của sản phẩm."))

    @api.depends('bsd_bg_ids.bsd_tien_bg')
    def _compute_tien_bg(self):
        for each in self:
            each.bsd_tien_bg = sum(each.bsd_bg_ids.mapped('bsd_tien_bg'))

    @api.depends('bsd_ps_ck_ids.bsd_tien', 'bsd_ps_ck_ids.bsd_tl_ck', 'bsd_ps_ck_ids.bsd_cach_tinh',
                 'bsd_ck_db_ids.bsd_tien', 'bsd_ck_db_ids.bsd_tl_ck', 'bsd_ck_db_ids.bsd_cach_tinh',
                 'bsd_ck_db_ids.state',
                 'bsd_gia_ban')
    def _compute_tien_ck(self):
        for each in self:
            _logger.debug("tính tiền chiết khấu")
            tien_ps_ck = 0
            for ck in each.bsd_ps_ck_ids:
                if ck.bsd_cach_tinh == 'phan_tram':
                    tien_ps_ck += ck.bsd_tl_ck * \
                                       (each.bsd_gia_ban + each.bsd_tien_bg) / 100
                else:
                    tien_ps_ck += each.bsd_tien
            for ck_db in each.bsd_ck_db_ids.filtered(lambda t: t.state == 'duyet'):
                if ck_db.bsd_cach_tinh == 'phan_tram':
                    tien_ps_ck += ck_db.bsd_tl_ck * (each.bsd_gia_ban + each.bsd_tien_bg) / 100
                else:
                    tien_ps_ck += ck_db.bsd_tien
            each.bsd_tien_ck = tien_ps_ck

    @api.depends('bsd_gia_ban', 'bsd_tien_ck', 'bsd_tien_bg')
    def _compute_gia_truoc_thue(self):
        for each in self:
            each.bsd_gia_truoc_thue = each.bsd_gia_ban - each.bsd_tien_ck + each.bsd_tien_bg

    @api.depends('bsd_thue_suat', 'bsd_gia_truoc_thue', 'bsd_tien_qsdd')
    def _compute_tien_thue(self):
        for each in self:
            each.bsd_tien_thue = (each.bsd_gia_truoc_thue - each.bsd_tien_qsdd) * each.bsd_thue_suat / 100

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_ten_bao_gia = 'Bảng tính giá sản phẩm ' + self.bsd_unit_id.name
        self.bsd_dot_mb_id = self.bsd_unit_id.bsd_dot_mb_id
        self.bsd_tien_dc = self.bsd_unit_id.bsd_tien_dc
        self.bsd_du_an_id = self.bsd_unit_id.bsd_du_an_id
        self.bsd_thang_pql = self.bsd_unit_id.bsd_thang_pql
        self.bsd_tien_pql = self.bsd_unit_id.bsd_tien_pql
        self.bsd_dt_sd = self.bsd_unit_id.bsd_dt_sd
        self.bsd_qsdd_m2 = self.bsd_unit_id.bsd_qsdd_m2
        self.bsd_tl_pbt = self.bsd_unit_id.bsd_tl_pbt

    @api.depends('bsd_gia_truoc_thue', 'bsd_tien_thue', 'bsd_tien_pbt')
    def _compute_tong_gia(self):
        for each in self:
            each.bsd_tong_gia = each.bsd_gia_truoc_thue + each.bsd_tien_thue + each.bsd_tien_pbt

    # KD.09.03 Xác nhận báo giá
    def action_xac_nhan(self):
        if not self.bsd_ltt_ids:
            raise UserError("Bảng tính giá chưa có lịch thanh toán.\nVui lòng kiểm tra lại thông tin.")
        if not self.bsd_bg_ids:
            raise UserError("Bảng tính giá phải chọn tối thiểu 1 điều kiện bàn giao.\nVui lòng kiểm tra lại thông tin.")

        self.write({
            'state': 'xac_nhan',
        })

    # KD.09.05 In báo giá
    def action_in_bg(self):
        return self.env.ref('bsd_kinh_doanh.bsd_bao_gia_report_action').read()[0]

    def _cb_du_lieu_dtt(self, stt, ma_dtt, dot_tt, lai_phat, ngay_hh_tt, cs_tt, tien_dot_tt, tinh_pql, tinh_pbt):
        res = {}
        if ngay_hh_tt:
            ngay_ah_cd = ngay_hh_tt + datetime.timedelta(days=lai_phat.bsd_an_han)
        else:
            ngay_ah_cd = False
        res.update({
            'bsd_stt': stt,
            'bsd_ma_dtt': ma_dtt,
            'bsd_ten_dtt': 'Đợt ' + str(stt),
            'bsd_ngay_hh_tt': ngay_hh_tt,
            'bsd_tien_dot_tt': tien_dot_tt,
            'bsd_tinh_pql': tinh_pql,
            'bsd_tinh_pbt': tinh_pbt,
            'bsd_ngay_ah': ngay_ah_cd,
            'bsd_tinh_phat': lai_phat.bsd_tinh_phat,
            'bsd_lai_phat': lai_phat.bsd_lai_phat,
            'bsd_tien_td': lai_phat.bsd_tien_td,
            'bsd_tl_td': lai_phat.bsd_tl_td,
            'bsd_cs_tt_id': cs_tt.id,
            'bsd_cs_tt_ct_id': dot_tt.id,
            'bsd_bao_gia_id': self.id,
            'bsd_dot_ky_hd': dot_tt.bsd_dot_ky_hd,
            'bsd_tien_dc': 0,
            'bsd_loai': 'dtt'
        })
        return res

    # Tạo lịch thanh toán
    def action_lich_tt(self):
        # Xóa lịch thanh toán hiện tại
        self.bsd_ltt_ids.unlink()
        self.bsd_dot_pbt_ids.unlink()
        self.bsd_dot_pql_ids.unlink()
        self.write({
            'bsd_da_co_lich': True
        })

        # hàm cộng tháng
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year, month, day)

        # tạo biến cục bộ
        stt = 0  # Đánh số thứ tự record đợt thanh toán
        ngay_hh_tt = datetime.datetime.now()  # Ngày giá trị mặc đính tính ngày hết hạn thanh toán
        cs_tt = self.bsd_cs_tt_id
        dot_tt_ids = cs_tt.bsd_ct_ids
        lai_phat = cs_tt.bsd_lai_phat_tt_id
        # dùng để tính tiền đợt thanh toán cuối
        tong_tien_dot_tt = 0
        # Kiểm tra chính sách thanh toán chi tiết
        if len(dot_tt_ids.filtered(lambda x: x.bsd_cach_tinh == 'dkbg')) > 1:
            raise UserError(_("Chính sách thanh toán chi tiết có nhiều hơn 1 đợt dự kiến bàn giao."))
        if len(dot_tt_ids.filtered(lambda x: x.bsd_dot_cuoi)) > 1:
            raise UserError(_("Chính sách thanh toán chi tiết có nhiều hơn 1 đợt dự thanh toán cuối."))
        # Tạo các đợt thanh toán
        for dot in dot_tt_ids.sorted('bsd_stt'):
            # Tạo dữ liệu đợt cố định
            if dot.bsd_cach_tinh == 'cd' and not dot.bsd_dot_cuoi:
                dot_cd = dot
                stt += 1
                # cập nhật lại ngày hết hạn thanh toán
                ngay_hh_tt = dot_cd.bsd_ngay_cd
                # tính tiền đợt thanh toán
                tien_dot_tt = dot_cd.bsd_tl_tt * (self.bsd_tong_gia - self.bsd_tien_pbt) / 100
                # làm trong tiền đợt thanh toán
                tien_dot_tt = tien_dot_tt - (tien_dot_tt % 1000)
                # cộng tiền đợt thanh toán
                tong_tien_dot_tt += tien_dot_tt
                self.bsd_ltt_ids.\
                    create(self._cb_du_lieu_dtt(stt, 'CD', dot_cd, lai_phat, ngay_hh_tt, cs_tt,
                                                tien_dot_tt, dot_cd.bsd_tinh_pql, dot_cd.bsd_tinh_pbt))
            # Tạo dữ liệu đợt tự động
            elif dot.bsd_cach_tinh == 'td':
                dot_td = dot
                ngay_hh_tt_td = ngay_hh_tt
                list_ngay_hh_tt_td = []
                if dot_td.bsd_lap_lai == '1':
                    for dot_i in range(0, dot_td.bsd_so_dot):
                        if dot_td.bsd_tiep_theo == 'ngay':
                            ngay_hh_tt_td += datetime.timedelta(days=dot_td.bsd_so_ngay)
                        else:
                            ngay_hh_tt_td = add_months(ngay_hh_tt_td, dot_td.bsd_so_thang)
                        list_ngay_hh_tt_td.append(ngay_hh_tt_td)
                else:
                    if dot_td.bsd_tiep_theo == 'ngay':
                        ngay_hh_tt_td += datetime.timedelta(days=dot_td.bsd_so_ngay)
                    else:
                        ngay_hh_tt_td = add_months(ngay_hh_tt_td, dot_td.bsd_so_thang)
                    list_ngay_hh_tt_td.append(ngay_hh_tt_td)
                # cộng thời gian gia hạn cuối của đợt tự động
                list_ngay_hh_tt_td[-1] += datetime.timedelta(days=dot_td.bsd_ngay_gh)
                # Gán lại ngày cuối cùng tự động thanh toán
                ngay_hh_tt = list_ngay_hh_tt_td[-1]
                # Kiểm tra nếu đợt tự động có tích chọn thu phí quản lý hoặc phí bảo trì
                # thì gắn vào đợt tự động đầu tiên
                da_tao_pql = False
                da_tao_pbt = False
                for ngay in list_ngay_hh_tt_td:
                    stt += 1
                    if dot_td.bsd_ngay_thang > 0:
                        last_day = calendar.monthrange(ngay.year, ngay.month)[1]

                        if dot_td.bsd_ngay_thang > last_day:
                            ngay = ngay.replace(day=last_day)
                        else:
                            ngay = ngay.replace(day=dot_td.bsd_ngay_thang)
                    tien_dot_tt = dot_td.bsd_tl_tt * (self.bsd_tong_gia - self.bsd_tien_pbt) / 100
                    # làm trong tiền đợt thanh toán
                    tien_dot_tt = tien_dot_tt - (tien_dot_tt % 1000)
                    # cộng tiền đợt thanh toán
                    tong_tien_dot_tt += tien_dot_tt
                    if dot_td.bsd_tinh_pql and not dot_td.bsd_tinh_pbt and not da_tao_pql:
                        self.bsd_ltt_ids.create(
                            self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay, cs_tt, tien_dot_tt, True, False))
                        da_tao_pql = True
                    elif not dot_td.bsd_tinh_pql and dot_td.bsd_tinh_pbt and not da_tao_pbt:
                        self.bsd_ltt_ids.create(
                            self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay, cs_tt, tien_dot_tt, False, True))
                        da_tao_pbt = True
                    elif dot_td.bsd_tinh_pql and dot_td.bsd_tinh_pbt and not da_tao_pbt and not da_tao_pql:
                        self.bsd_ltt_ids.create(
                            self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay, cs_tt, tien_dot_tt, True, True))
                        da_tao_pql = True
                        da_tao_pbt = True
                    else:
                        self.bsd_ltt_ids.create(
                            self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay, cs_tt, tien_dot_tt, False, False))

            # Tạo đợt thanh toán theo dự kiến bàn giao
            elif dot.bsd_cach_tinh == 'dkbg':
                dot_dkbg = dot
                ngay_hh_tt_dkbg = self.bsd_unit_id.bsd_ngay_dkbg or self.bsd_unit_id.bsd_du_an_id.bsd_ngay_dkbg or False
                stt += 1
                # cập nhật lại ngày hết hạn thanh toán
                ngay_hh_tt = ngay_hh_tt_dkbg
                tien_dot_tt = dot_dkbg.bsd_tl_tt * (self.bsd_tong_gia - self.bsd_tien_pbt) / 100
                # làm trong tiền đợt thanh toán
                tien_dot_tt = tien_dot_tt - (tien_dot_tt % 1000)
                # cộng tiền đợt thanh toán
                tong_tien_dot_tt += tien_dot_tt
                self.bsd_ltt_ids.\
                    create(self._cb_du_lieu_dtt(stt, 'DKBG', dot_dkbg, lai_phat, ngay_hh_tt_dkbg, cs_tt,
                                                tien_dot_tt, dot_dkbg.bsd_tinh_pql, dot_dkbg.bsd_tinh_pbt))

            # Tạo đợt thanh toán cuối
            elif dot.bsd_dot_cuoi:
                dot_cuoi = dot
                stt += 1
                tien_dot_tt = (self.bsd_tong_gia - self.bsd_tien_pbt) - tong_tien_dot_tt
                self.bsd_ltt_ids.\
                    create(self._cb_du_lieu_dtt(stt, 'DBGC', dot_cuoi, lai_phat, False, cs_tt,
                                                tien_dot_tt, dot_cuoi.bsd_tinh_pql, dot_cuoi.bsd_tinh_pbt))

        # Tạo đợt thu phí quản lý
        dot_pql = self.bsd_ltt_ids.filtered(lambda d: d.bsd_tinh_pql)
        if dot_pql:
            dot_pql = dot_pql[0]
            self.bsd_ltt_ids.create({
                'bsd_stt': dot_pql.bsd_stt,
                'bsd_ma_dtt': 'PQL',
                'bsd_ten_dtt': dot_pql.bsd_ten_dtt,
                'bsd_ngay_hh_tt': dot_pql.bsd_ngay_hh_tt,
                'bsd_tien_dot_tt': self.bsd_tien_pql,
                'bsd_cs_tt_id': dot_pql.bsd_cs_tt_id.id,
                'bsd_cs_tt_ct_id': dot_pql.bsd_cs_tt_ct_id.id,
                'bsd_bao_gia_id': self.id,
                'bsd_parent_id': dot_pql.id,
                'bsd_loai': 'pql'
            })
        # Tạo đợt thu phí bảo trì
        dot_pbt = self.bsd_ltt_ids.filtered(lambda d: d.bsd_tinh_pbt)
        if dot_pbt:
            dot_pbt = dot_pbt[0]
            self.bsd_ltt_ids.create({
                'bsd_stt': dot_pbt.bsd_stt,
                'bsd_ma_dtt': 'PBT',
                'bsd_ten_dtt': dot_pbt.bsd_ten_dtt,
                'bsd_ngay_hh_tt': dot_pbt.bsd_ngay_hh_tt,
                'bsd_tien_dot_tt': self.bsd_tien_pbt,
                'bsd_cs_tt_id': dot_pbt.bsd_cs_tt_id.id,
                'bsd_cs_tt_ct_id': dot_pbt.bsd_cs_tt_ct_id.id,
                'bsd_bao_gia_id': self.id,
                'bsd_parent_id': dot_pbt.id,
                'bsd_loai': 'pbt'
            })

    # Xóa lịch thanh toán
    def action_xoa_lich_tt(self):
        # Xóa lịch thanh toán hiện tại
        self.bsd_ltt_ids.unlink()
        self.bsd_dot_pbt_ids.unlink()
        self.bsd_dot_pql_ids.unlink()
        self.write({
            'bsd_da_co_lich': False
        })

    # KD.09.06 Ký báo giá
    def action_ky_bg(self):
        if self.bsd_giu_cho_id:
            giu_cho = self.env['bsd.giu_cho'].search([('state', '=', 'giu_cho'),
                                                      ('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                      ('bsd_stt_bg', '<', self.bsd_giu_cho_id.bsd_stt_bg)])
            if giu_cho:
                raise UserError("Có giữ chỗ ưu tiên ký bảng giá trước.\nVui lòng chờ đến lượt của bạn.")
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_ky_bg_action').read()[0]
        return action

    # KD.09.07 Hủy báo giá
    def action_huy(self):
        dat_coc = self.env['bsd.dat_coc'].search([('state', '!=', 'huy'), ('bsd_bao_gia_id', '=', self.id)])
        if dat_coc:
            raise UserError("Đã có phát sinh Phiếu cọc, bạn không thể hủy Báo giá.")
        else:
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
            raise UserError(_('Dự án chưa có mã bảng tính giá.'))
        vals['bsd_ma_bao_gia'] = sequence.next_by_id()
        return super(BsdBaoGia, self).create(vals)

    # KD.09.09 Tạo Bảng tính giá từ màn hình Giữ chỗ
    def action_tao_dat_coc(self):
        context = {
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_bao_gia_id': self.id,
        }
        action = self.env.ref('bsd_kinh_doanh.bsd_dat_coc_action_popup').read()[0]
        action['context'] = context
        return action

    def _compute_dat_coc(self):
        for each in self:
            dat_coc = self.env['bsd.dat_coc'].search([('bsd_bao_gia_id', '=', self.id)])
            each.bsd_so_dat_coc = len(dat_coc)

    def action_view_dat_coc(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_dat_coc_action').read()[0]

        dat_coc = self.env['bsd.dat_coc'].search([('bsd_bao_gia_id', '=', self.id)])
        if len(dat_coc) > 1:
            action['domain'] = [('id', 'in', dat_coc.ids)]
        elif dat_coc:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_dat_coc_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = dat_coc.id
        # Prepare the context.
        context = {
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_bao_gia_id': self.id,
        }
        action['context'] = context
        return action

    # Sử dụng trên popup
    def action_luu(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bảng tính giá',
            'res_model': 'bsd.bao_gia',
            'res_id': self.id,
            'target': 'current',
            'view_mode': 'form'
        }

    def action_chon_ck(self):
        if self.bsd_ltt_ids:
            raise UserError(_("Bảng tính giá đã có lịch thanh toán.\n"
                              "Vui lòng xóa lịch thanh toán trước khi chọn chiết khấu."))
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_chon_ck_action').read()[0]
        return action

    def action_chon_dkbg(self):
        if self.bsd_ltt_ids:
            raise UserError(_("Bảng tính giá đã có lịch thanh toán.\n"
                              "Vui lòng xóa lịch thanh toán trước khi chọn điều kiện bàn giao."))
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_chon_dkbg_action').read()[0]
        return action

    def action_ck_db(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_ck_db_action_popup').read()[0]
        action['context'] = {'default_bsd_bao_gia_id': self.id}
        return action


class BsdBaoGiaKhuyenMai(models.Model):
    _name = 'bsd.bao_gia_km'
    _description = "Thông tin chương trình khuyến mãi cho bảng tính giá"
    _rec_name = 'bsd_khuyen_mai_id'

    bsd_khuyen_mai_id = fields.Many2one('bsd.khuyen_mai', string="Khuyến mãi", required=True)
    bsd_ma_km = fields.Char(related='bsd_khuyen_mai_id.bsd_ma_km')
    bsd_tu_ngay = fields.Date(related='bsd_khuyen_mai_id.bsd_tu_ngay')
    bsd_den_ngay = fields.Date(related='bsd_khuyen_mai_id.bsd_den_ngay')
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá", required=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán")
    bsd_ngay_hldc = fields.Date(related='bsd_khuyen_mai_id.bsd_ngay_hldc')
    bsd_gia_tri = fields.Monetary(related='bsd_khuyen_mai_id.bsd_gia_tri')
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_dot_mb_id')
    def _onchange_dot_mb(self):
        res = {}
        list_id = []
        if self.bsd_dot_mb_id:
            # Lấy các điều kiện bàn giao trong đợt mở bán
            khuyen_mai = self.bsd_dot_mb_id.bsd_km_ids
            # Lọc các điều kiện bàn giao có nhóm sản phẩm trùng với unit trong bảng tính giá
            list_id = khuyen_mai.filtered(
                lambda d: d.state == 'duyet' and d.bsd_loai == 'khong').ids
        res.update({
            'domain': {
                'bsd_khuyen_mai_id': [('id', 'in', list_id)]
            }
        })
        return res
