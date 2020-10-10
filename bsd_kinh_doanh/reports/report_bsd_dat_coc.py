# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
import logging
import datetime
from num2words import num2words
_logger = logging.getLogger(__name__)


class BsdWizardReportDatCoc(models.TransientModel):
    _name = 'bsd.dat_coc.report.wizard'
    _description = 'Chọn mẫu in Đặt cọc'

    def _get_dc(self):
        dc = self.env['bsd.dat_coc'].browse(self._context.get('active_ids', []))
        return dc

    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", default=_get_dc, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_dat_coc_chuan', 'Phiếu đặt cọc'),
                                   ('bsd_mau_in_dat_coc_chuan_html', 'Phiếu đặt cọc (html)')], string="Mẫu in", required=True,
                                  default='bsd_mau_in_dat_coc_chuan')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_dat_coc_id.ids,
            'model': self.bsd_dat_coc_id._name,
        }
        if not self.bsd_dat_coc_id.bsd_ngay_in_dc:
            self.bsd_dat_coc_id.write({
                'bsd_ngay_in_dc': datetime.datetime.now(),
                'bsd_ngay_hh_kdc': datetime.datetime.now() + datetime.timedelta(days=self.bsd_dat_coc_id.bsd_du_an_id.bsd_hh_pc)
            })
        ref_id = 'bsd_kinh_doanh.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdDatCoc(models.AbstractModel):
    _name = 'report.bsd_kinh_doanh.bsd_dat_coc_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        dat_coc = self.env['bsd.dat_coc'].browse(data['ids'])
        tien_dat_coc_chu = num2words(dat_coc.bsd_du_an_id.bsd_tien_dc, lang='vi_VN') + ' ' + 'đồng'
        tl_tt = dat_coc.bsd_cs_tt_id.bsd_ct_ids.filtered(lambda t: t.bsd_stt == 1)[0].bsd_tl_tt

        tai_khoan = dat_coc.bsd_du_an_id.bsd_tk_ng_ids
        tai_khoan = tai_khoan.filtered(lambda t: t.bsd_tk_chinh)
        if not tai_khoan:
            raise UserError("Dự án chưa cấu hình tài khoản chính.\n Vui lòng chọn tài khoản chính cho dự án.")
        if len(tai_khoan) > 1:
            raise UserError("Dự án cấu hình nhiều hơn 1 tài khoản chính.\n Vui lòng kiểm tra lại thông tin.")
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': dat_coc,
            'tien_dat_coc_chu': tien_dat_coc_chu,
            'tl_tt': tl_tt,
            'chu_tk': tai_khoan.acc_holder_name,
            'so_tk': tai_khoan.acc_number,
            'ngan_hang': tai_khoan.bank_id.name,
            'chi_nhanh': tai_khoan.bsd_chi_nhanh
        }