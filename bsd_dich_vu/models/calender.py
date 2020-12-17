# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def default_get(self, fields):
        if self.env.context.get('default_bsd_tb_bg_id'):
            self = self.with_context(
                default_res_model_id=self.env.ref('bsd_dich_vu.model_bsd_tb_bg').id,
                default_res_id=self.env.context['default_bsd_tb_bg_id']
            )
        if self.env.context.get('default_bsd_tb_nt_id'):
            self = self.with_context(
                default_res_model_id=self.env.ref('bsd_dich_vu.model_bsd_tb_nt').id,
                default_res_id=self.env.context['default_bsd_tb_nt_id']
            )
        defaults = super(CalendarEvent, self).default_get(fields)

        # sync res_model / res_id to thông báo bàn giao id
        if 'bsd_tb_bg_id' not in defaults and defaults.get('res_id') and (defaults.get('res_model') or defaults.get('res_model_id')):
            if (defaults.get('res_model') and defaults['res_model'] == 'bsd.tb_bg') or (defaults.get('res_model_id') and self.env['ir.model'].sudo().browse(defaults['res_model_id']).model == 'bsd.tb_bg'):
                defaults['bsd_tb_nt_id'] = defaults['res_id']
        # sync res_model / res_id to thông báo nghiệm thu id
        if 'bsd_tb_nt_id' not in defaults and defaults.get('res_id') and (defaults.get('res_model') or defaults.get('res_model_id')):
            if (defaults.get('res_model') and defaults['res_model'] == 'bsd.tb_bg') or (defaults.get('res_model_id') and self.env['ir.model'].sudo().browse(defaults['res_model_id']).model == 'bsd.tb_nt'):
                defaults['bsd_tb_nt_id'] = defaults['res_id']
        return defaults

    def _compute_is_highlighted(self):
        for event in self:
            event.is_highlighted = False
        super(CalendarEvent, self)._compute_is_highlighted()
        if self.env.context.get('active_model') == 'bsd.tb_bg':
            bsd_tb_bg_id = self.env.context.get('active_id')
            for event in self:
                if event.bsd_tb_bg_id.id == bsd_tb_bg_id:
                    event.is_highlighted = True
                else:
                    event.is_highlighted = False
        if self.env.context.get('active_model') == 'bsd.tb_nt':
            bsd_tb_nt_id = self.env.context.get('active_id')
            for event in self:
                if event.bsd_tb_nt_id.id == bsd_tb_nt_id:
                    event.is_highlighted = True
                else:
                    event.is_highlighted = False

    bsd_tb_bg_id = fields.Many2one('bsd.tb_bg', 'TB bàn giao')
    bsd_tb_nt_id = fields.Many2one('bsd.tb_nt', 'TB nghiệm thu')

    @api.model
    def create(self, vals):
        event = super(CalendarEvent, self).create(vals)

        if event.bsd_tb_bg_id and not event.activity_ids:
            event.bsd_tb_bg_id.log_meeting(event.name, event.start, event.duration)
        if event.bsd_tb_nt_id and not event.activity_ids:
            event.bsd_tb_nt_id.log_meeting(event.name, event.start, event.duration)
        return event
