# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdBaoGiaLTT(models.Model):
    _name = 'bsd.lich_thanh_toan'
    _description = "Lịch thanh toán cho báo giá"

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Bảng tính giá", help="Bảng tính giá", required=True)
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="'Đặt cọc", help="Phiếu đặt cọc", readonly=True)
    bsd_stt = fields.Integer(string='Số thứ tự', help="Số thứ tự đợt thanh toán")
    bsd_ma_dtt = fields.Char(string="Mã đợt thanh toán", help="Mã đợt thanh toán", required=True)
    bsd_ten_dtt = fields.Char(string="Tên đợt thanh toán", help="Tên đợt thanh toán", required=True)
    bsd_ngay_hh_tt = fields.Date(string="Hạn thanh toán", help="Thời hạn thanh toán của đợt thanh toán")
    bsd_tien_dot_tt = fields.Monetary(string="Tiền", help="Tiền thanh toán của đợt thanh toán",
                                      required=True)
    bsd_tien_thanh_toan = fields.Monetary(string="Đã thanh toán", help="Tổng tiền đã thanh toán")
    bsd_tien_con_lai = fields.Monetary(string="Phải thanh toán", help="Số tiền còn phải thanh toán",
                                       compute='_compute_tien_con_lai')
    bsd_ngay_tt = fields.Date(string="Ngày thanh toán", help="Lần thanh toán gần nhất")
    bsd_tinh_pql = fields.Boolean(string="Phí quản lý", help="Tính phí quản lý vào đợt thanh toán hay không")
    bsd_tinh_pbt = fields.Boolean(string="Phí bảo trì", help="Tính phí bảo trì vào đợt thanh toán hay không")
    bsd_ngay_ah = fields.Date(string="Ngày ân hạn", help="Ngày ân hạn thanh toán")
    bsd_tinh_phat = fields.Selection([('htt', 'Hạn thanh toán'), ('nah', 'Ngày ân hạn')], string="Tính phạt",
                                     required=True, default="htt")
    bsd_lai_phat = fields.Float(string="Lãi phạt(%/ngày)", help="Tỷ lệ đóng lãi phạt theo ngày", required=True)
    bsd_tien_td = fields.Monetary(string="Tiền phạt tối đa", help="Tiền phạt chậm thanh toán tối đa", required=True)
    bsd_tl_td = fields.Float(string="Tỷ lệ phạt tối đa", help="Tỷ lệ tối đa phạt chậm thanh toán", required=True)
    bsd_phat_thd = fields.Float(string="Phạt trước hợp đồng", required=True,
                                help="""Phần trăm phí phạt (theo giá trị hợp đồng) trong 
                                        trường hợp chấm dứt giao dịch trước khi ký hợp đồng""")
    bsd_phat_shd = fields.Float(string="Phạt sau hợp đồng", required=True,
                                help="""Phần trăm phí phạt (theo giá trị hợp đồng) trong trường hợp chấm dứt 
                                        giao dịch sau khi ký hợp đồng""")
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán", required=True)
    bsd_cs_tt_ct_id = fields.Many2one('bsd.cs_tt_ct', string="CSTT chi tiết", required=True,
                                      help="Đợt thanh toán theo chính sách thanh toán")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.depends('bsd_tien_dot_tt', 'bsd_tien_thanh_toan')
    def _compute_tien_con_lai(self):
        for each in self:
            each.bsd_tien_con_lai = each.bsd_tien_dot_tt - each.bsd_tien_thanh_toan

    @api.model
    def create(self, vals):
        rec = super(BsdBaoGiaLTT, self).create(vals)
        tien_dot_tt = rec.bsd_tien_dot_tt
        if rec.bsd_tinh_pql:
            tien_dot_tt += rec.bsd_bao_gia_id.bsd_thang_pql * rec.bsd_bao_gia_id.bsd_tien_pql
        if rec.bsd_tinh_pbt:
            tien_dot_tt += rec.bsd_bao_gia_id.bsd_tien_pbt
        rec.write({
            'bsd_tien_dot_tt': tien_dot_tt,
        })
        return rec