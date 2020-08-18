# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdHopDongMuaBan(models.Model):
    _name = 'bsd.hd_ban'
    _description = "Hợp đồng mua bán"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_hd_ban'

    bsd_ma_hd_ban = fields.Char(string="Mã", help="Mã hợp đồng mua bán", required=True, readonly=True, copy=False,
                                default='/')
    _sql_constraints = [
        ('bsd_ma_hd_ban_unique', 'unique (bsd_ma_hd_ban)',
         'Mã hợp đồng đã tồn tại !'),
    ]
    bsd_ngay_hd_ban = fields.Datetime(string="Ngày", help="Ngày làm hợp đồng mua bán", required=True,
                                      default=lambda self: fields.Datetime.now(),
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Tên đặt cọc", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', related="bsd_dat_coc_id.bsd_bao_gia_id", store=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án",
                                   related="bsd_dat_coc_id.bsd_du_an_id", store=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Tên đợt mở bán",
                                    related="bsd_dat_coc_id.bsd_dot_mb_id", store=True)
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá", help="Bảng giá bán",
                                      related="bsd_dat_coc_id.bsd_bang_gia_id", store=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Tên căn hộ",
                                  related="bsd_dat_coc_id.bsd_unit_id", store=True)
    bsd_ngay_cn = fields.Date(related='bsd_unit_id.bsd_ngay_cn', store=True)
    bsd_ten_sp = fields.Char(related="bsd_unit_id.name", store=True)
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng", help="Diện tích tim tường",
                             related="bsd_dat_coc_id.bsd_dt_xd", store=True)
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế",
                             related="bsd_dat_coc_id.bsd_dt_sd", store=True)
    bsd_thue_id = fields.Many2one('bsd.thue_suat', string="Thuế", help="Thuế",
                                  related="bsd_dat_coc_id.bsd_thue_id", store=True)
    bsd_qsdd_m2 = fields.Monetary(string="Giá trị QSDĐ/ m2", help="Giá trị quyền sử dụng đất trên m2",
                                  related="bsd_dat_coc_id.bsd_qsdd_m2", store=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", related="bsd_dat_coc_id.bsd_thue_suat",
                                 store=True, digits=(12, 2))
    bsd_tl_pbt = fields.Float(string="Tỷ lệ phí bảo trì", help="Tỷ lệ phí bảo trì",
                              related="bsd_dat_coc_id.bsd_tl_pbt", store=True)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán",
                                   related="bsd_dat_coc_id.bsd_cs_tt_id", store=True)
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán", related="bsd_dat_coc_id.bsd_gia_ban", store=True)
    bsd_tien_ck = fields.Monetary(string="Chiết khấu", help="Tổng tiền chiết khấu",
                                  related="bsd_dat_coc_id.bsd_tien_ck", store=True)
    bsd_tien_bg = fields.Monetary(string="Tiền bàn giao", help="Tổng tiền bàn giao",
                                  related="bsd_dat_coc_id.bsd_tien_bg", store=True)
    bsd_gia_truoc_thue = fields.Monetary(string="Giá bán trước thuế",
                                         help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ chiết khấu""",
                                         related="bsd_dat_coc_id.bsd_gia_truoc_thue", store=True)
    bsd_tien_qsdd = fields.Monetary(string="Giá trị QSDĐ",
                                    help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""",
                                    related="bsd_dat_coc_id.bsd_tien_qsdd", store=True)
    bsd_tien_thue = fields.Monetary(string="Tiền thuế",
                                    help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""",
                                    related="bsd_dat_coc_id.bsd_tien_thue", store=True)
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán",
                                   related="bsd_dat_coc_id.bsd_tien_pbt", store=True)
    bsd_tong_gia = fields.Monetary(string="Tổng giá bán",
                                   help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                   related="bsd_dat_coc_id.bsd_tong_gia", store=True)
    bsd_thang_pql = fields.Integer(string="Số tháng đóng phí quản lý", related="bsd_dat_coc_id.bsd_thang_pql", store=True,
                                   help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức")
    bsd_tien_pql = fields.Monetary(string="Phí quản lý", help="Số tiền phí quản lý cần đóng",
                                   related="bsd_dat_coc_id.bsd_tien_pql", store=True)

    state = fields.Selection([('nhap', 'Nháp'),
                              ('ht_dc', 'Hoàn tất đặt cọc'),
                              ('tt_dot1', 'Thanh toán đợt 1'),
                              ('da_ky_ttdc', 'Đã ký TTĐC'),
                              ('du_dk', 'Đủ điều kiện'),
                              ('da_ky', 'Đã ký HĐ'),
                              ('dang_tt', 'Đang thanh toán'),
                              ('du_dkbg', 'Đủ ĐKBG'),
                              ('da_bg', 'Đã bàn giao'),
                              ('ht_tt', 'Hoàn tất thanh toán'),
                              ('bg_gt', 'Bàn giao giấy tờ'),
                              ('da_ht', 'Đã hoàn tất'),
                              ('thanh_ly', 'Thanh lý'),
                              ('huy', 'Hủy')], string="Trạng thái", default="nhap",
                             help="Trạng thái", tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_bg_ids = fields.One2many('bsd.ban_giao', 'bsd_hd_ban_id', string="Bàn giao", readonly=True)
    bsd_ltt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_hd_ban_id', string="Lịch thanh toán",
                                  readonly=True, domain=[('bsd_loai', '=', 'dtt')])
    bsd_dot_pbt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_hd_ban_id', string="Đợt thu phí bảo trì",
                                      readonly=True, domain=[('bsd_loai', '=', 'pbt')])
    bsd_dot_pql_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_hd_ban_id', string="Đợt thu phí quản lý",
                                      readonly=True, domain=[('bsd_loai', '=', 'pql')])
    bsd_dong_sh_ids = fields.One2many('bsd.dong_so_huu', 'bsd_hd_ban_id', string="Đồng sở hữu hiện tại",
                                      readonly=True, domain=[('state', '=', 'active')],
                                      states={'nhap': [('readonly', False)]})
    bsd_dong_sh_cu_ids = fields.One2many('bsd.dong_so_huu', 'bsd_hd_ban_id', string="Đồng sở hữu cũ",
                                         readonly=True, domain=[('state', '=', 'inactive')])
    bsd_ngay_in_hdb = fields.Datetime(string="Ngày in hợp đồng", help="Ngày in hợp đồng mua bán", readonly=True)
    bsd_ngay_hh_khdb = fields.Datetime(string="Hết hạn ký HĐ", help="Ngày hết hạn ký hợp đồng mua bán",
                                       readonly=True)
    bsd_ngay_up_hdb = fields.Datetime(string="Upload hợp đồng", readonly=True,
                                      help="""Ngày tải lên hệ thống hợp đồng bán đã được người mua
                                             ký xác nhận""")
    bsd_ngay_ky_hdb = fields.Datetime(string="Ngày ký hợp đồng", help="Ngày ký hợp đồng mua bán", readonly=True)

    bsd_km_ids = fields.One2many('bsd.bao_gia_km', 'bsd_hd_ban_id', string="Danh sách khuyến mãi",
                                 help="Danh sách khuyến mãi", readonly=True,)

    bsd_ps_ck_ids = fields.One2many('bsd.ps_ck', 'bsd_hd_ban_id', string="Phát sinh chiết khấu",
                                    readonly=True)
    bsd_ck_db_ids = fields.One2many('bsd.ck_db', 'bsd_hd_ban_id', string="Danh sách chiết khấu đặt biệt",
                                    readonly=True)
    bsd_dh_ck_ttn = fields.Boolean(string="Đã hưởng CK Nhanh", help="Đánh dấu hợp đồng đã hưởng CK nhanh",
                                   readonly=True, default=False)
    bsd_co_ck_ms = fields.Boolean(string="Xác nhận CK mua sỉ", help="Xác nhận CK mua sỉ")
    bsd_hd_ms_id = fields.Many2one('bsd.hd_ban', string="HĐ tính CK mua sỉ",
                                   readonly=True, help="Họp đồng áp dụng chiết khấu mua sỉ")
    bsd_co_ttdc = fields.Boolean(string="Thỏa thuận đặt cọc", related="bsd_dat_coc_id.bsd_co_ttdc",
                                 help="Đánh dấu hợp đồng cần ký thỏa thuận đặt cọc trước khi ký hợp đồng", store=True)
    bsd_so_ttdc = fields.Char(string="Số TTĐC", help="Số thỏa thuận đặt cọc", readonly=True)
    bsd_ngay_in_ttdc = fields.Datetime(string="Ngày in TTDC", help="Ngày in thỏa thuận đặt cọc", readonly=True)
    bsd_ngay_hh_ttdc = fields.Datetime(string="Hạn ký TTDC", help="Hiệu lực của thỏa thuận đặt cọc", readonly=True)
    bsd_ngay_ky_ttdc = fields.Datetime(string="Ngày ký TTDC", help="Ngày ký thỏa thuận đặt cọc", readonly=True)
    bsd_duyet_db = fields.Boolean(string="Duyệt đặc biệt", help="Duyệt đặc biệt", readonly=True)
    bsd_ngay_duyet_db = fields.Datetime(string="Ngày duyệt", help="Ngày duyệt", readonly=True)
    bsd_nguoi_duyet_db_id = fields.Many2one('res.users', string="Người duyệt", readonly=True, tracking=2)
    bsd_ngay_dkbg = fields.Date(string="Ngày DKBG", help="Ngày dự kiến bàn giao ký kết với khách hàng",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_cn_ids = fields.One2many('bsd.hd_ban_cn', 'bsd_hd_ban_id', string="Chuyển nhượng hợp đồng",
                                 domain=[('state', '=', 'duyet')], readonly=True)
    bsd_duyet_bgdb = fields.Boolean(string="Duyệt BGĐB", help="Duyệt bàn giao đặc biệt", readonly=True)
    bsd_ngay_duyet_bgdb = fields.Datetime(string="Ngày duyệt BGĐB", help="Ngày duyệt bàn giao đặc biệt", readonly=True)
    bsd_nguoi_duyet_bgdb_id = fields.Many2one('res.users', string="Người duyệt BGĐB",
                                              help="Người duyệt bàn giao đặc biệt", readonly=True)

    bsd_tl_tt_hd = fields.Float(string="Tỷ lệ thanh toán HĐ", help="Tỷ lệ thanh toán hợp đồng", digits=(10, 1))
    bsd_tien_tt_hd = fields.Monetary(string="Tiền thanh toán HĐ", help="Tiền thanh toán hợp đồng")

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_ngay_dkbg = self.bsd_unit_id.bsd_ngay_dkbg

    # Tên hiện thị record
    def name_get(self):
        res = []
        for hd in self:
            res.append((hd.id, "%s" % hd.bsd_ten_sp))
        return res
    
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

    # DV.01.11 - Theo dõi chiết khấu mua sỉ (nút nhấn wizard)
    def action_ck_ms(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_ms_hdb_action').read()[0]
        return action

    # DV.01.11 - Theo dõi chiết khấu mua sỉ
    def tao_ck_ms(self, chiet_khau, tien=0, tl_ck=0):
        # Tạo dữ liệu trong bảng chiết khấu
        ps_ch_ms = self.bsd_ps_ck_ids.create({
            'bsd_loai_ck': 'mua_si',
            'bsd_chiet_khau_id': chiet_khau.id,
            'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
            'bsd_bao_gia_id': self.bsd_bao_gia_id.id,
            'bsd_hd_ban_id': self.id,
            'bsd_tien': tien,
            'bsd_tl_ck': tl_ck,
        })
        # Tính lại tiền các đợt chưa thanh toán
        dot_da_tt = self.bsd_ltt_ids.filtered(lambda x: x.bsd_thanh_toan in ['da_tt', 'dang_tt'])
        _logger.debug(dot_da_tt)
        tong_tien_phai_tt = self.bsd_tong_gia - self.bsd_tien_pbt - sum(dot_da_tt.mapped('bsd_tien_dot_tt'))
        _logger.debug(tong_tien_phai_tt)
        dot_phai_tt = self.bsd_ltt_ids\
            .filtered(lambda x: x.bsd_thanh_toan == 'chua_tt')\
            .sorted('bsd_stt')
        _logger.debug(dot_phai_tt)
        tl_con_tt = 0
        for dot in dot_phai_tt:
            tl_con_tt += dot.bsd_cs_tt_ct_id.bsd_tl_tt
        _logger.debug(tl_con_tt)
        so_dot_tt = len(dot_phai_tt)
        if so_dot_tt < 1:
            raise UserError("Không còn đợt chưa thanh toán")
        elif so_dot_tt == 1:
            dot_phai_tt.bsd_tien_dot_tt = tong_tien_phai_tt
        else:
            tien_da_chia_dot = 0
            for dot in dot_phai_tt:
                # kiểm tra đợt cuối
                if dot == dot_phai_tt[-1]:
                    dot.bsd_tien_dot_tt = tong_tien_phai_tt - tien_da_chia_dot
                    break
                # Tính tiền đợt thanh toán khác cuối
                tien_tt = (tong_tien_phai_tt * dot.bsd_cs_tt_ct_id.bsd_tl_tt) / tl_con_tt
                dot.bsd_tien_dot_tt = tien_tt - (tien_tt % 1000)
                tien_da_chia_dot += dot.bsd_tien_dot_tt
                _logger.debug(dot.bsd_tien_dot_tt)
        # Tạo dự liệu bảng phát sinh giao dịch chiết khấu
        self.env['bsd.ps_gd_ck'].create({
            'bsd_ma_ck': ps_ch_ms.bsd_ma_ck,
            'bsd_ten_ck': ps_ch_ms.bsd_ten_ck,
            'bsd_hd_ban_id': self.id,
            'bsd_unit_id': self.bsd_unit_id.id,
            'bsd_loai_ck': ps_ch_ms.bsd_loai_ck,
            'bsd_tl_ck': ps_ch_ms.bsd_tl_ck,
            'bsd_tien': ps_ch_ms.bsd_tien_ck,
            'bsd_tien_ck': ps_ch_ms.bsd_tien_ck,
        })

    # DV.01.12 - Ước tính chiết khấu thanh toán
    def action_uoc_tinh_ck(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_uoc_tinh_ck_tt_action').read()[0]
        return action

    # Cập nhật đồng sở hữu từ báo giá
    @api.onchange('bsd_dat_coc_id')
    def _onchange_dat_coc(self):
        for each in self:
            lines = [(5, 0, 0)]
            for line in each.bsd_dat_coc_id.bsd_bao_gia_id.bsd_dsh_ids:
                vals = {
                    'bsd_dong_sh_id': line.id,
                    'bsd_lan_td': 0
                }
                lines.append((0, 0, vals))
            each.bsd_dong_sh_ids = lines

    # DV.01.07 - Kiểm tra trùng mã đặt cọc
    @api.constrains('bsd_dat_coc_id')
    def _constrains_dat_coc(self):
        if len(self.env['bsd.hd_ban'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id)])) > 1:
            raise UserError("Phiếu đặt cọc đã được tạo hợp đồng. Xin vui lòng kiểm tra lại.")

    # DV.01.01 - Xác nhận hợp đồng
    def action_xac_nhan(self):
        self.write({
            'state': 'ht_dc',
        })
        self.tao_cong_no_dot_tt()
        self.tao_cong_no_phi()

    # DV.01.02 In hợp đồng
    def action_in_hd(self):
        return self.env.ref('bsd_dich_vu.bsd_hd_ban_report_action').read()[0]

    # DV.01.03 Upload hợp đồng
    def action_upload_hdb(self):
        self.write({
            'bsd_ngay_up_hdb': datetime.datetime.now(),
        })

    # DV.01.04 Ký hợp đồng
    def action_ky_hdb(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_hdb_action').read()[0]
        return action

    # DV.01.08 Theo dõi công nợ hợp đồng
    def tao_cong_no_dot_tt(self):
        for dot_tt in self.bsd_ltt_ids.sorted('bsd_stt'):
            if dot_tt.bsd_stt == 1:
                self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': dot_tt.bsd_ten_dtt,
                        'bsd_ngay': dot_tt.bsd_ngay_hh_tt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_ps_tang': dot_tt.bsd_tien_dot_tt - dot_tt.bsd_tien_dc,
                        'bsd_ps_giam': 0,
                        'bsd_loai_ct': 'dot_tt',
                        'bsd_phat_sinh': 'tang',
                        'bsd_hd_ban_id': self.id,
                        'bsd_dot_tt_id': dot_tt.id,
                        'state': 'da_gs',
                })
            else:
                self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': dot_tt.bsd_ten_dtt,
                        'bsd_ngay': dot_tt.bsd_ngay_hh_tt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_ps_tang': dot_tt.bsd_tien_dot_tt,
                        'bsd_ps_giam': 0,
                        'bsd_loai_ct': 'dot_tt',
                        'bsd_phat_sinh': 'tang',
                        'bsd_hd_ban_id': self.id,
                        'bsd_dot_tt_id': dot_tt.id,
                        'state': 'da_gs',
                })

    # DV.01.17 Ký thỏa thuận đặt cọc
    def action_ky_ttdc(self):
        _logger.debug("Ký thỏa thuận")
        action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_ttdc_action').read()[0]
        return action

    # DV.01.18 Theo dõi công nợ phí
    def tao_cong_no_phi(self):
        pql = self.bsd_ltt_ids\
                   .filtered(lambda x: x.bsd_tinh_pql)\
                   .bsd_child_ids.filtered(lambda r: r.bsd_loai == 'pql')
        if pql:
            self.env['bsd.cong_no'].create({
                    'bsd_chung_tu': pql[0].bsd_ten_dtt,
                    'bsd_ngay': pql[0].bsd_ngay_hh_tt,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_du_an_id': self.bsd_du_an_id.id,
                    'bsd_ps_tang': pql[0].bsd_tien_dot_tt,
                    'bsd_ps_giam': 0,
                    'bsd_loai_ct': 'pql',
                    'bsd_phat_sinh': 'tang',
                    'bsd_hd_ban_id': self.id,
                    'bsd_dot_tt_id': pql[0].id,
                    'state': 'da_gs',
            })
        pbt = self.bsd_ltt_ids\
                  .filtered(lambda x: x.bsd_tinh_pbt)\
                  .bsd_child_ids.filtered(lambda r: r.bsd_loai == 'pbt')
        if pbt:
            self.env['bsd.cong_no'].create({
                    'bsd_chung_tu': pbt[0].bsd_ten_dtt,
                    'bsd_ngay': pbt[0].bsd_ngay_hh_tt,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_du_an_id': self.bsd_du_an_id.id,
                    'bsd_ps_tang': pbt[0].bsd_tien_dot_tt,
                    'bsd_ps_giam': 0,
                    'bsd_loai_ct': 'pbt',
                    'bsd_phat_sinh': 'tang',
                    'bsd_hd_ban_id': self.id,
                    'bsd_dot_tt_id': pbt[0].id,
                    'state': 'da_gs',
            })

    # DV.01.14 - Duyệt hợp đồng đặc biệt
    def action_duyet_db(self):
        self.write({
            'bsd_duyet_db': True,
            'bsd_ngay_duyet_db': fields.Datetime.now(),
            'bsd_nguoi_duyet_db_id': self.env.uid,
        })

    # DV.01.20 - Duyệt bàn giao đặc biệt
    def action_duyet_bgdb(self):
        self.write({
            'bsd_duyet_bgdb': True,
            'bsd_ngay_duyet_bgdb': fields.Datetime.now(),
            'bsd_nguoi_duyet_bgdb_id': self.env.uid,
        })

    # DV.01.24 Xử lý TTĐC quá hạn ký
    def auto_tao_ds_td_ttdc(self):
        self.env['bsd.ds_td'].create({
            'bsd_ten': 'Gia hạn ký TTĐC ' + self.bsd_ma_hd_ban,
            'bsd_loai_td': 'vp_tg',
            'bsd_loai_yc': 'gia_han',
            'bsd_loai_dt': 'ttdc',
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_unit_id': self.bsd_unit_id.id,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_hd_ban_id': self.id,
            'bsd_ngay_hh': self.bsd_ngay_hh_ttdc,
            'bsd_tien_da_tt': self.bsd_tien_tt_hd,
        })

    # DV.01.25 Xử lý Hợp đồng quá hạn ký
    def auto_tao_ds_td_hd(self):
        self.env['bsd.ds_td'].create({
            'bsd_ten': 'Gia hạn ký hợp đồng ' + self.bsd_ma_hd_ban,
            'bsd_loai_td': 'vp_tg',
            'bsd_loai_yc': 'gia_han',
            'bsd_loai_dt': 'hd_ban',
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_unit_id': self.bsd_unit_id.id,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_hd_ban_id': self.id,
            'bsd_ngay_hh': self.bsd_ngay_hh_khdb,
            'bsd_tien_da_tt': self.bsd_tien_tt_hd,
        })

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_dat_coc_id' in vals:
            dat_coc = self.env['bsd.dat_coc'].browse(vals['bsd_dat_coc_id'])
            sequence = dat_coc.bsd_du_an_id.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã hợp đồng'))
        vals['bsd_ma_hd_ban'] = sequence.next_by_id()
        res = super(BsdHopDongMuaBan, self).create(vals)
        ids_bg = res.bsd_dat_coc_id.bsd_bg_ids.ids
        ids_ltt = res.bsd_dat_coc_id.bsd_ltt_ids.ids
        ids_km = res.bsd_dat_coc_id.bsd_km_ids.ids
        ids_ck = res.bsd_dat_coc_id.bsd_ps_ck_ids.ids
        ids_db = res.bsd_dat_coc_id.bsd_ck_db_ids.ids
        ids_pbt = res.bsd_dat_coc_id.bsd_dot_pbt_ids.ids
        ids_pql = res.bsd_dat_coc_id.bsd_dot_pql_ids.ids
        res.write({
            'bsd_bg_ids': [(6, 0, ids_bg)],
            'bsd_ltt_ids': [(6, 0, ids_ltt)],
            'bsd_km_ids': [(6, 0, ids_km)],
            'bsd_ps_ck_ids': [(6, 0, ids_ck)],
            'bsd_ck_db_ids': [(6, 0, ids_db)],
            'bsd_dot_pbt_ids': [(6, 0, ids_pbt)],
            'bsd_dot_pql_ids': [(6, 0, ids_pql)],
        })
        # Cập nhật đồng sở hữu từ đặt cọc
        ids_dsh = res.bsd_dat_coc_id.bsd_dsh_ids
        for dsh in ids_dsh:
            self.env['bsd.dong_so_huu'].create({
                'bsd_hd_ban_id': res.id,
                'bsd_dong_sh_id': dsh.id,
                'bsd_lan_td': 0
            })
        return res


class BsdBanGiao(models.Model):
    _inherit = 'bsd.ban_giao'

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", help="Hợp đồng mua bán", readonly=True)


class BsdBaoGiaLTT(models.Model):
    _inherit = 'bsd.lich_thanh_toan'
    _rec_name = "bsd_ma_ht"

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", help="Hợp đồng mua bán", readonly=True)
    bsd_ma_ht = fields.Char(string="Mã tầng", help="Mã tầng", compute='_compute_ma_ht', store=True)

    @api.depends('bsd_hd_ban_id.bsd_ma_hd_ban', 'bsd_ten_dtt')
    def _compute_ma_ht(self):
        for each in self:
            if each.bsd_hd_ban_id:
                each.bsd_ma_ht = '{ten_dtt}-{ma_hd}'.format(ten_dtt=each.bsd_ten_dtt,
                                                            ma_hd=each.bsd_hd_ban_id.bsd_ma_hd_ban)
            else:
                each.bsd_ma_ht = each.bsd_ten_dtt

    def name_get(self):
        res = []
        for dot_tt in self:
            res.append((dot_tt.id, "%s" % dot_tt.bsd_ten_dtt))
        return res


class BsdKhuyenMai(models.Model):
    _inherit = 'bsd.bao_gia_km'

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", help="Hợp đồng mua bán", readonly=True)


class BsdPsCk(models.Model):
    _inherit = 'bsd.ps_ck'

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", help="Hợp đồng mua bán", readonly=True)


class BsdCkDb(models.Model):
    _inherit = 'bsd.ck_db'

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", help="Hợp đồng mua bán", readonly=True)


class BsdDongSoHuu(models.Model):
    _name = 'bsd.dong_so_huu'
    _description = 'Người đồng sở hữu'
    _rec_name = 'bsd_dong_sh_id'

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", help="Hợp đồng mua bán", readonly=True)
    bsd_dong_sh_id = fields.Many2one('res.partner', string="Đồng sở hữu", help="Người đồng sở hữu", required=True)
    bsd_mobile = fields.Char(related='bsd_dong_sh_id.mobile', string="Di động")
    bsd_email = fields.Char(related='bsd_dong_sh_id.email', string="Email")
    bsd_pl_dsh_id = fields.Many2one('bsd.pl_dsh', string="Phụ lục HĐ", help="Phụ lục hợp đồng thay đổi chủ sở hữu",
                                    readonly=True)
    bsd_hd_ban_cn_id = fields.Many2one('bsd.hd_ban_cn', string="Chuyển nhượng", help="Chuyển nhượng hợp đồng",
                                       readonly=True)
    bsd_lan_td = fields.Integer(string="Lần thay đổi", help="Lần thay đổi chủ sở hữu", readonly=True)
    state = fields.Selection([('active', 'Đang hiệu lực'), ('inactive', 'Hết hiệu lực')], default='active',
                             string="Trạng thái", required=True, readonly=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsd_hd_ban_ids = fields.One2many('bsd.hd_ban', 'bsd_khach_hang_id', string="Danh sách hợp đồng",
                                     domain=[('state', '!=', 'nhap')])

    bsd_sl_hd_ban = fields.Integer(string="# Hợp đồng", compute="_compute_sl_hd", store=True)

    @api.depends('bsd_hd_ban_ids', 'bsd_hd_ban_ids.state')
    def _compute_sl_hd(self):
        for each in self:
            each.bsd_sl_hd_ban = len(each.bsd_hd_ban_ids)

    def action_view_hd_ban(self):
        action = self.env.ref('bsd_dich_vu.bsd_hd_ban_action').read()[0]

        hd_ban = self.env['bsd.hd_ban'].search([('bsd_khach_hang_id', '=', self.id)])
        if len(hd_ban) > 1:
            action['domain'] = [('id', 'in', hd_ban.ids)]
        elif hd_ban:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_hd_ban_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = hd_ban.id
        # Prepare the context.
        context = {
            'default_bsd_khach_hang_id': self.id,
        }
        action['context'] = context
        return action