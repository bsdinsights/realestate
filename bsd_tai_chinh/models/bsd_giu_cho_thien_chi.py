# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdGiuChoThienChi(models.Model):
    _inherit = 'bsd.gc_tc'

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_gc_tc_id', string="Công nợ chứng tự",
                                 domain=[('bsd_loai', '=', 'pt_gctc'), ('state', '=', 'hieu_luc')],
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
            phieu_thu = self.env['bsd.phieu_thu'].search([('bsd_gc_tc_id', '=', self.id)])
            each.bsd_so_pt = len(phieu_thu)

    def action_view_pt(self):
        action = self.env.ref('bsd_tai_chinh.bsd_phieu_thu_action').read()[0]

        phieu_thu = self.env['bsd.phieu_thu'].search([('bsd_gc_tc_id', '=', self.id)])
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
            hoan_tien = self.env['bsd.hoan_tien'].search([('bsd_gc_tc_id', '=', self.id)])
            each.bsd_so_ht = len(hoan_tien)

    def action_view_ht(self):
        action = self.env.ref('bsd_tai_chinh.bsd_hoan_tien_action').read()[0]

        hoan_tien = self.env['bsd.hoan_tien'].search([('bsd_gc_tc_id', '=', self.id)])
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

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien_gc')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tien_gc - each.bsd_tien_da_tt

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
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_gc_tc_id': self.id,
        }
        action = self.env.ref('bsd_tai_chinh.bsd_wizard_tt_gc_tc_action').read()[0]
        action['context'] = context
        return action

    # Sinh số thứ tự cho phiếu
    def create_stt(self):
        # Tính ngày ưu tiên ráp căn
        # Cập nhật lại hạn giữ chỗ thiện chí khi thanh toán
        bsd_ngay_hh_gctc = self.bsd_ngay_tt + datetime.timedelta(days=self.bsd_du_an_id.bsd_gc_tmb)
        # Kiểm tra lại hạn giữ chỗ có lớn hơn thời gian hiện tại
        if bsd_ngay_hh_gctc <= datetime.datetime.now():
            raise UserError(_("Hạn giữ chỗ thiện chí trước hiện tại. Vui lòng kiểm tra lại thông tin."))
        ngay_ut = self.bsd_ngay_tt
        stt = self.bsd_du_an_id.bsd_sequence_gc_tc_id.next_by_id()
        self.write({
            'bsd_stt': stt,
            'bsd_ngay_ut': ngay_ut,
            'bsd_ngay_hh_gctc': bsd_ngay_hh_gctc,
        })

        # Kiểm tra lại ngày ưu tiên của giữ chỗ thiện chí
        # Lấy giữ chỗ thiện chí đang ở trạng thái giữ chỗ
        gc_tc_dang_giu_cho = self.env['bsd.gc_tc'].search([('state', '=', 'giu_cho'),
                                                           ('bsd_du_an_id', '=', self.bsd_du_an_id.id)], limit=1)
        # Cập nhật trạng thái giữ chỗ nếu ngày thanh toán nhỏ hơn giữ chỗ đang có trạng thái giữ chỗ
        if self.bsd_ngay_ut < gc_tc_dang_giu_cho.bsd_ngay_ut:
            self.write({
                'state': 'giu_cho'
            })
            gc_tc_dang_giu_cho.write({
                'state': 'cho_rc'
            })


