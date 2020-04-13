# -*- coding:utf-8 -*-

from odoo import models, fields, api
import datetime


class BsdHopDongMuaBan(models.Model):
    _name = 'bsd.hd_ban'
    _description = "Hợp đồng mua bán"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_hd_ban'

    bsd_ma_hd_ban = fields.Char(string="Mã", help="Mã hợp đồng mua bán", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_hd_ban_unique', 'unique (bsd_ma_hd_ban)',
         'Mã hợp đồng đã tồn tại !'),
    ]
    bsd_ngay_hd_ban = fields.Datetime(string="Ngày", help="Ngày làm hợp đồng mua bán", required=True,
                                      default=fields.Datetime.now(),
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
    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', related="bsd_dat_coc_id.bsd_bao_gia_id")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án",
                                   related="bsd_dat_coc_id.bsd_du_an_id", store=True)
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Tên đợt mở bán",
                                    related="bsd_dat_coc_id.bsd_dot_mb_id", store=True)
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá", help="Bảng giá bán",
                                      related="bsd_dat_coc_id.bsd_bang_gia_id", store=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", help="Tên căn hộ",
                                  related="bsd_dat_coc_id.bsd_unit_id", store=True)
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng", help="Diện tích tim tường",
                             related="bsd_dat_coc_id.bsd_dt_xd", store=True)
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế",
                             related="bsd_dat_coc_id.bsd_dt_sd", store=True)
    bsd_thue_id = fields.Many2one('account.tax', string="Mã thuế", help="Mã thuế",
                                  related="bsd_dat_coc_id.bsd_thue_id", store=True)
    bsd_qsdd_m2 = fields.Monetary(string="QSDĐ/ m2", help="Giá trị quyền sử dụng đất trên m2",
                                  related="bsd_dat_coc_id.bsd_qsdd_m2", store=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất", related="bsd_dat_coc_id.bsd_thue_suat", store=True)
    bsd_tl_pbt = fields.Float(string="% phí bảo trì", help="Tỷ lệ phí bảo trì",
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
    bsd_thang_pql = fields.Integer(string="Số tháng đóng phí quản lý",related="bsd_dat_coc_id.bsd_thang_pql", store=True,
                                   help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức")
    bsd_tien_pql = fields.Monetary(string="Phí quản lý/ tháng", help="Số tiền phí quản lý cần đóng mỗi tháng",
                                   related="bsd_dat_coc_id.bsd_tien_pql", store=True)

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('da_ky', 'Đã ký'), ('huy', 'Hủy')], string="Trạng thái", default="nhap", help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_bg_ids = fields.One2many('bsd.ban_giao', 'bsd_hd_ban_id', string="Bàn giao", readonly=True)
    bsd_ltt_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_hd_ban_id', string="Lịch thanh toán", readonly=True)
    bsd_dong_sh_ids = fields.One2many('bsd.dong_so_huu', 'bsd_hd_ban_id', string="Đồng sở hữu")

    bsd_ngay_in_hdb = fields.Datetime(string="Ngày in hợp đồng", help="Ngày in hợp đồng mua bán", readonly=True)
    bsd_ngay_hh_khdb = fields.Datetime(string="Hết hạn ký HĐ", help="Ngày hết hạn ký hợp đồng mua bán",
                                       readonly=True)
    bsd_ngay_up_hdb = fields.Datetime(string="Upload hợp đồng", readonly=True,
                                      help="""Ngày tải lên hệ thống hợp đồng bán đã được người mua
                                             ký xác nhận""")
    bsd_ngay_ky_hdb = fields.Datetime(string="Ngày ký hợp đồng", help="Ngày ký hợp đồng mua bán", readonly=True)

    # DV.01.01 - Xác nhận hợp đồng
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

    # KD.10.02 In đặt cọc
    def action_in_hd(self):
        self.write({
            'bsd_ngay_in_hdc': datetime.datetime.now(),
            'bsd_ngay_hh_khdb': datetime.datetime.now() + datetime.timedelta(days=self.bsd_du_an_id.bsd_hh_hd)
        })

    @api.model
    def create(self, vals):
        res = super(BsdHopDongMuaBan, self).create(vals)
        ids_bg = res.bsd_dat_coc_id.bsd_bg_ids.ids
        ids_ltt = res.bsd_dat_coc_id.bsd_ltt_ids.ids
        res.write({
            'bsd_bg_ids': [(6, 0, ids_bg)],
            'bsd_ltt_ids': [(6, 0, ids_ltt)]
        })
        return res


class BsdBanGiao(models.Model):
    _inherit = 'bsd.ban_giao'

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", help="Hợp đồng mua bán", readonly=True)


class BsdBaoGiaLTT(models.Model):
    _inherit = 'bsd.lich_thanh_toan'

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", help="Hợp đồng mua bán", readonly=True)


class BsdDongSoHuu(models.Model):
    _name = 'bsd.dong_so_huu'
    _description = 'Người đồng sở hữu'
    _rec_name = 'bsd_dong_sh_id'

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng mua bán", help="Hợp đồng mua bán", readonly=True)
    bsd_dong_sh_id = fields.Many2one('res.partner', string="Đồng sở hữu", help="Người đồng sở hữu", required=True)
    bsd_mobile = fields.Char(related='bsd_dong_sh_id.mobile')
    bsd_email = fields.Char(related='bsd_dong_sh_id.email')
