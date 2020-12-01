# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdGiuCho(models.Model):
    _inherit = 'bsd.giu_cho'

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_giu_cho_id', string="Công nợ chứng tự",
                                 domain=[('bsd_loai', '=', 'pt_gc')],
                                 readonly=True)
    bsd_ngay_tt = fields.Datetime(compute='_compute_tien_tt', store=True)
    bsd_thanh_toan = fields.Selection(compute='_compute_tien_tt', store=True)

    bsd_tt_ht = fields.Selection([('khong', 'Không có'),
                                  ('chua_ht', 'Chưa hoàn tiền'),
                                  ('da_ht', 'Đã hoàn tiền')], string="Hoàn tiền GC",
                                 help="Hoàn tiền giữ chỗ", default="khong",
                                 readonly=True)
    bsd_so_ht = fields.Integer(string="# Hoàn tiền", compute='_compute_ht')
    bsd_so_pt = fields.Integer(string="# Thanh toán", compute='_compute_tt')

    def _compute_tt(self):
        for each in self:
            phieu_thu = self.env['bsd.phieu_thu'].search([('bsd_giu_cho_id', '=', self.id)])
            each.bsd_so_pt = len(phieu_thu)

    def action_view_pt(self):
        action = self.env.ref('bsd_tai_chinh.bsd_phieu_thu_action').read()[0]

        phieu_thu = self.env['bsd.phieu_thu'].search([('bsd_giu_cho_id', '=', self.id)])
        if len(phieu_thu) > 1:
            action['domain'] = [('id', 'in', phieu_thu.ids)]
        elif phieu_thu:
            form_view = [(self.env.ref('bsd_tai_chinh.bsd_phieu_thu_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = phieu_thu.id
        return action

    def _compute_ht(self):
        for each in self:
            hoan_tien = self.env['bsd.hoan_tien'].search([('bsd_giu_cho_id', '=', self.id)])
            each.bsd_so_ht = len(hoan_tien)

    def action_view_ht(self):
        action = self.env.ref('bsd_tai_chinh.bsd_hoan_tien_action').read()[0]

        hoan_tien = self.env['bsd.hoan_tien'].search([('bsd_giu_cho_id', '=', self.id)])
        if len(hoan_tien) > 1:
            action['domain'] = [('id', 'in', hoan_tien.ids)]
        elif hoan_tien:
            form_view = [(self.env.ref('bsd_tai_chinh.bsd_hoan_tien_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = hoan_tien.id
        return action

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien_gc', 'bsd_tien_gctc')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tien_gc - each.bsd_tien_da_tt - each.bsd_tien_gctc

            if each.bsd_tien_phai_tt == 0:
                each.bsd_thanh_toan = 'da_tt'
            elif 0 < each.bsd_tien_phai_tt < each.bsd_tien_gc:
                each.bsd_thanh_toan = 'dang_tt'
            else:
                each.bsd_thanh_toan = 'chua_tt'

            if each.bsd_ct_ids:
                each.bsd_ngay_tt = max(each.bsd_ct_ids.mapped('bsd_ngay_pb'))
            else:
                each.bsd_ngay_tt = None

    # Tạo thanh toán
    def action_thanh_toan(self):
        context = {
            'default_bsd_loai_pt': 'giu_cho',
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_giu_cho_id': self.id,
            'default_bsd_unit_id': self.bsd_unit_id.id
        }
        action = self.env.ref('bsd_tai_chinh.bsd_phieu_thu_action_popup').read()[0]
        action['context'] = context
        return action

    # Tính lại hạn ưu tiên báo giá khi thanh toán tiền giữ chỗ
    def tinh_lai_hbg(self):
        # Chỉ ghi lại hạn ưu tiên khi chưa có đợt mở bán
        if self.bsd_dot_mb_id:
            pass
        else:
            giu_cho_unit = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                           ('state', '=', 'giu_cho')])
            time_gc = self.bsd_du_an_id.bsd_gc_tmb
            ngay_hh_bg = self.bsd_ngay_tt
            ngay_hh_gc = self.bsd_ngay_tt + datetime.timedelta(days=time_gc)
            stt = self.bsd_unit_id.bsd_sequence_gc_id.next_by_id()
            if giu_cho_unit:
                self.write({
                    'bsd_ngay_hh_bg': ngay_hh_bg,
                    'bsd_ngay_hh_gc': ngay_hh_gc,
                    'state': 'dang_cho',
                    'bsd_stt_bg': stt
                })
            else:
                self.write({
                    'bsd_ngay_hh_bg': ngay_hh_bg,
                    'bsd_ngay_hh_gc': ngay_hh_gc,
                    'state': 'giu_cho',
                    'bsd_stt_bg': stt
                })