# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BsdProject(models.Model):
    _name = "bsd.du_an"
    _rec_name = "bsd_ten"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Thông tin dự án"

    bsd_ten = fields.Char(string="Tên dự án", required=True, help="Tên dự án")
    bsd_ma = fields.Char(string="Mã dự án", required=True, help="Mã dự án")
    bsd_chu_dau_tu = fields.Many2one('res.partner', string="Chủ dự án", required=True, help="Tên chủ đầu tư của dự án")
    bsd_loai = fields.Selection([('sep', 'Seperate'),
                                 ('com', 'Complex'),
                                 ('res', 'Research')], string="Loại dự án", help="Loại hình dự án")
    bsd_loai_hinh_su_dung = fields.Selection([('con', 'Condo'),
                                              ('res', 'Căn hộ'),
                                              ('pen', 'Nhà phố')], string="Loại hình sử dụng", help="Loại hình sử dụng")
    bsd_giay_phep_dau_tu = fields.Char(string="Giấy phép đầu tư", help="Giấy phép đầu tư của dự án")
    bsd_ngay_cap_phep = fields.Date(string="Ngày cấp phép", help="Ngày cấp phép đầu tư của dự án")
    bsd_dia_chi = fields.Text(string="Địa chỉ", help="Địa chỉ của dự án")
    bsd_co_hd_coc = fields.Boolean(string="Có HĐ cọc?", help="Dự án có quy định làm hợp đồng cọc không?")
    bsd_ty_le_coc = fields.Float(string="Tỷ lệ đặt cọc", required=True,
                                 help="Tỷ lệ(%) tiền cần đặt cọc dựa trên giá trị căn hộ")
    bsd_ngay_du_kien_cat_noc = fields.Date(string="Ngày dự kiến cất nóc",
                                           help="""Thông tin ngày dự kiến cất nóc được sử dụng để xác định thời gian 
                                                   bắt đầu thu phí quản lý, bảo trì và thu tiền đợt cuối""")
    bsd_ngay_du_kien_ban_giao = fields.Date(string="Ngày dự kiến bàn giao", required=True,
                                            help="Ngày dự kiến bàn giao căn hộ cho khách hàng")
    bsd_ngay_hoan_tat_phap_ly = fields.Date(string="Ngày hoàn tất pháp lý",
                                            help="Ngày hoàn thành tất cả các thủ tục cho khách hàng")
    bsd_ngay_cnqsd_dat = fields.Date(string="Ngày chứng nhận quyền sử dụng đất",
                                     help="Ngày trên sổ đỏ hoặc ngày chứng nhân quyền thuê đất của chủ đầu tư")
    bsd_so_cho_giu_xe = fields.Integer(string="Số chỗ giữ xe")
    bsd_ngay_thuc_te_cat_noc = fields.Date(string="Ngày thực tế cất nóc",
                                           help="""Sau ngày thực tế cất nóc, chủ đầu tư có thể thu phí bảo trì,
                                                   phí quản lý và thu tiền đợt cuối của căn hộ""")
    bsd_ngay_cap_phep_ban = fields.Date(string="Ngày cấp phép bán",
                                        help="""Ngày Sở Xây Dựng chính thức cấp phép dự án đã đủ điều kiện mở bán""")
    bsd_dinh_dang_du_an = fields.Char(string="Định dạng dự án", required=True,
                                      help="Định dạng dự án được sử dụng để tự động tạo mã căn hộ")
    bsd_dinh_dang_khu = fields.Char(string="Định dạng tòa nhà", required=True,
                                    help="Định dạng khu, tòa nhà được sử dụng để tự động tạo mã căn hộ")
    bsd_dinh_dang_tang = fields.Char(string="Định dạng tầng", required=True,
                                     help="Định dạng tầng được sử dụng để tự động tạo mã căn hộ")
    bsd_gia_tri_su_dung_dat = fields.Monetary(string="Giá trị sử dụng đất", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_phi_bao_tri = fields.Float(string="Phí bảo trì (%)", required=True)
    bsd_so_thang_phi_quan_ly = fields.Integer(string="Số tháng đóng phí quản lý", required=True,
                                              help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức")
    bsd_phi_quan_ly = fields.Monetary(string="Tiền phí quản lý", required=True,
                                      help="Số tiền quản lý cần đóng mỗi tháng")
    bsd_tien_giu_cho = fields.Monetary(string="Tiền giữ chỗ", required=True,
                                       help="Tiền giữ chỗ khi mua căn hộ của dự án")
    bsd_tien_dat_coc = fields.Monetary(string="Tiền đặt cọc", required=True,
                                       help="Tiền đặt cọc khi mua căn hộ của dự án")
    bsd_int_hieu_luc_bao_gia = fields.Integer(string="Hiệu lực báo giá", required=True,
                                              help="Số ngày báo giá hết hiệu lực, được tính từ ngày tạo báo giá")
    bsd_int_het_han_ky_phieu_coc = fields.Integer(string="Hết hạn ký phiếu cọc", required=True,
                                                  help="Số ngày phiếu cọc hết hiệu lực ký, được tính từ ngày in phiếu cọc")
    bsd_int_het_han_ky_hop_dong = fields.Integer(string="Hết hạn ký hợp đồng", required=True,
                                                 help="Số ngày hợp đồng hết hiệu lực ky, được tính kể từ ngày in hợp đồng")
    bsd_int_canh_bao_sau_giu_cho = fields.Integer(string="Cảnh báo sau giữ chỗ",
                                                  help="Số ngày cảnh báo sau khi tạo giữ chỗ")
    bsd_int_canh_bao_sau_dat_coc = fields.Integer(string="Cảnh báo sau đặt cọc",
                                                  help="Số ngày cảnh báo sau khi tạo đặt cọc")
    bsd_time_quan_tam = fields.Float(string="Thời gian hiệu lực quan tâm (giờ)",
                                           help="Số giờ hiệu lực của phiếu quan tâm bất động sản")
    bsd_so_giu_cho_NVBH = fields.Integer(string="Số giữ chỗ NVBH", required=True,
                                         help="Số lượng căn hộ tối đa mà nhân viên bán hàng được phép giữ chỗ")
    bsd_so_giu_cho_can_ho = fields.Integer(string="Số giữ chỗ Căn hộ", required=True,
                                           help="Số lượng giữ chỗ tối đa cho mỗi căn hộ")
    bsd_so_giu_cho_theo_ngay = fields.Integer(string="Số giữ chỗ theo ngày",
                                              help="số lượng giữ chỗ tối đa trên 1 ngày")
    bsd_so_giu_cho_NVBH_can_ho_ngay = fields.Integer(string="Số giữ chỗ NVBH/căn hộ/ngày",
                                                     help="""Số lượng giữ chỗ tối đa mỗi nhân viên bán hàng được
                                                      phép giữ chỗ theo căn hộ""")
    bsd_huy_giu_cho_truoc_mo_ban = fields.Integer(string="Hủy giữ chỗ trước mở bán",
                                                      help="Hủy giữ chỗ trước khi căn hộ được mở bán", required=True)
    bsd_hour_huy_giu_cho_sau_mo_ban = fields.Float(string="Hủy giữ chỗ sau mở bán(giờ)",
                                                   help="Số giờ giữ chỗ sau khi căn hộ được mở bán", required=True)
    bsd_ty_le_hoa_hong_nvbh = fields.Float(string="NVBH (%)", required=True,
                                           help="Tỷ lệ (%) hoa hồng được hưởng của nhân viên bán hàng")
    bsd_hoa_hong_quan_ly = fields.Float(string="Quản lý", help="Tiền hoa hồng được hương của quản lý", required=True)
    bsd_hoa_hong_nvdv = fields.Float(string="Dịch vụ", required=True,
                                     help="Tiền hoa hồng được hương của nhân viên dịch vụ khách hàng")
    state = fields.Selection([('active', 'Đang sử dụng'),
                                       ('inactive', 'Ngưng sử dụng')],
                                      string="Trạng thái", default='active')

    @api.constrains('bsd_ty_le_coc')
    def _check_ty_le_coc(self):
        for record in self:
            if record.bsd_ty_le_coc > 100 or record.bsd_ty_le_coc < 0:
                raise ValidationError("Tỷ lệ đặt cọc nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_phi_bao_tri')
    def _check_bsd_phi_bao_tri(self):
        for record in self:
            if record.bsd_phi_bao_tri > 100 or record.bsd_phi_bao_tri < 0:
                raise ValidationError("Phí bảo trì nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_int_hieu_luc_bao_gia')
    def _check_bsd_int_hieu_luc_bao_gia(self):
        for record in self:
            if record.bsd_int_hieu_luc_bao_gia > 100 or record.bsd_int_hieu_luc_bao_gia < 0:
                raise ValidationError("Hiệu lực báo giá nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_int_het_han_ky_phieu_coc')
    def _check_bsd_int_het_han_ky_phieu_coc(self):
        for record in self:
            if record.bsd_int_het_han_ky_phieu_coc > 100 or record.bsd_int_het_han_ky_phieu_coc < 0:
                raise ValidationError("Phiếu cọc nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_int_het_han_ky_hop_dong')
    def _check_bsd_int_het_han_ky_hop_dong(self):
        for record in self:
            if record.bsd_int_het_han_ky_hop_dong > 100 or record.bsd_int_het_han_ky_hop_dong < 0:
                raise ValidationError("Hợp đồng nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_int_canh_bao_sau_giu_cho')
    def _check_bsd_int_canh_bao_sau_giu_cho(self):
        for record in self:
            if record.bsd_int_canh_bao_sau_giu_cho > 100 or record.bsd_int_canh_bao_sau_giu_cho < 0:
                raise ValidationError("Cảnh báo sau giữ chỗ nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_int_canh_bao_sau_dat_coc')
    def _check_bsd_int_canh_bao_sau_dat_coc(self):
        for record in self:
            if record.bsd_int_canh_bao_sau_dat_coc > 100 or record.bsd_int_canh_bao_sau_dat_coc < 0:
                raise ValidationError("Cảnh báo sau đặt cọc nằm trong khoảng 0 đến 100")