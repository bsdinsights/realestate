# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from dateutil import tz
import logging
_logger = logging.getLogger(__name__)


class BsdWizardTBTT(models.TransientModel):
    _name = 'bsd.wizard.tao_tb_tt'
    _description = "Tạo tự động thông báo thanh toán"

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa/ Khu")
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng/ dãy")
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm")
    bsd_loai = fields.Selection([('tb_tt', 'Thông báo thanh toán'),
                                 ('tb_nn', 'Thông báo nhắc nợ')], string="Loại thông báo",
                                required=True,
                                default='tb_tt')

    def action_tao_tb(self):
        if self.bsd_loai == 'tb_tt':
            self._tao_tb_tt()
        else:
            self._tao_tb_nn()

    def _tao_tb_tt(self):
        where = "WHERE (hd_ban.state NOT IN ('nhap','da_ht','thanh_ly','huy'))"
        if self.bsd_du_an_id:
            where += ' AND (hd_ban.bsd_du_an_id = {0})'.format(self.bsd_du_an_id.id)
        if self.bsd_toa_nha_id:
            where += ' AND (hd_ban.bsd_toa_nha_id = {0})'.format(self.bsd_toa_nha_id.id)
        if self.bsd_toa_nha_id:
            where += ' AND (hd_ban.bsd_tang_id = {0})'.format(self.bsd_tang_id.id)
        if self.bsd_unit_id:
            where += ' AND (hd_ban.bsd_unit_id = {0})'.format(self.bsd_unit_id.id)
        self.env.cr.execute("""
        SELECT 
            hd_ban.bsd_khach_hang_id,
            hd_ban.bsd_unit_id,
            hd_ban.bsd_du_an_id,
            hd_ban.id,
            dot_tt.id,
            dot_tt.bsd_ngay_hh_tt,
            CASE
                WHEN cs_tt.bsd_tb_tt IS NOT NULL THEN cs_tt.bsd_tb_tt       
                ELSE 0
                END 
                AS ngay_tb_tt           
        FROM bsd_hd_ban as hd_ban  
            LEFT JOIN bsd_lich_thanh_toan as dot_tt ON dot_tt.bsd_hd_ban_id = hd_ban.id
            LEFT JOIN bsd_cs_tt as cs_tt ON dot_tt.bsd_cs_tt_id = cs_tt.id
        """ + where + ' AND dot_tt.bsd_ngay_hh_tt IS NOT NULL AND dot_tt.bsd_tb_tt = False;')
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone).date()
        for item in self.env.cr.fetchall():
            if 0 < (item[5] - ngay_ht).days <= item[6]:
                unit_id = self.env['product.product'].browse(item[1])
                self.env['bsd.tb_tt'].create({
                    'bsd_tieu_de': 'Thông báo thanh toán ' + unit_id.bsd_ten_unit,
                    'bsd_khach_hang_id': item[0],
                    'bsd_unit_id': item[1],
                    'bsd_du_an_id': item[2],
                    'bsd_hd_ban_id': item[3],
                    'bsd_dot_tt_id': item[4],
                    'bsd_loai': 'tb_tt'
                })
        action = self.env.ref('bsd_dich_vu.bsd_tb_tt_action').read()[0]
        action['target'] = 'main'
        return action

    def _tao_tb_nn(self):
        where = "WHERE (hd_ban.state NOT IN ('nhap','da_ht','thanh_ly','huy'))"
        if self.bsd_du_an_id:
            where += ' AND (hd_ban.bsd_du_an_id = {0})'.format(self.bsd_du_an_id.id)
        if self.bsd_toa_nha_id:
            where += ' AND (hd_ban.bsd_toa_nha_id = {0})'.format(self.bsd_toa_nha_id.id)
        if self.bsd_toa_nha_id:
            where += ' AND (hd_ban.bsd_tang_id = {0})'.format(self.bsd_tang_id.id)
        if self.bsd_unit_id:
            where += ' AND (hd_ban.bsd_unit_id = {0})'.format(self.bsd_unit_id.id)
        self.env.cr.execute("""
        SELECT 
            hd_ban.bsd_khach_hang_id,
            hd_ban.bsd_unit_id,
            hd_ban.bsd_du_an_id,
            hd_ban.id,
            dot_tt.id,
            dot_tt.bsd_ngay_hh_tt,
            CASE
                WHEN cs_tt.bsd_tb_tt IS NOT NULL THEN cs_tt.bsd_tb_tt       
                ELSE 0
                END 
                AS ngay_tb_tt           
        FROM bsd_hd_ban as hd_ban  
            LEFT JOIN bsd_lich_thanh_toan as dot_tt ON dot_tt.bsd_hd_ban_id = hd_ban.id
            LEFT JOIN bsd_cs_tt as cs_tt ON dot_tt.bsd_cs_tt_id = cs_tt.id
        """ + where + ' AND dot_tt.bsd_ngay_hh_tt IS NOT NULL AND dot_tt.bsd_tb_tt = False;')
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone).date()
        action = self.env.ref('bsd_dich_vu.bsd_tb_nn_action').read()[0]
        action['target'] = 'main'
        _logger.debug(action)
        return action
