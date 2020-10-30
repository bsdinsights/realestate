# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdDatCoc(models.Model):
    _inherit = 'bsd.dat_coc'

    bsd_so_hd_ban = fields.Integer(string="# Hợp đồng", compute='_compute_hd_ban')

    def _compute_hd_ban(self):
        for each in self:
            hd_ban = self.env['bsd.hd_ban'].search([('bsd_dat_coc_id', '=', self.id)])
            each.bsd_so_hd_ban = len(hd_ban)

    def action_view_hd_ban(self):
        action = self.env.ref('bsd_dich_vu.bsd_hd_ban_action').read()[0]

        hd_ban = self.env['bsd.hd_ban'].search([('bsd_dat_coc_id', '=', self.id)])
        if len(hd_ban) > 1:
            action['domain'] = [('id', 'in', hd_ban.ids)]
        elif hd_ban:
            form_view = [(self.env.ref('bsd_dich_vu.bsd_hd_ban_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = hd_ban.id
        # Prepare the context.
        context = {
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_dat_coc_id': self.id,
        }
        action['context'] = context
        return action

    # DV.10. Xử lý đặt cọc quá hạn
    def auto_tao_ds_td(self):
        self.env['bsd.ds_td'].create({
            'bsd_ten': 'Theo dõi gia hạn đặt cọc ' + self.bsd_ma_dat_coc,
            'bsd_loai_td': 'vp_tg',
            'bsd_loai_yc': 'gia_han',
            'bsd_loai_dt': 'dat_coc',
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_unit_id': self.bsd_unit_id.id,
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_tien_dc': self.bsd_tien_dc,
            'bsd_dat_coc_id': self.id,
            'bsd_ngay_hh': self.bsd_ngay_hh_kdc,
            'bsd_tien_da_tt': self.bsd_tien_da_tt,
        })

    # Tạo hợp đồng mua bán
    def action_tao_hd_mb(self):
        _logger.debug("Tạo HĐ")
        context = {
            'default_bsd_khach_hang_id': self.bsd_nguoi_dd_id.id,
            'default_bsd_dat_coc_id': self.id,
        }
        action = self.env.ref('bsd_dich_vu.bsd_hd_ban_action_popup').read()[0]
        action['context'] = context
        _logger.debug(action)
        # action = {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Tạo Hợp đồng mua bán',
        #     'view_mode': 'form',
        #     'res_model': 'bsd.hd_ban',
        #     'target': 'new',
        #     'context': context,
        #     'view_id': self.env.ref('bsd_dich_vu.bsd_hd_ban_form').id
        # }
        _logger.debug(action)
        return action
