# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdChietKhauChung(models.Model):
    _inherit = 'bsd.ck_ch'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", compute='_compute_dot_mb', store=True)
    bsd_dot_mb_ids = fields.One2many('bsd.dot_mb', 'bsd_ck_ch_id')

    @api.depends('bsd_dot_mb_ids')
    def _compute_dot_mb(self):
        for each in self:
            if len(each.bsd_dot_mb_ids) > 0:
                each.bsd_dot_mb_id = each.bsd_dot_mb_ids[0]


class BsdChietKhauNoiBo(models.Model):
    _inherit = 'bsd.ck_nb'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", compute='_compute_dot_mb', store=True)
    bsd_dot_mb_ids = fields.One2many('bsd.dot_mb', 'bsd_ck_nb_id')

    @api.depends('bsd_dot_mb_ids')
    def _compute_dot_mb(self):
        for each in self:
            if len(each.bsd_dot_mb_ids) > 0:
                each.bsd_dot_mb_id = each.bsd_dot_mb_ids[0]


class BsdChietKhauMuaSi(models.Model):
    _inherit = 'bsd.ck_ms'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", compute='_compute_dot_mb', store=True)
    bsd_dot_mb_ids = fields.One2many('bsd.dot_mb', 'bsd_ck_ms_id')

    @api.depends('bsd_dot_mb_ids')
    def _compute_dot_mb(self):
        for each in self:
            if len(each.bsd_dot_mb_ids) > 0:
                each.bsd_dot_mb_id = each.bsd_dot_mb_ids[0]


class BsdChietKhauCSTT(models.Model):
    _inherit = 'bsd.ck_cstt'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", compute='_compute_dot_mb', store=True)
    bsd_dot_mb_ids = fields.One2many('bsd.dot_mb', 'bsd_ck_cstt_id')

    @api.depends('bsd_dot_mb_ids')
    def _compute_dot_mb(self):
        for each in self:
            if len(each.bsd_dot_mb_ids) > 0:
                each.bsd_dot_mb_id = each.bsd_dot_mb_ids[0]


class BsdChietKhauTTN(models.Model):
    _inherit = 'bsd.ck_ttn'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", compute='_compute_dot_mb', store=True)
    bsd_dot_mb_ids = fields.One2many('bsd.dot_mb', 'bsd_ck_ttn_id')

    @api.depends('bsd_dot_mb_ids')
    def _compute_dot_mb(self):
        for each in self:
            if len(each.bsd_dot_mb_ids) > 0:
                each.bsd_dot_mb_id = each.bsd_dot_mb_ids[0]


class BsdChietKhauTTTH(models.Model):
    _inherit = 'bsd.ck_ttth'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", compute='_compute_dot_mb', store=True)
    bsd_dot_mb_ids = fields.One2many('bsd.dot_mb', 'bsd_ck_ttth_id')

    @api.depends('bsd_dot_mb_ids')
    def _compute_dot_mb(self):
        for each in self:
            if len(each.bsd_dot_mb_ids) > 0:
                each.bsd_dot_mb_id = each.bsd_dot_mb_ids[0]