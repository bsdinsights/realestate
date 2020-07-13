# -*- coding:utf-8 -*-

from odoo import models, fields, api


class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = fields.Text('Message', required=True)

    def action_ok(self):
        return {'type': 'ir.actions.act_window_close'}