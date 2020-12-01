# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdWizardTTDOT(models.TransientModel):
    _name = 'bsd.wizard.tt_dot'
    _description = 'Thanh toán nhanh các đợt thanh toán của hợp đồng'
    _rec_name = 'bsd_hd_ban_id'

    bsd_ngay_pt = fields.Date(string="Ngày thanh toán", help="Ngày thanh toán", required=True,
                              default=lambda self: fields.Date.today())

    @api.constrains('bsd_ngay_pt')
    def _constrains_ngay_pt(self):
        today = datetime.date.today()
        if self.bsd_ngay_pt > today:
            raise UserError(_("Ngày thanh toán không được lớn hơn ngày hiện tại."))

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

    @api.onchange('bsd_hd_ban_id')
    def _onchange_ck(self):
        res = {}
        list_dtt = self.bsd_hd_ban_id.bsd_ltt_ids\
                       .filtered(lambda x: x.bsd_thanh_toan != 'da_tt' and x.bsd_loai == 'dtt').ids or []
        res.update({
            'domain': {
                'bsd_ltt_ids': [('id', 'in', list_dtt)],
            }
        })
        return res

    @api.onchange('bsd_ltt_ids')
    def _onchange_dot_tt(self):
        # Tổng tiền các đợt thanh toán đã chọn
        # Tính tổng tiền phạt thanh toán
        dot_tt_ids = self.bsd_ltt_ids.sorted('bsd_stt')
        cs_tt = self.bsd_hd_ban_id.bsd_cs_tt_id
        tong_so_ngay_phat = 0
        tong_tien_phat = 0
        _logger.debug("số lần lập")
        _logger.debug(dot_tt_ids)
        for dot_tt in dot_tt_ids:
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
                tien_phat = float_round(dot_tt.bsd_tien_phai_tt * (dot_tt.bsd_lai_phat/100 / so_ngay_nam) * so_ngay_tp, 0)
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
                so_ngay_tp = 0
                tien_phat = 0
            _logger.debug("tiền từng đợt")
            _logger.debug(tien_phat)
            _logger.debug(dot_tt)
            tong_tien_phat += tien_phat
            tong_so_ngay_phat += so_ngay_tp
        _logger.debug("tổng tiền")
        _logger.debug(tong_tien_phat)
        self.bsd_tien_lp_ut = tien_phat
        self.bsd_tien = sum(self.bsd_ltt_ids.mapped('bsd_tien_phai_tt'))

    def _get_pt(self):
        return self.env.ref('bsd_danh_muc.bsd_tien_mat').id

    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True)
    bsd_pt_tt_id = fields.Many2one('bsd.pt_tt', string="Hình thức", help="Hình thức thanh toán",
                                   required=True, default=_get_pt)
    bsd_so_nk = fields.Selection([('tien_mat', 'Tiền mặt'), ('ngan_hang', 'Ngân hàng')], string="Sổ nhật ký",
                                 required=True, default="tien_mat")
    bsd_tk_nh_id = fields.Many2one('res.partner.bank', string="Tài khoản ngân hàng",
                                   help="Số tài khoản ngân hàng của khách hàng")
    bsd_ngan_hang_id = fields.Many2one('res.bank', string="Tên ngân hàng", help="Tên ngân hàng")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True)
    bsd_tien_kh = fields.Monetary(string="Tiền", help="Tiền", required=True)
    bsd_tien = fields.Monetary(string="Tiền thanh toán", help="Tiền thanh toán", readonly=1)
    bsd_tien_con_lai = fields.Monetary(string="Còn lại", help="Còn lại",
                                       compute='_compute_tien_ct', store=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ltt_ids = fields.Many2many('bsd.lich_thanh_toan', string="Đợt thanh toán")
    bsd_ct_ids = fields.One2many('bsd.wizard.tt_dot.ct', 'bsd_tt_dot_id', string="DS đợt thanh toán")
    bsd_tien_lp_ut = fields.Monetary(string="Tiền phạt ước tính", readonly=True)

    @api.depends('bsd_tien', 'bsd_tien_kh')
    def _compute_tien_ct(self):
        for each in self:
            con_lai = each.bsd_tien_kh - each.bsd_tien
            if con_lai < 0:
                each.bsd_tien_con_lai = 0
            else:
                each.bsd_tien_con_lai = con_lai

    def action_xac_nhan(self):
        _logger.debug("Xác nhận")
        _logger.debug(self.bsd_ct_ids.mapped('bsd_dot_tt_id'))

    def action_tao(self):
        for dot in self.bsd_ltt_ids:
            self.write({
                'bsd_ct_ids': [(0, 0, {'bsd_dot_tt_id': dot.id})]
            })
        action = self.env.ref('bsd_tai_chinh.bsd_wizard_tt_dot_action_2').read()[0]
        action['res_id'] = self.id
        return action


class BsdWizardTTDOTChiTiet(models.TransientModel):
    _name = 'bsd.wizard.tt_dot.ct'
    _description = "Các chi tiết đợt thanh toán"
    _rec_name = 'bsd_dot_tt_id'
    _order = 'bsd_stt'

    bsd_tt_dot_id = fields.Many2one('bsd.wizard.tt_dot', string="Thanh toán đợt")
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán")
    bsd_tien_dot_tt = fields.Monetary(related='bsd_dot_tt_id.bsd_tien_dot_tt')
    bsd_stt = fields.Integer(related='bsd_dot_tt_id.bsd_stt')
    bsd_co_tt_lp = fields.Boolean(string="Bao gồm tiền phạt", help="Bao gồm lãi phạt chậm thanh toán")
    bsd_lp_ut = fields.Monetary(string="Tiền lãi phạt chậm TT", help="Tiền lãi phạt chậm thanh toán")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
