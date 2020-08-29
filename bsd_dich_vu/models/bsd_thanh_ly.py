# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdThanhLy(models.Model):
    _name = 'bsd.thanh_ly'
    _description = "Thanh lý chấm dứt hợp đồng"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã thanh lý", required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã thanh lý đã tồn tại !')
    ]
    bsd_ngay_tao = fields.Datetime(string="Ngày", help="Ngày tạo thanh lý",
                                   required=True, default=lambda self: fields.Datetime.now(),
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ten = fields.Char(string="Tiêu đề", required=True, help="Tiêu đề",
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_loai_dt = fields.Selection([('dat_coc', 'Đặt cọc'),
                                    ('dc_cb', 'Đặt cọc - Chuẩn bị HĐ'),
                                    ('tt_dc', 'Thỏa thuận đặt cọc'),
                                    ('hd_ban', 'Hợp đồng mua bán')], string="Đối tượng", required=True,
                                   help="Đối tượng", default='dat_coc',
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai_tl = fields.Selection([('thuong', 'Thường'), ('dat_biet', 'Đặt biệt')], string="Loại thanh lý",
                                   help="""Loại thanh lý:\n
                                        - Thường: Không được duyệt giảm tỷ lệ phạt hoặc hoàn tiền. \n
                                        - Đặc biệt: Được xét duyệt giảm tỷ lệ phạt hoặc hoàn tiền. \n""",
                                   required=True, default='thuong',
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ds_td_id = fields.Many2one('bsd.ds_td', string="Danh sách theo dõi", help="Danh sách theo dõi", required=True)
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
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
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
    bsd_mo_bl = fields.Boolean(string="Mở bán lại", help="Đánh dấu sản phẩm được mở bán lại?",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Đợt mở bán",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tl_phat = fields.Float(string="Tỷ lệ phạt", help="Tỷ lệ phần trăm mà khách hàng bị phạt",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_tien_phat = fields.Monetary(string="Tiền phạt", help="Số tiền khách hàng bị phạt do vi phạm hợp đồng",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tien_hoan = fields.Monetary(string="Số tiền hoàn", help="Số tiền khách hàng được hoàn lại")
    bsd_tt_ht = fields.Selection([('chua_ht', 'Chưa hoàn tiền'),
                                  ('dang_ht', 'Đang hoàn tiền'),
                                  ('da_ht', 'Đã hoàn tiền')], string="Tình trạng", help="Tình trạng hoàn tiền")
    bsd_ngay_in = fields.Datetime(string="Ngày in biên bản", help="Ngày in biên bản", readonly=True)
    bsd_ngay_ky = fields.Datetime(string="Ngày ký biên bản", help="Ngày ký biên bản", readonly=True)
    bsd_ngay_th = fields.Datetime(string="Ngày thu hồi", help="Ngày thu hồi biên bản", readonly=True)
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

    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('da_ky', 'Đã ký'),
                              ('da_tl', 'Đã thanh lý'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_ds_td_id')
    def _onchange_ds_td(self):
        self.bsd_du_an_id = self.bsd_ds_td_id.bsd_du_an_id
        self.bsd_dat_coc_id = self.bsd_ds_td_id.bsd_dat_coc_id
        self.bsd_unit_id = self.bsd_ds_td_id.bsd_unit_id
        self.bsd_khach_hang_id = self.bsd_ds_td_id.bsd_khach_hang_id
        self.bsd_tien_dc = self.bsd_ds_td_id.bsd_tien_dc
        # self.bsd_ngay_hh = self.bsd_ds_td_id.bsd_ngay_hh
        self.bsd_hd_ban_id = self.bsd_ds_td_id.bsd_hd_ban_id
        self.bsd_tong_gt_hd = self.bsd_ds_td_id.bsd_tong_gt_hd
        self.bsd_loai_dt = self.bsd_ds_td_id.bsd_loai_dt

    @api.depends('bsd_loai_dt', 'bsd_hd_ban_id', 'bsd_dat_coc_id')
    def _compute_tt(self):
        if self.bsd_loai_dt in ['dat_coc']:
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

    # DV.13.01 Xác nhận thanh lý
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    # DV.13.02 In biên bản thanh lý
    def action_in(self):
        return self.env.ref('bsd_dich_vu.bsd_thanh_ly_report_action').read()[0]

    # DV.13.03 Ký biên bản thanh lý
    def action_ky(self):
        return self.env.ref('bsd_dich_vu.bsd_wizard_ky_thanh_ly_action').read()[0]

    # DV.13.04 Hoàn tiền thanh lý
    def action_hoan_tien(self):
        if self.bsd_loai_dt == 'dat_coc':
            self.bsd_dat_coc_id.write({
                'state': 'da_tl',
            })
        else:
            self.bsd_hd_ban_id.write({
                'state': 'thanh_ly',
            })
        self.write({
            'state': 'da_tl',
        })
        # gọi hàm xử lý hoàn tiền đặt cọc
        if self.bsd_loai_dt == 'dat_coc':
            self._xu_ly_dat_coc()

    # DV.13.05 Mở bán lại
    def _mo_ban_lai(self):
        pass

    # DV.13.06 Hủy thanh lý
    def action_huy(self):
        pass

    # DV.13.07 Xử lý hoàn tiền đặt cọc
    def _xu_ly_dat_coc(self):
        # Tạo record bảng điều chỉnh giảm
        giam_no = self.env['bsd.giam_no'].create({
            'bsd_loai_dc': 'tl_dc',
            'bsd_dien_giai': 'Thanh lý đặt cọc ' + self.bsd_dat_coc_id.bsd_ma_dat_coc,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_tien': self.bsd_tien_dc,
            'state': 'nhap'
        })
        giam_no.action_xac_nhan()
        giam_no.action_vao_so()
        # Tạo record phát sinh tăng từ chứng từ thanh lý
        self.env['bsd.cong_no'].create({
            'bsd_chung_tu': self.bsd_ma,
            'bsd_ngay': fields.Datetime.now(),
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_ps_tang': self.bsd_tien_phat,
            'bsd_loai_ct': 'tl_dc',
            'bsd_thanh_ly_id': self.id,
        })
        # Tạo record trong bảng công nợ chứng từ
        self.env['bsd.cong_no_ct'].create({
            'bsd_ngay_pb': fields.Datetime.now(),
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_thanh_ly_id': self.id,
            'bsd_giam_no_id': giam_no.id,
            'bsd_tien_pb': self.bsd_tien_phat,
            'bsd_loai': 'giam_tl',
            'state': 'hoan_thanh',
        })
        if self.bsd_dat_coc_id.bsd_thanh_toan == 'dang_tt':
            self.env['bsd.cong_no_ct'].create({
                'bsd_ngay_pb': fields.Datetime.now(),
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
                'bsd_giam_no_id': giam_no.id,
                'bsd_tien_pb': self.bsd_tien_dc - self.bsd_tien_phat - self.bsd_tien_hoan,
                'bsd_loai': 'giam_dc',
                'state': 'hoan_thanh',
            })

        # Tạo record hoàn tiền từ thanh lý
        hoan_tien = self.env['bsd.hoan_tien'].create({
                        'bsd_ngay_ct': fields.Datetime.now(),
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_loai': 'tl_dc',
                        'bsd_giam_no_id': giam_no.id,
                        'bsd_tien': self.bsd_tien_hoan,
                        'bsd_dien_giai': 'Hoàn tiền cho ' + self.bsd_ma + ' cho ' + self.bsd_dat_coc_id.bsd_ma_dat_coc,
                        'state': 'nhap',
                })
        hoan_tien.action_xac_nhan()
    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã thanh lý'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdThanhLy, self).create(vals)
