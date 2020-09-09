# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # bsd_loai_cty = fields.Selection([('kh', 'Khách hàng'),
    #                                  ('doi_tac', 'Đối tác'),
    #                                  ('san', 'Sàn - Đại lý'),
    #                                  ('chu_dt', 'Chủ đầu tư')],
    #                                 string="Loại công ty", help="Loại công ty", default='kh')
    bsd_loai_cty_ids = fields.Many2many('bsd.loai_cong_ty', help="Loại công ty", string="Loại công ty")
    bsd_cty_me = fields.Char(string="Công ty mẹ")
    bsd_phan_loai = fields.Selection([('trong_nuoc', 'Trong nước'),
                                      ('ngoai_nuoc', 'Ngoài nước')], string="Phân loại")
    bsd_nguoi_dd_id = fields.Many2one('res.partner', string="Người đại diện", help="Người đại diện pháp luật",
                                   required=True)
    bsd_nguoi_uq = fields.Selection([('khong', 'Không'), ('co', 'Có')],
                                    string="Người ủy quyền",
                                    help="Doanh nghiệp (Chủ đầu tư) – người đại diện hiện tại"
                                         " có phải là người ủy quyền không?", default='khong')
    bsd_phone_2 = fields.Char(string="Điện thoại khác", help="Số điện thoại khác của công ty")
    bsd_email_2 = fields.Char(string="Email 2", help="Thư điện tử thứ 2 của công ty")
    bsd_fax = fields.Char(string="Số Fax", help="Số Fax")
    bsd_so_gpkd = fields.Char(string="Số giấp phép ĐKKD", help="Mã số giấy phép đăng ký kinh doanh")
    bsd_ngay_gpkd = fields.Date(string="Ngày cấp", help="Ngày cấp giấy phép đăng ký kinh doanh")
    bsd_noi_gpkd = fields.Char(string="Nơi cấp", help="Nơi cấp giấy phép đăng ký kinh doanh")
    bsd_mt_gpkd = fields.Char(string="Mô tả(GP.ĐKKD)", help="Thêm thông tin về giấy phép kinh doanh")

    bsd_ngay_vat = fields.Date(string="Ngày cấp (VAT)", help="Ngày cấp mã số thuế")
    bsd_noi_vat = fields.Char(string="Nơi cấp (VAT)", help="Nơi cấp mã số thuế")
    bsd_ngay_tl = fields.Date(string="Ngày thành lập", help="Thông tin ngày thành lập công ty")
    bsd_nganh_nghe = fields.Many2many('bsd.cty_nganh_nghe', string="Ngành nghề",
                                      help="Ngành nghề hoạt động của công ty")

    bsd_mt_cty = fields.Char(string="Mô tả", help="Thông tin mô tả công ty")
    bsd_ma_sic = fields.Char(string="Mã SIC", help="Thông tin mã SIC của công ty")
    bsd_quyen_sh = fields.Selection([('chung', 'Chung (Nhà nước)'), ('rieng', 'Riêng (Tư nhân)'),
                                     ('cty_con', 'Công ty con'), ('khac', 'Khác')],
                                    string="Quyền sỏ hữu", help="Quyền sở hữu")


class BsdLoaiCty(models.Model):
    _name = 'bsd.loai_cong_ty'
    _rec_name = 'bsd_ten'

    bsd_ten = fields.Char(string="Loại công ty", required=True)


class BsdNganhNghe(models.Model):
    _name = 'bsd.cty_nganh_nghe'
    _rec_name = 'bsd_ten'

    bsd_ten = fields.Char(string="Ngành nghề", required=True)

