# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdNghiemThu(models.Model):
    _inherit = 'bsd.nghiem_thu'

    bsd_phi_ps_id = fields.Many2one('bsd.phi_ps', string="Phí phát sinh", readonly=True,
                                    help="Phí phát sinh từ lần nghiệm thu trước")
    bsd_tt_thanh_toan = fields.Selection(related="bsd_phi_ps_id.bsd_thanh_toan", store=True, string="TT thanh toán")
    bsd_tien_phai_tt = fields.Monetary(related="bsd_phi_ps_id.bsd_tien_phai_tt", store=True)

    def action_tt_pps(self):
        action = self.env.ref('bsd_tai_chinh.bsd_wizard_tt_pps_nt_action').read()[0]
        action['context'] = {'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
                             'default_bsd_nghiem_thu_id': self.id}
        return action
