# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name = fields.Char(compute='_compute_name', store=True, required=False)

    @api.depends('bsd_ma_unit')
    def _compute_name(self):
        for each in self:
            each.name = each.bsd_ma_unit

    def name_get(self):
        return [(template.id, template.bsd_ma_unit)for template in self]

    bsd_stt = fields.Char(string="Số thứ tự", help="Số thứ tự sản phẩm", required=True,
                          readonly=True,
                          states={'chuan_bi': [('readonly', False)]})
    bsd_ten_unit = fields.Char(string="Mã sản phẩm",
                               help="Mã sản phẩm bao gồm mã tòa nhà, mã tầng và số sản phẩm",
                               readonly=True,
                               states={'chuan_bi': [('readonly', False)]})
    bsd_ma_unit = fields.Char(string="Mã SP (hệ thống)",
                              help="Mã đầy đủ của sản phẩm bao gồm mã dữ án, mã tòa nhà, mã tầng và số sản phẩm",
                              readonly=True,
                              states={'chuan_bi': [('readonly', False)]})
    bsd_ten_sp = fields.Char(string="Tên sản phẩm", help="Tên sản phẩm",
                             readonly=True,
                             states={'chuan_bi': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_unit_unique', 'unique (bsd_ma_unit)',
         'Mã unit đã tồn tại !'),
    ]
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True, help="Tên dự án",
                                   readonly=True,
                                   states={'chuan_bi': [('readonly', False)]})
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà/ khu", required=True, help="Tên tòa nhà hoặc khu",
                                     readonly=True,
                                     states={'chuan_bi': [('readonly', False)]})
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng/ dãy", required=True, help="Tên tầng lầu hoặc dãy nhà",
                                  readonly=True,
                                  states={'chuan_bi': [('readonly', False)]})
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc của sản phẩm",
                                  readonly=True,
                                  states={'chuan_bi': [('readonly', False)]})
    bsd_tien_gc = fields.Monetary(string="Tiền giữ chỗ", help="Tiền giữ chỗ của sản phẩm",
                                  readonly=True,
                                  states={'chuan_bi': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Thông tin về sản phẩm",
                                readonly=True,
                                states={'chuan_bi': [('readonly', False)]})
    bsd_san_gd_id = fields.Many2one('res.partner', string="Sàn giao dịch",
                                    help="Sàn giao dịch đang bán(sản phẩm) theo đợt mở bán",
                                    readonly=True,
                                    states={'chuan_bi': [('readonly', False)]})
    bsd_loai_sd_ids = fields.Many2many('bsd.lh_sd', string="Loại hình sử dụng", help="Loại hình sử dụng",
                                       readonly=True,
                                       states={'chuan_bi': [('readonly', False)]})
    bsd_loai_sp_id = fields.Many2one('bsd.loai_sp', string="Loại sản phẩm",
                                     help="Phân nhóm đặc tính kỹ thuật của sản phẩm",
                                     readonly=True,
                                     states={'chuan_bi': [('readonly', False)]})
    bsd_huong = fields.Selection([('1', 'Đông'),
                                  ('2', 'Tây'),
                                  ('3', 'Nam'),
                                  ('4', 'Bắc'),
                                  ('5', 'Đông nam'),
                                  ('6', 'Đông bắc'),
                                  ('7', 'Tây nam'),
                                  ('8', 'Tây bắc')], string="Hướng", help="Hướng nhà",
                                 readonly=True,
                                 states={'chuan_bi': [('readonly', False)]})
    bsd_view_ids = fields.Many2many('bsd.view', string="Hướng nhìn",
                                    relation="bsd_view_unit_rel",
                                    column1="bsd_unit_id",
                                    column2="bsd_view_id",
                                    readonly=True,
                                    states={'chuan_bi': [('readonly', False)]})
    bsd_so_pn = fields.Integer(string="Số phòng ngủ", help="Số phòng ngủ của sản phẩm",
                               readonly=True,
                               states={'chuan_bi': [('readonly', False)]})
    # bsd_loai_bds = fields.Selection([('1', 'Liền thổ(đất)'),
    #                                  ('2', 'Căn hộ'),
    #                                  ('3', 'Phức hợp'),
    #                                  ('4', 'Nghỉ dưỡng')],
    #                                 help="Loại hình sử dụng của sản phẩm",
    #                                 string="Loại bất động sản",
    #                                 readonly=True,
    #                                 states={'chuan_bi': [('readonly', False)]})
    # bsd_phan_loai = fields.Selection([('1', 'Condotel'),
    #                                   ('2', 'Apartment')], string="Phân loại", help="Phân loại",
    #                                  readonly=True,
    #                                  states={'chuan_bi': [('readonly', False)]})
    # bsd_loai_unit = fields.Selection([('1', 'Căn hộ'),
    #                                   ('2', 'Căn hộ nhiều tầng'),
    #                                   ('3', 'Siêu thị/cửa hàng'),
    #                                   ('4', 'Penthouse')], string="Loại sản phẩm", help="Loại sản phẩm",
    #                                  readonly=True,
    #                                  states={'chuan_bi': [('readonly', False)]})
    bsd_tl_tc = fields.Float(string="Tỷ lệ tiền cọc",
                             help="Tỷ lệ thanh toán tối thiểu để ký thỏa thuận đặt cọc",
                             readonly=True,
                             states={'chuan_bi': [('readonly', False)]})
    bsd_dt_cl = fields.Float(string="Chênh lệch (+/-)",
                             help="Tỷ lệ chênh lệch giữa diện tích xây dựng và diện tích sử dụng",
                             required=True,
                             readonly=True,
                             states={'chuan_bi': [('readonly', False)]})
    bsd_dt_xd = fields.Float(string="Diện tích xây dựng",
                             help="Diện tích tim tường", required=True,
                             readonly=True,
                             states={'chuan_bi': [('readonly', False)]})
    bsd_dt_sd = fields.Float(string="Diện tích sử dụng", help="Diện tích thông thủy thiết kế", required=True,
                             readonly=True,
                             states={'chuan_bi': [('readonly', False)]})
    bsd_dt_tt = fields.Float(string="Diện tích thực tế", help="Diện tích thông thủy thực tế",
                             readonly=True,
                             states={'chuan_bi': [('readonly', False)]})
    bsd_dt_sh = fields.Float(string="Diện tích sổ hồng", help="Diện tích sổ hồng",
                             readonly=True,
                             states={'chuan_bi': [('readonly', False)]})
    bsd_don_gia = fields.Monetary(string="Đơn giá bán/m2", help="Đơn giá bán trước thuế theo m2",
                                  readonly=True,
                                  states={'chuan_bi': [('readonly', False)]})
    bsd_gia_ban = fields.Monetary(string="Giá bán", help="Giá bán trước thuế của sản phẩm",
                                  readonly=True,
                                  states={'chuan_bi': [('readonly', False)]})
    bsd_qsdd_m2 = fields.Monetary(string="QSDĐ/ m2", help="Giá trị quyền sử dụng đất theo m2",
                                  readonly=True,
                                  states={'chuan_bi': [('readonly', False)]})
    bsd_tien_qsdd = fields.Monetary(string="Giá trị QSDĐ", help="""
                                                                    Tổng giá trị sử dụng đất của sản phẩm được tính theo
                                                                    công thức: diện tích sử dụng(thông thủy) * 
                                                                    QSDĐ/m2
                                                                    """,
                                    readonly=True, compute='_compute_bsd_tong_gtsd_dat', store=True)
    bsd_tl_pbt = fields.Float(string="Tỷ lệ phí bảo trì", help="Tỷ lệ phí bảo trì", required=True,
                              readonly=True,
                              states={'chuan_bi': [('readonly', False)]})
    bsd_tien_pbt = fields.Monetary(string="Phí bảo trì", help="""
                                                                Tổng tiền phí bảo trì được tính theo công thức:
                                                                Tỷ lệ phí bảo trì * giá bán trước thuế
                                                                """,
                                   compute='_compute_bsd_phi_bao_tri', store=True)
    bsd_thue_suat = fields.Float(string="Thuế suất", help="Thuế suất",
                                 readonly=True,
                                 states={'chuan_bi': [('readonly', False)]})
    bsd_tien_thue = fields.Monetary(string="Tiền thuế", help="""Tiền thuế của sản phẩm được tính theo công thức:
                                                            (giá bán - Giá trị QSDĐ)* thuế suất""",
                                    readonly=True, compute='_compute_tien_thue', store=True)
    bsd_tong_gb = fields.Monetary(string="Tổng giá bán", help="""Tổng giá bán của sản phẩm tính theo công thức:
                                                                        giá bán + tiền thuế + tiền phí bảo trì""",
                                  readonly=True, compute='_compute_bsd_tong_gia_ban', store=True)
    bsd_uu_tien = fields.Selection([('0', 'Không'),
                                    ('1', 'Có')], string="Ưu tiên", help="Ưu tiên bán của sản phẩm",
                                   default='0', readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt ưu tiên",
                                         help="Người duyệt ưu tiên", readonly=True)
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt ưu tiên", help="Ngày duyệt ưu tiên", readonly=True)
    bsd_lan_duyet = fields.Integer(string="Lần ưu tiên", help="Lần ưu tiên", readonly=True)
    bsd_ghi_chu = fields.Char(string="Ghi chú ưu tiên", help="Ghi chú ưu tiên", readonly=True)
    bsd_nguoi_huy_id = fields.Many2one('res.users', string="Người hủy ưu tiên", help="Người hủy ưu tiên", readonly=True)
    bsd_ngay_huy = fields.Datetime(string="Ngày hủy ưu tiên", readonly=True, help="Ngày hủy ưu tiên")
    bsd_tt_vay = fields.Selection([('0', 'Không'),
                                   ('1', 'Có')], string="Tình trạng vay", default='0',
                                  help="Tình trạng vay ngân hàng của sản phẩm",
                                  readonly=True,
                                  states={'chuan_bi': [('readonly', False)]})
    bsd_ngay_dkbg = fields.Date(string="Ngày dự kiến bàn giao", help="Ngày dự kiến bàn giao",
                                readonly=True,
                                states={'chuan_bi': [('readonly', False)]})
    bsd_thang_pql = fields.Integer(string="Số tháng đóng PQL", help="Số tháng đóng phí quản lý",
                                   readonly=True,
                                   states={'chuan_bi': [('readonly', False)]})
    bsd_don_gia_pql = fields.Monetary(string="Đơn giá PQL", help="Đơn giá Phí quản lý m2/tháng", required=True,
                                      readonly=True,
                                      states={'chuan_bi': [('readonly', False)]})
    bsd_tien_pql = fields.Monetary(string="Phí quản lý", help="Số tiền phí quản lý",
                                   compute="_compute_tien_pql", store=True)
    bsd_dk_bg = fields.Float(string="Điều kiện bàn giao",
                             help="% thanh toán đủ điều kiện bàn giao(tối thiểu",
                             readonly=True,
                             states={'chuan_bi': [('readonly', False)]})
    bsd_ngay_bg = fields.Date(string="Ngày bàn giao",
                              help="Ngày bàn giao thực tế sản phẩm cho khách hàng",
                              readonly=True,
                              states={'chuan_bi': [('readonly', False)]})
    bsd_ngay_cn = fields.Date(string="Ngày ht cất nóc",
                              help="Ngày chứng nhận cất nóc (bê tông tầng mái)",
                              readonly=True,
                              states={'chuan_bi': [('readonly', False)]})
    bsd_ngay_cap_sh = fields.Date(string="Ngày cấp sổ hồng",
                                  help="Ngày khách hàng nhận sổ hồng",
                                  readonly=True)
    state = fields.Selection([('chuan_bi', 'Chuẩn bị'),
                              ('san_sang', 'Sẵn sàng'),
                              ('dat_cho', 'Đặt chỗ'),
                              ('giu_cho', 'Giữ chỗ'),
                              ('dat_coc', 'Đặt cọc'),
                              ('chuyen_coc', 'Chuyển cọc'),
                              ('da_tc', 'Đã thu cọc'),
                              ('ht_dc', 'Hoàn tất đặt cọc'),
                              ('tt_dot_1', 'Thanh toán đợt 1'),
                              ('ky_tt_coc', 'Ký thỏa thuận cọc'),
                              ('du_dk', 'Đủ điều kiện'),
                              ('da_ban', 'Đã bán')], string="Trạng thái",
                             default="chuan_bi", tracking=1, help="Trạng thái", required=True, readonly=True)

    @api.constrains('bsd_tl_pbt')
    def _check_bsd_phi_bao_tri(self):
        for record in self:
            if record.bsd_tl_pbt > 100 or record.bsd_tl_pbt < 0:
                raise ValidationError("Phí bảo trì nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_thue_suat')
    def _check_bsd_thue_suat(self):
        for record in self:
            if record.bsd_thue_suat > 100 or record.bsd_thue_suat < 0:
                raise ValidationError("Thuế suất nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_tl_tc')
    def _check_bsd_tl_tc(self):
        for record in self:
            if record.bsd_tl_tc > 100 or record.bsd_tl_tc < 0:
                raise ValidationError("Tỷ lệ tiền cọc nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_so_pn')
    def _check_bsd_so_pn(self):
        for record in self:
            if record.bsd_so_pn < 0:
                raise ValidationError("Số phòng ngủ phải lớn hơn 0")

    @api.constrains('bsd_dt_cl')
    def _check_bsd_dt_cl(self):
        for record in self:
            if record.bsd_dt_cl > 100 or record.bsd_dt_cl < 0:
                raise ValidationError("Diện tích chênh lệch nằm trong khoảng 0 đến 100")

    @api.constrains('bsd_dt_xd')
    def _check_bsd_dt_xd(self):
        for record in self:
            if record.bsd_dt_xd <= 0:
                raise ValidationError("Diện tích xây dựng phải lớn hơn 0")

    @api.constrains('bsd_dt_sd')
    def _check_bsd_dt_sd(self):
        for record in self:
            if record.bsd_dt_sd <= 0:
                raise ValidationError("Diện tích sử dụng phải lớn hơn 0")

    @api.constrains('bsd_dt_tt')
    def _check_bsd_dt_tt(self):
        for record in self:
            if record.bsd_dt_tt < 0:
                raise ValidationError("Diện tích thực tế phải lớn hơn 0")

    @api.constrains('bsd_dt_sh')
    def _check_bsd_dt_sh(self):
        for record in self:
            if record.bsd_dt_sh < 0:
                raise ValidationError("Diện tích sổ hồng phải lớn hơn 0")

    @api.constrains('bsd_tien_gc')
    def _check_bsd_tien_gc(self):
        for record in self:
            if record.bsd_tien_gc <= 0:
                raise ValidationError("Tiền giữ chỗ phải lớn hơn 0")

    @api.constrains('bsd_tien_dc')
    def _check_bsd_tien_dc(self):
        for record in self:
            if record.bsd_tien_dc <= 0:
                raise ValidationError("Tiền đặt cọc phải lớn hơn 0")

    @api.constrains('bsd_don_gia')
    def _check_bsd_don_gia(self):
        for record in self:
            if record.bsd_don_gia <= 0:
                raise ValidationError("Đơn giá bán trước thuế phải lớn hơn 0")

    @api.constrains('bsd_gia_ban')
    def _check_bsd_gia_ban(self):
        for record in self:
            if record.bsd_gia_ban <= 0:
                raise ValidationError("Giá bán phải lớn hơn 0")

    @api.constrains('bsd_qsdd_m2')
    def _check_bsd_qsdd_m2(self):
        for record in self:
            if record.bsd_qsdd_m2 <= 0:
                raise ValidationError("Giá trị quyền sử dụng đất theo m2 phải lớn hơn 0")

    @api.constrains('bsd_don_gia_pql')
    def _check_bsd_don_gia_pql(self):
        for record in self:
            if record.bsd_don_gia_pql <= 0:
                raise ValidationError("Đơn giá phí quản lý phải lớn hơn 0")

    @api.constrains('bsd_thang_pql')
    def _check_bsd_thang_pql(self):
        for record in self:
            if record.bsd_don_gia_pql <= 0:
                raise ValidationError("Số tháng đóng phí quản lý phải lớn hơn 0")

    @api.onchange('bsd_du_an_id')
    def _onchange_du_an(self):
        self.bsd_tien_gc = self.bsd_du_an_id.bsd_tien_gc
        self.bsd_tien_dc = self.bsd_du_an_id.bsd_tien_dc
        self.bsd_qsdd_m2 = self.bsd_du_an_id.bsd_qsdd_m2
        self.bsd_tl_pbt = self.bsd_du_an_id.bsd_tl_pbt
        self.bsd_ngay_dkbg = self.bsd_du_an_id.bsd_ngay_dkbg

    @api.depends('bsd_don_gia_pql', 'bsd_dt_sd', 'bsd_thang_pql')
    def _compute_tien_pql(self):
        for each in self:
            each.bsd_tien_pql = each.bsd_don_gia_pql * each.bsd_dt_sd * each.bsd_thang_pql

    @api.depends('bsd_dt_sd', 'bsd_qsdd_m2')
    def _compute_bsd_tong_gtsd_dat(self):
        for each in self:
            each.bsd_tien_qsdd = each.bsd_dt_sd * each.bsd_qsdd_m2

    @api.depends('bsd_tl_pbt', 'bsd_gia_ban')
    def _compute_bsd_phi_bao_tri(self):
        for each in self:
            each.bsd_tien_pbt = each.bsd_tl_pbt * each.bsd_gia_ban / 100

    @api.depends('bsd_gia_ban', 'bsd_tien_qsdd', 'bsd_thue_suat')
    def _compute_tien_thue(self):
        for each in self:
            each.bsd_tien_thue = (each.bsd_gia_ban - each.bsd_tien_qsdd) * each.bsd_thue_suat / 100

    @api.depends('bsd_gia_ban', 'bsd_tien_thue', 'bsd_tien_pbt')
    def _compute_bsd_tong_gia_ban(self):
        for each in self:
            each.bsd_tong_gb = each.bsd_gia_ban + each.bsd_tien_thue + each.bsd_tien_pbt

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

    def _create_sequence(self):
        seq = {
            'name': _('Trình tự giữ chỗ %s') % self.bsd_ma_unit,
            'implementation': 'no_gap',
            'padding': 1,
            'code': self.bsd_ma_unit,
            'number_increment': 1,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(ProductTemplate, self).create(vals_list)
        for template in templates:
            du_an = template.bsd_du_an_id
            toa_nha = template.bsd_toa_nha_id
            tang = template.bsd_tang_id
            if not template.bsd_ma_unit:
                template.write({
                    'bsd_ma_unit': du_an.bsd_ma_da + du_an.bsd_dd_da +
                            toa_nha.bsd_ma_tn + du_an.bsd_dd_khu +
                                   tang.bsd_ten_tang + du_an.bsd_dd_tang + templates.bsd_stt
                })
            if not template.bsd_ten_unit:
                template.write({
                    'bsd_ten_unit': toa_nha.bsd_ma_tn + du_an.bsd_dd_khu +
                                    tang.bsd_ten_tang + du_an.bsd_dd_tang + templates.bsd_stt
                })
            template._create_sequence()
        return templates

    def write(self, vals):
        # cập nhật lại code trong sequence
        if 'bsd_ma_unit' in vals.keys():
            self.env['ir.sequence'].search([('code', '=', self.bsd_ma_unit)]).write({
                'code': vals['bsd_ma_unit']
            })
        return super(ProductTemplate, self).write(vals)

    def unlink(self):
        if self.env['bsd.giu_cho'].search([('bsd_product_tmpl_id', '=' , self.id)], limit=1):
            raise UserError(_("Sản phẩm đã phát sinh giữ chỗ. Không thể xóa sản phẩm"))
        return super(ProductTemplate, self).unlink()


class BsdHuongNhin(models.Model):
    _name = "bsd.view"
    _rec_name = "bsd_ten"

    bsd_ten = fields.Char(string="Hướng nhìn", help="Hướng nhìn", required=True)