# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import datetime

_logger = logging.getLogger(__name__)


class BsdViPhamHopDong(models.Model):
    _inherit = 'bsd.vp_hd'

    bsd_so_phi_ps = fields.Integer(string="# Phí PS", help="Phí phát sinh", compute='_compute_phi_ps')
    bsd_so_ht = fields.Integer(string="# Hoàn tiền", help="Hoàn tiền", compute='_compute_ht')

    def _compute_ht(self):
        for each in self:
            each.bsd_so_ht = len(each.env['bsd.hoan_tien'].search([('bsd_vp_hd_id', '=', self.id)]))

    def action_view_ht(self):
        action = self.env.ref('bsd_tai_chinh.bsd_hoan_tien_action').read()[0]

        hoan_tien = self.env['bsd.hoan_tien'].search([('bsd_vp_hd_id', '=', self.id)])
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

    def _compute_phi_ps(self):
        for each in self:
            each.bsd_so_phi_ps = len(each.env['bsd.phi_ps'].search([('bsd_vp_hd_id', '=', self.id)]))

    def action_view_pps(self):
        action = self.env.ref('bsd_tai_chinh.bsd_phi_ps_action').read()[0]

        phi_ps = self.env['bsd.phi_ps'].search([('bsd_vp_hd_id', '=', self.id)])
        if len(phi_ps) > 1:
            action['domain'] = [('id', 'in', phi_ps.ids)]
        elif phi_ps:
            form_view = [(self.env.ref('bsd_tai_chinh.bsd_phi_ps_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = phi_ps.id
        return action

    def action_xu_ly(self):
        # nếu là chủ đầu tư thì tạo hoàn tiền
        if self.bsd_ben_vp == 'chu_dt':
            self.env['bsd.hoan_tien'].create({
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_loai': 'vp_hd',
                'bsd_vp_hd_id': self.id,
                'bsd_tien': self.bsd_so_tp_tt,
                'bsd_hd_ban_id': self.bsd_hd_ban_id.id
            })
        # nếu là khách hàng thì tạo phí phát sinh
        else:
            self.env['bsd.phi_ps'].create({
                'bsd_ten_ps': self.bsd_khach_hang_id.display_name + ' - ' + self.bsd_ma,
                'bsd_vp_hd_id': self.id,
                'bsd_du_an_id': self.bsd_du_an_id.id,
                'bsd_loai': 'vp_hd',
                'bsd_tien_ps': self.bsd_so_tp_tt,
                'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                'bsd_unit_id': self.bsd_unit_id.id,
                'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                'bsd_dot_tt_id': self.bsd_dot_tt_id.id
            })

