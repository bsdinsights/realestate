# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdThongSoKyThuat(models.Model):
    _name = "bsd.thong_tin_ky_thuat"
    _rec_name = "bsd_ten"
    _description = "Bảng mô tả thông số kỹ thuật"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ten = fields.Char(string="Tên", required=True, help="Tên thông tin kỹ thuật sản phẩm")
    bsd_ma = fields.Char(string="Mã", required=True, help="Mã thông tin kỹ thuật sản phẩm")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_dien_giai_2 = fields.Char(string="Diễn giải 2", help="Diễn giải bằng tiếng Anh")
    bsd_loai_san_pham_id = fields.Many2one('bsd.loai_san_pham', string="Loại sản phẩm", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True)
    bsd_line_ids = fields.One2many('bsd.thong_tin_ky_thuat.line', 'bsd_thong_tin_ky_thuat_id', string="Bảng chi tiết")


class BsdThongTinKyThuatLine(models.Model):
    _name = 'bsd.thong_tin_ky_thuat.line'
    _description = "Bảng thông tin kỹ thuật chi tiết"
    _rec_name = "bsd_loai_phong"

    bsd_thong_tin_ky_thuat_id = fields.Many2one('bsd.thong_tin_ky_thuat', string="Thông tin kỹ thuật")
    bsd_loai_phong = fields.Char(string="Loại phòng", required=True)
    bsd_thiet_bi = fields.Char(string="Thiết bị", help="Các thành phần chi tiết của căn hộ")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_dac_ta = fields.Char(string="Đặc tả", help="Đặc tả kỹ thuật")
    bsd_nhan_hieu = fields.Char(string="Nhãn hiệu", help="Tên nhãn hiệu hoặc nhà cung cấp thiết bị")

    bsd_loai_phong_2 = fields.Char(string="Loại phòng 2")
    bsd_thiet_bi_2 = fields.Char(string="Thiết bị 2", help="Các thành phần chi tiết của căn hộ (tiếng nước ngoài)")
    bsd_dien_giai_2 = fields.Char(string="Diễn giải 2", help="Diễn giải (tiếng nước ngoài)")
    bsd_dac_ta_2 = fields.Char(string="Đặc tả 2", help="Đặc tả kỹ thuật (tiếng nước ngoài)")
    bsd_nhan_hieu_2 = fields.Char(string="Nhãn hiệu 2",
                                  help="Tên nhãn hiệu hoặc nhà cung cấp thiết bị (tiếng nước ngoài")
