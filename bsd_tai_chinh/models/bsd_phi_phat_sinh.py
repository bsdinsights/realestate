# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdPhiPhatSinh(models.Model):
    _name = 'bsd.phi_ps'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Bảng phí phát sinh'
    _rec_name = 'bsd_ten_ps'

    bsd_ma_ps = fields.Char(string="Mã", help="Mã chứng từ phí phát sinh", readonly=True, copy=False, required=True,
                            default='/')

    _sql_constraints = [
        ('bsd_ma_ps_unique', 'unique (bsd_ma_ps)',
         'Mã phí phát sinh đã tồn tại !'),
    ]

    bsd_ngay_ps = fields.Datetime(string="Ngày", help="Ngày tạo", required=True,
                                  default=lambda self: fields.Datetime.now(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_ten_ps = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one(related='bsd_hd_ban_id.bsd_unit_id', store=True)
    bsd_khach_hang_id = fields.Many2one(related='bsd_hd_ban_id.bsd_khach_hang_id', store=True)
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", required=True,
                                    help="Đợt thanh toán đính kèm phí phát sinh",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_so_tt_tb = fields.Integer(string="STT thông báo",
                                  help="STT hiển thị khoản phí trên thông báo thanh toán theo đợt",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection(selection='_method_choice', string="Phân loại", help="Nguồn gốc phát sinh phí phát sinh",
                                required=True, default='bg_gt',
                                readonly=True,
                                states={'nhap': [('readonly', False)]})

    @api.model
    def _method_choice(self):
        choices = [('bg_gt', 'Bàn giao giấy tờ'), ('khac', 'Khác')]
        if self.env['res.users'].has_group('base.group_system'):
            choices += [('nt', 'Nghiệm thu'), ('pl_hd', 'Phụ lục HĐ'), ('vp_hd', 'Vi phạm HĐ')]
        return choices

    bsd_tien_ps = fields.Monetary(string="Số tiền", help="Số tiền", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_tien_thue = fields.Monetary(string="Tiền thuế", help="Tiền thuế", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tien_tang = fields.Monetary(string="Điều chỉnh tăng", help="Số tiền điều chỉnh tăng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tien_giam = fields.Monetary(string="Điều chỉnh giảm", help="Số tiền điều chỉnh giảm", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tong_tien = fields.Monetary(string="Tổng tiền", help="Tổng tiền", compute='_compute_tong_tien')

    @api.depends('bsd_tien_ps', 'bsd_tien_thue', 'bsd_tien_tang', 'bsd_tien_giam')
    def _compute_tong_tien(self):
        for each in self:
            each.bsd_tong_tien = each.bsd_tien_ps + each.bsd_tien_thue + each.bsd_tien_tang - each.bsd_tien_giam

    bsd_ngay_tt = fields.Datetime(string="Ngày thanh toán", help="Ngày thanh toán", compute='_compute_tien_tt',
                                  store=True)

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Phải thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_phi_ps_id', string="Công nợ chứng tự", readonly=True)
    bsd_thanh_toan = fields.Selection([('chua_tt', 'Chưa thanh toán'), ('dang_tt', 'Đang thanh toán'),
                                       ('da_tt', 'Đã thanh toán')], string="Thanh toán", help="Tình trạng thanh toán",
                                      compute='_compute_tien_tt', store=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'), ('ghi_so', 'Ghi sổ'), ('huy', 'Hủy')],
                             string="Trạng thái", help="Trạng thái", required=True, readonly=True, default='nhap',
                             tracking=1)

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tong_tien')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tong_tien - each.bsd_tien_da_tt

            if each.bsd_tien_phai_tt == 0:
                each.bsd_thanh_toan = 'da_tt'
            elif 0 < each.bsd_tien_phai_tt < each.bsd_tong_tien:
                each.bsd_thanh_toan = 'dang_tt'
            else:
                each.bsd_thanh_toan = 'chua_tt'

            if each.bsd_ct_ids:
                each.bsd_ngay_tt = max(each.bsd_ct_ids.mapped('bsd_ngay_pb'))
            else:
                each.bsd_ngay_tt = None

    # TC.15.01 Xác nhận phí phát sinh
    def action_xac_nhan(self):
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý. Vui lòng kiểm tra lại thông tin!'))
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # TC.15.02 Ghi sổ phí phát sinh
    def action_ghi_so(self):
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý. Vui lòng kiểm tra lại thông tin!'))
        if self.state == 'xac_nhan':
            self.write({
                'state': 'ghi_so'
            })
        self.env['bsd.cong_no'].create({
                'bsd_chung_tu': self.bsd_ma_ps,
                'bsd_ngay': self.bsd_ngay_ps,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_ps_giam': 0,
                'bsd_ps_tang': self.bsd_tong_tien,
                'bsd_loai_ct': 'phi_ps',
                'bsd_phat_sinh': 'tang',
                'bsd_phi_ps_id': self.id,
                'state': 'da_gs',
            })

    # TC.15.03 Cấn trừ công nợ phí phát sinh
    def action_can_tru(self):
        if self.bsd_hd_ban_id.state == 'thanh_ly':
            raise UserError(_('Hợp đồng đã bị thanh lý. Vui lòng kiểm tra lại thông tin!'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cấn trừ công nợ',
            'res_model': 'bsd.can_tru',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                        'default_bsd_ct_ids': [(0, 0, {
                                                        'bsd_phi_ps_id': self.id,
                                                        'bsd_dot_tt_id': self.bsd_dot_tt_id.id,
                                                        'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                                                        'bsd_so_ct': self.bsd_ma_ps,
                                                        'bsd_loai_ct': 'pt_pps',
                                                        'bsd_tien': self.bsd_tong_tien,
                                                        'bsd_tien_phai_tt': self.bsd_tien_phai_tt,
                                                        }
                                                )]
                        }
        }

    # TC.15.04 Hủy phí phát sinh
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy'
            })

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phát sinh'))
        vals['bsd_ma_ps'] = sequence.next_by_id()
        return super(BsdPhiPhatSinh, self).create(vals)
