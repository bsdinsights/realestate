# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdThongBaoNghiemThu(models.Model):
    _name = 'bsd.tb_nt'
    _description = "Thông báo nghiệm thu"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_tb'

    bsd_ma_tb = fields.Char(string="Mã", help="Mã thông báo nghiệm thu", required=True, readonly=True,
                            copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_tb_unique', 'unique (bsd_ma_tb)',
         'Mã thông báo đã tồn tại !')
    ]
    bsd_ngay_tao_tb = fields.Datetime(string="Ngày", help="Ngày tạo thông báo nghiệm thu",
                                      required=True, default=lambda self: fields.Datetime.now(),
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_doi_tuong = fields.Char(string="Đối tượng", help="Đối tượng được tạo thông báo", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tao_td = fields.Boolean(string="Được tạo tự động", help="Đánh dấu thông báo được tạo tự động từ hệ thông",
                                readonly=True)
    bsd_cn_dkbg_unit_id = fields.Many2one('bsd.cn_dkbg_unit', string="Cập nhật DKBG chi tiết",
                                          help="Mã cập nhật DKBG chi tiết",
                                          readonly=True,
                                          states={'nhap': [('readonly', False)]})
    bsd_ngay_nt = fields.Date(string="Ngày nghiệm thu", help="Ngày nghiệm thu",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_ngay_tb = fields.Date(string="Ngày thông báo", help="Ngày thông báo nghiệm thu",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_ngay_ut = fields.Date(string="Ngày ước tính", help="Ngày ước tính",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_in = fields.Datetime(string="Ngày in", help="Ngày in thông báo nghiệm thu", readonly=True)
    bsd_nguoi_in_id = fields.Many2one("res.users", string="Người in", help="Người in thông báo nghiệm thu",
                                      readonly=True)
    bsd_ngay_gui = fields.Datetime(string="Ngày gửi", help="Ngày gửi nghiệm thu", readonly=True)
    bsd_ngay_dong = fields.Datetime(string="Ngày đóng", help="Ngày đóng nghiệm thu", readonly=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án")
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng")
    bsd_tien_ng = fields.Monetary(string="Nợ gốc",
                                  help="Tổng số tiền đợt thanh toán mà khách hàng chưa thanh toán và "
                                       "không bao gồm đợt thanh toán cuối")
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì cần phải thu của khách hàng")
    bsd_tien_pql = fields.Monetary(string="Phí quản lý", help="Phí quản lý cần phải thu của khách hàng")
    bsd_thang_pql = fields.Integer(string="Số tháng đóng PQL", related='bsd_unit_id.bsd_thang_pql',
                                   help="Số tháng đóng phí quản lý được quy định trên sản phẩm")
    bsd_don_gia_pql = fields.Monetary(string="Đơn giá PQL", related='bsd_unit_id.bsd_don_gia_pql',
                                      help="Đơn giá phí quản lý được quy định trên sản phẩm")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('dong_nt', 'Đóng nghiệm thu'), ('het_han', 'Hết hạn'),
                              ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)

    # DV.21.01 Xác nhận thông báo nghiêm thu
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # DV.21.02 In thông báo nghiệm thu
    def action_in_tb(self):
        return self.env.ref('bsd_dich_vu.bsd_tb_nt_report_action').read()[0]

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã thông báo nghiệm thu'))
        vals['bsd_ma_tb'] = sequence.next_by_id()
        return super(BsdThongBaoNghiemThu, self).create(vals)