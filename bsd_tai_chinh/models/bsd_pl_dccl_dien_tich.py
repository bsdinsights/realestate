# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import logging
_logger = logging.getLogger(__name__)


class BsdPLCLDT(models.Model):
    _inherit = 'bsd.pl_cldt'

    bsd_phieu_thu_id = fields.Many2one('bsd.phieu_thu', string="Thanh toán", help="Thanh toán trả trước nếu có",
                                       readonly=True)
    bsd_phi_ps_id = fields.Many2one('bsd.phi_ps', string="Phí phát sinh", help="Phí phát sinh nếu có",
                                    readonly=True)

    def action_view_thanh_toan(self):
        action = self.env.ref('bsd_tai_chinh.bsd_phieu_thu_action').read()[0]

        form_view = [(self.env.ref('bsd_tai_chinh.bsd_phieu_thu_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.bsd_phieu_thu_id.id
        return action

    def action_view_phi_ps(self):
        action = self.env.ref('bsd_tai_chinh.bsd_phi_ps_action').read()[0]

        form_view = [(self.env.ref('bsd_tai_chinh.bsd_phi_ps_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.bsd_phi_ps_id.id
        return action
