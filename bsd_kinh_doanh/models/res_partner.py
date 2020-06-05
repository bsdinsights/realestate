# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsd_ho_tl = fields.Char(string="Họ và tên lót", help="Họ và tên lót")
    bsd_ten = fields.Char(string="Tên", help="Tên khách hàng")
    bsd_ma_kh = fields.Char(string="Mã khách hàng", required=True, index=True, copy=False, default='Tạo mới')
    bsd_ngay_sinh = fields.Date(string="Ngày sinh", help="Ngày sinh")
    bsd_gioi_tinh = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')], string="Giới tính", help="Giới tính", default='nam')
    email = fields.Char(string="Email")
    bsd_loai_kh = fields.Selection([('vn', 'Việt Nam'),
                                    ('nc', 'Người nước ngoài')], string="Quốc tịch",
                                   help="Khách hàng là công dân Việt Nam hay Người nước ngoài",
                                   required=True, default='vn')
    bsd_nguoi_bh = fields.Boolean(string="Người bảo hộ", help="Khách hàng có người bảo hộ")
    bsd_cmnd = fields.Char(string="CMND/ CCCD", help="Số CMND/ CCCD")
    bsd_ngay_cap_cmnd = fields.Date(string="Ngày cấp CMND", help="Ngày cấp CMND/ CCCD")
    bsd_noi_cap_cmnd = fields.Char(string="Nơi cấp CMND", help="Nơi cấp CMND/ CCCD")
    bsd_ho_chieu = fields.Char(string="Hộ chiếu", help="Số hộ chiếu")
    bsd_ngay_cap_hc = fields.Date(string="Ngày cấp hộ chiếu", help="Ngày cấp hộ chiếu")
    bsd_noi_cap_hc = fields.Char(string="Nơi cấp hộ chiếu", help="Nơi cấp hộ chiếu")
    bsd_mst = fields.Char(string="Mã số thuế", help="Mã số thuế khách hàng")
    bsd_dia_chi_tt = fields.Char(string="Địa chỉ thường chú", help="Địa chỉ thường chú",
                                 compute="_compute_dia_chi_tt", store=True)
    bsd_quoc_gia_tt_id = fields.Many2one('res.country', string="Quốc gia", help="Tên quốc gia")
    bsd_tinh_tt_id = fields.Many2one('res.country.state', string="Tỉnh/ Thành", help="Tên tỉnh thành, thành phố")
    bsd_quan_tt_id = fields.Many2one('bsd.quan_huyen', string="Quận/ Huyện", help="Tên quận huyện")
    bsd_phuong_tt_id = fields.Many2one('bsd.phuong_xa', string="Phường/ Xã", help="Tên phường xã")
    bsd_so_nha_tt = fields.Char(string="Số nhà", help="Số nhà, tên đường")
    bsd_dia_chi_lh = fields.Char(string="Địa chỉ liên hệ", help="Địa chỉ liên hệ",
                                 compute="_compute_dia_chi_lh", store=True)
    bsd_quoc_gia_lh_id = fields.Many2one('res.country', string="Quốc gia", help="Tên quốc gia")
    bsd_tinh_lh_id = fields.Many2one('res.country.state', string="Tỉnh/ Thành", help="Tên tỉnh thành, thành phố")
    bsd_quan_lh_id = fields.Many2one('bsd.quan_huyen', string="Quận/ Huyện", help="Tên quận huyện")
    bsd_phuong_lh_id = fields.Many2one('bsd.phuong_xa', string="Phường/ Xã", help="Tên phường xã")
    bsd_so_nha_lh = fields.Char(string="Số nhà", help="Số nhà, tên đường")

    bsd_cung_dc = fields.Boolean(string="Đây là địa chỉ liên hệ", help="Đây là địa chỉ liên hệ")

    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1)
    # R.01 Ràng buộc số điện thoại là duy nhất
    _sql_constraints = [
        ('mobile_unique', 'unique (mobile)',
         'Số điện thoại đã tồn tại !'),
    ]

    # R.10 tên khách hàng
    @api.onchange('bsd_ho_tl', 'bsd_ten')
    def _onchange_ten(self):
        self.name = (self.bsd_ho_tl or "") + " " + (self.bsd_ten or "")

    # R.11 Load địa chỉ
    @api.onchange('bsd_cung_dc')
    def _onchange_dc(self):
        if self.bsd_cung_dc :
            self.bsd_quoc_gia_lh_id = self.bsd_quoc_gia_tt_id
            self.bsd_tinh_lh_id = self.bsd_tinh_tt_id
            self.bsd_quan_lh_id = self.bsd_quan_tt_id
            self.bsd_phuong_lh_id = self.bsd_phuong_tt_id
            self.bsd_so_nha_lh = self.bsd_so_nha_tt
        else:
            self.bsd_quoc_gia_lh_id = False
            self.bsd_tinh_lh_id = False
            self.bsd_quan_lh_id = False
            self.bsd_phuong_lh_id = False
            self.bsd_so_nha_lh = False

    # R.02 Tạo thông tin địa chỉ thường chú
    @api.depends('bsd_quoc_gia_tt_id', 'bsd_tinh_tt_id', 'bsd_quan_tt_id', 'bsd_phuong_tt_id', 'bsd_so_nha_tt')
    def _compute_dia_chi_tt(self):
        for each in self:
            each.bsd_dia_chi_tt = (each.bsd_so_nha_tt or ' ') + ', ' + (each.bsd_phuong_tt_id.bsd_ten or ' ') + ', ' + \
                                  (each.bsd_quan_tt_id.bsd_ten or ' ') + ', ' + (each.bsd_tinh_tt_id.name or ' ') + ', ' + \
                                  (each.bsd_quoc_gia_tt_id.name or ' ')

    # R.03 Tạo thông tin địa chỉ liên hệ
    @api.depends('bsd_quoc_gia_lh_id', 'bsd_tinh_lh_id', 'bsd_quan_lh_id', 'bsd_phuong_lh_id', 'bsd_so_nha_lh')
    def _compute_dia_chi_lh(self):
        for each in self:
            each.bsd_dia_chi_lh = (each.bsd_so_nha_lh or ' ') + ', ' + (each.bsd_phuong_lh_id.bsd_ten or ' ') + ', ' + \
                                  (each.bsd_quan_lh_id.bsd_ten or ' ') + ', ' + (each.bsd_tinh_lh_id.name or ' ') + ', ' + \
                                  (each.bsd_quoc_gia_lh_id.name or ' ')

    @api.model
    def create(self, vals):
        _logger.debug(vals)
        if vals.get('bsd_ma_kh', 'Tạo mới') == 'Tạo mới' and not vals.get('is_company'):
            vals['bsd_ma_kh'] = self.env['ir.sequence'].next_by_code('bsd.kh_cn') or '/'
        if vals.get('bsd_ma_kh', 'Tạo mới') == 'Tạo mới' and vals.get('is_company'):
            vals['bsd_ma_kh'] = self.env['ir.sequence'].next_by_code('bsd.kh_dn') or '/'
        return super(ResPartner, self).create(vals)

    def name_get(self):
        res = []
        for partner in self:
            res.append((partner.id, "[%s]%s" % (partner.bsd_ma_kh, partner.name)))
        return res
