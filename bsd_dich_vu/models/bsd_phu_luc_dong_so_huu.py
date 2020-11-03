# -*- coding:utf-8 -*-

from odoo import models, fields, api
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdPLDSH(models.Model):
    _name = 'bsd.pl_dsh'
    _description = "Phụ lục đồng sở hữu"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_pl_dsh'

    bsd_ma_pl_dsh = fields.Char(string="Mã", help="Mã phụ lục hợp đồng thay đổi chủ sở hữu", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
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
    bsd_du_an_id = fields.Many2one(string="Dự án", help="Tên dự án", related='bsd_hd_ban_id.bsd_du_an_id', store=True)
    bsd_unit_id = fields.Many2one(string="Sản phẩm", help="Tên Sản phẩm", related='bsd_hd_ban_id.bsd_unit_id', store=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_ky_pl = fields.Datetime(string="Ngày ký phụ lục", help="Ngày ký phụ lục đồng sở hữu", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('dk_pl', 'Đã ký phụ lục'), ('huy', 'Hủy')],
                             string="Trạng thái", help="Trạng thái", required=True, default="nhap", tracking=1)
    bsd_moi_ids = fields.One2many('bsd.pl_dsh_moi', 'bsd_pl_dsh_id', string="Đồng sở hữu mới",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_cu_ids = fields.One2many('bsd.pl_dsh_cu', 'bsd_pl_dsh_id', string="Đồng sở hữu cũ", readonly=True)

    # DV.02.01 - Xác nhận phụ lục hợp đồng
    def action_xac_nhan(self):
        self.write({
            'state': 'xac_nhan',
        })

    # DV.02.02 - Ký phụ lục hợp đồng
    def action_ky_pl(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_pl_dsh_action').read()[0]
        return action

    # DV.02.03 - Hủy phụ lục hợp đồng
    def action_huy(self):
        self.write({
            'state': 'huy'
        })

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
