# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BsdProject(models.Model):
    _name = "bsd.du_an"
    _rec_name = "bsd_ten_da"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Thông tin dự án"

    bsd_ten_da = fields.Char(string="Tên dự án", required=True, help="Tên dự án")
    bsd_ma_da = fields.Char(string="Mã dự án", required=True, help="Mã dự án")
    _sql_constraints = [
        ('bsd_ma_da_unique', 'unique (bsd_ma_da)',
         'Mã dự án đã tồn tại !'),
    ]
    bsd_chu_dt_id = fields.Many2one('res.partner', string="Chủ dự án", required=True, help="Tên chủ đầu tư của dự án")
    bsd_loai_da = fields.Selection([('da_rieng', 'Dự án riêng'),
                                    ('da_ph', 'Dự án phức hợp')], string="Loại dự án", help="Loại hình dự án")
    bsd_mh_kd = fields.Selection([('nha_o', 'Nhà ở'), ('nghi_duong', 'Nghỉ dưỡng')], string="Mô hình kinh doanh")
    bsd_loai_sd_ids = fields.Many2many('bsd.lh_sd', string="Loại hình sử dụng", help="Loại hình sử dụng")
    bsd_gp_dt = fields.Char(string="Giấy phép đầu tư", help="Giấy phép đầu tư của dự án")
    bsd_ngay_gp = fields.Date(string="Ngày cấp phép", help="Ngày cấp phép đầu tư của dự án")
    bsd_dia_chi = fields.Text(string="Địa chỉ", help="Địa chỉ của dự án")
    bsd_hd_coc = fields.Boolean(string="Có HĐ cọc?", help="Dự án có quy định làm hợp đồng cọc không?")
    bsd_tl_dc = fields.Float(string="Tỷ lệ đặt cọc",
                             help="Tỷ lệ(%) tiền cần đặt cọc dựa trên giá trị căn hộ")
    bsd_ngay_dkcn = fields.Date(string="Ngày dự kiến cất nóc",
                                help="""Thông tin ngày dự kiến cất nóc được sử dụng để xác định thời gian 
                                        bắt đầu thu phí quản lý, bảo trì và thu tiền đợt cuối""")
    bsd_ngay_dkbg = fields.Date(string="Ngày dự kiến bàn giao", required=True,
                                help="Ngày dự kiến bàn giao căn hộ cho khách hàng")
    bsd_ngay_htpl = fields.Date(string="Ngày hoàn tất pháp lý",
                                help="Ngày hoàn thành tất cả các thủ tục cho khách hàng")
    bsd_ngay_qsdd = fields.Date(string="Ngày chứng nhận quyền sử dụng đất",
                                help="Ngày trên sổ đỏ hoặc ngày chứng nhân quyền thuê đất của chủ đầu tư")
    bsd_cho_gx = fields.Integer(string="Số chỗ giữ xe")
    bsd_ngay_ttcn = fields.Date(string="Ngày thực tế cất nóc",
                                help="""Sau ngày thực tế cất nóc, chủ đầu tư có thể thu phí bảo trì,
                                        phí quản lý và thu tiền đợt cuối của căn hộ""")
    bsd_ngay_cpb = fields.Date(string="Ngày cấp phép bán",
                               help="""Ngày Sở Xây Dựng chính thức cấp phép dự án đã đủ điều kiện mở bán""")
    bsd_dd_da = fields.Char(string="Định dạng dự án", required=True,
                            help="Định dạng dự án được sử dụng để tự động tạo mã căn hộ")
    bsd_dd_khu = fields.Char(string="Định dạng tòa nhà", required=True,
                             help="Định dạng khu, tòa nhà được sử dụng để tự động tạo mã căn hộ")
    bsd_dd_tang = fields.Char(string="Định dạng tầng", required=True,
                              help="Định dạng tầng được sử dụng để tự động tạo mã căn hộ")
    bsd_qsdd_m2 = fields.Monetary(string="Giá trị QSDĐ/ m2", required=True,
                                  help="Giá trị quyền sử dụng đất trên m2")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_tl_pbt = fields.Float(string="Tỷ lệ phí bảo trì", required=True, help="Tỷ lệ phí bảo trì")
    bsd_thang_pql = fields.Integer(string="Số tháng đóng phí quản lý", required=True,
                                   help="Số tháng đóng phí quản lý trước đợt bàn giao tạm thời hoặc bàn giao chính thức")
    bsd_pql_m2 = fields.Monetary(string="Đơn giá PQL", required=True,
                                 help="Số tiền quản lý cần đóng, tính theo m2/ tháng")
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", required=True,
                                  help="Tiền giữ chỗ khi mua căn hộ của dự án")
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", required=True,
                                  help="Tiền đặt cọc khi mua căn hộ của dự án")
    bsd_hh_bg = fields.Integer(string="Hiệu lực bảng tính giá", required=True,
                               help="Số ngày báo giá hết hiệu lực, được tính từ ngày tạo báo giá")
    bsd_hh_pc = fields.Integer(string="Hạn ký phiếu cọc", required=True,
                               help="Số ngày phiếu cọc hết hiệu lực ký, được tính từ ngày in phiếu cọc")
    bsd_hh_hd = fields.Integer(string="Hạn ký hợp đồng", required=True,
                               help="Số ngày hợp đồng hết hiệu lực ký, được tính kể từ ngày in hợp đồng")
    bsd_cb_gc = fields.Integer(string="Cảnh báo sau giữ chỗ",
                               help="Số ngày cảnh báo sau khi tạo giữ chỗ")
    bsd_cb_dc = fields.Integer(string="Cảnh báo sau đặt cọc",
                               help="Số ngày cảnh báo sau khi tạo đặt cọc")
    bsd_hh_qt = fields.Float(string="Hiệu lực quan tâm(h)",
                             help="Số giờ hiệu lực của phiếu quan tâm bất động sản")
    bsd_gc_unit_nv = fields.Integer(string="Căn hộ/NVBH", required=True,
                                    help="Số lượng căn hộ tối đa mà mỗi nhân viên bán hàng được thực hiện giữ chỗ")
    bsd_gc_unit = fields.Integer(string="Giữ chỗ/Căn hộ", required=True,
                                 help="Số lượng giữ chỗ tối đa cho mỗi căn hộ")
    bsd_gc_nv_ngay = fields.Integer(string="NVBH/ngày",
                                    help="Số lượng giữ chỗ tối đa mà 1 nhân viên bán hàng được phép thực hiện trong 1 ngày")
    bsd_gc_unit_nv_ngay = fields.Integer(string="Căn hộ/NVBH/ngày",
                                         help="""Số lượng giữ chỗ tối đa trên 1 căn hộ mà 1 nhân viên bán hàng 
                                                được phép thực hiện trong 1 ngày""")
    bsd_gc_tmb = fields.Integer(string="Giữ chỗ dài hạn",
                                help="""Thời gian hiệu lực giữ chỗ dài hạn""",
                                required=True)
    bsd_gc_smb = fields.Float(string="Giữ chỗ ngắn hạn",
                              help="""Thời gian hiệu lực giữ chỗ ngắn hạn""",
                              required=True)
    bsd_hh_nv = fields.Float(string="Hoa hồng NVBH", required=True,
                             help="Tỷ lệ (%) hoa hồng được hưởng của nhân viên bán hàng")
    bsd_hh_ql = fields.Monetary(string="Quản lý", help="Tiền hoa hồng được hương của quản lý", required=True)
    bsd_hh_dv = fields.Monetary(string="Dịch vụ", required=True,
                                help="Tiền hoa hồng được hương của nhân viên dịch vụ khách hàng")
    state = fields.Selection([('chuan_bi', 'Chuẩn bị'),
                              ('phat_hanh', 'Đã ban hành')],
                             string="Trạng thái", default='chuan_bi', required=True, tracking=1, help="Trạng thái")
    bsd_tk_ng_ids = fields.One2many('bsd.da_tknh', 'bsd_du_an_id', string="Tài khoản ngân hàng")
    bsd_nh_tt_ids = fields.One2many('bsd.da_nh', 'bsd_du_an_id', string="Ngân hàng tài trợ")
    bsd_nh_cv_ids = fields.One2many('bsd.da_nh_vay', 'bsd_du_an_id', string="Ngân hàng cho vay")

    bsd_unit_ids = fields.One2many('product.template', 'bsd_du_an_id', string="Danh sách căn hộ", readonly=True)
    bsd_sl_unit = fields.Integer(string="# Căn hộ", compute="_compute_sl_unit")
    active = fields.Boolean(default=True)
    bsd_tong_dt = fields.Float(string="Tổng diện tích", help="Tổng diện tích dự án", digits=(14,0))

    @api.constrains('bsd_tl_dc')
    def _check_ty_le_coc(self):
        for record in self:
            if record.bsd_tl_dc > 100 or record.bsd_tl_dc < 0:
                raise ValidationError("Tỷ lệ đặt cọc nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_tl_pbt')
    def _check_bsd_phi_bao_tri(self):
        for record in self:
            if record.bsd_tl_pbt > 100 or record.bsd_tl_pbt < 0:
                raise ValidationError("Phí bảo trì nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_hh_bg')
    def _check_bsd_int_hieu_luc_bao_gia(self):
        for record in self:
            if record.bsd_hh_bg > 100 or record.bsd_hh_bg < 0:
                raise ValidationError("Hiệu lực báo giá nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_hh_pc')
    def _check_bsd_int_het_han_ky_phieu_coc(self):
        for record in self:
            if record.bsd_hh_pc > 100 or record.bsd_hh_pc < 0:
                raise ValidationError("Phiếu cọc nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_hh_hd')
    def _check_bsd_int_het_han_ky_hop_dong(self):
        for record in self:
            if record.bsd_hh_hd > 100 or record.bsd_hh_hd < 0:
                raise ValidationError("Hợp đồng nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_cb_gc')
    def _check_bsd_int_canh_bao_sau_giu_cho(self):
        for record in self:
            if record.bsd_cb_gc > 100 or record.bsd_cb_gc < 0:
                raise ValidationError("Cảnh báo sau giữ chỗ nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_cb_dc')
    def _check_bsd_int_canh_bao_sau_dat_coc(self):
        for record in self:
            if record.bsd_cb_dc > 100 or record.bsd_cb_dc < 0:
                raise ValidationError("Cảnh báo sau đặt cọc nằm trong khoảng 0 đến 100")

    @api.depends('bsd_unit_ids')
    def _compute_sl_unit(self):
        for each in self:
            each.bsd_sl_unit = len(each.bsd_unit_ids)

    def action_view_unit(self):
        action = self.env.ref('bsd_du_an.bsd_product_template_action').read()[0]
        action["context"] = {'group_by': 'bsd_toa_nha_id'}
        action["domain"] = [('bsd_du_an_id', '=', self.id)]
        return action


class BsdDuanNganHangTaiTro(models.Model):
    _name = 'bsd.da_nh'
    _description = "Bảng Ngân hàng của dự án"
    _rec_name = "bsd_ngan_hang_id"

    bsd_ngan_hang_id = fields.Many2one('res.bank', string="Ngân hàng", required=True)
    bsd_ma_nh = fields.Char(related="bsd_ngan_hang_id.bic", string="Mã")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    active = fields.Boolean(default=True)


class BsdDuanNganHangChoVay(models.Model):
    _name = 'bsd.da_nh_vay'
    _description = "Bảng Ngân hàng cho vay của dự án"
    _rec_name = "bsd_ngan_hang_id"

    bsd_ngan_hang_id = fields.Many2one('res.bank', string="Ngân hàng", required=True)
    bsd_ma_nh = fields.Char(related="bsd_ngan_hang_id.bic", string="Mã")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active')


class BsdDuanTaiKhoanNganHang(models.Model):
    _name = 'bsd.da_tknh'
    _description = "Bảng tài khoản ngân hàng của dự án"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_tk_nh_id'

    bsd_tk_nh_id = fields.Many2one('res.partner.bank', string="Tài khoản ngân hàng", required=True)
    bsd_ngan_hang_id = fields.Many2one(related='bsd_tk_nh_id.bank_id', string="Ngân hàng")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active')


class BsdLoaiHinhSuDung(models.Model):
    _name = 'bsd.lh_sd'
    _rec_name = 'bsd_ten'

    bsd_ten = fields.Char(string="Loại hình sử dụng", help="Loại hình sử dụng", required=True)