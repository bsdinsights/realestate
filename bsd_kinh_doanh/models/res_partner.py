# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsd_ho_tl = fields.Char(string="Họ và tên lót", help="Họ và tên lót")
    bsd_search_ten = fields.Char(string="Search tên", compute='_compute_search_name', store=True)

    @api.depends('display_name', 'bsd_cmnd', 'bsd_ma_kh', 'bsd_so_gpkd')
    def _compute_search_name(self):
        for each in self:
            each.bsd_search_ten = (each.bsd_cmnd or '') + (each.bsd_ma_kh or '') + \
                                   (each.display_name or '') + (each.bsd_so_gpkd or '')

    bsd_ma_kh = fields.Char(string="Mã khách hàng", required=True, readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_kh_unique', 'unique (bsd_ma_kh)',
         'Mã khách hàng đã tồn tại !'),
    ]
    bsd_loai_kh_cn_ids = fields.Many2many('bsd.loai_kh_cn',
                                          relation="bsd_loai_cn_rel",
                                          column1="bsd_cn_id",
                                          column2="bsd_loai_id",
                                          help="Loại khách hàng cá nhân", string="Loại khách hàng")
    bsd_la_kh = fields.Boolean(string="Khách hàng")
    bsd_ngay_sinh = fields.Date(string="Ngày sinh", help="Ngày sinh")
    bsd_gioi_tinh = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')], string="Giới tính", help="Giới tính", default='nam')
    bsd_loai_kh = fields.Selection([('vn', 'Việt Nam'),
                                    ('nc', 'Người nước ngoài')], string="Quốc tịch",
                                   help="Khách hàng là công dân Việt Nam hay Người nước ngoài",
                                   required=True, default='vn')
    bsd_nguoi_bh = fields.Boolean(string="Có người bảo hộ", help="Khách hàng có người bảo hộ")
    bsd_cmnd = fields.Char(string="CMND/ CCCD", help="Số CMND/ CCCD")
    bsd_ngay_cap_cmnd = fields.Date(string="Ngày cấp CMND", help="Ngày cấp CMND/ CCCD")
    bsd_noi_cap_cmnd = fields.Char(string="Nơi cấp CMND", help="Nơi cấp CMND")
    bsd_ho_chieu = fields.Char(string="Hộ chiếu", help="Số hộ chiếu")
    bsd_ngay_cap_hc = fields.Date(string="Ngày cấp hộ chiếu", help="Ngày cấp hộ chiếu")
    bsd_noi_cap_hc = fields.Char(string="Nơi cấp hộ chiếu", help="Nơi cấp hộ chiếu")
    bsd_mst = fields.Char(string="Mã số thuế", help="Mã số thuế khách hàng")
    bsd_dia_chi_tt = fields.Char(string="Địa chỉ thường trú", help="Địa chỉ thường trú",
                                 compute="_compute_dia_chi_tt", store=True)
    bsd_quoc_gia_tt_id = fields.Many2one('res.country', string="Quốc gia (TT)", help="Tên quốc gia")
    bsd_tinh_tt_id = fields.Many2one('res.country.state', string="Tỉnh/ Thành (TT)", help="Tên tỉnh thành, thành phố")
    bsd_quan_tt_id = fields.Many2one('bsd.quan_huyen', string="Quận/ Huyện (TT)", help="Tên quận huyện")
    bsd_phuong_tt_id = fields.Many2one('bsd.phuong_xa', string="Phường/ Xã (TT)", help="Tên phường xã")
    bsd_so_nha_tt = fields.Char(string="Số nhà (TT)", help="Số nhà, tên đường")
    bsd_dia_chi_lh = fields.Char(string="Địa chỉ liên hệ", help="Địa chỉ liên hệ",
                                 compute="_compute_dia_chi_lh", store=True)
    bsd_quoc_gia_lh_id = fields.Many2one('res.country', string="Quốc gia (LH)", help="Tên quốc gia")
    bsd_tinh_lh_id = fields.Many2one('res.country.state', string="Tỉnh/ Thành (LH)", help="Tên tỉnh thành, thành phố")
    bsd_quan_lh_id = fields.Many2one('bsd.quan_huyen', string="Quận/ Huyện (LH)", help="Tên quận huyện")
    bsd_phuong_lh_id = fields.Many2one('bsd.phuong_xa', string="Phường/ Xã (LH)", help="Tên phường xã")
    bsd_so_nha_lh = fields.Char(string="Số nhà (LH)", help="Số nhà, tên đường")

    bsd_cung_dc = fields.Boolean(string="Đây là địa chỉ thường trú", help="Đây là địa chỉ thường trú")

    bsd_giu_cho_ids = fields.One2many('bsd.giu_cho', 'bsd_kh_moi_id', string="DS giữ chỗ",
                                      domain=[('state', '!=', 'nhap')], readonly=True)
    bsd_gc_tc_ids = fields.One2many('bsd.gc_tc', 'bsd_kh_moi_id', string="DS giữ chỗ thiện chí",
                                    domain=[('state', '!=', 'nhap')], readonly=True)
    bsd_bao_gia_ids = fields.One2many('bsd.bao_gia', 'bsd_khach_hang_id', string="DS bảng tính giá",
                                      domain=[('state', '!=', 'nhap')], readonly=True)
    bsd_dat_coc_ids = fields.One2many('bsd.dat_coc', 'bsd_khach_hang_id', string="DS đặt cọc",
                                      domain=[('state', '!=', 'nhap')], reaonly=True)
    bsd_sl_giu_cho = fields.Integer(string="# Giữ chỗ", compute="_compute_sl_gc", store=True)

    bsd_nguoi_bh_id = fields.Many2one('res.partner', string="Người bảo hộ", help="Người bảo hộ")

    @api.constrains('bsd_cmnd')
    def _constrains_cmnd(self):
        if self.env['res.users'].has_group('bsd_kinh_doanh.group_manager'):
            pass
        else:
            khach_hang = self.env['res.partner'].search([('bsd_cmnd', '=', self.bsd_cmnd),
                                                         ('id', '!=', self.id),
                                                         ('bsd_cmnd', '!=', False)])
            if khach_hang:
                raise UserError("Chứng minh nhân dân đã được sử dụng.")

    @api.constrains('bsd_ngay_sinh')
    def _constrains_ngay_sinh(self):
        if not self.bsd_nguoi_bh and self.bsd_ngay_sinh:
            nam_ht = fields.Date.today().year
            nam_sinh = self.bsd_ngay_sinh.year
            if nam_ht - nam_sinh < 18:
                raise UserError(_("Khách hàng chưa đủ 18 tuổi, vui lòng kiểm tra lại."))

    @api.constrains('email')
    def _constrains_email(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if not match:
                raise ValidationError('Nhập thông tin email không đúng.')

    @api.depends('bsd_giu_cho_ids', 'bsd_giu_cho_ids.state')
    def _compute_sl_gc(self):
        for each in self:
            each.bsd_sl_giu_cho = len(each.bsd_giu_cho_ids)

    def action_view_giu_cho(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_giu_cho_action').read()[0]

        giu_cho = self.env['bsd.giu_cho'].search([('bsd_kh_moi_id', '=', self.id)])
        if len(giu_cho) > 1:
            action['domain'] = [('id', 'in', giu_cho.ids)]
        elif giu_cho:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_giu_cho_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = giu_cho.id
        # Prepare the context.
        context = {
            'default_bsd_khach_hang_id': self.id,
        }
        action['context'] = context
        return action

    # R.01 Ràng buộc số điện thoại là duy nhất
    _sql_constraints = [
        ('mobile_unique', 'unique (mobile)',
         'Số điện thoại đã tồn tại !'),
    ]

    # R.10 tên khách hàng
    @api.onchange('bsd_ho_tl', 'name')
    def _onchange_ten(self):
        self.bsd_ten = (self.bsd_ho_tl or "") + " " + (self.name or "")

    # R.11 Load địa chỉ
    @api.onchange('bsd_cung_dc')
    def _onchange_dc(self):
        if self.bsd_cung_dc:
            self.bsd_quoc_gia_tt_id = self.bsd_quoc_gia_lh_id
            self.bsd_tinh_tt_id = self.bsd_tinh_lh_id
            self.bsd_quan_tt_id = self.bsd_quan_lh_id
            self.bsd_phuong_tt_id = self.bsd_phuong_lh_id
            self.bsd_so_nha_tt = self.bsd_so_nha_lh

    # Xóa field khi thay đổi quốc gia thường trú
    @api.onchange('bsd_quoc_gia_tt_id')
    def _onchange_quoc_gia_tt(self):
        self.bsd_tinh_tt_id = False
        self.bsd_quan_tt_id = False
        self.bsd_phuong_tt_id = False

    # Xóa field khi thay đổi tỉnh thành thường trú
    @api.onchange('bsd_tinh_tt_id')
    def _onchange_tinh_tt(self):
        self.bsd_quan_tt_id = False
        self.bsd_phuong_tt_id = False

    # Xóa field khi thay đổi tỉnh thành thường trú
    @api.onchange('bsd_quan_tt_id')
    def _onchange_quan_tt(self):
        self.bsd_phuong_tt_id = False

    # Xóa field khi thay đổi quốc gia liên hệ
    @api.onchange('bsd_quoc_gia_lh_id')
    def _onchange_quoc_gia_lh(self):
        self.bsd_tinh_lh_id = False
        self.bsd_quan_lh_id = False
        self.bsd_phuong_lh_id = False

    # Xóa field khi thay đổi tỉnh thành liên hệ
    @api.onchange('bsd_tinh_lh_id')
    def _onchange_tinh_lh(self):
        self.bsd_quan_lh_id = False
        self.bsd_phuong_lh_id = False

    # Xóa field khi thay đổi tỉnh thành liên hệ
    @api.onchange('bsd_quan_lh_id')
    def _onchange_quan_lh(self):
        self.bsd_phuong_lh_id = False

    # R.02 Tạo thông tin địa chỉ thường chú
    @api.depends('bsd_quoc_gia_tt_id', 'bsd_tinh_tt_id', 'bsd_quan_tt_id', 'bsd_phuong_tt_id', 'bsd_so_nha_tt')
    def _compute_dia_chi_tt(self):
        for each in self:
            each.bsd_dia_chi_tt = ''
            if each.bsd_so_nha_tt:
                each.bsd_dia_chi_tt += each.bsd_so_nha_tt + ', '
            if each.bsd_phuong_tt_id:
                each.bsd_dia_chi_tt += each.bsd_phuong_tt_id.bsd_ten + ', '
            if each.bsd_quan_tt_id:
                each.bsd_dia_chi_tt += each.bsd_quan_tt_id.bsd_ten + ', '
            if each.bsd_tinh_tt_id:
                each.bsd_dia_chi_tt += each.bsd_tinh_tt_id.name + ', '
            if each.bsd_quoc_gia_tt_id:
                each.bsd_dia_chi_tt += each.bsd_quoc_gia_tt_id.name

    # R.03 Tạo thông tin địa chỉ liên hệ
    @api.depends('bsd_quoc_gia_lh_id', 'bsd_tinh_lh_id', 'bsd_quan_lh_id', 'bsd_phuong_lh_id', 'bsd_so_nha_lh')
    def _compute_dia_chi_lh(self):
        for each in self:
            each.bsd_dia_chi_lh = ''
            if each.bsd_so_nha_lh:
                each.bsd_dia_chi_lh += each.bsd_so_nha_lh + ', '
            if each.bsd_phuong_lh_id:
                each.bsd_dia_chi_lh += each.bsd_phuong_lh_id.bsd_ten + ', '
            if each.bsd_quan_lh_id:
                each.bsd_dia_chi_lh += each.bsd_quan_lh_id.bsd_ten + ', '
            if each.bsd_tinh_lh_id:
                each.bsd_dia_chi_lh += each.bsd_tinh_lh_id.name + ', '
            if each.bsd_quoc_gia_lh_id:
                each.bsd_dia_chi_lh += each.bsd_quoc_gia_lh_id.name

    @api.model
    def create(self, vals):
        sequence = False
        if vals.get('bsd_ma_kh', '/') == '/' and not vals.get('company_type'):
            sequence = self.env['bsd.ma_bo_cn_chung'].search([('bsd_loai_cn', '=', 'bsd.kh_cn'),
                                                              ('state', '=', 'active')], limit=1).bsd_ma_tt_id
        if vals.get('bsd_ma_kh', '/') == '/' and vals.get('company_type') == 'company':
            sequence = self.env['bsd.ma_bo_cn_chung'].search([('bsd_loai_cn', '=', 'bsd.kh_dn'),
                                                              ('state', '=', 'active')], limit=1).bsd_ma_tt_id
        _logger.debug("Tạo khách hàng")
        _logger.debug(vals)
        _logger.debug(sequence)
        if not sequence:
            raise UserError(_('Danh mục mã dùng chung chưa khai báo mã khách hàng.'))
        if sequence:
            vals['bsd_ma_kh'] = sequence.next_by_id()
        # Kiểm tra field cũng là địa chỉ thường trú
        if vals.get('bsd_cung_dc'):
            _logger.debug("tạo địa chỉ thường trứ")
            if not vals.get('bsd_quoc_gia_tt_id'):
                vals['bsd_quoc_gia_tt_id'] = vals.get('bsd_quoc_gia_lh_id')
            if not vals.get('bsd_tinh_tt_id'):
                vals['bsd_tinh_tt_id'] = vals.get('bsd_tinh_lh_id')
            if not vals.get('bsd_quan_tt_id'):
                vals['bsd_quan_tt_id'] = vals.get('bsd_quan_lh_id')
            if not vals.get('bsd_phuong_tt_id'):
                vals['bsd_phuong_tt_id'] = vals.get('bsd_phuong_lh_id')
            if not vals.get('bsd_so_nha_tt'):
                vals['bsd_so_nha_tt'] = vals.get('bsd_so_nha_lh')
        # Kiểm tra field cũng là địa chỉ trụ sở
        if vals.get('bsd_cung_ts'):
            vals['bsd_quoc_gia_ts_id'] = vals.get('bsd_quoc_gia_lh_id')
            vals['bsd_tinh_ts_id'] = vals.get('bsd_tinh_lh_id')
            vals['bsd_quan_ts_id'] = vals.get('bsd_quan_lh_id')
            vals['bsd_phuong_ts_id'] = vals.get('bsd_phuong_lh_id')
            vals['bsd_so_nha_ts'] = vals.get('bsd_so_nha_lh')

        # Cập nhật nhân viên kinh doanh assign
        vals['user_id'] = self.env.uid
        res = super(ResPartner, self).create(vals)
        return res

    def _get_name(self):
        partner = self
        name = partner.display_name or ''
        if self._context.get('show_ma_kh') and partner.bsd_ma_kh:
            name = "%s <%s>" % (name, partner.bsd_ma_kh)
        return name

    def name_get(self):
        res = []
        for partner in self:
            name = partner._get_name()
            res.append((partner.id, name))
        return res

    @api.depends('is_company', 'name', 'bsd_ho_tl')
    def _compute_display_name(self):
        for partner in self:
            if partner.is_company:
                partner.display_name = partner.name
            else:
                partner.display_name = (partner.bsd_ho_tl or '') + (' ' + (partner.name or ''))

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            if operator == 'ilike':
                args += [('bsd_search_ten', operator, name)]
            elif operator == '=':
                args += [('bsd_cmnd', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return models.lazy_name_get(recs.with_user(access_rights_uid))


class BsdLoaikhcn(models.Model):
    _name = 'bsd.loai_kh_cn'
    _rec_name = 'bsd_ten'

    bsd_ten = fields.Char(string="Loại khách hàng", required=True)
