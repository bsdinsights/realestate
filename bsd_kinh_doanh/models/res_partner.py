# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsd_ho_tl = fields.Char(string="Họ và tên lót", help="Họ và tên lót")
    bsd_ten = fields.Char(string="Họ và tên", help="Tên khách hàng")
    bsd_search_ten = fields.Char(string="Search tên", compute='_compute_search_name', store=True)

    @api.depends('bsd_ten', 'bsd_cmnd', 'bsd_ma_kh')
    def _compute_search_name(self):
        for each in self:
            each.bsd_search_ten = (each.bsd_cmnd or '') + ' - ' + (each.bsd_ma_kh or '') + ' - ' + (each.bsd_ten or '')

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
    bsd_nguoi_bh = fields.Boolean(string="Người bảo hộ", help="Khách hàng có người bảo hộ")
    bsd_cmnd = fields.Char(string="CMND/ CCCD", help="Số CMND/ CCCD")
    bsd_ngay_cap_cmnd = fields.Date(string="Ngày cấp CMND", help="Ngày cấp CMND/ CCCD")
    bsd_noi_cap_cmnd = fields.Many2one('res.country.state', string="Nơi cấp CMND", help="Nơi cấp CMND")
    bsd_ho_chieu = fields.Char(string="Hộ chiếu", help="Số hộ chiếu")
    bsd_ngay_cap_hc = fields.Date(string="Ngày cấp hộ chiếu", help="Ngày cấp hộ chiếu")
    bsd_noi_cap_hc = fields.Many2one('res.country.state', string="Nơi cấp hộ chiếu", help="Nơi cấp hộ chiếu")
    bsd_mst = fields.Char(string="Mã số thuế", help="Mã số thuế khách hàng")
    bsd_dia_chi_tt = fields.Char(string="Địa chỉ thường trú", help="Địa chỉ thường trú",
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

    bsd_giu_cho_ids = fields.One2many('bsd.giu_cho', 'bsd_kh_moi_id', string="DS giữ chỗ",
                                      domain=[('state', '!=', 'nhap')], readonly=True)
    bsd_bao_gia_ids = fields.One2many('bsd.bao_gia', 'bsd_khach_hang_id', string="DS bảng tính giá",
                                      domain=[('state', '!=', 'nhap')], readonly=True)
    bsd_dat_coc_ids = fields.One2many('bsd.dat_coc', 'bsd_khach_hang_id', string="DS đặt cọc",
                                      domain=[('state', '!=', 'nhap')], reaonly=True)
    bsd_sl_giu_cho = fields.Integer(string="# Giữ chỗ", compute="_compute_sl_gc", store=True)

    @api.constrains('bsd_cmnd')
    def _constrains_cmnd(self):
        if self.env['res.users'].has_group('bsd_kinh_doanh.group_manager'):
            pass
        else:
            khach_hang = self.env['res.partner'].search([('bsd_cmnd', '=', self.bsd_cmnd),
                                                         ('id', '!=', self.id)])
            if khach_hang:
                raise UserError("Chứng minh nhân dân đã được sử dụng")

    @api.constrains('bsd_ngay_sinh')
    def _constrains_ngay_sinh(self):
        if not self.bsd_nguoi_bh:
            nam_ht = fields.Date.today().year
            nam_sinh = self.bsd_ngay_sinh.year
            if nam_ht - nam_sinh < 18:
                raise UserError(_("Khách hàng chưa đủ 18 tuổi, vui lòng kiểm tra lại"))

    @api.constrains('email')
    def _constrains_email(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            _logger.debug(match)
            if not match:
                raise ValidationError('Nhập thông tin email không đúng')

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
        _logger.debug("tạo partner")
        _logger.debug(vals)
        _logger.debug(vals.get('bsd_la_kh'))
        sequence = False
        if vals.get('bsd_ma_kh', '/') == '/' and not vals.get('is_company') and vals.get('bsd_la_kh'):
            sequence = self.env['bsd.ma_bo_cn'].search([('bsd_loai_cn', '=', 'bsd.kh_cn')], limit=1).bsd_ma_tt_id
            vals['bsd_ma_kh'] = self.env['ir.sequence'].next_by_code('bsd.kh_cn') or '/'
        if vals.get('bsd_ma_kh', '/') == '/' and vals.get('is_company') and vals.get('bsd_la_kh'):
            sequence = self.env['bsd.ma_bo_cn'].search([('bsd_loai_cn', '=', 'bsd.kh_dn')], limit=1).bsd_ma_tt_id
        if not sequence and vals.get('bsd_la_kh'):
            raise UserError(_('Danh mục mã chưa khai báo mã khách hàng'))
        if sequence:
            vals['bsd_ma_kh'] = sequence.next_by_id()
        return super(ResPartner, self).create(vals)

    def name_get(self):
        res = []
        for partner in self:
            if not partner.is_company:
                if partner.bsd_la_kh:
                    res.append((partner.id, "[%s]%s" % (partner.bsd_ma_kh, partner.bsd_ten)))
                else:
                    res.append((partner.id, "%s" % partner.name))
            else:
                if partner.bsd_la_kh:
                    res.append((partner.id, "[%s]%s" % (partner.bsd_ma_kh, partner.name)))
                else:
                    res.append((partner.id, "%s" % partner.name))
        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if not (name == '' and operator == 'ilike'):
            args += [('bsd_search_ten', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return models.lazy_name_get(recs.with_user(access_rights_uid))


class BsdLoaikhcn(models.Model):
    _name = 'bsd.loai_kh_cn'
    _rec_name = 'bsd_ten'

    bsd_ten = fields.Char(string="Loại khách hàng", required=True)
