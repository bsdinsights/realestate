# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdPmgTtc(models.Model):
    _name = 'bsd.pmg_ttc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Bảng phí môi giới"

    bsd_ma_phi_mg = fields.Char(string="Mã", help="Mã phí môi giới", required=True)
    bsd_ten_phi_mg = fields.Char(string="Tên", help="Tên phí môi giới", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string='Dự án', help="Tên dự án", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_ap_dung = fields.Selection([('ctv', 'Cộng tác viên'),
                                    ('dvlt', 'Đơn vị liên kết'),
                                    ('khgt', 'Khách hàng giới thiệu')], string="Áp dụng", default="ctv",
                                   help="Đối tượng áp dụng", required=True)
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng phí môi giới", required=True)
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng phí môi giới", required=True)

    bsd_dieu_kien = fields.Selection([('1', 'Số lượng'), ('2', 'Tiền')], string="Điều kiện", required=True,
                                      help="Loại điều kiện tính phí môi giới", default="1")
    bsd_muc = fields.Selection([('1', 'Mức 1'),
                                ('2', 'Mức 2'),
                                ('3', 'Mức 3'),
                                ('4', 'Mức 4'),
                                ('5', 'Mức 5')], string="Mức", help="Mức phí", default='1')
    bsd_sl_tu = fields.Integer(string="Số lượng từ", help="Số lượng căn hộ được bán thấp nhất")
    bsd_sl_den = fields.Integer(string="Số lượng đến", help="Số lượng căn hộ được bán cao nhất")

    bsd_tien_tu = fields.Monetary(string="Số tiền từ", help="Số tiền căn hộ được bán thấp nhất")
    bsd_tien_den = fields.Monetary(string="Số tiền đến", help="Số tiền căn hộ được bán cao nhất")

    bsd_cach_tinh = fields.Selection([('ty_le', 'Phần trăm'), ('tien', 'Tiền')],
                                     string="Cách tính", help="Cách trả phí hoa môi giới", default='ty_le',
                                     required=True)
    bsd_ty_le = fields.Float(string="Tỷ lệ (%)", help="Tỷ lệ được sử dụng để tính phí mô giới")
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền phí môi giới")
    state = fields.Selection([('active', "Đang sử dụng"),
                              ('inactive', "Không sử dụng")], string='Trạng thái', default='active')

    bsd_ctv_ids = fields.One2many('bsd.pmg_ctv', 'bsd_pmg_ttc_id', string="Công tác viên")
    bsd_cty_ids = fields.One2many('bsd.pmg_cty', 'bsd_pmg_ttc_id', string="Đơn vị")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)


class BsdPmgCtv(models.Model):
    _name = "bsd.pmg_ctv"
    _description = "Phí môi giới công tác viên"

    bsd_kh_cn_id = fields.Many2one('res.partner', string="Tên", help="Tên công tác viên", required=True,
                                   domain=[('company_type', '=', 'person')])
    bsd_email = fields.Char(related='bsd_kh_cn_id.email')
    bsd_mobile = fields.Char(related='bsd_kh_cn_id.mobile')
    bsd_pmg_ttc_id = fields.Many2one('bsd.pmg_ttc', string="Bảng phí môi giới")


class BsdPmgCty(models.Model):
    _name = "bsd.pmg_cty"
    _description = "Phí môi giới công ty"

    bsd_kh_ct_id = fields.Many2one('res.partner', string="Tên", help="Tên công ty", required=True,
                                   domain=[('company_type', '=', 'company')])
    bsd_email = fields.Char(related='bsd_kh_ct_id.email')
    bsd_mobile = fields.Char(related='bsd_kh_ct_id.mobile')
    bsd_pmg_ttc_id = fields.Many2one('bsd.pmg_ttc', string="Bảng phí môi giới")