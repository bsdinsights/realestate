# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsd_ten_cty_en = fields.Char(string="Tên công ty (en)", help="Tên công ty bằng tiếng anh")
    bsd_loai_cty_ids = fields.Many2many('bsd.loai_cong_ty',
                                        relation="bsd_loai_dn_rel",
                                        column1="bsd_dn_id",
                                        column2="bsd_loai_id",
                                        help="Loại công ty", string="Loại công ty")
    bsd_cty_me = fields.Char(string="Công ty mẹ")
    bsd_phan_loai = fields.Selection([('trong_nuoc', 'Trong nước'),
                                      ('ngoai_nuoc', 'Ngoài nước')], string="Phân loại")
    bsd_nguoi_dd_id = fields.Many2one('res.partner', string="Người đại diện", help="Người đại diện pháp luật")
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
    bsd_mt_gpkd = fields.Char(string="Mô tả (GP.ĐKKD)", help="Thêm thông tin về giấy phép kinh doanh")

    bsd_ngay_vat = fields.Date(string="Ngày cấp (VAT)", help="Ngày cấp mã số thuế")
    bsd_noi_vat = fields.Char(string="Nơi cấp (VAT)", help="Nơi cấp mã số thuế")
    bsd_ngay_tl = fields.Date(string="Ngày thành lập", help="Thông tin ngày thành lập công ty")
    bsd_nganh_nghe = fields.Many2many('bsd.cty_nganh_nghe', string="Ngành nghề",
                                      help="Ngành nghề hoạt động của công ty")

    bsd_mt_cty = fields.Char(string="Mô tả", help="Thông tin mô tả công ty")
    bsd_ma_sic = fields.Char(string="Mã SIC", help="Thông tin mã SIC của công ty")
    bsd_quyen_sh = fields.Selection([('chung', 'Chung (Nhà nước)'), ('rieng', 'Riêng (Tư nhân)'),
                                     ('cty_con', 'Công ty con'), ('khac', 'Khác')],
                                    string="Quyền sở hữu", help="Quyền sở hữu")
    bsd_dia_chi_ts = fields.Char(string="Địa chỉ trụ sở", help="Địa chỉ trụ sở",
                                 compute="_compute_dia_chi_ts", store=True)
    bsd_quoc_gia_ts_id = fields.Many2one('res.country', string="Quốc gia (TS)", help="Tên quốc gia đặt trụ sở công ty")
    bsd_tinh_ts_id = fields.Many2one('res.country.state', string="Tỉnh/ Thành (TS)",
                                     help="Tên tỉnh thành, thành phố đặt trụ sở công ty")
    bsd_quan_ts_id = fields.Many2one('bsd.quan_huyen', string="Quận/ Huyện (TS)",
                                     help="Tên quận huyện đặt trụ sở công ty")
    bsd_phuong_ts_id = fields.Many2one('bsd.phuong_xa', string="Phường/ Xã (TS)",
                                       help="Tên phường xã đặt trụ sở công ty")
    bsd_so_nha_ts = fields.Char(string="Số nhà (TS)", help="Số nhà, tên đường đặt trụ sở công ty")
    bsd_cung_ts = fields.Boolean(string="Đây là địa chỉ trụ sở", help="Đãy là địa chỉ trụ sợ")

    @api.onchange('bsd_cung_ts')
    def _onchange_ts(self):
        if self.bsd_cung_ts:
            self.bsd_quoc_gia_ts_id = self.bsd_quoc_gia_lh_id
            self.bsd_tinh_ts_id = self.bsd_tinh_lh_id
            self.bsd_quan_ts_id = self.bsd_quan_lh_id
            self.bsd_phuong_ts_id = self.bsd_phuong_lh_id
            self.bsd_so_nha_ts = self.bsd_so_nha_lh

    @api.depends('bsd_quoc_gia_ts_id', 'bsd_tinh_ts_id', 'bsd_quan_ts_id', 'bsd_phuong_ts_id', 'bsd_so_nha_ts')
    def _compute_dia_chi_ts(self):
        for each in self:
            each.bsd_dia_chi_ts = ''
            if each.bsd_so_nha_ts:
                each.bsd_dia_chi_ts += each.bsd_so_nha_ts + ', '
            if each.bsd_phuong_ts_id:
                each.bsd_dia_chi_ts += each.bsd_phuong_ts_id.bsd_ten + ', '
            if each.bsd_quan_ts_id:
                each.bsd_dia_chi_ts += each.bsd_quan_ts_id.bsd_ten + ', '
            if each.bsd_tinh_ts_id:
                each.bsd_dia_chi_ts += each.bsd_tinh_ts_id.name + ', '
            if each.bsd_quoc_gia_ts_id:
                each.bsd_dia_chi_ts += each.bsd_quoc_gia_ts_id.name

    @api.onchange('name')
    def _onchange_ma_da(self):
        res = {}
        self.env.cr.execute("""SELECT bsd_cn_id FROM bsd_loai_cn_rel 
                                WHERE bsd_loai_id = {0}
                            """.format(self.env.ref('bsd_kinh_doanh.bsd_dd_cty').id))
        list_cn = [cn[0] for cn in self.env.cr.fetchall()]
        res.update({
            'domain': {
                'bsd_nguoi_dd_id': [('id', 'in', list_cn)],
            }
        })
        return res


class BsdLoaiCty(models.Model):
    _name = 'bsd.loai_cong_ty'
    _rec_name = 'bsd_ten'

    bsd_ten = fields.Char(string="Loại công ty", required=True)


class BsdNganhNghe(models.Model):
    _name = 'bsd.cty_nganh_nghe'
    _rec_name = 'bsd_ten'

    bsd_ten = fields.Char(string="Ngành nghề", required=True)

