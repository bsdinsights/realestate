# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging

_logger = logging.getLogger(__name__)


class BsdWizardTTPPSNT(models.TransientModel):
    _name = 'bsd.wizard.tt_pps_nt'
    _description = 'Thanh toán phí phát sinh từ nghiệm thu'
    _rec_name = 'bsd_nghiem_thu_id'

    bsd_ngay_pt = fields.Date(string="Ngày thanh toán", help="Ngày thanh toán", required=True,
                              default=lambda self: fields.Date.today())
    bsd_nghiem_thu_id = fields.Many2one('bsd.nghiem_thu', string="Nghiệm thu", required=True)
    bsd_phi_ps_id = fields.Many2one('bsd.phi_ps', string="Phí PS", required=True)
    bsd_tien_kh = fields.Monetary(string="Tiền khách hàng", required=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True)
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Tên dự án", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_nghiem_thu_id')
    def _onchange_nghiem_thu(self):
        self.bsd_du_an_id = self.bsd_nghiem_thu_id.bsd_du_an_id.id
        self.bsd_hd_ban_id = self.bsd_nghiem_thu_id.bsd_hd_ban_id.id
        self.bsd_unit_id = self.bsd_nghiem_thu_id.bsd_unit_id.id
        self.bsd_phi_ps_id = self.bsd_nghiem_thu_id.bsd_phi_ps_id
        self.bsd_tien_kh = self.bsd_nghiem_thu_id.bsd_phi_ps_id.bsd_tien_phai_tt

    def action_tao(self):
        # Tạo thanh toán
        now = datetime.datetime.now()
        get_time = now.replace(year=self.bsd_ngay_pt.year,
                               month=self.bsd_ngay_pt.month,
                               day=self.bsd_ngay_pt.day)
        phieu_thu = self.env['bsd.phieu_thu'].create({
            'bsd_ngay_pt': get_time,
            'bsd_loai_pt': 'hd',
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_du_an_id': self.bsd_du_an_id.id,
            'bsd_unit_id': self.bsd_unit_id.id,
            'bsd_tien_kh': self.bsd_tien_kh,
        })
        # Kiểm tra số tiền còn phải thu của giữ chỗ thiện chí
        phi_ps = self.env['bsd.cong_no_ct'].search([('bsd_phi_ps_id', '=', self.bsd_phi_ps_id.id),
                                                   ('state', '=', 'hieu_luc')])
        # Kiểm tra số tiền đã thanh toán
        if phi_ps:
            tien_da_tt = sum(phi_ps.mapped('bsd_tien_pb'))
        else:
            tien_da_tt = 0
        # Tính tiền phân bổ
        if self.bsd_phi_ps_id.bsd_tong_tien - tien_da_tt >= self.bsd_tien_kh:
            tien_tt = self.bsd_tien_kh
        else:
            raise UserError(_("Không thanh toán với số tiền lớn phí phát sinh"))
        self.env['bsd.cong_no_ct'].create({
            'bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'bsd_phi_ps_id': self.bsd_phi_ps_id.id,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_phieu_thu_id': phieu_thu.id,
            'bsd_tien_pb': tien_tt,
            'bsd_loai': 'pt_pps',
            'state': 'nhap',
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Thanh toán',
            'res_model': 'bsd.phieu_thu',
            'res_id': phieu_thu.id,
            'target': 'current',
            'view_mode': 'form'
        }