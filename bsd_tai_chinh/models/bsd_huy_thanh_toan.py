# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdHuyThanhToan(models.Model):
    _name = 'bsd.huy_tt'
    _description = 'Phiếu hủy thanh toán'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã phiếu hủy thanh toán", required=True, readonly=True, copy=False,
                         default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Số phiếu thu đã tồn tại !'),
    ]
    bsd_ngay = fields.Date(string="Ngày", help="Ngày hủy thanh toán", required=True,
                           readonly=True, default=lambda self: fields.Date.today(),
                           states={'nhap': [('readonly', False)]})

    bsd_loai = fields.Selection([('thanh_toan', 'Thanh toán'),
                                 ('can_tru', 'Cấn trừ công nợ')], default="thanh_toan", required=True, string="Loại",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Phiếu thanh toán", help="Phiếu thanh toán", readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_can_tru_id = fields.Many2one('bsd.can_tru', string="Cấn trừ", help="Cấn trừ", readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_loai_pt = fields.Selection([('dat_coc', 'Đặt cọc'),
                                    ('hd', 'Hợp đồng')], string="Loại thanh toán",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc", readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tien_kh = fields.Monetary(string="Thanh toán", help="Số tiền thanh toán của khách hàng", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})

    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'),
                              ('khong_duyet', 'Không duyệt'),
                              ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             required=True, readonly=True, default='nhap', tracking=1)
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", readonly=True)
    bsd_lai_phat_ids = fields.One2many(related='bsd_phieu_thu_id.bsd_lai_phat_ids')
    bsd_ct_tt_ids = fields.One2many(related='bsd_phieu_thu_id.bsd_ct_ids')
    bsd_ps_tt_id = fields.Many2one('bsd.phieu_thu', string="TT trả trước", help="Phát sinh thanh toán trả trước",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    # @api.onchange('bsd_loai')
    # def _onchange_loai(self):
    #     self.bsd_can_tru_id = False
    #     self.bsd_phieu_thu_id = False

    @api.onchange('bsd_can_tru_id', 'bsd_phieu_thu_id')
    def _onchange_ct_pt(self):
        if self.bsd_loai == 'can_tru':
            self.bsd_du_an_id = self.bsd_can_tru_id.bsd_du_an_id
            self.bsd_hd_ban_id = self.bsd_can_tru_id.bsd_hd_ban_id
            self.bsd_khach_hang_id = self.bsd_can_tru_id.bsd_khach_hang_id
            self.bsd_unit_id = self.bsd_can_tru_id.bsd_hd_ban_id.bsd_unit_id
            self.bsd_tien_kh = self.bsd_can_tru_id.bsd_tien_can_tru
        elif self.bsd_loai == 'thanh_toan':
            if self.bsd_phieu_thu_id.bsd_loai_pt in ['dat_coc', 'hd']:
                self.bsd_loai_pt = self.bsd_phieu_thu_id.bsd_loai_pt
            else:
                self.bsd_loai_pt = False
            self.bsd_du_an_id = self.bsd_phieu_thu_id.bsd_du_an_id
            self.bsd_khach_hang_id = self.bsd_phieu_thu_id.bsd_khach_hang_id
            self.bsd_unit_id = self.bsd_phieu_thu_id.bsd_unit_id
            self.bsd_tien_kh = self.bsd_phieu_thu_id.bsd_tien_kh
            self.bsd_ps_tt_id = self.bsd_phieu_thu_id.bsd_tt_id

            if self.bsd_loai_pt == 'hd':
                self.bsd_hd_ban_id = self.bsd_phieu_thu_id.bsd_hd_ban_id
            else:
                self.bsd_dat_coc_id = self.bsd_phieu_thu_id.bsd_dat_coc_id

    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                "state": 'xac_nhan',
                'bsd_ngay_xn': fields.Date.today(),
                'bsd_nguoi_xn_id': self.env.uid
            })
            if self.bsd_loai == 'can_tru':
                self.bsd_can_tru_id.write({"state": "dang_huy"})
            else:
                self.bsd_phieu_thu_id.write({"state": "dang_huy"})
                if self.bsd_phieu_thu_id.bsd_tt_id:
                    self.bsd_phieu_thu_id.bsd_tt_id.write({"state": "dang_huy"})

    def action_duyet(self):
        # Kiểm tra đặt cọc
        if self.bsd_loai == 'thanh_toan' and self.bsd_loai_pt == 'dat_coc':
            # Kiểm tra đặt cọc đã được thanh lý hay chưa
            if self.bsd_dat_coc_id.state == 'thanh_ly':
                self.write({
                    'bsd_ly_do': "Đặt cọc đã bị thanh lý",
                    'state': 'huy',
                    'bsd_ngay_duyet': fields.Date.today(),
                    'bsd_nguoi_duyet_id': self.env.uid,
                })
                message_id = self.env['message.wizard'].create(
                    {'message': _("Đặt cọc đã bị thanh lý. Vui lòng kiểm tra lại thông tin.")})
                return {
                    'name': _('Thông báo'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'message.wizard',
                    'res_id': message_id.id,
                    'target': 'new'
                }
            # Kiểm tra đặt cọc đã tạo hợp đồng hay chưa
            dat_coc_co_hd = self.env['bsd.hd_ban'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id)], limit=1)
            if dat_coc_co_hd:
                raise UserError(_("Đặt cọc đã tạo hợp đồng. Vui lòng kiểm tra lại thông tin."))

        # Kiểm tra thanh toán có tạo ra thanh toán trả trước
        if self.bsd_loai == 'thanh_toan':
            if self.bsd_phieu_thu_id.bsd_tt_id:
                # Kiểm tra xem phiếu thanh toán trả trước có chi tiết thanh toán hay chưa
                if not self.bsd_phieu_thu_id.bsd_tt_id.bsd_ct_ids:
                    raise UserError(_("Tiền dư của phiếu thanh toán đã được cấn trừ. Vui lòng kiểm tra lại thông tin."))

        if self.state == 'xac_nhan':
            self.write({
                "state": "duyet",
                "bsd_ngay_duyet": fields.Date.today(),
                "bsd_nguoi_duyet_id": self.env.uid,
            })
            # Cập nhật trạng thái hủy cho thanh toán và thanh toán trả phát sinh
            if self.bsd_loai == 'thanh_toan':
                self.bsd_phieu_thu_id.write({
                    'state': 'huy',
                })
                self.bsd_phieu_thu_id.bsd_ct_ids.write({"state": 'vo_hieu_luc'})
                if self.bsd_phieu_thu_id.bsd_tt_id:
                    self.bsd_phieu_thu_id.bsd_tt_id.write({"state": 'huy'})
                # Cập nhật lại trạng thái của đặt cọc
                if self.bsd_dat_coc_id.state == 'da_tc':
                    self.bsd_dat_coc_id.write({
                        'state': 'xac_nhan',
                    })
                # Cập nhật lại trạng thái của sản phẩm
                if self.bsd_unit_id.state == 'da_tc':
                    self.bsd_unit_id.sudo().write({
                        'state': 'dat_coc'
                    })

    def action_khong_duyet(self):
        if self.state == 'xac_nhan':
            action = self.env.ref('bsd_tai_chinh.bsd_wizard_huy_tt_tu_choi_action').read()[0]
            return action

    def action_huy(self):
        if self.state == 'nhap':
            self.write({"state": "huy"})

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu hủy thanh toán.'))
        vals['bsd_ma'] = sequence.next_by_id()
        res = super(BsdHuyThanhToan, self).create(vals)
        return res
