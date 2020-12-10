# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdCanTru(models.Model):
    _name = 'bsd.can_tru'
    _description = 'Cấn trừ công nợ khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_so_ct'

    bsd_so_ct = fields.Char(string="Số", help="Số", required=True, readonly=True, copy=False,
                            default='/')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_khach_hang_id = fields.Many2one("res.partner", string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_ngay_ct = fields.Date(string="Ngày", help="Ngày cấn trừ", required=True,
                              default=lambda self: fields.Date.today(), readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_tien_can_tru = fields.Monetary(string="Tiền cấn trừ", compute='_compute_tien_can_tru', store=True)
    bsd_phieu_thu_ids = fields.Many2many('bsd.phieu_thu', string="Phiếu thanh toán", help="Phiếu thanh toán",
                                         readonly=True, required=True,
                                         states={'nhap': [('readonly', False)]})
    bsd_tong_tien_pt = fields.Monetary(string="Tiền có thể cấn trừ", help="Tổng số tiền còn lại của các phiếu thu",
                                       readonly=True)
    bsd_phi_ps_ids = fields.One2many('bsd.can_tru.ct_pps', 'bsd_can_tru_id', string="Phí phát sinh")
    bsd_so_pps = fields.Integer(string="# Phí ps", compute='_compute_pps', store=True)

    @api.depends('bsd_phi_ps_ids')
    def _compute_pps(self):
        for each in self:
            each.bsd_so_pps = len(each.bsd_phi_ps_ids)
    bsd_ltt_ids = fields.One2many('bsd.can_tru.ct_dot', 'bsd_can_tru_id', string="Đợt thanh toán")
    bsd_so_dot = fields.Integer(string="# Đợt", compute='_compute_dot', store=True)

    @api.depends('bsd_ltt_ids')
    def _compute_dot(self):
        for each in self:
            each.bsd_so_dot = len(each.bsd_ltt_ids)

    bsd_dot_phi_ids = fields.One2many('bsd.can_tru.ct_phi', 'bsd_can_tru_id', string="Phí")
    bsd_so_phi = fields.Integer(string="# Phí", compute='_compute_phi', store=True)

    @api.depends('bsd_dot_phi_ids')
    def _compute_phi(self):
        for each in self:
            each.bsd_so_phi = len(each.bsd_dot_phi_ids)

    @api.onchange('bsd_phieu_thu_ids')
    def _onchange_pt(self):
        self.bsd_tong_tien_pt = sum(self.bsd_phieu_thu_ids.mapped('bsd_tien_con_lai'))

    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng",
                                    readonly=True, required=True,
                                    states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd(self):
        self.bsd_du_an_id = self.bsd_hd_ban_id.bsd_du_an_id
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('huy', 'Hủy')], string="Trạng thái", requried=True, tracking=1,
                             default='nhap', readonly=True)

    @api.depends('bsd_ltt_ids', 'bsd_dot_phi_ids', 'bsd_phi_ps_ids')
    def _compute_tien_can_tru(self):
        self.bsd_tien_can_tru = sum(self.bsd_ltt_ids.mapped(lambda r: r.bsd_tien_tt + r.bsd_tt_phat)) + \
            sum(self.bsd_dot_phi_ids.mapped(lambda r: r.bsd_tien_tt)) + \
            sum(self.bsd_phi_ps_ids.mapped(lambda r: r.bsd_tien_tt))

    # TC.04.02 So sánh tiền cấn trừ và tiền còn lại
    @api.constrains('bsd_tien_can_tru', 'bsd_tong_tien_pt')
    def _constrains_tien_can_tru(self):
        if self.bsd_tien_can_tru > self.bsd_tong_tien_pt:
            raise UserError("Tiền cấn trừ không thể lớn hơn tiền có thể cấn trừ.")

    # TC.04.01 Load chứng từ cần cấn trừ
    def action_load(self):
        self.bsd_ltt_ids.sudo().unlink()
        self.bsd_dot_phi_ids.sudo().unlink()
        self.bsd_phi_ps_ids.sudo().unlink()
        for dot_tt in self.bsd_hd_ban_id.bsd_ltt_ids\
                .filtered(lambda x: (x.bsd_thanh_toan != 'da_tt' or x.bsd_tp_phai_tt > 0) and x.bsd_ngay_hh_tt)\
                .sorted('bsd_stt'):
            self.env['bsd.can_tru.ct_dot'].create({
                'bsd_dot_tt_id': dot_tt.id,
                'bsd_can_tru_id': self.id
            })
        # Kiểm tra sản phẩm đã có ngày chứng nhận cất nóc mới thu dc pql,pbt
        if self.bsd_hd_ban_id.bsd_unit_id.bsd_ngay_cn:
            phi_ids = self.bsd_hd_ban_id.bsd_dot_pbt_ids + self.bsd_hd_ban_id.bsd_dot_pql_ids
            for phi in phi_ids.filtered(lambda x: x.bsd_thanh_toan != 'da_tt'):
                self.env['bsd.can_tru.ct_phi'].create({
                    'bsd_phi_tt_id': phi.id,
                    'bsd_can_tru_id': self.id
                })
        for pps in self.bsd_hd_ban_id.bsd_phi_ps_ids.filtered(lambda x: x.bsd_thanh_toan != 'da_tt'):
            self.env['bsd.can_tru.ct_pps'].create({
                'bsd_pps_id': pps.id,
                'bsd_can_tru_id': self.id
            })

    # TC.04.03 Cấn trừ công nợ
    def action_can_tru(self):
        # Xóa các chi tiết không cấn trừ
        self.bsd_ltt_ids.filtered(lambda x: x.bsd_tien_tt == 0 and x.bsd_tt_phat == 0).sudo().unlink()
        self.bsd_dot_phi_ids.filtered(lambda x: x.bsd_tien_tt == 0).sudo().unlink()
        self.bsd_phi_ps_ids.filtered(lambda x: x.bsd_tien_tt == 0).sudo().unlink()
        # Ghi nhận giờ ngày thanh toán
        now = datetime.datetime.now()
        ngay_phan_bo = datetime.datetime.combine(self.bsd_ngay_ct, datetime.datetime.min.time())
        ngay_phan_bo = ngay_phan_bo.replace(hour=now.hour,
                                            minute=now.minute,
                                            second=now.second,
                                            microsecond=now.microsecond)
        # sắp xếp phiếu thu theo thứ tự tăng dần
        phieu_thu_ids = self.bsd_phieu_thu_ids.sorted('bsd_ngay_pt')
        # Cấn trừ đợt thanh toán
        for dot in self.bsd_ltt_ids.filtered(lambda x: x.bsd_tien_tt > 0).sorted('bsd_stt'):
            tien_tt = dot.bsd_tien_tt
            # Tiền còn phải thanh toán của đợt
            for phieu_thu in phieu_thu_ids:
                if phieu_thu.bsd_tien_con_lai <= 0:
                    continue
                if tien_tt > phieu_thu.bsd_tien_con_lai:
                    tien_se_tt = phieu_thu.bsd_tien_con_lai
                    tien_tt = tien_tt - tien_se_tt
                else:
                    tien_se_tt = tien_tt
                    tien_tt = 0
                # Tạo dữ liệu chi tiết thanh toán
                self.env['bsd.cong_no_ct'].create({
                    'bsd_ngay_pb': ngay_phan_bo,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_dot_tt_id': dot.bsd_dot_tt_id.id,
                    'bsd_phieu_thu_id': phieu_thu.id,
                    'bsd_can_tru_id': self.id,
                    'bsd_tien_pb': tien_se_tt,
                    'bsd_loai': 'pt_dtt',
                    'state': 'hieu_luc',
                }).kiem_tra_chung_tu()
                # Kiểm tra còn tiền thanh toán hay ko
                if tien_tt == 0:
                    break
        # Cấn trừ tiền phạt chậm thanh toán
        for dot_lp in self.bsd_ltt_ids.filtered(lambda x: x.bsd_tt_phat > 0).sorted('bsd_stt'):
            tien_tt = dot_lp.bsd_tt_phat
            # Tiền còn phải thanh toán của đợt
            for phieu_thu in phieu_thu_ids:
                if phieu_thu.bsd_tien_con_lai <= 0:
                    continue
                if tien_tt > phieu_thu.bsd_tien_con_lai:
                    tien_se_tt = phieu_thu.bsd_tien_con_lai
                    tien_tt = tien_tt - tien_se_tt
                else:
                    tien_se_tt = tien_tt
                    tien_tt = 0
                # Tạo dữ liệu chi tiết thanh toán phạt
                for lp in dot_lp:
                    dot_tt = lp.bsd_dot_tt_id
                    # lấy tiền sẽ thanh toán cấn vô từng đợt
                    tien_lp = tien_se_tt
                    lai_phat_dot = self.env['bsd.lai_phat'].search([('bsd_dot_tt_id', '=', dot_tt.id)]) \
                        .filtered(lambda x: x.bsd_thanh_toan != 'da_tt') \
                        .sorted('bsd_ngay_lp')
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
                # Kiểm tra còn tiền thanh toán hay ko
                if tien_tt == 0:
                    break
        # Cấn trừ phí
        for phi in self.bsd_dot_phi_ids.filtered(lambda x: x.bsd_tien_tt > 0):
            tien_tt = phi.bsd_tien_tt
            # Tiền còn phải thanh toán của đợt
            for phieu_thu in phieu_thu_ids:
                if phieu_thu.bsd_tien_con_lai <= 0:
                    continue
                if tien_tt > phieu_thu.bsd_tien_con_lai:
                    tien_se_tt = phieu_thu.bsd_tien_con_lai
                    tien_tt -= tien_se_tt
                else:
                    tien_se_tt = tien_tt
                    tien_tt = 0
                # Tạo dữ liệu chi tiết thanh toán
                self.env['bsd.cong_no_ct'].create({
                    'bsd_ngay_pb': ngay_phan_bo,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_dot_tt_id': phi.bsd_phi_tt_id.id,
                    'bsd_phieu_thu_id': phieu_thu.id,
                    'bsd_tien_pb': tien_se_tt,
                    'bsd_loai': 'pt_pql' if phi.bsd_phi_tt_id.bsd_loai == 'pql' else 'pt_pbt',
                    'state': 'hieu_luc',
                }).kiem_tra_chung_tu()
                # Kiểm tra tiền
                if tien_tt == 0:
                    break
        # Cấn trừ phí phát sinh
        for pps in self.bsd_phi_ps_ids.filtered(lambda x: x.bsd_tien_tt > 0):
            tien_tt = pps.bsd_tien_tt
            # Tiền còn phải thanh toán của đợt
            for phieu_thu in phieu_thu_ids:
                if phieu_thu.bsd_tien_con_lai <= 0:
                    continue
                if tien_tt > phieu_thu.bsd_tien_con_lai:
                    tien_se_tt = phieu_thu.bsd_tien_con_lai
                    tien_tt -= tien_se_tt
                else:
                    tien_se_tt = tien_tt
                    tien_tt = 0
                # Tạo dữ liệu chi tiết thanh toán
                self.env['bsd.cong_no_ct'].create({
                    'bsd_ngay_pb': ngay_phan_bo,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_phi_ps_id': pps.bsd_pps_id.id,
                    'bsd_phieu_thu_id': phieu_thu.id,
                    'bsd_tien_pb': tien_se_tt,
                    'bsd_loai': 'pt_pps',
                    'state': 'hieu_luc',
                }).kiem_tra_chung_tu()
                # Kiểm tra tiền
                if tien_tt == 0:
                    break
        # Ghi nhận trạng thái cấn trừ
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # TC.04.04 Hủy cấn trừ
    def action_huy_can_tru(self):
        if self.state == 'nhap':
            self.write({
                'state': 'huy_ct',
            })

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu cấn trừ.'))
        vals['bsd_so_ct'] = sequence.next_by_id()
        return super(BsdCanTru, self).create(vals)


class BsdCanTruChitietDot(models.Model):
    _name = 'bsd.can_tru.ct_dot'
    _rec_name = 'bsd_dot_tt_id'

    bsd_can_tru_id = fields.Many2one('bsd.can_tru', string="Cấn trừ")
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt TT",
                                    readonly=True,
                                    help="Đợt thanh toán của hợp đồng")
    bsd_stt = fields.Integer(related='bsd_dot_tt_id.bsd_stt')
    bsd_tien_dot_tt = fields.Monetary(related='bsd_dot_tt_id.bsd_tien_dot_tt')
    bsd_tien_phai_tt = fields.Monetary(related='bsd_dot_tt_id.bsd_tien_phai_tt', string="Phải thanh toán")
    bsd_tien_tt = fields.Monetary(string="TT đợt", help="Tiền thanh toán đợt")
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
            ngay_tt = self.bsd_can_tru_id.bsd_ngay_ct
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
                tien_phat = float_round(self.bsd_tien_tt * (dot_tt.bsd_lai_phat / 100 / so_ngay_nam) * so_ngay_tp, 0)
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


class BsdCanTruChitietPhi(models.Model):
    _name = 'bsd.can_tru.ct_phi'
    _rec_name = 'bsd_phi_tt_id'

    bsd_can_tru_id = fields.Many2one('bsd.can_tru', string="Cấn trừ")
    bsd_phi_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Phí", help="Phí bảo trì, phí quản lý của hợp đồng")
    bsd_tien_phi_tt = fields.Monetary(related='bsd_phi_tt_id.bsd_tien_dot_tt')
    bsd_tien_phai_tt = fields.Monetary(related='bsd_phi_tt_id.bsd_tien_phai_tt', string="Phải TT")
    bsd_tien_tt = fields.Monetary(string="Tiền TT", help="Tiền thanh toán phí")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)


class BsdCanTruChitietPPS(models.Model):
    _name = 'bsd.can_tru.ct_pps'
    _rec_name = 'bsd_pps_id'

    bsd_can_tru_id = fields.Many2one('bsd.can_tru', string="Cấn trừ")
    bsd_pps_id = fields.Many2one('bsd.phi_ps', string="Phí phát sinh", help="Phí phát sinh của hợp đồng")
    bsd_tien_phi_tt = fields.Monetary(related='bsd_pps_id.bsd_tong_tien', string="Tiền phát sinh")
    bsd_tien_phai_tt = fields.Monetary(related='bsd_pps_id.bsd_tien_phai_tt', string="Phải TT")
    bsd_tien_tt = fields.Monetary(string="Tiền TT", help="Tiền thanh toán phí phát sinh")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)