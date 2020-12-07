# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdWizardTTDOT(models.TransientModel):
    _name = 'bsd.wizard.tt_hd'
    _description = 'Thanh toán nhanh các đợt thanh toán của hợp đồng'
    _rec_name = 'bsd_hd_ban_id'

    bsd_ngay_pt = fields.Date(string="Ngày thanh toán", help="Ngày thanh toán", required=True,
                              default=lambda self: fields.Date.today())
    bsd_loai = fields.Selection([('dtt', 'Đợt thanh toán'),
                                 ('pbt_pql', 'Phí bảo trì và Phí quản lý'),
                                 ('lp', 'Tiền phạt chậm TT'),
                                 ('pps', 'Phí phát sinh')], string="Loại thanh toán",
                                default='dtt',
                                required=True)

    @api.constrains('bsd_ngay_pt')
    def _constrains_ngay_pt(self):
        today = datetime.date.today()
        if self.bsd_ngay_pt > today:
            raise UserError(_("Ngày thanh toán không được lớn hơn ngày hiện tại."))

    @api.constrains('bsd_tien_con_lai')
    def _constrains_tien_con_lai(self):
        if self.bsd_tien_con_lai < 0:
            raise UserError(_("Tiền còn lại không thể âm.\nVui lòng kiểm tra lại thông tin"))

    @api.model
    def default_get(self, fields_list):
        res = super(BsdWizardTTDOT, self).default_get(fields_list)
        hd_ban = self.env['bsd.hd_ban'].browse(self._context.get('active_ids', []))
        res.update({
            'bsd_hd_ban_id': hd_ban.id,
            'bsd_unit_id': hd_ban.bsd_unit_id.id,
            'bsd_khach_hang_id': hd_ban.bsd_khach_hang_id.id,
            'bsd_du_an_id': hd_ban.bsd_du_an_id.id,
        })
        return res

    @api.onchange('bsd_ltt_ids', 'bsd_dot_phi_ids', 'bsd_tien_kh',
                  'bsd_phi_ps_ids', 'bsd_loai', 'bsd_dot_lp_ids')
    def _onchange_tien(self):
        _logger.debug("call tính tiền")
        if self.bsd_loai == 'dtt':
            self.bsd_tien_con_lai = self.bsd_tien_kh - \
                sum(self.bsd_ltt_ids.mapped(lambda r: r.bsd_tien_tt + r.bsd_tt_phat)) - \
                sum(self.bsd_dot_phi_ids.mapped(lambda r: r.bsd_tien_tt)) - \
                sum(self.bsd_phi_ps_ids.mapped(lambda r: r.bsd_tien_tt))
        else:
            self.bsd_tien_con_lai = self.bsd_tien_kh - \
                sum(self.bsd_dot_phi_ids.mapped(lambda r: r.bsd_tien_tt)) - \
                sum(self.bsd_phi_ps_ids.mapped(lambda r: r.bsd_tien_tt)) - \
                sum(self.bsd_dot_lp_ids.mapped(lambda r: r.bsd_tt_phat))

    @api.onchange('bsd_ngay_pt')
    def _onchange_dot_tt(self):
        # Tổng tiền các đợt thanh toán đã chọn
        # Tính tổng tiền phạt thanh toán
        _logger.debug("thay đổi ngày tt")
        cs_tt = self.bsd_hd_ban_id.bsd_cs_tt_id
        for ct in self.bsd_ltt_ids:
            dot_tt = ct.bsd_dot_tt_id
            # Kiểm tra ngày làm mốc tính lãi phạt
            han_tinh_phat = dot_tt.bsd_ngay_hh_tt
            if dot_tt.bsd_tinh_phat == 'nah':
                han_tinh_phat = dot_tt.bsd_ngay_ah
            # Số ngày tính lãi phạt
            so_ngay_nam = cs_tt.bsd_lai_phat_tt_id.bsd_so_ngay_nam
            if self.bsd_ngay_pt > han_tinh_phat:
                # Số ngày tính phạt
                so_ngay_tp = (self.bsd_ngay_pt - han_tinh_phat).days
                # Tính lãi phạt
                tien_phat = float_round(ct.bsd_tien_tt * (dot_tt.bsd_lai_phat/100 / so_ngay_nam) * so_ngay_tp, 0)
                # Kiểm tra lãi phạt đã vượt lãi phạt tối đa của đợt chưa
                tong_tien_phat = dot_tt.bsd_tien_phat + tien_phat
                if dot_tt.bsd_tien_td == 0 and dot_tt.bsd_tl_td != 0:
                    tien_phat_toi_da = dot_tt.bsd_tien_dot_tt * dot_tt.bsd_tl_td / 100
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
                elif dot_tt.bsd_tien_td != 0 and dot_tt.bsd_tl_td == 0:
                    tien_phat_toi_da = dot_tt.bsd_tien_td
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
                elif dot_tt.bsd_tien_td != 0 and dot_tt.bsd_tl_td != 0:
                    tien_phat_toi_da_1 = dot_tt.bsd_tien_dot_tt * dot_tt.bsd_tl_td / 100
                    tien_phat_toi_da_2 = dot_tt.bsd_tien_td
                    tien_phat_toi_da = tien_phat_toi_da_1 if tien_phat_toi_da_1 < tien_phat_toi_da_2 else tien_phat_toi_da_2
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
            else:
                tien_phat = 0
            ct.update({
                'bsd_tien_lp_ut': tien_phat
            })

    # def _get_pt(self):
    #     return self.env.ref('bsd_danh_muc.bsd_tien_mat').id

    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True)
    # bsd_pt_tt_id = fields.Many2one('bsd.pt_tt', string="Hình thức", help="Hình thức thanh toán",
    #                                required=True, default=_get_pt)
    # bsd_so_nk = fields.Selection([('tien_mat', 'Tiền mặt'), ('ngan_hang', 'Ngân hàng')], string="Sổ nhật ký",
    #                              required=True, default="tien_mat")
    # bsd_tk_nh_id = fields.Many2one('res.partner.bank', string="Tài khoản ngân hàng",
    #                                help="Số tài khoản ngân hàng của khách hàng")
    # bsd_ngan_hang_id = fields.Many2one('res.bank', string="Tên ngân hàng", help="Tên ngân hàng")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True)
    bsd_tien_kh = fields.Monetary(string="Tiền", help="Tiền", required=True)
    bsd_tien_con_lai = fields.Monetary(string="Còn lại", help="Còn lại")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ltt_ids = fields.One2many('bsd.wizard.ct_dot', 'bsd_wizard_tt_id', string="Đợt thanh toán")

    bsd_dot_phi_ids = fields.One2many('bsd.wizard.ct_phi', 'bsd_wizard_tt_id', string="Phí")
    bsd_so_phi = fields.Integer(string="# Phí", compute='_compute_phi', store=True)

    @api.depends('bsd_dot_phi_ids')
    def _compute_phi(self):
        for each in self:
            each.bsd_so_phi = len(each.bsd_dot_phi_ids)

    bsd_phi_ps_ids = fields.One2many('bsd.wizard.ct_pps', 'bsd_wizard_tt_id', string="Phí phát sinh")
    bsd_so_pps = fields.Integer(string="# Phí ps", compute='_compute_pps', store=True)

    @api.depends('bsd_phi_ps_ids')
    def _compute_pps(self):
        for each in self:
            each.bsd_so_pps = len(each.bsd_phi_ps_ids)

    bsd_dot_lp_ids = fields.One2many('bsd.wizard.ct_lp', 'bsd_wizard_tt_id', string="Phí")
    bsd_so_lp = fields.Integer(string="# Phí", compute='_compute_lp', store=True)

    @api.depends('bsd_dot_lp_ids')
    def _compute_lp(self):
        for each in self:
            each.bsd_so_lp = len(each.bsd_dot_lp_ids)

    def action_tao(self):
        # Tạo thanh toán
        now = datetime.datetime.now()
        get_time = now.replace(year=self.bsd_ngay_pt.year,
                               month=self.bsd_ngay_pt.month,
                               day=self.bsd_ngay_pt.day)
        phieu_thu = self.env['bsd.phieu_thu'].create({
            'bsd_ngay_pt': get_time,
            'bsd_loai_pt': 'hd',
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_unit_id': self.bsd_unit_id.id,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_tien_kh': self.bsd_tien_kh,
        })
        # Tạo công nợ chứng từ cho đợt thanh toán theo thứ tự
        for dot in self.bsd_ltt_ids.filtered(lambda x: x.bsd_tien_tt > 0):
            self.env['bsd.cong_no_ct'].create({
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                'bsd_dot_tt_id': dot.bsd_dot_tt_id.id,
                'bsd_phieu_thu_id': phieu_thu.id,
                'bsd_tien_pb': dot.bsd_tien_tt,
                'bsd_loai': 'pt_dtt',
                'state': 'nhap',
            })
        # Tạo công nợ chứng từ cho phi
        for phi in self.bsd_dot_phi_ids.filtered(lambda x: x.bsd_tien_tt > 0):
            # kiểm tra phí bảo trì hay quản lý
            if phi.bsd_phi_tt_id.bsd_loai == 'pbt':
                self.env['bsd.cong_no_ct'].create({
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_dot_tt_id': phi.bsd_phi_tt_id.id,
                    'bsd_phieu_thu_id': phieu_thu.id,
                    'bsd_tien_pb': phi.bsd_tien_tt,
                    'bsd_loai': 'pt_pbt',
                    'state': 'nhap',
                })
            else:
                self.env['bsd.cong_no_ct'].create({
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_dot_tt_id': phi.bsd_phi_tt_id.id,
                    'bsd_phieu_thu_id': phieu_thu.id,
                    'bsd_tien_pb': phi.bsd_tien_tt,
                    'bsd_loai': 'pt_pql',
                    'state': 'nhap',
                })
        # Tạo công nợ chứng từ phí phát sinh
        for pps in self.bsd_phi_ps_ids:
            self.env['bsd.cong_no_ct'].create({
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                'bsd_phi_ps_id': pps.bsd_pps_id.id,
                'bsd_phieu_thu_id': phieu_thu.id,
                'bsd_tien_pb': pps.bsd_tien_tt,
                'bsd_loai': 'pt_pps',
                'state': 'nhap',
            })
        # Tạo công nợ chứng từ lãi phạt
        if self.bsd_loai == 'dtt':
            dot_lp = self.bsd_ltt_ids.filtered(lambda x: x.bsd_tt_phat > 0)
        else:
            dot_lp = self.bsd_dot_lp_ids.filtered(lambda x: x.bsd_tt_phat > 0)
        for lp in dot_lp:
            dot_tt = lp.bsd_dot_tt_id
            tien_lp = lp.bsd_tt_phat
            lai_phat_dot = self.env['bsd.lai_phat'].search([('bsd_dot_tt_id', '=', dot_tt.id)]).sorted('bsd_ngay_lp')
            for lai_phat in lai_phat_dot:
                if tien_lp > lai_phat.bsd_tien_phat:
                    tien_phat = lai_phat.bsd_tien_phat
                    tien_lp = tien_lp - lai_phat.bsd_tien_phat
                else:
                    tien_phat = tien_lp
                self.env['bsd.cong_no_ct'].create({
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_lai_phat_id': lai_phat.id,
                    'bsd_phieu_thu_id': phieu_thu.id,
                    'bsd_tien_pb': tien_phat,
                    'bsd_loai': 'pt_lp',
                    'state': 'nhap',
                })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Thanh toán',
            'res_model': 'bsd.phieu_thu',
            'res_id': phieu_thu.id,
            'target': 'current',
            'view_mode': 'form'
        }


class BsdWizardChitietDot(models.TransientModel):
    _name = 'bsd.wizard.ct_dot'
    _rec_name = 'bsd_dot_tt_id'
    
    bsd_wizard_tt_id = fields.Many2one('bsd.wizard.tt_hd', string="TT")
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt TT",
                                    readonly=True,
                                    help="Đợt thanh toán của hợp đồng")
    bsd_tien_dot_tt = fields.Monetary(related='bsd_dot_tt_id.bsd_tien_dot_tt')
    bsd_tien_phai_tt = fields.Monetary(related='bsd_dot_tt_id.bsd_tien_phai_tt', string="Phải thanh toán")
    bsd_tien_tt = fields.Monetary(string="TT Đợt", help="Tiền thanh toán đợt")
    bsd_tien_lp = fields.Monetary(related='bsd_dot_tt_id.bsd_tp_phai_tt', string="Tiền phạt")
    bsd_tt_phat = fields.Monetary(string="TT phạt", help="Tiền thanh toán tiền phạt chậm thanh toán đã phát sinh")
    bsd_tien_lp_ut = fields.Monetary(string="Ước tính phạt",
                                     help="Tiền phạt ước tính của đợt khi thanh toán")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_tien_tt')
    def _onchange_tien_tt(self):
        _logger.debug("Tính lại lãi phạt tt")
        if self.bsd_tien_tt > 0:
            dot_tt = self.bsd_dot_tt_id
            ngay_tt = self.bsd_wizard_tt_id.bsd_ngay_pt
            cs_tt = self.bsd_dot_tt_id.bsd_cs_tt_id
            # Kiểm tra ngày làm mốc tính lãi phạt
            han_tinh_phat = dot_tt.bsd_ngay_hh_tt
            if dot_tt.bsd_tinh_phat == 'nah':
                han_tinh_phat = dot_tt.bsd_ngay_ah
            # Số ngày tính lãi phạt
            so_ngay_nam = cs_tt.bsd_lai_phat_tt_id.bsd_so_ngay_nam
            if ngay_tt > han_tinh_phat:
                # Số ngày tính phạt
                so_ngay_tp = (ngay_tt - han_tinh_phat).days
                # Tính lãi phạt
                tien_phat = float_round(self.bsd_tien_tt * (dot_tt.bsd_lai_phat/100 / so_ngay_nam) * so_ngay_tp, 0)
                # Kiểm tra lãi phạt đã vượt lãi phạt tối đa của đợt chưa
                tong_tien_phat = dot_tt.bsd_tien_phat + tien_phat
                if dot_tt.bsd_tien_td == 0 and dot_tt.bsd_tl_td != 0:
                    tien_phat_toi_da = dot_tt.bsd_tien_dot_tt * dot_tt.bsd_tl_td / 100
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
                elif dot_tt.bsd_tien_td != 0 and dot_tt.bsd_tl_td == 0:
                    tien_phat_toi_da = dot_tt.bsd_tien_td
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
                elif dot_tt.bsd_tien_td != 0 and dot_tt.bsd_tl_td != 0:
                    tien_phat_toi_da_1 = dot_tt.bsd_tien_dot_tt * dot_tt.bsd_tl_td / 100
                    tien_phat_toi_da_2 = dot_tt.bsd_tien_td
                    tien_phat_toi_da = tien_phat_toi_da_1 if tien_phat_toi_da_1 < tien_phat_toi_da_2 else tien_phat_toi_da_2
                    if tong_tien_phat > tien_phat_toi_da:
                        tien_phat = tien_phat_toi_da - dot_tt.bsd_tien_phat
            else:
                tien_phat = 0
            self.bsd_tien_lp_ut = tien_phat

    @api.constrains('bsd_tien_phai_tt', 'bsd_tien_tt')
    def _constraint_tien_tt(self):
        if self.bsd_tien_tt > self.bsd_tien_phai_tt:
            raise UserError(_("Tiền thanh toán đợt không thể lớn hơn tiền phải thanh toán.\n"
                              "Vui lòng kiểm tra lại thông tin."))

    @api.constrains('bsd_tien_lp', 'bsd_tt_phat')
    def _constraint_tien_phat(self):
        if self.bsd_tt_phat > self.bsd_tien_lp:
            raise UserError(_("Tiền thanh toán phạt đợt không thể lớn hơn tiền phạt chậm thanh toán.\n"
                              "Vui lòng kiểm tra lại thông tin."))


class BsdWizardChitietPhi(models.TransientModel):
    _name = 'bsd.wizard.ct_phi'
    _rec_name = 'bsd_phi_tt_id'

    bsd_wizard_tt_id = fields.Many2one('bsd.wizard.tt_hd', string="TT")
    bsd_phi_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Phí", help="Phí bảo trì, phí quản lý của hợp đồng")
    bsd_tien_phi_tt = fields.Monetary(related='bsd_phi_tt_id.bsd_tien_dot_tt')
    bsd_tien_phai_tt = fields.Monetary(related='bsd_phi_tt_id.bsd_tien_phai_tt', string="Phải TT")
    bsd_tien_tt = fields.Monetary(string="Tiền TT", help="Tiền thanh toán phí")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    
    
class BsdWizardChitietPPS(models.TransientModel):
    _name = 'bsd.wizard.ct_pps'
    _rec_name = 'bsd_pps_id'

    bsd_wizard_tt_id = fields.Many2one('bsd.wizard.tt_hd', string="TT")
    bsd_pps_id = fields.Many2one('bsd.phi_ps', string="Phí phát sinh", help="Phí phát sinh của hợp đồng")
    bsd_tien_phi_tt = fields.Monetary(related='bsd_pps_id.bsd_tong_tien', string="Tiền phát sinh")
    bsd_tien_phai_tt = fields.Monetary(related='bsd_pps_id.bsd_tien_phai_tt', string="Phải TT")
    bsd_tien_tt = fields.Monetary(string="Tiền TT", help="Tiền thanh toán phí phát sinh")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)


class BsdWizardChitietLP(models.TransientModel):
    _name = 'bsd.wizard.ct_lp'
    _rec_name = 'bsd_dot_lp_id'

    bsd_wizard_tt_id = fields.Many2one('bsd.wizard.tt_hd', string="TT")
    bsd_dot_lp_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt tính phạt", help="Đợt thanh toán của hợp đồng")
    bsd_tien_pl = fields.Monetary(related='bsd_dot_lp_id.bsd_tien_phat', string="Tiền phạt")
    bsd_tp_phai_tt = fields.Monetary(related='bsd_dot_lp_id.bsd_tp_phai_tt')
    bsd_tt_phat = fields.Monetary(string="TT phạt", help="Tiền thanh toán phạt")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)