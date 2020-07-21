# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdDanhSachThongBao(models.TransientModel):
    _name = 'bsd.wizard.ds_tb'
    _description = "Danh sách thông báo"
    _rec_name = "bsd_loai"

    def _get_cn_dkbg(self):
        cn_dkbg = self.env['bsd.cn_dkbg'].browse(self._context.get('active_ids', []))
        cn_dkbg = cn_dkbg.filtered(lambda c: c.state == 'duyet' and c.bsd_loai != 'san_pham')
        return [(6, 0, cn_dkbg.ids)]

    bsd_ngay_ds_tb = fields.Datetime(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now())
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
                                  .format(','.join(da_tao_ct.mapped('bsd_ten_cn_dkbg')))))
        else:
            da_tao_ct = self.bsd_cn_dkbg_ids.filtered(lambda x: x.bsd_da_tao_tbbg)
            if da_tao_ct:
                raise UserError(_(" Cập nhật DKBG: {} đã tạo thông báo"
                                  .format(','.join(da_tao_ct.mapped('bsd_ten_cn_dkbg')))))
        # Lấy các chi tiết thỏa điều kiện trạng thái duyệt và có hợp đồng chưa thanh lý
        cn_dkbg_ct = self.env['bsd.cn_dkbg_ct'].search([('bsd_cn_dkbg_id', 'in', self.bsd_cn_dkbg_ids.ids),
                                                        ('state', '=', 'duyet')])
        cn_dkbg_ct = cn_dkbg_ct.filtered(lambda c: c.bsd_hd_ban_id.state != 'thanh_ly')
        # Lấy các unit ở chi tiết
        unit_ids = cn_dkbg_ct.mapped('bsd_unit_id')
        if len(unit_ids) < len(cn_dkbg_ct):
            raise UserError(_("Có sản phẩm bị trùng cập nhật dự kiến bàn giao"))
        # Tạo dự liệu bảng thông báo nghiệm thu
        if self.bsd_loai == 'nt':
            for ct in cn_dkbg_ct:
                hd_ban = ct.bsd_hd_ban_id
                dot_cuoi = hd_ban.bsd_ltt_ids.filtered(lambda x: x.bsd_cs_tt_ct_id.bsd_dot_cuoi)
                tien_ng = hd_ban.bsd_tong_gia - hd_ban.bsd_tien_pbt - hd_ban.bsd_tien_tt_hd - dot_cuoi.bsd_tien_dot_tt
                unit_id = ct.bsd_unit_id
                self.env['bsd.tb_nt'].create({
                    'bsd_ngay_tao_tb': fields.Datetime.now(),
                    'bsd_doi_tuong': "Thông báo Nghiệm thu",
                    'bsd_tao_td': True,
                    'bsd_cn_dkbg_unit_id': ct.id,
                    'bsd_ngay_tb': fields.Date.today(),
                    'bsd_ngay_nt': ct.bsd_ngay_dkbg_moi,
                    'bsd_ngay_ut': ct.bsd_cn_dkbg_id.bsd_ngay_ut,
                    'bsd_du_an_id': ct.bsd_du_an_id.id,
                    'bsd_unit_id': unit_id.id,
                    'bsd_hd_ban_id': hd_ban.id,
                    'bsd_khach_hang_id': hd_ban.bsd_khach_hang_id.id,
                    'bsd_tien_ng': tien_ng,
                    'bsd_tien_pbt': hd_ban.bsd_tien_pbt,
                    'bsd_tien_pql': hd_ban.bsd_tien_pql,
                    'bsd_thang_pql': hd_ban.bsd_thang_pql,
                    'bsd_don_gia_pql': unit_id.bsd_don_gia_pql,
                    'state': 'nhap',
                })
            # Cập nhật field đã tạo thông báo nghiệm thu
            self.bsd_cn_dkbg_ids.write({
                'bsd_da_tao_tbnt': True
            })

