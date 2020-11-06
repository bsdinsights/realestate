# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdDanhSachTheoDoi(models.Model):
    _name = 'bsd.ds_td'
    _description = "Danh sách theo dõi"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã danh sách theo dõi", required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã danh sách theo dõi đã tồn tại !')
    ]
    bsd_ngay_tao = fields.Datetime(string="Ngày", help="Ngày tạo danh sách theo dõi",
                                   required=True, default=lambda self: fields.Datetime.now(),
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ten = fields.Char(string="Tiêu đề", required=True, help="Tiêu đề",
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_loai_dt = fields.Selection([
        ('san_pham', 'Sản phẩm'),
        ('ky_dc', 'Quá hạn ký PĐC'),
        ('ky_ttdc', 'Quá hạn ký TTĐC/HHĐC'),
        ('ky_hdmb', 'Quá hạn ký HĐMB'),
        ('tl_dc', 'Thanh lý đặt cọc'),
        ('tl_dc_cbhd', 'Thanh lý đặt cọc (Chuẩn bị HĐ)'),
        ('tl_ttdc_hd', 'Thanh lý giao dịch'),
        ('vp_tt', 'Lịch thanh toán')], string="Loại theo dõi", required=True,
       help="Đối tượng", default='san_pham',
       readonly=True,
       states={'nhap': [('readonly', False)]})
    bsd_loai_td = fields.Selection([('vp_tg', 'Vi phạm thời gian'),
                                    ('yc_kh', 'Yêu cầu'),
                                    ('vp_tt', 'Vi phạm thanh toán')], string="Lý do",
                                   required=True, help="Lý do tạo danh sách theo dõi", default="yc_kh",
                                   readonly=True)
    bsd_loai_xl = fields.Selection([('gia_han', 'Gia hạn'),
                                    ('thanh_ly', 'Thanh lý'),
                                    ('tt_td', 'Tiếp tục theo dõi')], string="Loại xử lý",
                                   required=True, help="Loại xử lý", default='thanh_ly',
                                   readonly=True)
    bsd_nhom = fields.Selection([('kd', 'Kinh doanh'),
                                 ('dvkh', 'DVKH'),
                                 ('kt', 'Kế toán')], string="Nhóm",
                                required=True,
                                readonly=True, default='kd',
                                states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng",
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_hh = fields.Datetime(string="Ngày hết hạn",
                                  help="""Ngày hết hạn:\n
                                        - Nếu đối tượng là đặt cọc: Hạn ký đặt cọc \n
                                        - Nếu đối tượng là thỏa thuận đặt cọc: Hạn ký thỏa thuận đặt cọc\n
                                        - Nếu đối tượng là hơp đồng mua bán: Hạn ký hợp đồng""",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tong_gt_hd = fields.Monetary(string="Tổng giá trị HĐ", help="Tổng giá trị thanh toán theo Hợp đồng",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Số tiền khách hàng đã thanh toán",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_ngay_gh = fields.Date(string="Ngày gia hạn", help="Ngày gia hạn mới cho đặt cọc/ Thỏa thuận đặt cọc/ Hợp đồng",
                              readonly=True,
                              states={'nhap': [('readonly', False)], 'xn_tt': [('readonly', False)]})
    bsd_gui_thu = fields.Boolean(string="Gửi thư thanh lý", help="Gửi thư thanh lý",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)], 'xn_tt': [('readonly', False)]})
    bsd_ky_bb = fields.Boolean(string="Ký BB thanh lý", help="Ký biên bản thanh lý",
                               readonly=True,
                               states={'nhap': [('readonly', False)], 'xn_tt': [('readonly', False)]})
    bsd_mo_bl = fields.Boolean(string="Mở bán lại", help="Đánh dấu sản phẩm được mở bán lại?",
                               readonly=True,
                               states={'nhap': [('readonly', False)], 'xn_tt': [('readonly', False)]})
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Đợt mở bán",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)], 'xn_tt': [('readonly', False)]})
    bsd_pt_phat = fields.Selection([('tien', 'Số tiền hoàn'), ('phan_tram', 'Phần trăm')],
                                   string="Phương thức tính", help="Phương thức tính tiền thanh lý",
                                   required=True, default='tien', readonly=True,
                                   states={'nhap': [('readonly', False)], 'xn_tt': [('readonly', False)]})
    bsd_tl_phat = fields.Float(string="Tỷ lệ phạt", help="Tỷ lệ phần trăm mà khách hàng bị phạt",
                               readonly=True,
                               states={'nhap': [('readonly', False)], 'xn_tt': [('readonly', False)]})
    bsd_tien_hoan = fields.Monetary(string="Số tiền hoàn", help="Số tiền khách hàng được hoàn trả",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)], 'xn_tt': [('readonly', False)]})
    bsd_tong_tp = fields.Monetary(string="Tổng tiền phạt", help="Tổng số tiền phạt thanh lý",
                                  compute="_compute_tong_tien", store=True)

    @api.depends('bsd_pt_phat', 'bsd_tl_phat', 'bsd_tien_hoan')
    def _compute_tong_tien(self):
        for each in self:
            if each.bsd_pt_phat == 'tien':
                each.bsd_tong_tp = each.bsd_tien_da_tt - each.bsd_tien_hoan
            else:
                if self.bsd_loai_dt == 'tl_dc':
                    each.bsd_tong_tp = (each.bsd_tien_dc * each.bsd_tl_phat) / 100
                else:
                    each.bsd_tong_tp = (each.bsd_tong_gt_hd * each.bsd_tl_phat) / 100
    bsd_quyet_dinh = fields.Text(string="Quyết định", help="Quyết định xử lý cho Danh sách theo dõi",
                                 readonly=True, copy=False,
                                 states={'nhap': [('readonly', False)], 'xn_tt': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'), ('xn_tt', 'Xác nhận thông tin'),
                              ('xac_nhan', 'Đã có quyết định'),
                              ('hoan_thanh', 'Hoàn thành'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_dt_xd = fields.Float(string="Diện tích xây dựng", help="Diện tích xây dựng", compute="_compute_tt")
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế", compute="_compute_tt")
    bsd_thue_id = fields.Many2one('bsd.thue_suat', string="Mã thuế", help="Mã thuế", compute="_compute_tt")
    bsd_qsdd_m2 = fields.Float(string="QSDĐ/ m2", help="Giá trị quyền sử dụng đất trên m2", compute="_compute_tt")
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", compute="_compute_tt")
    bsd_tl_pbt = fields.Float(string="Tỷ lệ phí bảo trì", help="Tỷ lệ phí bảo trì", compute="_compute_tt")
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán",
                                   compute="_compute_tt")
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán", compute="_compute_tt")
    bsd_tien_ck = fields.Monetary(string="Tiền chiết khấu", help="Tổng tiền chiết khấu", compute="_compute_tt")
    bsd_tien_bg = fields.Monetary(string="Tiền bàn giao", help="Tổng tiền bàn giao", compute="_compute_tt")
    bsd_gia_truoc_thue = fields.Monetary(string="Giá bán trước thuế",
                                         help="Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ tiền chiết khấu",
                                         compute="_compute_tt")
    bsd_tien_qsdd = fields.Monetary(string="Giá trị QSDĐ",
                                    help="Giá trị quyền sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dụng",
                                    compute="_compute_tt")
    bsd_tien_thue = fields.Monetary(string="Tiền thuế",
                                    help="Tiền thuế: bằng giá bán trước thuế trừ giá trị QSDĐ/m2 nhân với thuế suất",
                                    compute="_compute_tt")
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân giá bán",
                                   compute="_compute_tt")
    bsd_tong_gia = fields.Monetary(string="Tổng giá bán",
                                   help="Tổng giá bán: bằng giá bán trước thuế cộng tiền thuế cộng phí bảo trì",
                                   compute="_compute_tt")

    bsd_ma_dat_coc = fields.Char(related='bsd_dat_coc_id.bsd_ma_dat_coc')
    bsd_ngay_dat_coc = fields.Date(related='bsd_dat_coc_id.bsd_ngay_dat_coc')
    bsd_co_ttdc = fields.Boolean(related='bsd_dat_coc_id.bsd_co_ttdc')
    bsd_kh_dc_id = fields.Many2one(related='bsd_dat_coc_id.bsd_khach_hang_id')
    bsd_bao_gia_dc_id = fields.Many2one(related='bsd_dat_coc_id.bsd_bao_gia_id')
    bsd_giu_cho_dc_id = fields.Many2one(related='bsd_dat_coc_id.bsd_giu_cho_id')
    bsd_du_an_dc_id = fields.Many2one(related='bsd_dat_coc_id.bsd_du_an_id')
    bsd_dot_mb_dc_id = fields.Many2one(related='bsd_dat_coc_id.bsd_dot_mb_id')
    bsd_bang_gia_dc_id = fields.Many2one(related='bsd_dat_coc_id.bsd_bang_gia_id')
    bsd_tien_gc = fields.Monetary(related='bsd_dat_coc_id.bsd_tien_gc')
    bsd_nvbh_id = fields.Many2one(related='bsd_dat_coc_id.bsd_nvbh_id')
    bsd_san_gd_id = fields.Many2one(related='bsd_dat_coc_id.bsd_san_gd_id')
    bsd_gioi_thieu_id = fields.Many2one(related='bsd_dat_coc_id.bsd_gioi_thieu_id')
    bsd_ctv_id = fields.Many2one(related='bsd_dat_coc_id.bsd_ctv_id')

    bsd_ma_hd_ban = fields.Char(related='bsd_hd_ban_id.bsd_ma_hd_ban')
    bsd_ngay_hd_ban = fields.Date(related='bsd_hd_ban_id.bsd_ngay_hd_ban')
    bsd_kh_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_khach_hang_id')
    bsd_bao_gia_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_bao_gia_id')
    bsd_dat_coc_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_dat_coc_id')
    bsd_du_an_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_du_an_id')
    bsd_dot_mb_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_dot_mb_id')
    bsd_bang_gia_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_bang_gia_id')
    state_hd = fields.Selection(related='bsd_hd_ban_id.state')

    bsd_parent_id = fields.Many2one('bsd.ds_td', string="DS theo dõi", readonly=True)
    bsd_child_ids = fields.One2many('bsd.ds_td', 'bsd_parent_id', string="DS theo dõi", readonly=True)

    bsd_so_tb_tl = fields.Integer(string="# TB thanh lý", compute='_compute_tb_tl')
    bsd_so_thanh_ly = fields.Integer(string="# Thanh lý", compute='_compute_thanh_ly')

    bsd_da_tb_tl = fields.Boolean(string="Đã tạo tbtl", default=False, readonly=True)
    bsd_da_thanh_ly = fields.Boolean(string="Đã tạo thanh lý", default=False, readonly=True)

    def _compute_tb_tl(self):
        for each in self:
            tb_tl = self.env['bsd.tb_tl'].search([('bsd_ds_td_id', '=', self.id)])
            each.bsd_so_tb_tl = len(tb_tl)

    def _compute_thanh_ly(self):
        for each in self:
            thanh_ly = self.env['bsd.thanh_ly'].search([('bsd_ds_td_id', '=', self.id)])
            each.bsd_so_thanh_ly = len(thanh_ly)

    def action_view_tb_tl(self):
        action = self.env.ref('bsd_dich_vu.bsd_tb_tl_action').read()[0]

        tb_tl = self.env['bsd.tb_tl'].search([('bsd_ds_td_id', '=', self.id)])
        if len(tb_tl) > 1:
            action['domain'] = [('id', 'in', tb_tl.ids)]
        elif tb_tl:
            form_view = [(self.env.ref('bsd_dich_vu.bsd_tb_tl_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = tb_tl.id
        # Prepare the context.
        context = {
            'default_bsd_ds_td_id': self.id,
        }
        action['context'] = context
        return action

    def action_view_thanh_ly(self):
        action = self.env.ref('bsd_dich_vu.bsd_thanh_ly_action').read()[0]

        thanh_ly = self.env['bsd.thanh_ly'].search([('bsd_ds_td_id', '=', self.id)])
        if len(thanh_ly) > 1:
            action['domain'] = [('id', 'in', thanh_ly.ids)]
        elif thanh_ly:
            form_view = [(self.env.ref('bsd_dich_vu.bsd_thanh_ly_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = thanh_ly.id
        # Prepare the context.
        context = {
            'default_bsd_ds_td_id': self.id,
        }
        action['context'] = context
        return action

    @api.onchange('bsd_mo_bl', 'bsd_hd_ban_id', 'bsd_dat_coc_id')
    def _onchange_dot_mb(self):
        if self.bsd_mo_bl:
            if self.bsd_dat_coc_id:
                self.bsd_dot_mb_id = self.bsd_dat_coc_id.bsd_dot_mb_id

            if self.bsd_hd_ban_id:
                self.bsd_dot_mb_id = self.bsd_hd_ban_id.bsd_dot_mb_id

    @api.depends('bsd_loai_dt', 'bsd_hd_ban_id', 'bsd_dat_coc_id')
    def _compute_tt(self):
        if self.bsd_loai_dt in ['tl_dc', 'ky_dc']:
            if self.bsd_dat_coc_id:
                self.bsd_dt_xd = self.bsd_dat_coc_id.bsd_dt_xd
                self.bsd_dt_sd = self.bsd_dat_coc_id.bsd_dt_sd
                self.bsd_thue_id = self.bsd_dat_coc_id.bsd_thue_id
                self.bsd_qsdd_m2 = self.bsd_dat_coc_id.bsd_qsdd_m2
                self.bsd_thue_suat = self.bsd_dat_coc_id.bsd_thue_suat
                self.bsd_tl_pbt = self.bsd_dat_coc_id.bsd_tl_pbt
                self.bsd_cs_tt_id = self.bsd_dat_coc_id.bsd_cs_tt_id
                self.bsd_gia_ban = self.bsd_dat_coc_id.bsd_gia_ban
                self.bsd_tien_ck = self.bsd_dat_coc_id.bsd_tien_ck
                self.bsd_tien_bg = self.bsd_dat_coc_id.bsd_tien_bg
                self.bsd_gia_truoc_thue = self.bsd_dat_coc_id.bsd_gia_truoc_thue
                self.bsd_tien_qsdd = self.bsd_dat_coc_id.bsd_tien_qsdd
                self.bsd_tien_thue = self.bsd_dat_coc_id.bsd_tien_thue
                self.bsd_tien_pbt = self.bsd_dat_coc_id.bsd_tien_pbt
                self.bsd_tong_gia = self.bsd_dat_coc_id.bsd_tong_gia
            else:
                self.bsd_dt_xd = False
                self.bsd_dt_sd = False
                self.bsd_thue_id = False
                self.bsd_qsdd_m2 = False
                self.bsd_thue_suat = False
                self.bsd_tl_pbt = False
                self.bsd_cs_tt_id = False
                self.bsd_gia_ban = False
                self.bsd_tien_ck = False
                self.bsd_tien_bg = False
                self.bsd_gia_truoc_thue = False
                self.bsd_tien_qsdd = False
                self.bsd_tien_thue = False
                self.bsd_tien_pbt = False
                self.bsd_tong_gia = False
        else:
            if self.bsd_hd_ban_id:
                self.bsd_dt_xd = self.bsd_hd_ban_id.bsd_dt_xd
                self.bsd_dt_sd = self.bsd_hd_ban_id.bsd_dt_sd
                self.bsd_thue_id = self.bsd_hd_ban_id.bsd_thue_id
                self.bsd_qsdd_m2 = self.bsd_hd_ban_id.bsd_qsdd_m2
                self.bsd_thue_suat = self.bsd_hd_ban_id.bsd_thue_suat
                self.bsd_tl_pbt = self.bsd_hd_ban_id.bsd_tl_pbt
                self.bsd_cs_tt_id = self.bsd_hd_ban_id.bsd_cs_tt_id
                self.bsd_gia_ban = self.bsd_hd_ban_id.bsd_gia_ban
                self.bsd_tien_ck = self.bsd_hd_ban_id.bsd_tien_ck
                self.bsd_tien_bg = self.bsd_hd_ban_id.bsd_tien_bg
                self.bsd_gia_truoc_thue = self.bsd_hd_ban_id.bsd_gia_truoc_thue
                self.bsd_tien_qsdd = self.bsd_hd_ban_id.bsd_tien_qsdd
                self.bsd_tien_thue = self.bsd_hd_ban_id.bsd_tien_thue
                self.bsd_tien_pbt = self.bsd_hd_ban_id.bsd_tien_pbt
                self.bsd_tong_gia = self.bsd_hd_ban_id.bsd_tong_gia
            else:
                self.bsd_dt_xd = False
                self.bsd_dt_sd = False
                self.bsd_thue_id = False
                self.bsd_qsdd_m2 = False
                self.bsd_thue_suat = False
                self.bsd_tl_pbt = False
                self.bsd_cs_tt_id = False
                self.bsd_gia_ban = False
                self.bsd_tien_ck = False
                self.bsd_tien_bg = False
                self.bsd_gia_truoc_thue = False
                self.bsd_tien_qsdd = False
                self.bsd_tien_thue = False
                self.bsd_tien_pbt = False
                self.bsd_tong_gia = False

    def action_xac_nhan_tt(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xn_tt',
            })

    # DV.15.01 Xác nhận thông tin trên danh sách theo dõi
    def action_xac_nhan(self):
        if not self.bsd_quyet_dinh:
            raise UserError(_("Trường thông tin quyết định không thể trống.\nVui lòng kiểm tra lại thông tin"))
        if self.state == 'xn_tt':
            self.write({
                'state': 'xac_nhan',
            })

    # DV.15.03 Gia hạn
    def action_gia_han(self):
        if self.bsd_loai_dt == 'ky_dc':
            if self.bsd_dat_coc_id:
                self.bsd_dat_coc_id.write({
                    'bsd_ngay_hh_kdc': self.bsd_ngay_gh
                })
        if self.bsd_loai_dt == 'ky_ttdc':
            if self.bsd_hd_ban_id:
                self.bsd_hd_ban_id.write({
                    'bsd_ngay_hh_ttdc': self.bsd_ngay_gh
                })
        if self.bsd_loai_dt == 'ky_hdmb':
            if self.bsd_hd_ban_id:
                self.bsd_hd_ban_id.write({
                    'bsd_ngay_hh_khdb': self.bsd_ngay_gh
                })
        self.write({
            'state': 'hoan_thanh'
        })

    def _tt_td(self):
        if self.bsd_loai_dt == 'tl_dc':
            tieu_de = 'Theo dõi thanh lý đặt cọc ' + self.bsd_dat_coc_id.bsd_ma_dat_coc
        else:
            tieu_de = 'Theo dõi thanh lý hợp đồng ' + self.bsd_hd_ban_id.bsd_ma_hd_ban
        self.copy(default={'bsd_loai_xl': 'thanh_ly',
                           'bsd_ngay_tao': fields.Datetime.now(),
                           'bsd_ten': tieu_de,
                           'bsd_ma': '/',
                           'state': 'nhap',
                           'bsd_parent_id': self.id})
        self.write({
            'bsd_loai_xl': 'tt_td'
        })

    def action_hoan_thanh(self):
        if self.bsd_gui_thu:
            self._tao_tb_tl()
        if self.bsd_ky_bb:
            self._tao_thanh_ly()
        else:
            self._tt_td()
        if self.state == 'xac_nhan':
            self.write({'state': 'hoan_thanh'})

    # DV.15.07 Hủy danh sách theo dõi
    def action_huy(self):
        return self.env.ref('bsd_dich_vu.bsd_wizard_huy_ds_td_action').read()[0]

    # DV.15.08 Tự động tạo thông báo thanh lý
    def _tao_tb_tl(self):
        if self.bsd_loai_td == 'vp_tg':
            loai_ld = 'qua_han'
        elif self.bsd_loai_td == 'yc_kh':
            loai_ld = 'yc_kh'
        elif self.bsd_loai_td == 'vp_tt':
            loai_ld = 'vp_dk'
        else:
            loai_ld = ''

        if self.bsd_loai_dt == 'tl_dc':
            self.env['bsd.tb_tl'].create({
                'bsd_ds_td_id': self.id,
                'bsd_loai_ld': loai_ld,
                'bsd_loai_dt': 'dat_coc',
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
                'bsd_unit_id': self.bsd_unit_id.id,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_tien_dc': self.bsd_tien_dc,
                'bsd_ngay_ky_dc': self.bsd_dat_coc_id.bsd_ngay_ky_dc,
                'bsd_tien_da_tt': self.bsd_tien_da_tt,
                'bsd_tien_phat': self.bsd_tong_tp
            })
        else:
            self.env['bsd.tb_tl'].create({
                'bsd_ds_td_id': self.id,
                'bsd_loai_ld': loai_ld,
                'bsd_loai_dt': 'hd_ban',
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                'bsd_unit_id': self.bsd_unit_id.id,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_tong_gt_hd': self.bsd_tong_gt_hd,
                'bsd_ngay_ky_hdb': self.bsd_hd_ban_id.bsd_ngay_ky_hdb,
                'bsd_tien_da_tt': self.bsd_tien_da_tt,
                'bsd_tien_phat': self.bsd_tong_tp
            })

    # DV.15.09 Tự động tạo thanh lý
    def _tao_thanh_ly(self):
        tien_hoan = self.bsd_tien_da_tt - self.bsd_tong_tp
        if self.bsd_loai_dt == 'tl_dc':
            self.env['bsd.thanh_ly'].create({
                'bsd_ten': "Thanh lý " + "đặt cọc " + self.bsd_unit_id.bsd_ten_unit,
                'bsd_ds_td_id': self.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
                'bsd_unit_id': self.bsd_unit_id.id,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_tien_dc': self.bsd_tien_dc,
                'bsd_tien_da_tt': self.bsd_tien_da_tt,
                'bsd_tien_phat': self.bsd_tong_tp,
                'bsd_tien_hoan': tien_hoan,
                'bsd_tien_hoan_tt': tien_hoan,
            })
        else:
            self.env['bsd.thanh_ly'].create({
                'bsd_ten': "Thanh lý " + "hợp đồng " + self.bsd_unit_id.bsd_ten_unit,
                'bsd_loai_dt': 'hd_ban',
                'bsd_ds_td_id': self.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_unit_id': self.bsd_unit_id.id,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                'bsd_tong_gt_hd': self.bsd_tong_gt_hd,
                'bsd_tien_da_tt': self.bsd_tien_da_tt,
                'bsd_tien_phat': self.bsd_tong_tp,
                'bsd_tien_hoan': tien_hoan,
                'bsd_tien_hoan_tt': tien_hoan
            })

    # DV.15.12 Kiểm tra dk đặt cọc
    @api.constrains('bsd_loai_dt', 'bsd_dat_coc_id')
    def _constrain_dat_coc(self):
        if self.bsd_loai_dt == 'tl_dc':
            hop_dong = self.env['bsd.hd_ban'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id)])
            if hop_dong:
                raise UserError("Đặc cọc đã được tạo hợp đồng. Vui lòng kiểm tra lại thông tin!")

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã danh sách theo dõi.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdDanhSachTheoDoi, self).create(vals)
