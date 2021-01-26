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
        cn_dkbg_ct = self.env['bsd.cn_dkbg_unit']
        _logger.debug("Tao thong bao thanh ly")
        message = '<ul>'
        for cn_dkbg in self.bsd_cn_dkbg_ids:
            sl_tao_tc = 0
            sl_tao_ko_tc = 0
            # Cập nhật chi tiết chưa có sản phẩm
            each_ct_khong_hd = cn_dkbg.bsd_ct_ids.filtered(lambda c: not c.bsd_hd_ban_id)
            cn_dkbg_ct_da_co_hd = cn_dkbg.bsd_ct_ids - each_ct_khong_hd
            if each_ct_khong_hd:
                sl_tao_ko_tc += len(each_ct_khong_hd)
                message += "<li>Những sản phẩm chưa có hợp đồng: {}</li>".format(
                    ','.join(each_ct_khong_hd.bsd_unit_id.mapped('bsd_ma_unit')))
            # hợp đồng đã bị thanh lý
            each_ct_khong_tl = cn_dkbg_ct_da_co_hd.filtered(lambda c: c.bsd_hd_ban_id.state != '12_thanh_ly')
            cn_dkbg_ct_da_tl = cn_dkbg.bsd_ct_ids - each_ct_khong_tl
            if cn_dkbg_ct_da_tl:
                hop_dong = cn_dkbg_ct_da_tl.mapped('bsd_hd_ban_id')
                if hop_dong:
                    sl_tao_ko_tc += len(cn_dkbg_ct_da_tl)
                    message += "<li>Những hợp đồng đã bị thanh lý: {}</li>".format(
                        ','.join(hop_dong.mapped('bsd_ma_hd_ban')))
            # Nếu tạo thông báo bàn giao thì kiểm tra tình trạng thanh toán đợt dự kiến bàn giao
            if self.bsd_loai != 'nt':
                each_chua_tt = each_ct_khong_tl.filtered(lambda c: c.bsd_dot_tt_id.bsd_thanh_toan != 'da_tt')
                _logger.debug("each_chua_tt")
                _logger.debug(each_chua_tt)
                cn_dkbg_ct_da_tt = each_ct_khong_tl - each_chua_tt
                # ghi chú các hợp đồng đã hoặc đang thanh toán
                if cn_dkbg_ct_da_tt:
                    hop_dong = cn_dkbg_ct_da_tt.mapped('bsd_hd_ban_id')
                    sl_tao_ko_tc += len(cn_dkbg_ct_da_tt)
                    if hop_dong:
                        message += "<li>Những hợp đồng đã thanh toán hoặc đang thanh toán: {}</li>".format(
                            ','.join(hop_dong.mapped('bsd_ma_hd_ban')))
                # gán lại biến
                each_ct_khong_tl = each_chua_tt
            cn_dkbg_ct += each_ct_khong_tl
            # Cập nhật số lượng tạo thành công và không thành công
            message += "<li>Số lượng chi tiết tạo không thành công: {0}</li>" \
                       "<li>Số lượng chi tiết tạo thành công: {1}</li></ul>".format(sl_tao_ko_tc, sl_tao_tc)
            _logger.debug("cn_dkbg_ct")
            _logger.debug(cn_dkbg_ct)

            # note trên cập nhật ngày dự kiến bàn giao chi tiết
            cn_dkbg.message_post(body=message)
        # Lấy các unit ở chi tiết
        unit_ids = cn_dkbg_ct.mapped('bsd_unit_id')
        if len(unit_ids) < len(cn_dkbg_ct):
            raise UserError(_("Có sản phẩm bị trùng cập nhật dự kiến bàn giao"))
        # Lấy hợp đồng tạo thông báo
        hd_ban_ids = tuple(cn_dkbg_ct.mapped('bsd_hd_ban_id').ids)
        _logger.debug("hop dong ban")
        _logger.debug(cn_dkbg_ct.mapped('bsd_hd_ban_id'))
        if not hd_ban_ids:
            if self.bsd_loai == 'nt':
                # Cập nhật field đã tạo thông báo nghiệm thu
                self.bsd_cn_dkbg_ids.write({
                    'bsd_da_tao_tbnt': True
                })
            else:
                # Cập nhật field đã tạo thông báo bàn giao
                self.bsd_cn_dkbg_ids.write({
                    'bsd_da_tao_tbbg': True
                })
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
        _logger.debug("str_hd_ban")
        _logger.debug(str_hd_ban)
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
                    ct.bsd_ngay_dkbg_moi,
                    ct.bsd_so_tb 
            FROM bsd_hd_ban AS hd_ban 
            JOIN bsd_cn_dkbg_unit AS ct ON ct.bsd_hd_ban_id = hd_ban.id 
            JOIN bsd_cn_dkbg AS cn ON cn.id = ct.bsd_cn_dkbg_id 
            JOIN product_product AS unit ON unit.id = hd_ban.bsd_unit_id 
            JOIN product_template AS tmpl ON tmpl.id = unit.product_tmpl_id 
            WHERE hd_ban.id IN {0} AND cn.id IN {1};
        """.format(str_hd_ban, str_cn))
        item_ids = [x for x in self.env.cr.fetchall()]
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
                }).action_uoc_tinh_tien_phat()
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
                    'bsd_doi_tuong': "Thông báo bàn giao " + item[11],
                    'bsd_tao_td': True,
                    'bsd_cn_dkbg_unit_id': item[12],
                    'bsd_tien_lp': item[13],
                    'bsd_dot_tt_id': item[14],
                    'bsd_ngay_hh_tt': item[15],
                    'bsd_ngay_dkbg': item[16],
                    'bsd_so_tb': item[17],
                    'state': 'nhap',
                }).action_uoc_tinh_tien_phat()
            # Cập nhật field đã tạo thông báo bàn giao
            self.bsd_cn_dkbg_ids.write({
                'bsd_da_tao_tbbg': True
            })
