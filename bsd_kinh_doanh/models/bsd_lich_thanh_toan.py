# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdBaoGiaLTT(models.Model):
    _name = 'bsd.lich_thanh_toan'
    _description = "Lịch thanh toán cho báo giá"
    _rec_name = 'bsd_ten_dtt'

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá", help="Bảng tính giá")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Phiếu đặt cọc", readonly=True)
    bsd_stt = fields.Integer(string='Số thứ tự', help="Số thứ tự đợt thanh toán", readonly=True)
    bsd_ma_dtt = fields.Char(string="Mã đợt TT", help="Mã đợt thanh toán", required=True, readonly=True)
    bsd_ten_dtt = fields.Char(string="Tên đợt TT", help="Tên đợt thanh toán", required=True)
    bsd_ngay_hh_tt = fields.Date(string="Hạn thanh toán", help="Thời hạn thanh toán của đợt thanh toán")
    bsd_tien_dot_tt = fields.Monetary(string="Số tiền", help="Tiền thanh toán của đợt thanh toán",
                                      required=True)
    bsd_tl_tt = fields.Float(string="Tỷ lệ TT", help="Tỷ lệ thanh toán hợp đồng mua bán",
                             related='bsd_cs_tt_ct_id.bsd_tl_tt', store=True)
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc", readonly=True)
    bsd_thanh_toan = fields.Selection([('chua_tt', 'Chưa thanh toán'),
                                       ('dang_tt', 'Đang thanh toán'),
                                       ('da_tt', 'Đã thanh toán')], string="Thanh toán", default="chua_tt",
                                      required=True)
    bsd_ngay_tt = fields.Datetime(string="Ngày thanh toán", help="Lần thanh toán gần nhất")
    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán")
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán")
    bsd_tinh_pql = fields.Boolean(string="Phí quản lý", help="Tính phí quản lý vào đợt thanh toán hay không")
    bsd_tinh_pbt = fields.Boolean(string="Phí bảo trì", help="Tính phí bảo trì vào đợt thanh toán hay không")
    bsd_ngay_ah = fields.Date(string="Ngày ân hạn", help="Ngày ân hạn thanh toán")
    bsd_tinh_phat = fields.Selection([('htt', 'Hạn thanh toán'), ('nah', 'Ngày ân hạn')], string="Tính phạt",
                                     default="htt")
    bsd_lai_phat = fields.Float(string="Lãi phạt", help="Tỷ lệ đóng lãi phạt theo năm")
    bsd_tien_td = fields.Monetary(string="Tiền phạt tối đa", help="Tiền phạt chậm thanh toán tối đa")
    bsd_tl_td = fields.Float(string="Tỷ lệ phạt tối đa", help="Tỷ lệ tối đa phạt chậm thanh toán")
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán", required=True)
    bsd_cs_tt_ct_id = fields.Many2one('bsd.cs_tt_ct', string="CSTT chi tiết", required=True,
                                      help="Đợt thanh toán theo chính sách thanh toán")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_dot_ky_hd = fields.Boolean(string="Đợt ký hợp đồng", help="Đánh dấu đợt thanh toán là đợt ký hợp đồng")
    bsd_parent_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", readonly=True)
    bsd_child_ids = fields.One2many('bsd.lich_thanh_toan', 'bsd_parent_id', string="Phí", readonly=True)
    bsd_loai = fields.Selection([('dtt', 'Đợt thanh toán'),
                                 ('pql', 'Phí quản lý'),
                                 ('pbt', 'Phí bảo trì')], string="Loại", help="Phân loại", readonly=True)

    # Thông báo thanh toán nhắc nợ
    bsd_tb_tt = fields.Boolean(string="TB thanh toán", readonly=True,
                               help="Số ngày (trước khi đến hạn thanh toán) để gửi thông tin thanh toán")
    bsd_ngay_tb_tt = fields.Date(string="Ngày TB thanh toán", readonly=True)
    bsd_canh_bao1 = fields.Boolean(string="Thông báo nhắc nợ 1", readonly=True,
                                   help="Đánh dấu đã tạo thông báo")
    bsd_canh_bao2 = fields.Boolean(string="Thông báo nhắc nợ 2", readonly=True,
                                   help="Đánh dấu đã tạo thông báo")
    bsd_canh_bao3 = fields.Boolean(string="Thông báo nhắc nợ 3", readonly=True,
                                   help="Đánh dấu đã tạo thông báo")
    bsd_canh_bao4 = fields.Boolean(string="Thông báo nhắc nợ 4", readonly=True,
                                   help="Đánh dấu đã tạo thông báo")
    bsd_canh_bao5 = fields.Boolean(string="Thông báo nhắc nợ 5", readonly=True,
                                   help="Đánh dấu đã tạo thông báo")

    bsd_ngay_cb1 = fields.Date(string="Ngày TBNN 1", readonly=True, help="Ngày tạo thông báo nhắc nợ")
    bsd_ngay_cb2 = fields.Date(string="Ngày TBNN 2", readonly=True, help="Ngày tạo thông báo nhắc nợ")
    bsd_ngay_cb3 = fields.Date(string="Ngày TBNN 3", readonly=True, help="Ngày tạo thông báo nhắc nợ")
    bsd_ngay_cb4 = fields.Date(string="Ngày TBNN 4", readonly=True, help="Ngày tạo thông báo nhắc nợ")
    bsd_ngay_cb5 = fields.Date(string="Ngày TBNN 5", readonly=True, help="Ngày tạo thông báo nhắc nợ")