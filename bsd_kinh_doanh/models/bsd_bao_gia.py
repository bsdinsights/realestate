# -*- coding:utf-8 -*-

from odoo import models, fields, api


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
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán")
    bsd_tien_ck = fields.Monetary(string="Chiết khấu", help="Tổng tiền chiết khấu")
    bsd_tien_bg = fields.Monetary(string="Tiền bàn giao", help="Tổng tiền bàn giao")
    bsd_gia_truoc_thue = fields.Monetary(string="Giá bán trước thuế",
                                         help="""Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ chiết khấu""")
    bsd_tien_qsdd = fields.Monetary(string="Giá trị QSDĐ",
                                    help="""Giá trị sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dung""")
    bsd_tien_thue = fields.Monetary(string="Tiền thuế",
                                    help="""Tiền thuế: Giá bán trước thuế trừ giá trị QSDĐ, nhân với thuế suất""")
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân với giá bán")
    bsd_tong_gia = fields.Monetary(string="Tổng giá bán",
                                   help="""Tổng giá bán: bằng Giá bán trước thuế cộng Tiền thuế cộng phí bảo trì""")
    bsd_thang_pql = fields.Integer(string="Số tháng đóng phí quản lý",
                                   help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức")
    bsd_tien_pql = fields.Monetary(string="Phí quản lý/ tháng", help="Số tiền phí quản lý cần đóng mỗi tháng")
    state = fields.Selection([('nhap','Nháp')], string="Trạng thái", default="nhap", help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.depends('bsd_unit_id')
    def _compute_tien_dc(self):
        if self.bsd_unit_id.bsd_tien_dc != 0:
            self.bsd_tien_dc = self.bsd_unit_id.bsd_tien_dc
        else:
            self.bsd_tien_dc = self.bsd_unit_id.bsd_du_an_id.bsd_tien_dc

    @api.depends('bsd_unit_id')
    def _compute_tl_pbt(self):
        if self.bsd_unit_id.bsd_tien_dc != 0:
            self.bsd_tl_pbt = self.bsd_unit_id.bsd_tl_pbt
        else:
            self.bsd_tl_pbt = self.bsd_unit_id.bsd_du_an_id.bsd_tl_pbt
