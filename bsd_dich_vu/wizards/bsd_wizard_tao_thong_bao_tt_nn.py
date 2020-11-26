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
            list_tb_tt = self._tao_tb_tt()
            action = self.env.ref('bsd_dich_vu.bsd_tb_tt_action').read()[0]
            action['target'] = 'main'
            return action
        else:
            list_tb_nn = self._tao_tb_nn()
            action = self.env.ref('bsd_dich_vu.bsd_tb_nn_action').read()[0]
            action['target'] = 'main'
            return action

    def _tao_tb_tt(self):
        where = "WHERE (hd_ban.state NOT IN ('nhap','da_ht','thanh_ly'))"
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
        """ + where + """ AND dot_tt.bsd_ngay_hh_tt IS NOT NULL 
        AND dot_tt.bsd_tb_tt IS NULL AND dot_tt.bsd_thanh_toan != 'da_tt';""")
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone).date()
        _logger.debug("chạy tạo thông báo tự động")
        list_tb_tt = []
        for item in self.env.cr.fetchall():
            _logger.debug(item)
            if 0 < (item[5] - ngay_ht).days <= item[6]:
                unit_id = self.env['product.product'].browse(item[1])
                list_tb_tt.append(self.env['bsd.tb_tt'].create({
                                    'bsd_tieu_de': 'Thông báo thanh toán ' + unit_id.bsd_ten_unit,
                                    'bsd_khach_hang_id': item[0],
                                    'bsd_unit_id': item[1],
                                    'bsd_du_an_id': item[2],
                                    'bsd_hd_ban_id': item[3],
                                    'bsd_dot_tt_id': item[4],
                                    'bsd_loai': 'tb_tt'
                                }).id)
                dot_tt = self.env['bsd.lich_thanh_toan'].browse(item[4])
                dot_tt.write({
                    'bsd_tb_tt': True,
                    'bsd_ngay_tb_tt': fields.Date.today()
                })
        return list_tb_tt

    def _tao_tb_nn(self):
        where = "WHERE (hd_ban.state NOT IN ('nhap','da_ht','thanh_ly'))"
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
            cs_tt.bsd_tl_cb1,
            CASE
                WHEN cs_tt.bsd_tl_cb1 = TRUE THEN cs_tt.bsd_canh_bao1       
                ELSE 0
                END 
                AS bsd_canh_bao1,             
            cs_tt.bsd_tl_cb2,
            CASE
                WHEN cs_tt.bsd_tl_cb2 = TRUE THEN cs_tt.bsd_canh_bao2       
                ELSE 0
                END 
                AS bsd_canh_bao2,
            cs_tt.bsd_tl_cb3,
            CASE
                WHEN cs_tt.bsd_tl_cb3 = TRUE THEN cs_tt.bsd_canh_bao3       
                ELSE 0
                END 
                AS bsd_canh_bao3, 
            cs_tt.bsd_tl_cb4,
            CASE
                WHEN cs_tt.bsd_tl_cb4 = TRUE THEN cs_tt.bsd_canh_bao4       
                ELSE 0
                END 
                AS bsd_canh_bao4, 
            cs_tt.bsd_tl_cb5,
            CASE
                WHEN cs_tt.bsd_tl_cb5 = TRUE THEN cs_tt.bsd_canh_bao5       
                ELSE 0
                END 
                AS bsd_canh_bao5                                                        
        FROM bsd_hd_ban as hd_ban  
            LEFT JOIN bsd_lich_thanh_toan as dot_tt ON dot_tt.bsd_hd_ban_id = hd_ban.id
            LEFT JOIN bsd_cs_tt as cs_tt ON dot_tt.bsd_cs_tt_id = cs_tt.id
        """ + where + ' AND dot_tt.bsd_ngay_hh_tt IS NOT NULL AND dot_tt.bsd_tb_tt = True;')
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone).date()
        list_tb_nn = []
        for item in self.env.cr.fetchall():
            so_ngay = (ngay_ht - item[5]).days
            if item[6]:
                if 0 < so_ngay <= item[7]:
                    list_tb_nn.append(self._tao_data(1, item, ngay_ht))
            if item[8]:
                if item[7] < so_ngay <= item[9]:
                    list_tb_nn.append(self._tao_data(2, item, ngay_ht))
            if item[10]:
                if item[9] < so_ngay <= item[11]:
                    list_tb_nn.append(self._tao_data(3, item, ngay_ht))
            if item[12]:
                if item[11] < so_ngay <= item[13]:
                    list_tb_nn.append(self._tao_data(4, item, ngay_ht))
            if item[14]:
                if item[13] < so_ngay <= item[15]:
                    list_tb_nn.append(self._tao_data(5, item, ngay_ht))
        return list_tb_nn
    # Tạo dữ liệu thông báo nhắc nợ
    def _tao_data(self, lan_nn, item, ngay_ht):
        unit_id = self.env['product.product'].browse(item[1])
        dot_tt = self.env['bsd.lich_thanh_toan'].browse(item[4])
        hd_ban = self.env['bsd.hd_ban'].browse(item[3])
        tb_nn = self.env['bsd.tb_nn'].create({
            'bsd_tieu_de': 'Thông báo nhắc nợ lần ' + str(lan_nn) + ' ' + unit_id.bsd_ten_unit,
            'bsd_khach_hang_id': item[0],
            'bsd_unit_id': item[1],
            'bsd_du_an_id': item[2],
            'bsd_hd_ban_id': item[3],
            'bsd_dot_tt_id': item[4],
            'bsd_lan_nn': lan_nn,
            'bsd_ngay_ut': fields.Date.today(),
            'bsd_tien_dot': dot_tt.bsd_tien_phai_tt,
            'bsd_ngay_hh_tt': dot_tt.bsd_ngay_hh_tt,
        })
        # Đánh dấu các đợt đã tạo thông báo nhắc nợ
        # Kiểm tra đợt đã tạo thông báo lần trước đó chưa
        if lan_nn == 1:
            dot_tt.write({
                'bsd_canh_bao1': True,
                'bsd_ngay_cb1': fields.Date.today(),
            })
        elif lan_nn == 2:
            dot_tt.write({
                'bsd_canh_bao2': True,
                'bsd_ngay_cb2': fields.Date.today(),
            })
            if not dot_tt.bsd_canh_bao1:
                self._tao_data(1, item, ngay_ht)
        elif lan_nn == 3:
            dot_tt.write({
                'bsd_canh_bao3': True,
                'bsd_ngay_cb3': fields.Date.today(),
            })
            if not dot_tt.bsd_canh_bao2:
                self._tao_data(2, item, ngay_ht)
        elif lan_nn == 4:
            dot_tt.write({
                'bsd_canh_bao4': True,
                'bsd_ngay_cb4': fields.Date.today(),
            })
            if not dot_tt.bsd_canh_bao3:
                self._tao_data(3, item, ngay_ht)
        elif lan_nn == 5:
            dot_tt.write({
                'bsd_canh_bao5': True,
                'bsd_ngay_cb5': fields.Date.today(),
            })
            if not dot_tt.bsd_canh_bao4:
                self._tao_data(4, item, ngay_ht)
        # Kiểm tra các đợt chưa thanh toán tạo thông báo thanh toán
        hd_ban.bsd_ltt_ids.filtered(lambda h: h.bsd_thanh_toan != 'da_tt' and not h.bsd_tb_tt)
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
            dot_tt.write({
                'bsd_tb_tt': True,
                'bsd_ngay_tb_tt': fields.Date.today(),
            })
        return tb_nn