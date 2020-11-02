# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class BsdKyDC(models.TransientModel):
    _name = 'bsd.wizard.ky_dc'
    _description = 'Xác nhận ngày ký đặt cọc'

    def _get_dc(self):
        dc = self.env['bsd.dat_coc'].browse(self._context.get('active_ids', []))
        return dc

    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", default=_get_dc, readonly=True)
    bsd_ngay_ky_dc = fields.Date(string="Ngày ký đặt cọc", required=True)

    def action_xac_nhan(self):
        self.bsd_dat_coc_id.write({
            'bsd_ngay_ky_dc': self.bsd_ngay_ky_dc,
            'state': 'dat_coc',
        })
        # tính lại ngày hạn thanh toán
        self.bsd_dat_coc_id.tinh_lai_han_tt()
        # Ghi nhận giao dịch chiết khấu
        self.bsd_dat_coc_id.tao_gd_chiet_khau()


class BsdHuyDC(models.TransientModel):
    _name = 'bsd.wizard.huy_dc'
    _description = 'Xác nhận hủy đặt cọc'

    def _get_dc(self):
        dc = self.env['bsd.dat_coc'].browse(self._context.get('active_ids', []))
        return dc

    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", default=_get_dc, readonly=True)
    bsd_loai_huy = fields.Selection([('sai_btg', 'Sai bảng tính giá'),
                                     ('vp_tt', 'Vi phạm thanh toán')],
                                    string="Loại", required=True, default='sai_btg')
    bsd_dien_giai = fields.Html(string="Chú thích", readonly=True,
                                default="""<p><b>Có 2 loại hủy đặt cọc:</b></p>
                                           <p>1. Hủy đặt cọc do làm sai bảng tính giá, 
                                           hệ thộng sẽ tự động hủy đặt cọc và bảng tính giá liên quan.</p>
                                           <p>2. Hủy đặt cọc do khách hàng vi phạm thanh toán 
                                           (Chưa thanh toán đủ tiền cọc khi đến hạn), hệ thống sẽ tự động hủy đặt cọc,
                                            bảng tính giá và giữ chỗ liên quan. 
                                """)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        dat_coc = self.bsd_dat_coc_id
        bao_gia = self.bsd_dat_coc_id.bsd_bao_gia_id
        giu_cho = self.bsd_dat_coc_id.bsd_giu_cho_id
        # Cập nhật trạng thái đặt cọc
        dat_coc.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'huy',
        })
        # Hủy bảng tính giá của đặt cọc
        bao_gia.write({
            'state': 'huy'
        })
        # Hủy công nợ đặt cọc
        cong_no = self.env['bsd.cong_no'].search([('bsd_dat_coc_id', '=', self.bsd_dat_coc_id.id)])
        if cong_no:
            cong_no.write({
                'state': 'huy'
            })
        if self.bsd_loai_huy == 'vp_tt':
            if giu_cho:
                giu_cho.write({'state': 'huy'})
                giu_cho_unit = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                              ('state', 'in', ['dat_cho', 'dang_cho', 'giu_cho'])])
                # Cập nhật trạng thái unit
                if not giu_cho_unit:
                    self.bsd_unit_id.write({
                        'state': 'san_sang',
                    })
                elif not giu_cho_unit.filtered(lambda g: g.state in ['dang_cho', 'giu_cho']):
                    self.bsd_unit_id.write({
                        'state': 'dat_cho'
                    })
        else:
            # Cập nhật trạng thái unit khi hủy bảng tính giá và đặt cọc
            if self.bsd_dat_coc_id.bsd_unit_id.state == 'dat_coc':
                self.bsd_dat_coc_id.bsd_unit_id.write({
                    'state': 'giu_cho'
                })



class BsdWizardChuyenDD(models.TransientModel):
    _name = 'bsd.wizard.chuyen_dd'
    _description = "Không duyệt chuyển người đại diện ký TTĐC/HĐMB"

    def _get_chuyen_dd(self):
        chuyen_dd = self.env['bsd.dat_coc.chuyen_dd'].browse(self._context.get('active_ids', []))
        return chuyen_dd

    bsd_chuyen_dd_id = fields.Many2one('bsd.dat_coc.chuyen_dd', string="Phiếu", default=_get_chuyen_dd, readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", required=True)

    def action_xac_nhan(self):
        self.bsd_chuyen_dd_id.write({
            'bsd_ly_do': self.bsd_ly_do,
            'state': 'nhap',
        })
