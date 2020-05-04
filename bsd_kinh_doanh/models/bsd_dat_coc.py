# -*- coding:utf-8 -*-

from odoo import models, fields, api
import datetime


class BsdDatCoc(models.Model):
    _name = 'bsd.dat_coc'
    _description = "Phiếu đặt cọc"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_dat_coc'

    bsd_ma_dat_coc = fields.Char(string="Mã đặt cọc", help="Mã đặt cọc", required=True)
    _sql_constraints = [
        ('bsd_ma_dat_coc_unique', 'unique (bsd_ma_dat_coc)',
         'Mã đặt cọc đã tồn tại !'),
    ]
    bsd_ngay_dat_coc = fields.Datetime(string="Ngày", help="Ngày đặt cọc", required=True,
                                       default=lambda self: fields.Datetime.now())
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True)
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", help="Tên báo giá", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', related="bsd_bao_gia_id.bsd_giu_cho_id")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án",
                                   related="bsd_bao_gia_id.bsd_du_an_id", store=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Tên đợt mở bán",
                                    related="bsd_bao_gia_id.bsd_dot_mb_id", store=True)
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá", help="Bảng giá bán",
                                      related="bsd_bao_gia_id.bsd_bang_gia_id", store=True)
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ",
                                  related="bsd_bao_gia_id.bsd_tien_gc", store=True)
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc",
                                  related="bsd_bao_gia_id.bsd_tien_dc",store=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Tên căn hộ",
                                  related="bsd_bao_gia_id.bsd_unit_id", store=True)
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng", help="Diện tích tim tường",
                             related="bsd_bao_gia_id.bsd_dt_xd", store=True)
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế",
                             related="bsd_bao_gia_id.bsd_dt_sd", store=True)
    bsd_thue_id = fields.Many2one('account.tax', string="Mã thuế", help="Mã thuế",
                                  related="bsd_bao_gia_id.bsd_thue_id", store=True)
    bsd_qsdd_m2 = fields.Monetary(string="QSDĐ/ m2", help="Giá trị quyền sử dụng đất trên m2",
                                  related="bsd_bao_gia_id.bsd_qsdd_m2", store=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", related="bsd_bao_gia_id.bsd_thue_suat", store=True)
    bsd_tl_pbt = fields.Float(string="% phí bảo trì", help="Tỷ lệ phí bảo trì",
                              related="bsd_bao_gia_id.bsd_tl_pbt", store=True)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán",
                                   related="bsd_bao_gia_id.bsd_cs_tt_id", store=True)
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán", related="bsd_bao_gia_id.bsd_gia_ban", store=True)
    bsd_tien_ck = fields.Monetary(string="Chiết khấu", help="Tổng tiền chiết khấu",
                                  related="bsd_bao_gia_id.bsd_tien_ck", store=True)
    bsd_tien_bg = fields.Monetary(string="Tiền bàn giao", help="Tổng tiền bàn giao",
                                  related="bsd_bao_gia_id.bsd_tien_bg", store=True)
    bsd_gia_truoc_thue = fields.Monetary(string="Giá bán trước thuế",
                                         help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ chiết khấu""",
                                         related="bsd_bao_gia_id.bsd_gia_truoc_thue", store=True)
    bsd_tien_qsdd = fields.Monetary(string="Giá trị QSDĐ",
                                    help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""",
                                    related="bsd_bao_gia_id.bsd_tien_qsdd", store=True)
    bsd_tien_thue = fields.Monetary(string="Tiền thuế",
                                    help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""",
                                    related="bsd_bao_gia_id.bsd_tien_thue", store=True)
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán",
                                   related="bsd_bao_gia_id.bsd_tien_pbt", store=True)
    bsd_tong_gia = fields.Monetary(string="Tổng giá bán",
                                   help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""",
                                   related="bsd_bao_gia_id.bsd_tong_gia", store=True)
    bsd_thang_pql = fields.Integer(string="Số tháng đóng phí quản lý",related="bsd_bao_gia_id.bsd_thang_pql", store=True,
                                   help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức")
    bsd_tien_pql = fields.Monetary(string="Phí quản lý/ tháng", help="Số tiền phí quản lý cần đóng mỗi tháng",
                                   related="bsd_bao_gia_id.bsd_tien_pql", store=True)

    state = fields.Selection([('nhap', 'Nháp'), ('dat_coc', 'Đặt cọc'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", help="Trạng thái", tracing=1, required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_bg_ids = fields.One2many('bsd.ban_giao', 'bsd_dat_coc_id', string="Bàn giao", readonly=True)
    bsd_ltt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_dat_coc_id', string="Lịch thanh toán", readonly=True)

    bsd_co_hdc = fields.Boolean(string="Hợp đồng cọc", help="Thông tin quy định có làm hợp đồng cọc hay không",
                                related="bsd_du_an_id.bsd_hd_coc", store=True)
    bsd_so_hdc = fields.Char(string="Số hợp đồng", help="Số hợp đồng đặt cọc")

    bsd_ngay_in_dc = fields.Datetime(string="Ngày in", help="Ngày in phiếu cọc, hợp đồng cọc", readonly=True)
    bsd_ngay_hh_kdc = fields.Datetime(string="Hết hạn ký cọc", help="Ngày hết hạn ký phiếu cọc, hợp đồng cọc",
                                      readonly=True)
    bsd_ngay_up_dc = fields.Datetime(string="Upload đặt cọc", readonly=True,
                                     help="""Ngày tải lên hệ thống phiếu đặt cọc, hợp đồng cọc đã được khách hàng 
                                             ký xác nhận""")
    bsd_ngay_ky_dc = fields.Datetime(string="Ngày ký đặt cọc", help="Ngày ký đặt cọc", readonly=True)

    bsd_thanh_toan = fields.Selection([('chua_tt', 'Chưa thanh toán'),
                                       ('dang_tt', 'Đang thanh toán'),
                                       ('da_tt', 'Đã thanh toán')], string="Thanh toán", default="chua_tt",
                                      help="Thanh toán",
                                      required=True)
    bsd_ngay_tt = fields.Datetime(string="Ngày thanh toán", help="Ngày (kế toán xác nhận) thanh toán giữ chỗ")

    @api.model
    def create(self, vals):
        res = super(BsdDatCoc, self).create(vals)
        ids_bg = res.bsd_bao_gia_id.bsd_bg_ids.ids
        ids_ltt = res.bsd_bao_gia_id.bsd_ltt_ids.ids
        res.write({
            'bsd_bg_ids': [(6, 0, ids_bg)],
            'bsd_ltt_ids': [(6, 0, ids_ltt)]
        })
        return res

    # KD.10.06 Theo dõi công nợ đặt cọc
    def _tao_rec_cong_no(self):
        self.env['bsd.cong_no'].create({
            'bsd_chung_tu': self.bsd_ma_dat_coc,
            'bsd_ngay': self.bsd_ngay_dat_coc,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_tien': self.bsd_tien_dc,
            'bsd_tien_thanh_toan': 0,
            'bsd_loai_ct': 'dat_coc',
            'bsd_phat_sinh': 'tang',
            'bsd_dat_coc_id': self.id,
            'bsd_phan_bo': 'chua_pb',
            'state': 'da_gs',
        })

    # KD.10.01 Xác nhận đặt cọc
    def action_xac_nhan(self):
        self.write({
            'state': 'dat_coc',
        })
        self._tao_rec_cong_no()

    # KD.10.02 In đặt cọc
    def action_in_dc(self):
        return self.env.ref('bsd_kinh_doanh.bsd_dat_coc_report_action').read()[0]

    # KD.10.03 Upload đặt cọc
    def action_upload_dc(self):
        self.write({
            'bsd_ngay_up_dc': datetime.datetime.now(),
        })

    # Tạo công nợ đợt thạnh toán khi ký phiếu cọc
    def tao_cong_no_dot_tt(self):
        for dot_tt in self.bsd_ltt_ids.filtered(lambda d: d.bsd_gd_tt == 'dat_coc').sorted('bsd_stt'):
            if dot_tt.bsd_stt == 1:
                self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': dot_tt.bsd_ma_dtt,
                        'bsd_ngay': dot_tt.bsd_ngay_hh_tt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_tien': dot_tt.bsd_tien_dot_tt,
                        'bsd_tien_thanh_toan': self.bsd_tien_dc,
                        'bsd_loai_ct': 'dot_tt',
                        'bsd_phat_sinh': 'tang',
                        'bsd_dot_tt_id': dot_tt.id,
                        'bsd_phan_bo': 'chua_pb',
                        'state': 'da_gs',
                })
            else:
                self.env['bsd.cong_no'].create({
                        'bsd_chung_tu': dot_tt.bsd_ma_dtt,
                        'bsd_ngay': dot_tt.bsd_ngay_hh_tt,
                        'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'bsd_du_an_id': self.bsd_du_an_id.id,
                        'bsd_tien': dot_tt.bsd_tien_dot_tt,
                        'bsd_tien_thanh_toan': 0,
                        'bsd_loai_ct': 'dot_tt',
                        'bsd_phat_sinh': 'tang',
                        'bsd_dot_tt_id': dot_tt.id,
                        'bsd_phan_bo': 'chua_pb',
                        'state': 'da_gs',
                })

    # KD.10.04 Ký đặt cọc
    def action_ky_dc(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_ky_dc_action').read()[0]
        return action

    # KD.10.05 Hủy đặt cọc
    def action_huy(self):
        pass
