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
    bsd_loai_td = fields.Selection([('vp_tg', 'Vi phạm thời gian'),
                                    ('yc_kh', 'Yêu cầu khách hàng'),
                                    ('vp_tt', 'Vi phạm thanh toán')], string="Loại theo dõi",
                                   required=True, help="Loại theo dõi", default="yc_kh")
    bsd_loai_yc = fields.Selection([('gia_han', 'Gia hạn'),
                                    ('thanh_ly', 'Thanh lý'),
                                    ('tt_td', 'Tiếp tục theo dõi')], string="Loại yêu cầu",
                                   required=True, help="Loại yêu cầu", default='thanh_ly')
    bsd_loai_dt = fields.Selection([('dat_coc', 'Đặt cọc'),
                                    ('dc_cb', 'Đặt cọc - Chuẩn bị HĐ'),
                                    ('tt_dc', 'Thỏa thuận đặt cọc'),
                                    ('hd_ban', 'Hợp đồng mua bán')], string="Đối tượng", required=True,
                                   help="Đối tượng", default='dat_coc')
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng")
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm")
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng")
    bsd_ngay_hh = fields.Datetime(string="ngày hết hạn",
                                  help="""Ngày hết hạn:\n 
                                        - Nếu đối tượng là đặt cọc: Hạn ký đặt cọc \n
                                        - Nếu đối tượng là thỏa thuận đặt cọc: Hạn ký thỏa thuận đặt cọc\n
                                        - Nếu đối tượng là hơp đồng mua bán: Hạn ký hợp đồng""")
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc")
    bsd_tong_gt_hd = fields.Monetary(string="Tổng giá trị HĐ", help="Tổng giá trị thanh toán theo Hợp đồng")
    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Số tiền khách hàng đã thanh toán")
    bsd_ngay_gh = fields.Date(string="Ngày gia hạn", help="Ngày gia hạn mới cho đặt cọc/ Thỏa thuận đặt cọc/ Hợp đồng")
    bsd_gui_thu = fields.Boolean(string="Gửi thư thanh lý", help="Gửi thư thanh lý")
    bsd_ky_bb = fields.Boolean(string="Ký BB thanh lý", help="Ký biên bản thanh lý")
    bsd_mo_bl = fields.Boolean(string="Mở bán lại", help="Đánh dấu sản phẩm được mở bán lại?")
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Đợt mở bán")
    bsd_tl_phat = fields.Float(string="Tỷ lệ phạt", help="Tỷ lệ phần trăm mà khách hàng bị phạt")
    bsd_tien_phat = fields.Monetary(string="Tiền phạt", help="Số tiền khách hàng bị phạt do vi phạm hợp đồng")
    bsd_quyet_dinh = fields.Char(string="Quyết định", help="Quyết định xử lý cho Danh sách theo dõi")
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('hoan_thanh', 'Hoàn thành'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng", help="Diện tích xây dựng")
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế")
    bsd_thue_id = fields.Many2one('bsd.thue_suat', string="Mã thuế", help="Mã thuế")
    bsd_qsdd_m2 = fields.Float(string="QSDĐ/ m2", help="Giá trị quyền sử dụng đất trên m2")
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất")
    bsd_tl_pbt = fields.Float(string="Tỷ lệ phí bảo trì", help="Tỷ lệ phí bảo trì")
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="CS thanh toán", help="Chính sách thanh toán")
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán")
    bsd_tien_ck = fields.Monetary(string="Tiền chiết khấu", help="Tổng tiền chiết khấu")
    bsd_tien_bg = fields.Monetary(string="Tiền bàn giao", help="Tổng tiền bàn giao")
    bsd_gia_truoc_thue = fields.Monetary(string="Giá bán trước thuế",
                                         help="Giá bán trước thuế: bằng giá bán cộng tiền bàn giao trừ tiền chiết khấu")
    bsd_tien_qsdd = fields.Monetary(string="Giá trị QSDĐ",
                                    help="Giá trị quyền sử dụng đất: bằng QSDĐ/m2 nhân với diện tích sử dụng")
    bsd_tien_thue = fields.Monetary(string="Tiền thuế",
                                    help="Tiền thuế: bằng giá bán trước thuế trừ giá trị QSDĐ/m2 nhân với thuế suất")
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="Phí bảo trì: bằng % phí bảo trì nhân giá bán")
    bsd_tong_gia = fields.Monetary(string="Tổng giá bán",
                                   help="Tổng giá bán: bằng giá bán trước thuế cộng tiền thuế cộng phí bảo trì")

    bsd_ma_dat_coc = fields.Char(related='bsd_dat_coc_id.bsd_ma_dat_coc')
    bsd_ngay_dat_coc = fields.Datetime(related='bsd_dat_coc_id.bsd_ngay_dat_coc')
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
    bsd_ngay_hd_ban = fields.Datetime(related='bsd_hd_ban_id.bsd_ngay_hd_ban')
    bsd_kh_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_khach_hang_id')
    bsd_bao_gia_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_bao_gia_id')
    bsd_dat_coc_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_dat_coc_id')
    bsd_du_an_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_du_an_id')
    bsd_dot_mb_id = fields.Many2one(related='bsd_hd_ban_id.bsd_dot_mb_id')
    bsd_bang_gia_hd_id = fields.Many2one(related='bsd_hd_ban_id.bsd_bang_gia_id')
    state_hd = fields.Selection(related='bsd_hd_ban_id.state')

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã danh sách theo dõi'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdDanhSachTheoDoi, self).create(vals)