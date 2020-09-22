# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re
import logging
_logger = logging.getLogger(__name__)


class BsdDuAn(models.Model):
    _inherit = 'bsd.du_an'

    bsd_gc_tc_ids = fields.One2many('bsd.gc_tc', 'bsd_du_an_id', string="DS giữ chỗ thiện chí")
    bsd_so_gctc = fields.Integer(string="# Số GCTC", compute='_compute_so_gctc', store=True)

    @api.depends('bsd_gc_tc_ids')
    def _compute_so_gctc(self):
        for each in self:
            each.bsd_so_gctc = len(each.bsd_gc_tc_ids)

    def action_view_gc_tc(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_gc_tc_action').read()[0]

        gc_tc = self.env['bsd.gc_tc'].search([('bsd_gc_tc_id', '=', self.id)])
        if len(gc_tc) > 1:
            action['domain'] = [('id', 'in', gc_tc.ids)]
        elif gc_tc:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_gc_tc_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = gc_tc.id
        # Prepare the context.
        context = {
            'default_bsd_du_an_id': self.id,
        }
        action['context'] = context
        return action
