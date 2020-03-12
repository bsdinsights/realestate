# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bsd_so_thu_tu = fields.Char(string="Số thứ tự", help="Số căn hộ")
    bsd_ma_can_ho = fields.Char(string="Mã căn hộ",
                                help="Mã căn hộ bao gồm mã tòa nhà, mã tầng và số căn hộ")
    name = fields.Char(string="Mã hệ thống",
                       help="Mã đầy đủ của căn hộ bao gồm mã dự án, mã tòa nhà, mã tầng và số căn hộ")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True)
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng", required=True)
    bsd_tien_dat_coc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc của căn hộ")
    bsd_tien_giu_cho = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ của căn hộ")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Thông tin về căn hộ")
    bsd_dot_mo_ban = fields.Integer(string="Đợt mở bán", help="Đợt mở bán hiện tại của căn hộ", readonly=True)
    bsd_san_giao_dich = fields.Char(string="Sàn giao dịch", help="Sàn giao dịch đang bán(căn hộ) theo đợt mở bán",
                                    readony=True)
    bsd_bi_thanh_ly = fields.Selection([('0', 'Không'), ('1', 'Có')], string="Thanh lý", readonly=True,
                                       default="0",
                                       help="Thông tin căn hộ có từng bị thanh lý hợp đồng hay không")
    bsd_lan_thanh_ly = fields.Integer(string="Lần thanh lý",
                                      readonly=True,
                                      help="Số lần căn hộ bị thanh lý hợp đồng")
    bsd_phan_nhom_id = fields.Char(string="Phân nhóm", required=True,
                                help="Phân nhóm đặc tính kỹ thuật của căn hộ")
    bsd_huong = fields.Selection([('1', 'Đông'),
                                  ('2', 'Tây'),
                                  ('3', 'Nam'),
                                  ('4', 'Bắc'),
                                  ('5', 'Đông nam'),
                                  ('6', 'Đông bắc'),
                                  ('7', 'Tây nam'),
                                  ('8', 'Tây bắc')], string="Hướng")
    bsd_view = fields.Selection([('1', 'Phố'),
                                 ('2', 'Hồ bơi'),
                                 ('3', 'Công viên'),
                                 ('4', 'Mặt tiền'),
                                 ('5', 'Bãi biển/sông/hồ/núi'),
                                 ('6', 'Rừng'),
                                 ('7', 'Cao tốc'),
                                 ('8', 'Hồ'),
                                 ('9', 'Biển')], string="View", help="Góc nhìn của căn hộ")
    bsd_so_phong_ngu = fields.Integer(string="Số phòng ngủ", help="Số phòng ngủ của căn hộ")
    bsd_loai_bat_dong_san = fields.Selection([('1', 'Liền thổ(đất)'),
                                              ('2', 'Căn hộ'),
                                              ('3', 'Phức hợp'),
                                              ('4', 'Nghỉ dưỡng')],
                                             help="Loại hình sử dụng của căn hộ",
                                             string="Loại bất động sản")
    bsd_phan_loai = fields.Selection([('1', 'Condotel'),
                                      ('2', 'Apartment')], string="Phân loại")
    bsd_loai_can_ho = fields.Selection([('1', 'Căn hộ'),
                                        ('2', 'Căn hộ nhiều tầng'),
                                        ('3', 'Siêu thị/cửa hàng'),
                                        ('4', 'Penthouse')], string="Loại căn hộ")
    bsd_tien_coc = fields.Float(string="% Tiền cọc",
                                help="% thanh toán tối thiểu để ký thỏa thuận đặt cọc")
    bsd_dien_tich_chenh_lech = fields.Float(string="Diện tích chênh lệch (%)",
                                            help="% Chênh lệch giữa diện tích xây dựng và diện tích sử dụng")
    bsd_dien_tich_xay_dung = fields.Float(string="Diện tích xây dựng",
                                          help="Diện tích tim tường")
    bsd_dien_tich_su_dung = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế")
    bsd_dien_tich_thuc_te = fields.Float(string="Diện tích thực tế", help="Diện tích thông thủy thực tế")
    bsd_dien_tich_so_hong = fields.Float(string="Diện tích sổ hồng", help="Diện tích sổ hồng")
    bsd_don_gia_ban_m2 = fields.Monetary(string="Đơn giá bán/m2", help="Đơn giá bán trước thuế theo m2")
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán trước thuế của căn hộ")
    bsd_gia_tri_day_m2 = fields.Monetary(string="Giá trị đất/m2", help="Giá trị quyền sử dụng đất theo m2")
    bsd_tong_gtsd_dat = fields.Monetary(string="Tổng GTSD đất", help="""
                                                                    Tổng giá trị sử dụng đất của căn hộ được tính theo
                                                                    công thức: diện tích sử dụng(thông thủy) * giá trị
                                                                    đất/m2
                                                                    """,
                                        readonly=True)
    bsd_ty_le_phi_bao_tri = fields.Float(string="% phí bảo trì", help="Tỷ lệ phí bảo trì")
    bsd_phi_bao_tri = fields.Monetary(string="Phí bảo trì", help="""
                                                                Tổng tiền phí bảo trì được tính theo công thức:
                                                                % phí bảo trì * giá bán trước thuế
                                                                """,
                                      readonly=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="% thuế")
    bsd_tien_thue = fields.Monetary(string="Tiền thuế", help="""Tiền thuế của căn hộ được tính theo công thức:
                                                            (giá bán - tổng GTSD đất)* thuế suất""",
                                    readonly=True)
    bsd_tong_gia_ban = fields.Monetary(string="Tổng giá bán", help="""Tổng giá bán của căn hộ tính theo công thức:
                                                                        giá bán + tiền thuế + tiền phí bảo trì""",
                                       readonly=True)
    bsd_uu_tien = fields.Selection([('0', 'Không'),
                                    ('1', 'Có')], string="Ưu tiên", help="Ưu tiên bán của căn hộ",
                                   default='0', readonly=True)
    bsd_nguoi_duyet_uu_tien_id = fields.Many2one('res.users', string="Người duyệt ưu tiên",
                                              help="Người duyệt ưu tiên", readonly=True)
    bsd_ngay_duyet_uu_tien = fields.Date(string="Ngày duyệt ưu tiên", help="Ngày duyệt ưu tiên", readonly=True)
    bsd_lan_uu_tien = fields.Integer(string="Lần ưu tiên", help="Lần ưu tiên", readonly=True)
    bsd_ghi_chu_uu_tien = fields.Char(string="Ghi chú ưu tiên", help="Ghi chú ưu tiên", readonly=True)
    bsd_nguoi_huy_uu_tien_id = fields.Many2one('res.users', string="Người hủy ưu tiên", readonly=True)
    bsd_ngay_huy_uu_tien = fields.Date(string="Ngày hủy ưu tiên", readonly=True)
    bsd_tinh_trang_vay = fields.Selection([('0', 'Không'),
                                           ('1', 'Có')], string="Tình trạng", default='0',
                                          help="Tình trạng vay ngân hàng của căn hộ")
    bsd_ngay_du_kien_bao_giao = fields.Date(string="Ngày dự kiến bàn giao")
    bsd_so_thang_dong_phi_quan_ly = fields.Integer(string="Số tháng đóng phí quản lý")
    bsd_phi_quan_ly_m2_thang = fields.Monetary(string="Đơn giá phí quản lý/m2/tháng")
    bsd_dieu_kien_ban_giao = fields.Float(string="Điều kiện bàn giao",
                                          help="% thanh toán đủ điều kiện bàn giao(tối thiểu")
    bsd_ngay_ban_giao = fields.Date(string="Ngày bàn giao", help="Ngày bàn giao thực tế căn hộ cho khách hàng")
    bsd_ngay_cat_noc = fields.Date(string="Ngày cất nóc", help="Ngày chứng nhận cất nóc (bê tông tầng mái)")
    bsd_ngay_nhan_ho_so = fields.Date(string="Ngày nhận hồ sơ",
                                      help="Ngày chủ đầu tư nhận đầy đủ hồ sơ và gửi lên trên sở nhà đất để làm sổ hồng")
    bsd_trang_thai = fields.Selection([('chuan_bị', 'Chuẩn bị'),
                                       ('san_sang', 'Sẵn sàng'),
                                       ('dat_cho', 'Đặt chỗ'),
                                       ('giu_cho', 'Giữ chỗ'),
                                       ('dat_coc', 'Đặt cọc'),
                                       ('chuyen_coc', 'Chuyển cọc'),
                                       ('da_thu_coc', 'Đã thu cọc'),
                                       ('hoan_tat_dat_coc', 'Hoàn tất đặt cọc'),
                                       ('thanh_toan_dot_1', 'Thanh toán đợt 1'),
                                       ('ky_thoa_thuan_coc', 'Ký thỏa thuận cọc'),
                                       ('du_dieu_kien', 'Đủ điều kiện'),
                                       ('da_ban', 'Đã bán')
                                       ], string="Tình trạng", default="Chuẩn bị")






