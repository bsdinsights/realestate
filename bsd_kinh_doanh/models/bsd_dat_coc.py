# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import datetime
import calendar

_logger = logging.getLogger(__name__)


class BsdDatCoc(models.Model):
    _name = 'bsd.dat_coc'
    _description = "Phiếu đặt cọc"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_dat_coc'

    bsd_ma_dat_coc = fields.Char(string="Mã đặt cọc", help="Mã đặt cọc", required=True, readonly=True, copy=False,
                                 default='/')
    _sql_constraints = [
        ('bsd_ma_dat_coc_unique', 'unique (bsd_ma_dat_coc)',
         'Mã đặt cọc đã tồn tại !'),
    ]
    bsd_ngay_dat_coc = fields.Date(string="Ngày", help="Ngày đặt cọc", required=True,
                                   default=lambda self: fields.Date.today(),
                                   readonly=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True)
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá", help="Tên bảng tính giá", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    # Thông tin dữ liệu được load từ báo giá
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True)
    bsd_nvbh_id = fields.Many2one('hr.employee', string="Nhân viên KD", help="Nhân viên kinh doanh",
                                  readonly=True, required=True)
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch", domain=[('is_company', '=', True)],
                                    readonly=True, help="Sàn giao dịch")
    bsd_ctv_id = fields.Many2one('res.partner', string="Công tác viên", domain=[('is_company', '=', False)],
                                 help="Cộng tác viên",readonly=True)
    bsd_gioi_thieu_id = fields.Many2one('res.partner', string="Giới thiệu", help="Cá nhân hoặc đơn vị giới thiệu",
                                        readonly=True)
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Tên giữ chỗ", readonly=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True, readonly=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Tên đợt mở bán", readonly=True, required=True)
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá", help="Bảng giá bán",
                                      related="bsd_dot_mb_id.bsd_bang_gia_id", store=True)
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ", readonly=True)
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc", readonly=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Tên sản phẩm", readonly=1)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán", readonly=1)
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán", readonly=True)
    bsd_thang_pql = fields.Integer(string="Số tháng đóng phí quản lý",
                                   help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức",
                                   readonly=True)
    bsd_tien_pql = fields.Monetary(string="Phí quản lý", help="Số tiền phí quản lý",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_thue_id = fields.Many2one('bsd.thue_suat', string="Thuế", help="Thuế")

    @api.onchange('bsd_bao_gia_id')
    def _onchange_bao_gia(self):
        self.bsd_khach_hang_id = self.bsd_bao_gia_id.bsd_khach_hang_id
        self.bsd_nvbh_id = self.bsd_bao_gia_id.bsd_nvbh_id
        self.bsd_san_gd_id = self.bsd_bao_gia_id.bsd_san_gd_id
        self.bsd_ctv_id = self.bsd_bao_gia_id.bsd_ctv_id
        self.bsd_gioi_thieu_id = self.bsd_bao_gia_id.bsd_gioi_thieu_id
        self.bsd_giu_cho_id = self.bsd_bao_gia_id.bsd_giu_cho_id
        self.bsd_du_an_id = self.bsd_bao_gia_id.bsd_du_an_id
        self.bsd_dot_mb_id = self.bsd_bao_gia_id.bsd_dot_mb_id
        self.bsd_tien_gc = self.bsd_bao_gia_id.bsd_tien_gc
        self.bsd_unit_id = self.bsd_bao_gia_id.bsd_unit_id
        self.bsd_tien_dc = self.bsd_bao_gia_id.bsd_tien_dc
        self.bsd_cs_tt_id = self.bsd_bao_gia_id.bsd_cs_tt_id
        self.bsd_gia_ban = self.bsd_bao_gia_id.bsd_gia_ban
        self.bsd_thang_pql = self.bsd_bao_gia_id.bsd_thang_pql
        self.bsd_tien_pql = self.bsd_bao_gia_id.bsd_tien_pql
        self.bsd_thue_id = self.bsd_bao_gia_id.bsd_thue_id
        self.bsd_co_ttdc = self.bsd_bao_gia_id.bsd_du_an_id.bsd_hd_coc
        self.bsd_tien_ck = self.bsd_bao_gia_id.bsd_tien_ck

    # Hết thông tin load từ báo giá
    bsd_ten_sp = fields.Char(related="bsd_unit_id.name", store=True)
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng", help="Diện tích tim tường",
                             related="bsd_unit_id.bsd_dt_xd", store=True)
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế",
                             related="bsd_unit_id.bsd_dt_sd", store=True)

    bsd_qsdd_m2 = fields.Monetary(string="Giá trị QSDĐ/ m2", help="Giá trị quyền sử dụng đất trên m2",
                                  related="bsd_unit_id.bsd_qsdd_m2", store=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", related="bsd_thue_id.bsd_thue_suat", store=True,
                                 digits=(12, 2))
    bsd_tl_pbt = fields.Float(string="Tỷ lệ phí bảo trì", help="Tỷ lệ phí bảo trì",
                              related="bsd_unit_id.bsd_tl_pbt", store=True)
    bsd_tien_ck = fields.Monetary(string="Chiết khấu", help="Tổng tiền chiết khấu", store=True)

    bsd_tien_bg = fields.Monetary(string="Giá trị ĐKBG", help="Tổng tiền bàn giao",
                                  compute='_compute_tien_bg', store=True)

    @api.depends('bsd_bg_ids.bsd_tien_bg')
    def _compute_tien_bg(self):
        for each in self:
            each.bsd_tien_bg = sum(each.bsd_bg_ids.mapped('bsd_tien_bg'))

    bsd_gia_truoc_thue = fields.Monetary(string="Giá bán trước thuế",
                                         help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ chiết khấu""",
                                         compute='_compute_gia_truoc_thue', store=True)

    @api.depends('bsd_gia_ban', 'bsd_tien_ck', 'bsd_tien_bg')
    def _compute_gia_truoc_thue(self):
        for each in self:
            each.bsd_gia_truoc_thue = each.bsd_gia_ban - each.bsd_tien_ck + each.bsd_tien_bg

    bsd_tien_qsdd = fields.Monetary(string="Giá trị QSDĐ",
                                    help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""",
                                    related="bsd_unit_id.bsd_tien_qsdd", store=True)
    bsd_tien_thue = fields.Monetary(string="Tiền thuế",
                                    help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""",
                                    compute='_compute_tien_thue', store=True)

    @api.depends('bsd_thue_suat', 'bsd_gia_truoc_thue', 'bsd_tien_qsdd')
    def _compute_tien_thue(self):
        for each in self:
            each.bsd_tien_thue = (each.bsd_gia_truoc_thue - each.bsd_tien_qsdd) * each.bsd_thue_suat / 100
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán",
                                   compute="_compute_tien_pbt", store=True)

    @api.depends('bsd_gia_ban', 'bsd_tl_pbt')
    def _compute_tien_pbt(self):
        for each in self:
            each.bsd_tien_pbt = each.bsd_gia_ban * each.bsd_tl_pbt / 100

    bsd_tong_gia = fields.Monetary(string="Tổng giá bán",
                                   help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                   compute="_compute_tong_gia", store=True)

    @api.depends('bsd_gia_truoc_thue', 'bsd_tien_thue', 'bsd_tien_pbt')
    def _compute_tong_gia(self):
        for each in self:
            each.bsd_tong_gia = each.bsd_gia_truoc_thue + each.bsd_tien_thue + each.bsd_tien_pbt

    state = fields.Selection([('xac_nhan', 'Đặt cọc'),
                              ('da_tc', 'Đã thu cọc'),
                              ('dat_coc', 'Đã ký'),
                              ('hoan_thanh', 'Hoàn thành'),
                              ('het_han', 'Hết hạn'),
                              ('da_tl', 'Đã thanh lý'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="xac_nhan", help="Trạng thái", tracing=1, required=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_bg_ids = fields.One2many('bsd.ban_giao', 'bsd_dat_coc_id', string="Điều kiện bàn giao", readonly=True)
    bsd_ltt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_dat_coc_id', string="Lịch thanh toán",
                                  readonly=True, domain=[('bsd_loai', 'in', ['dtt'])])
    bsd_dot_pbt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_dat_coc_id', string="Đợt thu phí bảo trì",
                                      readonly=True, domain=[('bsd_loai', '=', 'pbt')])
    bsd_dot_pql_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_dat_coc_id', string="Đợt thu phí quản lý",
                                      readonly=True, domain=[('bsd_loai', '=', 'pql')])
    bsd_co_ttdc = fields.Boolean(string="Thỏa thuận đặt cọc", help="Thông tin quy định thỏa thuận đặt cọc hay không")

    bsd_ngay_in_dc = fields.Date(string="Ngày in", help="Ngày in phiếu cọc, hợp đồng cọc", readonly=True)
    bsd_ngay_hh_kdc = fields.Date(string="Hạn ký đặt cọc", help="Ngày hết hạn ký phiếu cọc",
                                      readonly=True)
    bsd_ngay_up_dc = fields.Date(string="Upload đặt cọc", readonly=True,
                                     help="""Ngày tải lên hệ thống phiếu đặt cọc đã được khách hàng 
                                             ký xác nhận""")
    bsd_ngay_ky_dc = fields.Date(string="Ngày ký đặt cọc", help="Ngày ký đặt cọc", readonly=True)

    bsd_thanh_toan = fields.Selection([('chua_tt', 'Chưa thanh toán'),
                                       ('dang_tt', 'Đang thanh toán'),
                                       ('da_tt', 'Đã thanh toán')], string="Tình trạng TT", default="chua_tt",
                                      help="Thanh toán", readonly=True,
                                      required=True)
    bsd_ngay_tt = fields.Datetime(string="Ngày TT cọc", help="Ngày (kế toán xác nhận) thanh toán giữ chỗ", readonly=True)

    bsd_tien_ttd = fields.Monetary(string="Đã thanh toán/ đợt", help="Tiền đã thanh toán theo đợt thanh toán",)
    bsd_km_ids = fields.One2many('bsd.bao_gia_km', 'bsd_dat_coc_id', string="Khuyến mãi",
                                 help="Khuyến mãi")
    bsd_ps_ck_ids = fields.One2many('bsd.ps_ck', 'bsd_dat_coc_id', string="Chiết khấu", readonly=True)
    bsd_ck_db_ids = fields.One2many('bsd.ck_db', 'bsd_dat_coc_id', string="Chiết khấu đặt biệt",
                                    readonly=True,
                                    states={'xac_nhan': [('readonly', False)],
                                            'da_tc': [('readonly', False)]})
    bsd_dong_sh_ids = fields.One2many('bsd.dong_so_huu', 'bsd_dat_coc_id', string="Đồng sở hữu", readonly=True)
    bsd_nguoi_dd_id = fields.Many2one('res.partner', string="Người ký TTĐC/HĐ",required=True, tracking=2,
                                      help="Người đại diện ký thỏa thuận đặt cọc và hợp đồng mua bán", readonly=True)
    bsd_so_chuyen_dd = fields.Integer(string="# Phiếu thay đổi thông tin", compute="_compute_chuyen_dd")

    def _compute_chuyen_dd(self):
        for each in self:
            chuyen_dd = self.env['bsd.dat_coc.chuyen_dd'].search([('bsd_dat_coc_id', '=', self.id)])
            each.bsd_so_chuyen_dd = len(chuyen_dd)

    def action_view_chuyen_dd(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_dat_coc_chuyen_dd_action').read()[0]

        chuyen_dd = self.env['bsd.dat_coc.chuyen_dd'].search([('bsd_dat_coc_id', '=', self.id)])
        if len(chuyen_dd) > 1:
            action['domain'] = [('id', 'in', chuyen_dd.ids)]
        elif chuyen_dd:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_dat_coc_chuyen_dd_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = chuyen_dd.id
        # Prepare the context.
        context = {
            'default_bsd_tieu_de': 'Phiếu thay đổi đại diện đặt cọc ' + self.bsd_ma_dat_coc,
            'default_bsd_dat_coc_id': self.id
        }
        action['context'] = context
        return action

    @api.onchange('bsd_khach_hang_id')
    def _onchange_kh(self):
        self.bsd_nguoi_dd_id = self.bsd_khach_hang_id

    @api.constrains('bsd_tien_dc')
    def _check_bsd_tien_dc(self):
        for record in self:
            if record.bsd_tien_dc < 0:
                raise ValidationError("Tiền đặt cọc phải lớn hơn 0.")

    # Tên hiện thị record
    def name_get(self):
        res = []
        for dc in self:
            res.append((dc.id, "{0} - {1}".format(dc.bsd_ma_dat_coc, dc.bsd_ten_sp)))
        return res

    @api.model
    def create(self, vals):
        # KD.10.07 kiểm tra báo giá đã có đặt cọc chưa:
        if 'bsd_bao_gia_id' in vals.keys():
            id_bao_gia = vals['bsd_bao_gia_id']
            dat_coc = self.env['bsd.dat_coc'].search([('bsd_bao_gia_id', '=', id_bao_gia)])
            _logger.debug(dat_coc)
            if dat_coc:
                raise UserError("Bảng tính giá đã được tạo Đặt cọc.\nVui lòng kiểm tra lại thông tin!")
        sequence = False
        if 'bsd_bao_gia_id' in vals:
            bao_gia = self.env['bsd.bao_gia'].browse(vals['bsd_bao_gia_id'])
            sequence = bao_gia.bsd_du_an_id.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu đặt cọc.'))
        vals['bsd_ma_dat_coc'] = sequence.next_by_id()
        res = super(BsdDatCoc, self).create(vals)
        ids_bg = res.bsd_bao_gia_id.bsd_bg_ids.ids
        ids_ltt = res.bsd_bao_gia_id.bsd_ltt_ids.ids
        ids_km = res.bsd_bao_gia_id.bsd_km_ids.ids
        ids_ck = res.bsd_bao_gia_id.bsd_ps_ck_ids.ids
        ids_db = res.bsd_bao_gia_id.bsd_ck_db_ids.ids
        ids_dsh = res.bsd_bao_gia_id.bsd_dong_sh_ids.ids
        ids_pbt = res.bsd_bao_gia_id.bsd_dot_pbt_ids.ids
        ids_pql = res.bsd_bao_gia_id.bsd_dot_pql_ids.ids
        res.write({
            'bsd_bg_ids': [(6, 0, ids_bg)],
            'bsd_ltt_ids': [(6, 0, ids_ltt)],
            'bsd_km_ids': [(6, 0, ids_km)],
            'bsd_ps_ck_ids': [(6, 0, ids_ck)],
            'bsd_ck_db_ids': [(6, 0, ids_db)],
            'bsd_dong_sh_ids': [(6, 0, ids_dsh)],
            'bsd_dot_pbt_ids': [(6, 0, ids_pbt)],
            'bsd_dot_pql_ids': [(6, 0, ids_pql)],
        })
        return res

    # KD.10.06 Theo dõi công nợ đặt cọc
    def _tao_rec_cong_no(self):
        self.env['bsd.cong_no'].create({
            'bsd_chung_tu': self.bsd_ma_dat_coc,
            'bsd_ngay': self.bsd_ngay_dat_coc,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_ps_tang': self.bsd_tien_dc,
            'bsd_ps_giam': 0,
            'bsd_loai_ct': 'dat_coc',
            'bsd_phat_sinh': 'tang',
            'bsd_dat_coc_id': self.id,
            'state': 'da_gs',
        })

    # KD.10.01 Xác nhận đặt cọc
    def action_xac_nhan(self):
        # self.write({
        #     'state': 'xac_nhan',
        # })
        # Cập nhật trạng thái hoàn thành cho báo giá đã ký khi tạo đặt cọc
        self.bsd_bao_gia_id.write({
            'state': 'hoan_thanh',
        })
        self._tao_rec_cong_no()

    # KD.10.02 In đặt cọc
    def action_in_dc(self):
        return self.env.ref('bsd_kinh_doanh.bsd_dat_coc_report_action').read()[0]

    # KD.10.03 Upload đặt cọc
    def action_upload_dc(self):
        self.write({
            'bsd_ngay_up_dc': datetime.date.today(),
        })

    # KD.10.04 Ký đặt cọc
    def action_ky_dc(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_ky_dc_action').read()[0]
        return action

    # KD.10.05 Hủy đặt cọc
    def action_huy(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_huy_dc_action').read()[0]
        return action

    # R.14 Đã thanh toán đợt
    def _compute_tien_ttd(self):
        for each in self:
            if each.bsd_thanh_toan == 'da_tt':
                ltt_dc = each.bsd_ltt_ids.filtered(lambda l: l.bsd_gd_tt == 'dat_coc').ids
                cong_no = each.env['bsd.cong_no'].search([('bsd_dat_coc_id', '=', each.id),
                                                          ('bsd_dot_tt_id', 'in', ltt_dc),
                                                          ('bsd_loai_ct', '=', 'phieu_thu')])
                each.bsd_tien_ttd = 0
                if cong_no:
                    each.bsd_tien_ttd = sum(cong_no.mapped('bsd_ps_giam'))
            else:
                each.bsd_tien_ttd = 0

    # KD.10.07 Tính lại hạn thanh toán khi ký cọc
    def tinh_lai_han_tt(self):
        # Kiểm tra ngày ngày tính chính sách thanh toán theo ngày ký đặt cọc hay không
        if self.bsd_cs_tt_id.bsd_ngay_tinh != 'ndc':
            pass

        # hàm cộng tháng
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year, month, day)
        # ngày ký đặt cọc:
        ngay_ky_dc = self.bsd_ngay_ky_dc
        ltts = self.bsd_ltt_ids.filtered(lambda l: l.bsd_loai == 'dtt').sorted('bsd_stt')
        # kiểm tra cách tính của đợt thanh toán đầu tiên
        if ltts[0].bsd_cs_tt_ct_id.bsd_cach_tinh != 'td':
            pass
        else:
            ngay_hh_tt_dot = ngay_ky_dc
            for dot in ltts:
                lai_phat = dot.bsd_cs_tt_id.bsd_lai_phat_tt_id
                cs_tt_ct_id = dot.bsd_cs_tt_ct_id  # lấy lại cách sinh lịch thanh toán
                # Kiểm tra khi gặp đợt không phải tự động sẽ dừng vòng for
                if cs_tt_ct_id.bsd_cach_tinh != 'td':
                    # ngay_hh_tt_dot = dot.bsd_ngay_hh_tt
                    # continue
                    break
                if cs_tt_ct_id.bsd_tiep_theo == 'ngay':
                    ngay_hh_tt_dot += datetime.timedelta(days=cs_tt_ct_id.bsd_so_ngay)
                else:
                    ngay_hh_tt_dot = add_months(ngay_hh_tt_dot, cs_tt_ct_id.bsd_so_thang)

                ngay_an_han = ngay_hh_tt_dot + datetime.timedelta(days=lai_phat.bsd_an_han)

                dot.write({
                    'bsd_ngay_hh_tt': ngay_hh_tt_dot,
                    'bsd_ngay_ah': ngay_an_han,
                })
                dot.bsd_child_ids.write({
                    'bsd_ngay_hh_tt': dot.bsd_ngay_hh_tt,
                })

    # Override hàm search name của odoo
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        # private implementation of name_search, allows passing a dedicated user
        # for the name_get part to solve some access rights issues
        args = list(args or [])
        if not (name == '' and operator == 'ilike'):
            args += [('bsd_ten_sp', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return models.lazy_name_get(recs.with_user(access_rights_uid))

    # # Tạo thong báo hủy giữ chỗ
    # def tao_tb_huy_gc(self):
    #     giu_cho = self.bsd_bao_gia_id.bsd_giu_cho_id
    #     giu_cho.activity_schedule(act_type_xmlid='mail.mail_activity_data_todo',
    #                               summary='Hủy giữ chỗ đặt cọc bị hủy')

    # Tạo phiếu thay đổi người ký TTĐC/HĐMB
    def action_tao_thay_doi(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_dat_coc_chuyen_dd_action_popup').read()[0]
        action['context'] = {
            'default_bsd_tieu_de': 'Phiếu thay đổi đại diện đặt cọc ' + self.bsd_ma_dat_coc,
            'default_bsd_dat_coc_id': self.id
        }
        return action
