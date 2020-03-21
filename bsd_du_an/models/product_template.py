# -*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _rec_name = 'bsd_ten_unit'

    name = fields.Char(required=False)
    bsd_stt = fields.Char(string="Số thứ tự", help="Số căn hộ", required=True)
    bsd_ten_unit = fields.Char(string="Tên căn hộ", help="Têm căn hộ bao gồm mã tòa nhà, mã tầng và số căn hộ",
                               required=True)
    bsd_ma_unit = fields.Char(string="Mã căn hộ", required=True,
                              help="Mã đầy đủ của căn hộ bao gồm mã dữ án, mã tòa nhà, mã tầng và số căn hộ")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True)
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng", required=True)
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc của căn hộ", required=True)
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ của căn hộ")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Thông tin về căn hộ")
    bsd_dot_mb = fields.Integer(string="Đợt mở bán", help="Đợt mở bán hiện tại của căn hộ")
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch",
                                    help="Sàn giao dịch đang bán(căn hộ) theo đợt mở bán")
    bsd_thanh_ly = fields.Selection([('0', 'Không'), ('1', 'Có')], string="Thanh lý",
                                    default="0",
                                    help="Thông tin căn hộ có từng bị thanh lý hợp đồng hay không")
    bsd_lan_tl = fields.Integer(string="Lần thanh lý",
                                help="Số lần căn hộ bị thanh lý hợp đồng")
    bsd_loai_sp_id = fields.Many2one('bsd.loai_sp', string="Phân nhóm",
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
    bsd_so_pn = fields.Integer(string="Số phòng ngủ", help="Số phòng ngủ của căn hộ")
    bsd_loai_bds = fields.Selection([('1', 'Liền thổ(đất)'),
                                              ('2', 'Căn hộ'),
                                              ('3', 'Phức hợp'),
                                              ('4', 'Nghỉ dưỡng')],
                                             help="Loại hình sử dụng của căn hộ",
                                             string="Loại bất động sản")
    bsd_phan_loai = fields.Selection([('1', 'Condotel'),
                                      ('2', 'Apartment')], string="Phân loại")
    bsd_loai_unit = fields.Selection([('1', 'Căn hộ'),
                                        ('2', 'Căn hộ nhiều tầng'),
                                        ('3', 'Siêu thị/cửa hàng'),
                                        ('4', 'Penthouse')], string="Loại căn hộ")
    bsd_tl_tc = fields.Float(string="% Tiền cọc",
                             help="% thanh toán tối thiểu để ký thỏa thuận đặt cọc")
    bsd_dt_cl = fields.Float(string="Diện tích chênh lệch (%)",
                             help="% Chênh lệch giữa diện tích xây dựng và diện tích sử dụng")
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng",
                             help="Diện tích tim tường")
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế")
    bsd_dt_tt = fields.Float(string="Diện tích thực tế", help="Diện tích thông thủy thực tế")
    bsd_dt_sh = fields.Float(string="Diện tích sổ hồng", help="Diện tích sổ hồng")
    bsd_don_gia = fields.Monetary(string="Đơn giá bán/m2", help="Đơn giá bán trước thuế theo m2")
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán trước thuế của căn hộ")
    bsd_gt_dat = fields.Monetary(string="Giá trị đất/m2", help="Giá trị quyền sử dụng đất theo m2")
    bsd_tong_gtd = fields.Monetary(string="Tổng GTSD đất", help="""
                                                                    Tổng giá trị sử dụng đất của căn hộ được tính theo
                                                                    công thức: diện tích sử dụng(thông thủy) * giá trị
                                                                    đất/m2
                                                                    """,
                                   readonly=True, compute='_compute_bsd_tong_gtsd_dat', store=True)
    bsd_tl_bt = fields.Float(string="% phí bảo trì", help="Tỷ lệ phí bảo trì")
    bsd_phi_bt = fields.Monetary(string="Phí bảo trì", help="""
                                                                Tổng tiền phí bảo trì được tính theo công thức:
                                                                % phí bảo trì * giá bán trước thuế
                                                                """,
                                      readonly=True, compute='_compute_bsd_phi_bao_tri', store=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="% thuế")
    bsd_tien_thue = fields.Monetary(string="Tiền thuế", help="""Tiền thuế của căn hộ được tính theo công thức:
                                                            (giá bán - tổng GTSD đất)* thuế suất""",
                                    readonly=True, compute='_compute_tien_thue', store=True)
    bsd_tong_gb = fields.Monetary(string="Tổng giá bán", help="""Tổng giá bán của căn hộ tính theo công thức:
                                                                        giá bán + tiền thuế + tiền phí bảo trì""",
                                       readonly=True, compute='_compute_bsd_tong_gia_ban', store=True)
    bsd_uu_tien = fields.Selection([('0', 'Không'),
                                    ('1', 'Có')], string="Ưu tiên", help="Ưu tiên bán của căn hộ",
                                   default='0', readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt ưu tiên",
                                              help="Người duyệt ưu tiên", readonly=True)
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt ưu tiên", help="Ngày duyệt ưu tiên", readonly=True)
    bsd_lan_duyet = fields.Integer(string="Lần ưu tiên", help="Lần ưu tiên", readonly=True)
    bsd_ghi_chu = fields.Char(string="Ghi chú ưu tiên", help="Ghi chú ưu tiên", readonly=True)
    bsd_nguoi_huy_id = fields.Many2one('res.users', string="Người hủy ưu tiên", readonly=True)
    bsd_ngay_huy = fields.Datetime(string="Ngày hủy ưu tiên", readonly=True)
    bsd_tt_vay = fields.Selection([('0', 'Không'),
                                           ('1', 'Có')], string="Tình trạng vay", default='0',
                                          help="Tình trạng vay ngân hàng của căn hộ")
    bsd_ngay_dkbg = fields.Date(string="Dự kiến bàn giao")
    bsd_thang_ql = fields.Integer(string="Số tháng đóng phí quản lý")
    bsd_phi_ql = fields.Monetary(string="Phí quản lý/m2/tháng")
    bsd_dk_bg = fields.Float(string="Điều kiện bàn giao",
                             help="% thanh toán đủ điều kiện bàn giao(tối thiểu")
    bsd_ngay_bg = fields.Date(string="Ngày bàn giao", help="Ngày bàn giao thực tế căn hộ cho khách hàng")
    bsd_ngay_cn = fields.Date(string="Ngày cất nóc", help="Ngày chứng nhận cất nóc (bê tông tầng mái)")
    bsd_ngay_hs = fields.Date(string="Ngày nhận hồ sơ",
                                      help="Ngày chủ đầu tư nhận đầy đủ hồ sơ và gửi lên trên sở nhà đất để làm sổ hồng")
    state = fields.Selection([('chuan_bi', 'Chuẩn bị'),
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
                                       ], string="Tình trạng", default="chuan_bi")

    @api.depends('bsd_dt_sd', 'bsd_gt_dat')
    def _compute_bsd_tong_gtsd_dat(self):
        for each in self:
            each.bsd_tong_gtd = each.bsd_dt_sd * each.bsd_dt_sd

    @api.depends('bsd_tl_bt', 'bsd_gia_ban')
    def _compute_bsd_phi_bao_tri(self):
        for each in self:
            each.bsd_phi_bt = each.bsd_tl_bt * each.bsd_gia_ban

    @api.depends('bsd_gia_ban', 'bsd_tong_gtd', 'bsd_thue_suat')
    def _compute_tien_thue(self):
        for each in self:
            each.bsd_tien_thue = (each.bsd_gia_ban - each.bsd_tong_gtd) * each.bsd_thue_suat

    @api.depends('bsd_gia_ban', 'bsd_tien_thue', 'bsd_phi_bt')
    def _compute_bsd_tong_gia_ban(self):
        for each in self:
            each.bsd_tong_gia_ban = each.bsd_gia_ban + each.bsd_tien_thue + each.bsd_phi_bt

    def action_uu_tien(self):
        self.write({
            'bsd_uu_tien': '1',
            'bsd_nguoi_duyet_id': self.env.uid,
            'bsd_ngay_duyet': datetime.today(),
            'bsd_lan_duyet': self.bsd_lan_duyet + 1,
        })

    def action_huy_uu_tien(self):
        self.write({
            'bsd_uu_tien': '0',
            'bsd_nguoi_huy_id': self.env.uid,
            'bsd_ngay_huy': datetime.today(),
        })

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(ProductTemplate, self).create(vals_list)
        _logger.debug("tạo product")
        _logger.debug(templates)
        for template in templates:
            du_an = template.bsd_du_an_id
            _logger.debug(du_an)
            toa_nha = template.bsd_toa_nha_id
            _logger.debug(toa_nha)
            tang = template.bsd_tang_id
            _logger.debug(tang)
            if not template.bsd_ma_unit:
                template.write({
                    'bsd_ma_unit': du_an.bsd_ma_da + du_an.bsd_dd_da +
                            toa_nha.bsd_ma_tn + du_an.bsd_dd_khu + tang.bsd_ma_tang + du_an.bsd_dd_tang
                })
            if not template.bsd_ten_unit:
                template.write({
                    'bsd_ten_unit': toa_nha.bsd_ma_tn + du_an.bsd_dd_khu + tang.bsd_ma_tang + du_an.bsd_dd_tang
                })
        return templates
