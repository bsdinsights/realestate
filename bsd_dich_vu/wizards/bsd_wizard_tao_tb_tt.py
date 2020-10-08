# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdWizardTBTT(models.TransientModel):
    _name = 'bsd.wizard.tao_tb_tt'
    _description = "Tạo tự động thông báo thanh toán"

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án")
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa/ Khu")
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng/ dãy")
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm")

    def action_tao_tb(self):
        where = "WHERE (hd_ban.state NOT IN ('nhap','da_ht','thanh_ly','huy'))"
        if self.bsd_du_an_id:
            where += ' AND (hd_ban.bsd_du_an_id = {0})'.format(self.bsd_du_an_id.id)
        if self.bsd_toa_nha_id:
            where += ' AND (hd_ban.bsd_toa_nha_id = {0})'.format(self.bsd_toa_nha_id.id)
        if self.bsd_toa_nha_id:
            where += ' AND (hd_ban.bsd_tang_id = {0})'.format(self.bsd_tang_id.id)
        if self.bsd_unit_id:
            where += ' AND (hd_ban.bsd_unit_id = {0})'.format(self.bsd_unit_id.id)
        where += ';'
        self.env.cr.execute("""
        SELECT 
            hd_ban.bsd_khach_hang_id,
            hd_ban.bsd_unit_id,
            hd_ban.bsd_du_an_id,
            hd_ban.id,dot_tt.id 
        FROM bsd_hd_ban as hd_ban  
            LEFT JOIN bsd_lich_thanh_toan as dot_tt ON dot_tt.bsd_hd_ban_id = hd_ban.id
        """ + where)
        for item in self.env.cr.fetchall():
            self.env['bsd.tb_tt'].create({
                'bsd_tieu_de': 'Thông báo thanh toán',
                'bsd_khach_hang_id': item[0],
                'bsd_unit_id': item[1],
                'bsd_du_an_id': item[2],
                'bsd_hd_ban_id': item[3],
                'bsd_dot_tt_id': item[4],
                'bsd_loai': 'tb_tt'
            })
        action = self.env.ref('bsd_dich_vu.bsd_tb_tt_action').read()[0]
        return action


