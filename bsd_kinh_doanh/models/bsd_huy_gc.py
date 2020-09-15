# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdHuyGC(models.Model):
    _name = 'bsd.huy_gc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_huy_gc'
    _description = 'Phiếu đề nghị hủy giữ chỗ'

    bsd_ma_huy_gc = fields.Char(string="Mã", required=True, readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_huy_gc_unique', 'unique (bsd_ma_huy_gc)',
         'Mã hủy giữ chỗ đã tồn tại !'),
    ]
    bsd_ngay_huy_gc = fields.Datetime(string="Ngày", help="Ngày hủy", required=True,
                                      default=lambda self: fields.Datetime.now(),
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án",required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_loai_gc = fields.Selection([('gc_tc', 'Giữ chỗ thiện chí'), ('giu_cho', 'Giữ chỗ')],
                                   string="Loại", required=True, default='gc_tc', help="Loại phiếu hủy",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_gc_tc_id = fields.Many2one('bsd.gc_tc', string="Giữ chỗ thiện chí", help="Giữ chỗ thiện chí bị hủy",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", help="Giữ chỗ",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_tien = fields.Monetary(string="Số tiền", help="Số tiền", required=True,                              readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Số tiền đã thanh toán", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_hoan_tien = fields.Boolean(string="Hoàn tiền", help="Hoàn tiền",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_tien_ht = fields.Monetary(string="Số tiền hoàn", help="Số tiền hoàn", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('khong_duyet', 'Không duyệt'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             tracking=1, default="nhap", required=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_gc_tc_id', 'bsd_giu_cho_id', 'bsd_loai_gc')
    def _compute_tien(self):
        for each in self:
            if each.bsd_loai_gc == 'gc_tc':
                each.bsd_tien = each.bsd_gc_tc_id.bsd_tien_gc
                each.bsd_tien_da_tt = each.bsd_gc_tc_id.bsd_tien_da_tt
                each.bsd_tien_ht = each.bsd_gc_tc_id.bsd_tien_da_tt
            elif each.bsd_loai_gc == 'giu_cho':
                each.bsd_tien = each.bsd_giu_cho_id.bsd_tien_gc
                each.bsd_tien_da_tt = each.bsd_giu_cho_id.bsd_tien_da_tt
                each.bsd_tien_ht = each.bsd_giu_cho_id.bsd_tien_da_tt

    # KD.14.01 Xác nhận hủy giữ chỗ
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })
        if self.bsd_loai_gc == 'giu_cho':
            # Kiểm tra giữ chỗ đã làm báo giá chưa
            bao_gia = self.env['bsd.bao_gia'].search([('bsd_giu_cho_id', '=', self.bsd_giu_cho_id.id),
                                                      ('state', 'not in', ['huy'])])
            if bao_gia:
                raise UserError("Bạn cần hủy Bảng tính giá trước khi đóng giữ chỗ")

    # KD.14.02 Duyệt hủy giữ chỗ
    def action_duyet(self):
        if self.bsd_loai_gc == 'giu_cho':
            # Kiểm tra giữ chỗ đã làm báo giá chưa
            bao_gia = self.env['bsd.bao_gia'].search([('bsd_giu_cho_id', '=', self.bsd_giu_cho_id.id),
                                                      ('state', 'not in', ['huy'])])
            if bao_gia:
                raise UserError("Bạn cần hủy Bảng tính giá trước khi đóng giữ chỗ")
            # Cập nhật trạng thái giữ chỗ, mã hủy giữ chỗ
            if self.bsd_giu_cho_id.state == 'huy':
                raise UserError("Giữ chỗ đã bị hủy. Vui lòng kiểm tra lại.")
            else:
                # Cập nhật phiếu giữ chỗ
                self.bsd_giu_cho_id.write({
                    'state': 'huy',
                    'bsd_huy_gc_id': self.id
                })
                # hủy ráp căn nếu có của giữ chỗ
                if self.bsd_giu_cho_id.bsd_rap_can_id:
                    self.bsd_giu_cho_id.bsd_rap_can_id.write({'state': 'huy'})
                # Cập nhật trạng thái unit
                giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                          ('state', 'in', ['dat_cho', 'giu_cho']),
                                                          ('id', '!=', self.id)])
                if not self.bsd_unit_id.bsd_dot_mb_id:
                    if not giu_cho:
                        self.bsd_unit_id.write({
                            'state': 'chuan_bi',
                        })
                    elif not giu_cho.filtered(lambda g: g.state == 'giu_cho'):
                        self.bsd_unit_id.write({
                            'state': 'dat_cho'
                        })
                else:
                    if not giu_cho:
                        self.bsd_unit_id.write({
                            'state': 'san_sang',
                        })
                    elif not giu_cho.filtered(lambda g: g.state == 'giu_cho'):
                        self.bsd_unit_id.write({
                            'state': 'dat_cho'
                        })
        if self.bsd_loai_gc == 'gc_tc':
            if self.bsd_gc_tc_id.state == 'huy':
                raise UserError("Giữ chỗ thiện chí đã bị hủy. Vui lòng kiểm tra lại!")
            if self.bsd_gc_tc_id.bsd_rap_can_id:
                if self.bsd_gc_tc_id.bsd_rap_can_id.state not in ['huy', 'nhap']:
                    raise UserError("Giữ chỗ thiện chí đã ráp căn. Vui lòng kiểm tra lại!")
            self.bsd_gc_tc_id.write({
                'state': 'huy',
                'bsd_huy_gc_id': self.id
            })
        # Cập nhật trạng thái phiếu hủy
        self.write({
            'state': 'duyet',
        })
        # Theo dõi công nợ
        self._tao_cong_no()

    # KD.14.03 Không duyệt Hủy giữ chỗ
    def action_khong_duyet(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_huy_gc_action').read()[0]
        return action

    # KD.14.04 Hủy hủy giữ chỗ
    def action_huy(self):
        if self.state == 'xac_nhan':
            self.write({'state': 'huy'})

    # KD.14.05 Theo dõi công nợ hủy giữ chỗ
    def _tao_cong_no(self):
        # Theo dõi công nợ hủy giữ chỗ thiện chí
        if self.bsd_gc_tc_id and self.bsd_loai_gc == 'gc_tc':
            # Tạo điều chỉnh giảm
            giam_no = self.env['bsd.giam_no'].create({
                            'bsd_so_ct': self.bsd_ma_huy_gc,
                            'bsd_ngay_ct': self.bsd_ngay_huy_gc,
                            'bsd_loai_dc': 'huy_gctc',
                            'bsd_dien_giai': 'Hủy giữ chỗ thiện chí [' + self.bsd_gc_tc_id.bsd_ma_gctc + ']',
                            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                            'bsd_du_an_id': self.bsd_du_an_id.id,
                            'bsd_unit_id': self.bsd_unit_id.id,
                            'bsd_tien': self.bsd_tien,
                            'state': 'nhap',
            })
            giam_no.action_xac_nhan()
            # Tạo công nợ
            giam_no.action_vao_so()
            # Tạo công nợ chứng từ
            if self.bsd_tien > self.bsd_tien_da_tt:
                # tạo record trong bảng công nợ chứng từ
                self.env['bsd.cong_no_ct'].create({
                    'bsd_ngay_pb': self.bsd_ngay_huy_gc,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_gc_tc_id': self.bsd_gc_tc_id.id,
                    'bsd_giam_no_id': giam_no.id,
                    'bsd_tien_pb': self.bsd_tien - self.bsd_tien_da_tt,
                    'bsd_loai': 'giam_gctc',
                    'state': 'hoan_thanh',
                })
            # Tạo hoàn tiền nếu được check
            if self.bsd_hoan_tien:
                # tạo record trong bảng hoàn tiền
                self.env['bsd.hoan_tien'].create({
                    'bsd_ngay_ct': self.bsd_ngay_huy_gc,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_du_an_id': self.bsd_du_an_id.id,
                    'bsd_loai': 'dc_giam',
                    'bsd_giam_no_id': giam_no.id,
                    'bsd_tien': self.bsd_tien_ht,
                    'bsd_dien_giai': 'Hoàn tiền cho đề nghị hủy ' + self.bsd_ma_huy_gc,
                    'state': 'nhap',
                })
        # Theo dõi công nợ hủy giữ chỗ
        if self.bsd_giu_cho_id and self.bsd_loai_gc == 'giu_cho':
            # Tạo điều chỉnh giảm
            giam_no = self.env['bsd.giam_no'].create({
                            'bsd_so_ct': self.bsd_ma_huy_gc,
                            'bsd_ngay_ct': self.bsd_ngay_huy_gc,
                            'bsd_loai_dc': 'huy_gc',
                            'bsd_dien_giai': 'Hủy giữ chỗ [' + self.bsd_giu_cho_id.bsd_ma_gc + ']',
                            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                            'bsd_unit_id': self.bsd_unit_id.id,
                            'bsd_du_an_id': self.bsd_du_an_id.id,
                            'bsd_tien': self.bsd_tien,
                            'state': 'nhap',
            })
            giam_no.action_xac_nhan()
            # Tạo công nợ
            giam_no.action_vao_so()
            # Tạo công nợ chứng từ
            if self.bsd_tien > self.bsd_tien_da_tt:
                # tạo record trong bảng công nợ chứng từ
                self.env['bsd.cong_no_ct'].create({
                    'bsd_ngay_pb': self.bsd_ngay_huy_gc,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_giu_cho_id': self.bsd_giu_cho_id.id,
                    'bsd_giam_no_id': giam_no.id,
                    'bsd_tien_pb': self.bsd_tien - self.bsd_tien_da_tt,
                    'bsd_loai': 'giam_gc',
                    'state': 'hoan_thanh',
                })
            # Tạo hoàn tiền nếu được check
            if self.bsd_hoan_tien:
                # tạo record trong bảng hoàn tiền
                self.env['bsd.hoan_tien'].create({
                    'bsd_so_ct': self.bsd_ma_huy_gc,
                    'bsd_ngay_ct': self.bsd_ngay_huy_gc,
                    'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                    'bsd_du_an_id': self.bsd_du_an_id.id,
                    'bsd_loai': 'dc_giam',
                    'bsd_giam_no_id': giam_no.id,
                    'bsd_tien': self.bsd_tien_ht,
                    'bsd_dien_giai': 'Hoàn tiền cho đề nghị hủy ' + self.bsd_ma_huy_gc,
                    'state': 'nhap',
                })

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu hủy giữ chỗ'))
        vals['bsd_ma_huy_gc'] = sequence.next_by_id()
        res = super(BsdHuyGC, self).create(vals)
        return res
