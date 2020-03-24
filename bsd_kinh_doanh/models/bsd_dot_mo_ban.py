# -*- coding:utf-8

from odoo import models, fields, api


class BsdDotMoBan(models.Model):
    _name = 'bsd.dot_mb'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_dot_mb'
    _description = 'Thông tin đợt mở bán'

    bsd_ma_dot_mb = fields.Char(string="Mã đợt mở bán", required=True,
                                readonly=True,
                                states={'cph': [('readonly', False)]})
    bsd_ten_dot_mb = fields.Char(string="Tên đợt mở bán", required=True,
                                 readonly=True,
                                 states={'cph': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án",
                                   readonly=True,
                                   states={'cph': [('readonly', False)]})
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá",
                                      readonly=True,
                                      states={'cph': [('readonly', False)]})
    bsd_ck_ch_id = fields.Many2one('bsd.ck_ch', string="CK chung",
                                   readonly=True,
                                   states={'cph': [('readonly', False)]})
    bsd_ck_nb_id = fields.Many2one('bsd.ck_nb', string="CK nội bộ",
                                   readonly=True,
                                   states={'cph': [('readonly', False)]})
    bsd_ck_ms_id = fields.Many2one('bsd.ck_ms', string="CK mua sỉ",
                                   readonly=True,
                                   states={'cph': [('readonly', False)]})
    bsd_ck_ttth_id = fields.Many2one('bsd.ck_ttth', string="CK TT trước hạn",
                                     readonly=True,
                                     states={'cph': [('readonly', False)]})
    bsd_ck_ttn_id = fields.Many2one('bsd.ck_ttn', string="CK TT nhanh",
                                    readonly=True,
                                    states={'cph': [('readonly', False)]})
    bsd_ck_cstt_id = fields.Many2one('bsd.ck_cstt', string="CK chính sách TT",
                                     readonly=True,
                                     states={'cph': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng của đợt mở bán",
                                readonly=True,
                                states={'cph': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng của đợt mở bán",
                               readonly=True,
                               states={'cph': [('readonly', False)]})
    bsd_ngay_ph = fields.Date(string="Ngày phát hành", help="Ngày duyệt phát hành đợt mở bán",
                              readonly=True,
                              states={'cph': [('readonly', False)]})
    bsd_nguoi_ph = fields.Many2one('res.users', string="Người phát hành",
                                   help="Người duyệt phát hành đợt mở bán",
                                   readonly=True,
                                   states={'cph': [('readonly', False)]})
    bsd_tu_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Từ tòa nhà",
                                        readonly=True,
                                        states={'cph': [('readonly', False)]})
    bsd_tu_tang_id = fields.Many2one('bsd.tang', string="Từ tầng",
                                     readonly=True,
                                     states={'cph': [('readonly', False)]})
    bsd_den_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Đến tòa nhà",
                                         readonly=True,
                                         states={'cph': [('readonly', False)]})
    bsd_den_tang_id = fields.Many2one('bsd.tang', string="Đến tầng",
                                      readonly=True,
                                      states={'cph': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True,
                                states={'cph': [('readonly', False)]})
    state = fields.Selection([('cph', 'Chưa phát hành'), ('ph', 'Phát hành'),
                              ('thnb', 'Thu hồi mở bán'), ('thch', 'Thu hồi căn hộ')],
                             string="Trạng thái", default="cph", tracking=1)
    bsd_san_gd = fields.Boolean(string="Sàn giao dịch", default=False,
                                help="""Thông tin quy định đợt mở bán chỉ cho phép các sàn giao dịch được bán, 
                                        hay cho sàn giao dịch và chủ đầu tư đều được bán""",
                                readonly=True,
                                states={'cph': [('readonly', False)]})
    bsd_sgd_ids = fields.One2many('bsd.dot_mb_sgd', 'bsd_dot_mb_id', string="Các sàn giao dịch",
                                  readonly=True,
                                  states={'cph': [('readonly', False)]})
    bsd_km_ids = fields.One2many('bsd.dot_mb_km', 'bsd_dot_mb_id', string="Khuyến mãi",
                                 readonly=True,
                                 states={'cph': [('readonly', False)]})
    bsd_dkbg_ids = fields.One2many('bsd.dot_mb_dkbg', 'bsd_dot_mb_id', string="Bàn giao",
                                   readonly=True,
                                   states={'cph': [('readonly', False)]})
    bsd_cb_ids = fields.One2many('bsd.dot_mb_cb', 'bsd_dot_mb_id', string="Chuẩn bị unit",
                                 readonly=True,
                                 states={'cph': [('readonly', False)]})
    bsd_ph_ids = fields.One2many('bsd.dot_mb_unit', 'bsd_dot_mb_id', string="Phát hành unit",
                                 readonly=True,
                                 states={'cph': [('readonly', False)]})


class BsdDotMoBanSanGiaoDich(models.Model):
    _name = 'bsd.dot_mb_sgd'
    _description = 'Thông tin sàn giao dich cho đợt mở bán'
    _rec_name = 'bsd_san_gd_id'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán")
    bsd_san_gd_id = fields.Many2one('res.partner', string="Tên sàn giao dịch", domain=[('is_company', '=', True)],
                                    help="Sàn giao dịch được bán các căn hộ trong đợt mở bán")
    bsd_san_gd_phone = fields.Char(string="Số điện thoại", related="bsd_san_gd_id.phone")
    bsd_san_gd_street = fields.Char('Đường', related="bsd_san_gd_id.street")
    bsd_san_gd_city = fields.Char('Thành phố', related="bsd_san_gd_id.city")
    bsd_san_gd_state_id = fields.Many2one("res.country.state", string='Tỉnh thành', related="bsd_san_gd_id.state_id")
    bsd_san_gd_country_id = fields.Many2one('res.country', string='Quốc gia', related="bsd_san_gd_id.country_id")


class BsdDotMoBanKhuyenMai(models.Model):
    _name = 'bsd.dot_mb_km'
    _description = "Thông tin chương trình khuyến mãi cho đợt mở bán"
    _rec_name = 'bsd_khuyen_mai_id'

    bsd_khuyen_mai_id = fields.Many2one('bsd.khuyen_mai', string="Khuyến mãi")
    bsd_ma_km = fields.Char(related='bsd_khuyen_mai_id.bsd_ma_km')
    bsd_tu_ngay = fields.Date(related='bsd_khuyen_mai_id.bsd_tu_ngay')
    bsd_den_ngay = fields.Date(related='bsd_khuyen_mai_id.bsd_den_ngay')
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", required=True)


class BsdDotMoBanDKBG(models.Model):
    _name = 'bsd.dot_mb_dkbg'
    _description = 'Thông tin điều kiện bàn giao cho đợt mở bán'
    _rec_name = 'bsd_dk_bg_id'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", required=True)
    bsd_dk_bg_id = fields.Many2one('bsd.dk_bg', string="Bàn giao")
    bsd_ma_dkbg = fields.Char(related="bsd_dk_bg_id.bsd_ma_dkbg")
    bsd_loai_bg = fields.Selection(related="bsd_dk_bg_id.bsd_loai_bg")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_tien = fields.Monetary(related="bsd_dk_bg_id.bsd_tien")
    bsd_ty_le = fields.Float(related="bsd_dk_bg_id.bsd_ty_le")


class BsdDotMoBanCB(models.Model):
    _name = 'bsd.dot_mb_cb'
    _description = 'Thông tin căn hộ chuẩn bị cho đợt mở bán'
    _rec_name = 'bsd_unit_id'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True)
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", required=True)
    bsd_gia_ban = fields.Monetary(string="Giá bán", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)


class BsdDotMoBanUnit(models.Model):
    _name = 'bsd.dot_mb_unit'
    _description = 'Thông tin căn hộ phát hành cho đợt mở bán'
    _rec_name = 'bsd_unit_id'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True)
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", required=True)
    bsd_gia_ban = fields.Monetary(string="Giá bán", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
