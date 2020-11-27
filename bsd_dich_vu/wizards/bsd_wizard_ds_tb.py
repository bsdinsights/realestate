# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdDanhSachThongBao(models.TransientModel):
    _name = 'bsd.wizard.ds_tb'
    _description = "Danh sách thông báo"
    _rec_name = "bsd_loai"

    def _get_cn_dkbg(self):
        cn_dkbg = self.env['bsd.cn_dkbg'].browse(self._context.get('active_ids', []))
        cn_dkbg = cn_dkbg.filtered(lambda c: c.state == 'duyet' and c.bsd_loai != 'san_pham')
        return [(6, 0, cn_dkbg.ids)]

    bsd_ngay_ds_tb = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Date.today())
    bsd_loai = fields.Selection([('nt', 'Nghiệm thu'), ('bg', 'Bàn giao')], string="Loại thông báo",
                                required=True, default='nt')
    bsd_cn_dkbg_ids = fields.Many2many('bsd.cn_dkbg', string="Danh sách cập nhật DKBG", default=_get_cn_dkbg,
                                       domain=[('state', '=', 'duyet'), ('bsd_loai', '!=', 'san_pham')])

    def action_xac_nhan(self):
        # Kiểm tra null dữ liệu cập nhật dkbg
        if not self.bsd_cn_dkbg_ids:
            raise UserError(_("Vui lòng chọn danh sách Cập nhật DKBG cần tạo thông báo"))

        # Kiểm tra các cập nhật dkbg đã tạo thông báo chưa
        if self.bsd_loai == 'nt':
            da_tao_ct = self.bsd_cn_dkbg_ids.filtered(lambda x: x.bsd_da_tao_tbnt)
            if da_tao_ct:
                raise UserError(_(" Cập nhật DKBG: {} đã tạo thông báo"
                                  .format(','.join(da_tao_ct.mapped('bsd_ten')))))
        else:
            da_tao_ct = self.bsd_cn_dkbg_ids.filtered(lambda x: x.bsd_da_tao_tbbg)
            if da_tao_ct:
                raise UserError(_(" Cập nhật DKBG: {} đã tạo thông báo"
                                  .format(','.join(da_tao_ct.mapped('bsd_ten')))))
        # Lấy các chi tiết thỏa điều kiện trạng thái duyệt và có hợp đồng chưa thanh lý
        cn_dkbg_ct = self.env['bsd.cn_dkbg_unit'].search([('bsd_cn_dkbg_id', 'in', self.bsd_cn_dkbg_ids.ids),
                                                         ('state', '=', 'duyet')])
        cn_dkbg_ct = cn_dkbg_ct.filtered(lambda c: c.bsd_hd_ban_id.state != 'thanh_ly')
        # Lấy các unit ở chi tiết
        unit_ids = cn_dkbg_ct.mapped('bsd_unit_id')
        if len(unit_ids) < len(cn_dkbg_ct):
            raise UserError(_("Có sản phẩm bị trùng cập nhật dự kiến bàn giao"))
        # Lấy hợp đồng tạo thông báo
        hd_ban_ids = tuple(cn_dkbg_ct.mapped('bsd_hd_ban_id').ids)
        _logger.debug("id hợp đồng")
        _logger.debug(str(hd_ban_ids))
        if not hd_ban_ids:
            return
        elif len(hd_ban_ids) == 1:
            str_hd_ban = str(hd_ban_ids).replace(',', '')
        else:
            str_hd_ban = str(hd_ban_ids)
        # Lấy in của danh sách cập nhật DKBG
        cn_dkbg = tuple(self.bsd_cn_dkbg_ids.ids)
        if len(cn_dkbg) == 1:
            str_cn = str(cn_dkbg).replace(',', '')
        else:
            str_cn = str(cn_dkbg)

        self.env.cr.execute("""
            SELECT  hd_ban.id,
                    hd_ban.bsd_du_an_id,
                    hd_ban.bsd_unit_id,
                    hd_ban.bsd_khach_hang_id,
                    hd_ban.bsd_no_goc,
                    hd_ban.bsd_pbt_phai_tt,
                    hd_ban.bsd_pql_phai_tt,
                    hd_ban.bsd_thang_pql,
                    tmpl.bsd_don_gia_pql,
                    ct.bsd_ngay_dkbg_moi,
                    cn.bsd_ngay_ut,
                    tmpl.bsd_ma_unit, 
                    ct.id,
                    hd_ban.bsd_lt_phai_tt,
                    ct.bsd_dot_tt_id,
                    ct.bsd_ngay_htt_moi,
                    ct.bsd_ngay_dkbg_moi 
            FROM bsd_hd_ban AS hd_ban 
            JOIN bsd_cn_dkbg_unit AS ct ON ct.bsd_hd_ban_id = hd_ban.id 
            JOIN bsd_cn_dkbg AS cn ON cn.id = ct.bsd_cn_dkbg_id 
            JOIN product_product AS unit ON unit.id = hd_ban.bsd_unit_id 
            JOIN product_template AS tmpl ON tmpl.id = unit.product_tmpl_id 
            WHERE hd_ban.id IN {0} AND cn.id IN {1};
        """.format(str_hd_ban, str_cn))
        item_ids = [x for x in self.env.cr.fetchall()]
        _logger.debug(item_ids)
        # DV.20.02 Tạo dự liệu bảng thông báo nghiệm thu
        if self.bsd_loai == 'nt':
            for item in item_ids:
                self.env['bsd.tb_nt'].create({
                    'bsd_hd_ban_id': item[0],
                    'bsd_du_an_id': item[1],
                    'bsd_unit_id': item[2],
                    'bsd_khach_hang_id': item[3],
                    'bsd_tien_ng': item[4],
                    'bsd_tien_pbt': item[5],
                    'bsd_tien_pql': item[6],
                    'bsd_thang_pql': item[7],
                    'bsd_don_gia_pql': item[8],
                    'bsd_ngay_nt': item[9],
                    'bsd_ngay_ut': item[10],
                    'bsd_doi_tuong': "Thông báo nghiệm thu " + item[11],
                    'bsd_tao_td': True,
                    'bsd_cn_dkbg_unit_id': item[12],
                    'bsd_tien_lp': item[13],
                    'state': 'nhap',
                })
            # Cập nhật field đã tạo thông báo nghiệm thu
            self.bsd_cn_dkbg_ids.write({
                'bsd_da_tao_tbnt': True
            })
        # DV.20.03 Tạo dữ liệu bảng thông báo bàn giao
        else:
            for item in item_ids:
                self.env['bsd.tb_bg'].create({
                    'bsd_hd_ban_id': item[0],
                    'bsd_du_an_id': item[1],
                    'bsd_unit_id': item[2],
                    'bsd_khach_hang_id': item[3],
                    'bsd_tien_ng': item[4],
                    'bsd_tien_pbt': item[5],
                    'bsd_tien_pql': item[6],
                    'bsd_thang_pql': item[7],
                    'bsd_don_gia_pql': item[8],
                    'bsd_ngay_bg': item[9],
                    'bsd_ngay_ut': item[10],
                    'bsd_doi_tuong': "Thông báo nghiệm thu " + item[11],
                    'bsd_tao_td': True,
                    'bsd_cn_dkbg_unit_id': item[12],
                    'bsd_tien_lp': item[13],
                    'bsd_dot_tt_id': item[14],
                    'bsd_ngay_hh_tt': item[15],
                    'bsd_ngay_dkbg': item[16],
                    'state': 'nhap',
                })
            # Cập nhật field đã tạo thông báo nghiệm thu
            self.bsd_cn_dkbg_ids.write({
                'bsd_da_tao_tbbg': True
            })
