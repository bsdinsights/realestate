# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
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
    bsd_ma_kh = fields.Char(string="Mã kh", help="Mã khách hàng", required=True, readonly=True)
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
    bsd_loai = fields.Selection([('tat_ca', 'Tất cả'),
                                 ('dtt', 'Đợt thanh toán'),
                                 ('pps', 'Phí phát sinh')], string="Lọc theo",
                                help="Phân loại lọc dữ liệu",
                                default='tat_ca', required=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('can_tru', 'Cấn trừ'),
                              ('huy_ct', 'Hủy cấn trừ')], string="Trạng thái", requried=True, tracking=1,
                             default='nhap', readonly=True)
    bsd_ct_ids = fields.One2many('bsd.can_tru_ct', 'bsd_can_tru_id', string="Chi tiết", readonly=True,
                                 states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_khach_hang_id')
    def _onchange_ma_kh(self):
        self.bsd_ma_kh = self.bsd_khach_hang_id.bsd_ma_kh

    # TC.04.02 So sánh tiền cấn trừ và tiền còn lại
    @api.constrains('bsd_tien_can_tru', 'bsd_tong_tien_pt')
    def _constrains_tien_can_tru(self):
        if self.bsd_tien_can_tru > self.bsd_tong_tien_pt:
            raise UserError("Tiền cấn trừ không thể lớn hơn tiền có thể cấn trừ.")

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_can_tru')
    def _compute_tien_can_tru(self):
        for each in self:
            each.bsd_tien_can_tru = sum(each.bsd_ct_ids.mapped('bsd_tien_can_tru'))

    # TC.04.01 Load chứng từ cần cấn trừ
    def action_load(self):
        for dot_tt in self.bsd_hd_ban_id.bsd_ltt_ids\
                .filtered(lambda x: (x.bsd_thanh_toan != 'da_tt' or x.bsd_tien_phat > 0) and x.bsd_ngay_hh_tt)\
                .sorted('bsd_stt'):
            self.env['bsd.wizard.ct_dot'].create({
                'bsd_dot_tt_id': dot_tt.id,
                'bsd_wizard_tt_id': self.id
            })
        # Kiểm tra sản phẩm đã có ngày chứng nhận cất nóc mới thu dc pql,pbt
        if self.bsd_unit_id.bsd_ngay_cn:
            for phi in (self.bsd_hd_ban_id.bsd_dot_pbt_ids + self.bsd_hd_ban_id.bsd_dot_pql_ids):
                self.env['bsd.wizard.ct_phi'].create({
                    'bsd_phi_tt_id': phi.id,
                    'bsd_wizard_tt_id': self.id
                })
        for pps in self.bsd_hd_ban_id.bsd_phi_ps_ids:
            self.env['bsd.wizard.ct_pps'].create({
                'bsd_pps_id': pps.id,
                'bsd_wizard_tt_id': self.id
            })
        for dot_tt in self.bsd_hd_ban_id.bsd_ltt_ids\
                .filtered(lambda x: x.bsd_tien_phat > 0 and x.bsd_ngay_hh_tt)\
                .sorted('bsd_stt'):
            self.env['bsd.wizard.ct_lp'].create({
                'bsd_dot_tt_id': dot_tt.id,
                'bsd_wizard_tt_id': self.id
            })

    # TC.04.03 Cấn trừ công nợ
    def action_can_tru(self):
        self.write({
            'state': 'can_tru'
        })
        # Xóa chứng từ không cấn trừ
        self.bsd_ct_ids.filtered(lambda x: x.bsd_tien_can_tru <= 0).unlink()
        # Lọc các công nợ là đợt thanh toán sorted theo số thứ tự
        ct_dtt = self.bsd_ct_ids.filtered(lambda x: x.bsd_dot_tt_id and not x.bsd_phi_ps_id)\
            .sorted(lambda x: x.bsd_dot_tt_id.bsd_stt)
        for ct in (self.bsd_ct_ids - ct_dtt):
            self.env['bsd.cong_no_ct'].create({
                'bsd_ngay_pb': self.bsd_ngay_can_tru,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_hd_ban_id': ct.bsd_hd_ban_id.id,
                'bsd_phi_ps_id': ct.bsd_phi_ps_id.id,
                'bsd_phieu_thu_id': self.bsd_phieu_thu_id.id,
                'bsd_tien_pb': ct.bsd_tien_can_tru,
                'bsd_loai': ct.bsd_loai_ct,
                'state': 'hieu_luc',
                'bsd_can_tru_id': self.id,
            })
        for ct in ct_dtt:
            self.env['bsd.cong_no_ct'].create({
                'bsd_ngay_pb': self.bsd_ngay_can_tru,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_hd_ban_id': ct.bsd_hd_ban_id.id,
                'bsd_dot_tt_id': ct.bsd_dot_tt_id.id,
                'bsd_phieu_thu_id': self.bsd_phieu_thu_id.id,
                'bsd_tien_pb': ct.bsd_tien_can_tru,
                'bsd_loai': ct.bsd_loai_ct,
                'state': 'hieu_luc',
                'bsd_can_tru_id': self.id,
            })

    # TC.04.04 Hủy cấn trừ
    def action_huy_can_tru(self):
        self.write({
            'state': 'huy_ct',
        })
        self.env['bsd.cong_no_ct'].search([('bsd_can_tru_id', '=', self.id)]).unlink()

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu cấn trừ.'))
        vals['bsd_so_ct'] = sequence.next_by_id()
        return super(BsdCanTru, self).create(vals)


class BsdCanTruChiTiet(models.Model):
    _name = 'bsd.can_tru_ct'
    _description = 'Cấn trừ công nợ chi tiết'
    _rec_name = 'bsd_so_ct'

    bsd_can_tru_id = fields.Many2one('bsd.can_tru', string="Cấn trừ")
    bsd_loai_ct = fields.Selection([('pt_gctc', 'Giữ chỗ thiện chí'),
                                    ('pt_gc', 'Giữ chỗ'),
                                    ('pt_dc', 'Đặt cọc'),
                                    ('pt_pps', 'Phí phát sinh'),
                                    ('pt_dtt', 'Đợt thanh toán')], string="Loại chứng từ",
                                   help="Loại chứng từ")
    bsd_so_ct = fields.Char(string="Số chứng từ", help="Số chứng từ")
    bsd_ngay_ct = fields.Datetime(string="Ngày chứng từ", help="Ngày chứng từ")
    bsd_tien = fields.Monetary(string="Tiền", help="Tiền trên chứng từ")
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Phải thanh toán",)
    bsd_tien_can_tru = fields.Monetary(string="Tiền cấn trừ", help="Tiền cấn trừ")

    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí")
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ")
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc")
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng")
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán")
    bsd_phi_ps_id = fields.Many2one('bsd.phi_ps', string="Phí phát sinh")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.constrains('bsd_tien_can_tru', 'bsd_tien_phai_tt')
    def _constrains_tien_can_tru(self):
        if self.bsd_tien_can_tru > self.bsd_tien_phai_tt:
            raise UserError("Tiền cấn trừ không thể lớn hơn tiền phải thanh toán.")

