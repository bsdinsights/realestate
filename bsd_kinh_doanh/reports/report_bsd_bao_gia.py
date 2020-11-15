# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
import logging
import datetime
_logger = logging.getLogger(__name__)


class BsdWizardReportBaoGia(models.TransientModel):
    _name = 'bsd.bao_gia.report.wizard'
    _description = 'Chọn mẫu in báo giá'

    def _get_bg(self):
        bg = self.env['bsd.bao_gia'].browse(self._context.get('active_ids', []))
        return bg

    bsd_bao_gia_id = fields.Many2one('bsd.bao_gia', string="Báo giá", default=_get_bg, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_bao_gia_chuan', 'Bảng tính giá'),
                                   ('bsd_mau_in_bao_gia_chuan_html', 'Bảng tính giá (html)')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_bao_gia_chuan')

    def action_in(self):
        tai_khoan = self.bsd_bao_gia_id.bsd_du_an_id.bsd_tk_ng_ids
        tai_khoan = tai_khoan.filtered(lambda t: t.bsd_tk_chinh)
        if not tai_khoan:
            raise UserError("Dự án chưa cấu hình tài khoản chính.\n Vui lòng chọn tài khoản chính cho dự án.")
        if len(tai_khoan) > 1:
            raise UserError("Dự án cấu hình nhiều hơn 1 tài khoản chính.\n Vui lòng kiểm tra lại thông tin.")
        data = {
            'ids': self.bsd_bao_gia_id.ids,
            'model': self.bsd_bao_gia_id._name,
        }
        if not self.bsd_bao_gia_id.bsd_ngay_in_bg:
            self.bsd_bao_gia_id.write({
                'bsd_ngay_in_bg': datetime.datetime.now(),
                'bsd_ngay_hh_kbg': datetime.datetime.now() + datetime.timedelta(days=self.bsd_bao_gia_id.bsd_du_an_id.bsd_hh_bg)
            })
        ref_id = 'bsd_kinh_doanh.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdBaoGia(models.AbstractModel):
    _name = 'report.bsd_kinh_doanh.bsd_bao_gia_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        bao_gia = self.env['bsd.bao_gia'].browse(data['ids'])
        tai_khoan = bao_gia.bsd_du_an_id.bsd_tk_ng_ids
        tai_khoan = tai_khoan.filtered(lambda t: t.bsd_tk_chinh)
        res = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': bao_gia,
            'chu_tk': tai_khoan.acc_holder_name,
            'so_tk': tai_khoan.acc_number,
            'ngan_hang': tai_khoan.bank_id.name,
            'chi_nhanh': tai_khoan.bsd_chi_nhanh

        }
        return res
