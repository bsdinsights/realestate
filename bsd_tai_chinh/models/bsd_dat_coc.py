# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdDatCoc(models.Model):
    _inherit = 'bsd.dat_coc'

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_dat_coc_id', string="Công nợ chứng tự",
                                 domain=[('bsd_loai', '=', 'pt_dc'), ('state', '=', 'hieu_luc')],
                                 readonly=True)
    bsd_ngay_tt = fields.Datetime(compute='_compute_tien_tt', store=True, string="Ngày TT cọc")
    bsd_thanh_toan = fields.Selection(compute='_compute_tien_tt', store=True)

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien_dc')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.filtered(lambda x: not x.bsd_dot_tt_id).mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tien_dc - each.bsd_tien_gc - each.bsd_tien_da_tt

            if each.bsd_tien_phai_tt == 0:
                each.bsd_thanh_toan = 'da_tt'
            elif 0 < each.bsd_tien_phai_tt < each.bsd_tien_dc:
                each.bsd_thanh_toan = 'dang_tt'
            else:
                each.bsd_thanh_toan = 'chua_tt'

            if each.bsd_ct_ids:
                each.bsd_ngay_tt = max(each.bsd_ct_ids.mapped('bsd_ngay_pb'))
            else:
                each.bsd_ngay_tt = None

    # KD.10.10 - Cập nhật trạng thái đặt cọc khi thanh toán tiền cọc,
    # Hủy tất cả giữ chỗ còn lại của sản phẩm, hoàn tiền cho những giữ chỗ có tiền giữ chỗ
    def cap_nhat_trang_thai(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'da_tc',
            })
        if self.bsd_unit_id.state == 'dat_coc':
            self.bsd_unit_id.sudo().write({
                'state': 'da_tc'
            })
        # Đánh dấu hoàn thành cho giữ chỗ chuyển sang đặt cọc
        self.bsd_giu_cho_id.write({'state': 'hoan_thanh'})
        # Lấy tất cả các giữ chỗ còn lại của sản phẩm
        giu_cho = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', self.bsd_unit_id.id),
                                                  ('state', 'in', ['dang_cho', 'giu_cho'])])
        # Hủy tất cả các giữ chỗ sau mở bán của sp
        giu_cho.filtered(lambda g: not g.bsd_truoc_mb).write({'state': 'huy'})
        # Hủy giữ chỗ trước mở bán có tiền giữ chỗ và tạo phiếu hoàn tiền cho
        gc_truoc_mb = giu_cho.filtered(lambda g: g.bsd_truoc_mb)
        gc_truoc_mb.write({'state': 'huy'})
        for gc in gc_truoc_mb:
            self.env['bsd.hoan_tien'].create({
                'bsd_ngay_ct': fields.Datetime.now(),
                'bsd_khach_hang_id': gc.bsd_khach_hang_id.id,
                'bsd_du_an_id': gc.bsd_du_an_id.id,
                'bsd_loai': 'giu_cho',
                'bsd_giu_cho_id': gc.id,
                'bsd_tien': gc.bsd_tien_gc,
                'bsd_dien_giai': 'Hoàn tiền giữ chỗ cho sản phẩm đã thu cọc ' + self.bsd_ma_dat_coc,
                'state': 'nhap',
            })

    # Tạo thanh toán
    def action_thanh_toan(self):
        context = {
            'default_bsd_khach_hang_id': self.bsd_khach_hang_id.id,
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_dat_coc_id': self.id,
            'default_bsd_unit_id': self.bsd_unit_id.id
        }
        action = self.env.ref('bsd_tai_chinh.bsd_wizard_tt_dat_coc_action').read()[0]
        action['context'] = context
        return action
