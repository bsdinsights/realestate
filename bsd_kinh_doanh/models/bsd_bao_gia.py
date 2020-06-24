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
    _description = "Bảng tính giá căn hộ"
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
    bsd_ngay_bao_gia = fields.Datetime(string="Ngày", help="Ngày bảng tính giá", required=True,
                                       default=lambda self: fields.Datetime.now(),
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Tên giữ chỗ", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án",
                                   related="bsd_giu_cho_id.bsd_du_an_id", store=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Tên đợt mở bán",
                                    related="bsd_giu_cho_id.bsd_dot_mb_id", store=True)
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá", help="Bảng giá bán",
                                      related="bsd_dot_mb_id.bsd_bang_gia_id", store=True)
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ",
                                  related="bsd_giu_cho_id.bsd_tien_gc", store=True)
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc", compute='_compute_tien_dc', store=True)

    def _get_nhan_vien(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)])

    bsd_nvbh_id = fields.Many2one('hr.employee', string="Nhân viên BH", help="Nhân viên bán hàng",
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

    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Tên căn hộ",
                                  related="bsd_giu_cho_id.bsd_unit_id", store=True)
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng", help="Diện tích tim tường",
                             related="bsd_unit_id.bsd_dt_xd", store=True)
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế",
                             related="bsd_unit_id.bsd_dt_sd", store=True)
    bsd_thue_id = fields.Many2one('account.tax', string="Thuế", help="Thuế", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_qsdd_m2 = fields.Monetary(string="Giá trị QSDĐ/ m2", help="Giá trị quyền sử dụng đất trên m2",
                                  related="bsd_unit_id.bsd_qsdd_m2", store=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", related="bsd_thue_id.amount", store=True,
                                 digits=(12, 2))
    bsd_tl_pbt = fields.Float(string="Tỷ lệ phí bảo trì", help="Tỷ lệ phí bảo trì", compute='_compute_tl_pbt', store=True)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán", compute="_compute_gia_ban", store=True)
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

    state = fields.Selection([('nhap', 'Nháp'), ('cho_duyet', 'Chờ duyệt'),
                              ('da_duyet', 'Đã duyệt'), ('dat_coc', 'Đặt cọc'),
                              ('huy', 'Hủy')], string="Trạng thái", default="nhap", help="Trạng thái", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_bg_ids = fields.One2many('bsd.ban_giao', 'bsd_bao_gia_id', string="Bàn giao",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_ltt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_bao_gia_id', string="Lịch thanh toán",
                                  readonly=True)
    bsd_ps_ck_ids = fields.One2many('bsd.ps_ck', 'bsd_bao_gia_id', string="Phát sinh chiết khấu",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})

    bsd_ngay_in_bg = fields.Datetime(string="Ngày in báo giá", help="Ngày in báo giá", readonly=True)
    bsd_ngay_hh_kbg = fields.Datetime(string="Hết hạn ký BG", help="Ngày hết hiệu lực ký báo giá", readonly=True)
    bsd_ngay_ky_bg = fields.Datetime(string="Ngày ký báo giá", help="Ngày ký báo giá", readonly=True)

    bsd_ngay_hl_bg = fields.Datetime(string="Hiệu lực báo giá", help="Hiệu lực bảng tính giá",
                                     compute="_compute_ngay_hl", store=True)

    bsd_dsh_ids = fields.Many2many('res.partner', string="Đồng sở hữu",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_pt_tt_id = fields.Many2one('bsd.pt_tt', string="Phương thức thanh toán", help="Phương thức thanh toán",
                                   required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_so_dat_coc = fields.Integer(string="# Đặt cọc", compute='_compute_dat_coc')

    bsd_km_ids = fields.One2many('bsd.bao_gia_km', 'bsd_bao_gia_id', string="Danh sách khuyến mãi",
                                 help="Danh sách khuyến mãi",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_ck_db_ids = fields.One2many('bsd.ck_db', 'bsd_bao_gia_id', string="Danh sách chiết khấu đặt biệt",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})

    # R.33 Hiệu lực báo giá
    @api.depends('bsd_ngay_bao_gia')
    def _compute_ngay_hl(self):
        for each in self:
            so_ngay = datetime.timedelta(days=each.bsd_du_an_id.bsd_hh_bg)
            each.bsd_ngay_hl_bg = each.bsd_ngay_bao_gia + so_ngay

    # KD.09.02 Ưu tiên báo giá theo Giữ chỗ
    # @api.constrains('bsd_giu_cho_id')
    # def _constrain_gc_tc(self):
    #     if self.bsd_giu_cho_id:
    #         giu_cho = self.env['bsd.giu_cho'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
    #                                                   ('state', '=', 'giu_cho'),
    #                                                   ('bsd_unit_id', '=', self.bsd_unit_id.id),
    #                                                   ('bsd_ngay_hh_bg', '<', self.bsd_giu_cho_id.bsd_ngay_hh_bg)])
    #         if giu_cho:
    #             raise UserError("Có Giữ chỗ cần được Báo giá trước .\n Vui lòng chờ đến lược của bạn!")

    @api.depends('bsd_tien_gc', 'bsd_unit_id')
    def _compute_tien_dc(self):
        for each in self:
            if each.bsd_unit_id.bsd_tien_dc != 0:
                each.bsd_tien_dc = each.bsd_unit_id.bsd_tien_dc
            else:
                each.bsd_tien_dc = each.bsd_unit_id.bsd_du_an_id.bsd_tien_dc
            each.bsd_tien_dc = each.bsd_tien_dc - each.bsd_tien_gc

    @api.depends('bsd_unit_id.bsd_tl_pbt')
    def _compute_tl_pbt(self):
        for each in self:
            if each.bsd_unit_id.bsd_tl_pbt != 0:
                each.bsd_tl_pbt = each.bsd_unit_id.bsd_tl_pbt
            else:
                each.bsd_tl_pbt = each.bsd_unit_id.bsd_du_an_id.bsd_tl_pbt

    @api.depends('bsd_gia_ban', 'bsd_tl_pbt')
    def _compute_tien_pbt(self):
        for each in self:
            each.bsd_tien_pbt = each.bsd_gia_ban * each.bsd_tl_pbt / 100

    @api.depends('bsd_unit_id', 'bsd_bang_gia_id.item_ids.fixed_price')
    def _compute_gia_ban(self):
        for each in self:
            item = each.bsd_bang_gia_id.item_ids.filtered(
                lambda x: x.product_tmpl_id == each.bsd_unit_id.product_tmpl_id)
            each.bsd_gia_ban = item.fixed_price

    @api.depends('bsd_bg_ids.bsd_tien_bg')
    def _compute_tien_bg(self):
        for each in self:
            each.bsd_tien_bg = sum(each.bsd_bg_ids.mapped('bsd_tien_bg'))

    @api.depends('bsd_ps_ck_ids.bsd_tien_ck', 'bsd_ck_db_ids.bsd_tien_ck', 'bsd_ck_db_ids.state')
    def _compute_tien_ck(self):
        for each in self:
            tien_ck_db = sum(each.bsd_ck_db_ids.filtered(lambda t: t.state == 'duyet').mapped('bsd_tien_ck'))
            each.bsd_tien_ck = sum(each.bsd_ps_ck_ids.mapped('bsd_tien_ck')) + tien_ck_db

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
                each.bsd_thang_pql = each.bsd_unit_id.bsd_thang_pql
            else:
                each.bsd_thang_pql = each.bsd_unit_id.bsd_du_an_id.bsd_thang_pql

            each.bsd_tien_pql = each.bsd_unit_id.bsd_tien_pql

    @api.depends('bsd_gia_truoc_thue', 'bsd_tien_thue', 'bsd_tien_pbt')
    def _compute_tong_gia(self):
        for each in self:
            each.bsd_tong_gia = each.bsd_gia_truoc_thue + each.bsd_tien_thue + each.bsd_tien_pbt

    # KD.09.03 Xác nhận báo giá
    def action_xac_nhan(self):
        if not self.bsd_ltt_ids:
            raise UserError("Bảng tính giá chưa có lịch thanh toán.\n Vui lòng kiểm tra lại")
        else:
            self.write({
                'state': 'cho_duyet',
            })

    # KD.09.04 Duyệt báo giá
    def action_duyet(self):
        self.write({
            'state': 'da_duyet',
        })

    # KD.09.05 In báo giá
    def action_in_bg(self):
        return self.env.ref('bsd_kinh_doanh.bsd_bao_gia_report_action').read()[0]

    def _cb_du_lieu_dtt(self, stt, ma_dtt, dot_tt, lai_phat, ngay_hh_tt, cs_tt):
        res = {}
        if ngay_hh_tt:
            ngay_ah_cd = ngay_hh_tt + datetime.timedelta(days=lai_phat.bsd_an_han)
        else:
            ngay_ah_cd = False

        tien_dot_tt = float_round(dot_tt.bsd_tl_tt * (self.bsd_tong_gia - self.bsd_tien_pbt) / 100, precision_digits=0)

        res.update({
            'bsd_stt': stt,
            'bsd_ma_dtt': ma_dtt,
            'bsd_ten_dtt': 'Đợt ' + str(stt),
            'bsd_ngay_hh_tt': ngay_hh_tt,
            'bsd_tien_dot_tt': tien_dot_tt,
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
            'bsd_gd_tt': dot_tt.bsd_gd_tt,
            'bsd_tien_dc': self.bsd_tien_gc + self.bsd_tien_dc if stt == 1 else 0
        })
        return res

    def action_lich_tt(self):
        # Xóa lịch thanh toán hiện tại
        self.bsd_ltt_ids.unlink()
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
        ngay_hh_tt = datetime.datetime.now()  # Ngày giá trị mặc đính tính ngày hết hạn thanh toán
        cs_tt = self.bsd_cs_tt_id
        dot_tt_ids = cs_tt.bsd_ct_ids
        lai_phat = cs_tt.bsd_lai_phat_tt_id

        for dot in dot_tt_ids.sorted('bsd_stt'):
            # Tạo dữ liệu đợt cố định
            if dot.bsd_cach_tinh == 'cd':
                dot_cd = dot
                stt += 1
                # cập nhật lại ngày hết hạn thanh toán
                ngay_hh_tt = dot_cd.bsd_ngay_cd
                self.bsd_ltt_ids.create(self._cb_du_lieu_dtt(stt, 'CD', dot_cd, lai_phat, ngay_hh_tt, cs_tt))
            # Tạo dữ liệu đợt tự động
            elif dot.bsd_cach_tinh == 'td':
                dot_td = dot
                ngay_hh_tt_td = ngay_hh_tt
                list_ngay_hh_tt_td = []
                if dot_td.bsd_lap_lai == '1':
                    for dot_i in range(0, dot_td.bsd_so_dot + 1):
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

                # Gán lại ngày cuối cùng tự động thanh toán
                ngay_hh_tt = list_ngay_hh_tt_td[-1]
                for ngay in list_ngay_hh_tt_td:
                    stt += 1
                    self.bsd_ltt_ids.create(self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay, cs_tt))

            # Tạo đợt thanh toán theo dự kiến bàn giao
            elif dot.bsd_cach_tinh == 'dkbg':
                dot_dkbg = dot
                ngay_hh_tt_dkbg = self.bsd_unit_id.bsd_ngay_dkbg or self.bsd_unit_id.bsd_du_an_id.bsd_ngay_dkbg or False
                stt += 1
                self.bsd_ltt_ids.create(self._cb_du_lieu_dtt(stt, 'DKBG', dot_dkbg, lai_phat, ngay_hh_tt_dkbg, cs_tt))

            # Tạo đợt bàn giao cuối
            else:
                dot_cuoi = dot
                stt += 1
                self.bsd_ltt_ids.create(self._cb_du_lieu_dtt(stt, 'DBGC', dot_cuoi, lai_phat, False, cs_tt))

    def action_huy(self):
        pass

    # KD.09.06 Ký báo giá
    def action_ky_bg(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_ky_bg_action').read()[0]
        return action

    # KD.09.07 Hủy báo giá
    def action_huy(self):
        dat_coc = self.env['bsd.dat_coc'].search([('state', '!=', 'huy'), ('bsd_bao_gia_id', '=', self.id)])
        if dat_coc:
            raise UserError("Đã có phát sinh Phiếu cọc. Bạn không thể hủy Báo giá")
        else:
            self.write({
                'state': 'huy',
            })

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_giu_cho_id' in vals:
            giu_cho = self.env['bsd.giu_cho'].browse(vals['bsd_giu_cho_id'])
            sequence = giu_cho.bsd_du_an_id.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu báo giá'))
        vals['bsd_ma_bao_gia'] = sequence.next_by_id()
        return super(BsdBaoGia, self).create(vals)

    # KD.09.09 Tạo Bảng tính giá từ màn hình Giữ chỗ
    def action_tao_dat_coc(self):
        context = {
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_bao_gia_id': self.id,
        }
        return {
            "name": "Tạo đặt cọc",
            "res_model": 'bsd.dat_coc',
            "view": [[False, 'form']],
            "type": 'ir.actions.act_window',
            "view_mode": "form",
            "context": context,
            "target": "new"
        }

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


class BsdBaoGiaKhuyenMai(models.Model):
    _name = 'bsd.bao_gia_km'
    _description = "Thông tin chương trình khuyến mãi cho bảng tính giá"
    _rec_name = 'bsd_khuyen_mai_id'

    bsd_khuyen_mai_id = fields.Many2one('bsd.khuyen_mai', string="Khuyến mãi")
    bsd_ma_km = fields.Char(related='bsd_khuyen_mai_id.bsd_ma_km')
    bsd_tu_ngay = fields.Date(related='bsd_khuyen_mai_id.bsd_tu_ngay')
    bsd_den_ngay = fields.Date(related='bsd_khuyen_mai_id.bsd_den_ngay')
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá", required=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán")
    bsd_ngay_hldc = fields.Date(related='bsd_khuyen_mai_id.bsd_ngay_hldc')
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc")
