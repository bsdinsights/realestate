# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdPLDSH(models.Model):
    _name = 'bsd.pl_dsh'
    _description = "Phụ lục đồng sở hữu"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_pl_dsh'

    bsd_ma_pl_dsh = fields.Char(string="Mã", help="Mã phụ lục hợp đồng thay đổi chủ sở hữu",
                                required=True, readonly=True,
                                copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_pl_dsh_unique', 'unique (bsd_ma_pl_dsh)',
         'Mã phụ lục hợp đồng đã tồn tại !'),
    ]
    bsd_ngay_pl_dsh = fields.Datetime(string="Ngày", help="Ngày phụ lục hợp đồng", required=True,
                                      default=lambda self: fields.Datetime.now(),
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng mua bán", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd(self):
        self.bsd_du_an_id = self.bsd_hd_ban_id.bsd_du_an_id
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True, readonly=True)

    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Tên Sản phẩm", required=True, readonly=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_ky_pl = fields.Date(string="Ngày ký PL", help="Ngày ký phụ lục hợp đồng", readonly=True)
    bsd_nguoi_xn_ky_id = fields.Many2one('res.users', string="Người xác nhận ký",
                                         help="Người xác nhận ký phụ lục hợp đồng", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", help="Ngày duyệt phụ lục hợp đồng", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", help="Ngày xác nhận phụ lục hợp đồng", readonly=True)
    bsd_nguoi_huy_id = fields.Many2one('res.users', string="Người hủy", readonly=True)
    bsd_ngay_huy = fields.Date(string="Ngày hủy", help="Ngày hủy phụ lục hợp đồng", readonly=True)
    bsd_ly_do_huy = fields.Char(string="Lý do hủy", help="Lý do hủy phụ lục", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'), ('duyet', 'Duyệt'),
                              ('dk_pl', 'Đã ký phụ lục'), ('huy', 'Hủy')],
                             string="Trạng thái", help="Trạng thái", required=True, default="nhap", tracking=1)
    bsd_ly_do = fields.Char(string="Lý do không duyệt", readonly=True, tracking=2)
    bsd_moi_ids = fields.One2many('bsd.pl_dsh_moi', 'bsd_pl_dsh_id', string="Đồng sở hữu mới",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_cu_ids = fields.One2many('bsd.pl_dsh_cu', 'bsd_pl_dsh_id', string="Đồng sở hữu cũ", readonly=True)

    # DV.02.01 - Xác nhận phụ lục hợp đồng
    def action_xac_nhan(self):
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_("Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin."))
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
                'bsd_ngay_xn': fields.Date.today(),
                'bsd_nguoi_xn_id': self.env.uid,
            })

    # Hủy phụ lục hợp đồng
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            return self.env.ref('bsd_dich_vu.bsd_wizard_huy_pl_action').read()[0]

    # Không duyệt phụ lục hợp đồng
    def action_khong_duyet(self):
        if self.state == 'xac_nhan':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_khong_duyet_pl_action').read()[0]
            return action

    def action_duyet(self):
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_("Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin."))
        if self.state == 'xac_nhan':
            self.write({
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ngay_duyet': fields.Date.today(),
                'state': 'duyet',
            })

    # Ký phụ lục hợp đồng
    def action_ky_pl(self):
        # Kiểm tra hợp đồng đã bị thanh lý chưa
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_("Hợp đồng đã bị thanh lý.\nVui lòng kiểm tra lại thông tin."))
        if self.state == 'duyet':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_pl_action').read()[0]
            return action

    # DV.02.04 - Cập nhật đồng sở hữu mới trên hợp đồng
    def update_dsh(self):
        old_dsh = self.bsd_hd_ban_id.bsd_dong_sh_ids
        new_dsh = self.env['bsd.dong_so_huu']
        if not old_dsh:
            for moi in self.bsd_moi_ids:
                new_dsh.create({
                    'bsd_dong_sh_id': moi.bsd_dong_sh_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_pl_dsh_id': self.id,
                    'bsd_lan_td': 1,
                    'bsd_quan_he': moi.bsd_quan_he,
                    'state': 'active',
                })
        else:
            old_dsh_active = old_dsh.filtered(lambda o: o.state == 'active')
            if old_dsh_active:
                old_dsh_active.write({
                    'state': 'inactive'
                })
            lan_td = max(old_dsh.mapped('bsd_lan_td'))
            for moi in self.bsd_moi_ids:
                new_dsh.create({
                    'bsd_dong_sh_id': moi.bsd_dong_sh_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_pl_dsh_id': self.id,
                    'bsd_lan_td': lan_td + 1,
                    'bsd_quan_he': moi.bsd_quan_he,
                    'state': 'active',
                })

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có quy định mã phụ lục thay đổi đồng sở hữu.'))
        vals['bsd_ma_pl_dsh'] = sequence.next_by_id()
        res = super(BsdPLDSH, self).create(vals)
        # R.04 lọc các đồng sở hữu cũ
        ids_dsh = res.bsd_hd_ban_id.bsd_dong_sh_ids.filtered(lambda x: x.state == 'active')
        _logger.debug(ids_dsh)
        for id_dsh in ids_dsh:
            res.bsd_cu_ids.create({
                'bsd_dong_sh_id': id_dsh.bsd_dong_sh_id.id,
                'bsd_pl_dsh_id': res.id,
                'bsd_quan_he': id_dsh.bsd_quan_he,
            })
        return res


class BsdPLDSHMoi(models.Model):
    _name = 'bsd.pl_dsh_moi'
    _description = "Danh sách đồng sở hữu mới"

    bsd_dong_sh_id = fields.Many2one('res.partner', string="Đồng sở hữu", required=True)
    bsd_mobile = fields.Char(related='bsd_dong_sh_id.mobile', string="Di động")
    bsd_email = fields.Char(related='bsd_dong_sh_id.email', string="Email")
    bsd_quan_he = fields.Selection([('vo', 'Vợ'),
                                    ('chong', 'Chồng'),
                                    ('con', 'Con'),
                                    ('chau', 'Cháu'),
                                    ('nguoi_than', 'Người thân'),
                                    ('ban', 'Bạn'),
                                    ('khac', 'Khác')
                                    ], string="Mối quan hệ", required=True)
    bsd_pl_dsh_id = fields.Many2one('bsd.pl_dsh', string="Phụ lục HĐ", help="Mã phụ lục hợp đồng thay đổi chủ sở hữu")


class BsdPLDSHCu(models.Model):
    _name = 'bsd.pl_dsh_cu'
    _description = "Danh sách đồng sở hữu cũ"

    bsd_dong_sh_id = fields.Many2one('res.partner', string="Đồng sở hữu", required=True)
    bsd_mobile = fields.Char(related='bsd_dong_sh_id.mobile', string="Di động")
    bsd_email = fields.Char(related='bsd_dong_sh_id.email', string="Email")
    bsd_quan_he = fields.Selection([('vo', 'Vợ'),
                                    ('chong', 'Chồng'),
                                    ('con', 'Con'),
                                    ('chau', 'Cháu'),
                                    ('nguoi_than', 'Người thân'),
                                    ('ban', 'Bạn'),
                                    ('khac', 'Khác')
                                    ], string="Mối quan hệ", required=True)
    bsd_pl_dsh_id = fields.Many2one('bsd.pl_dsh', string="Phụ lục HĐ", help="Mã phụ lục hợp đồng thay đổi chủ sở hữu")
