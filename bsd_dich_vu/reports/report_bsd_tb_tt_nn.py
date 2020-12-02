# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
import logging
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportThongBaoTT(models.TransientModel):
    _name = 'bsd.tb_tt.report.wizard'
    _description = 'Chọn mẫu in thông báo thanh toán'

    def _get_tb_tt(self):
        tb_tt = self.env['bsd.tb_tt'].browse(self._context.get('active_ids', []))
        return tb_tt

    bsd_tb_tt_id = fields.Many2one('bsd.tb_tt', string="Thông báo", default=_get_tb_tt, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_tb_tt_html', 'Thông báo thanh toán (html)'),
                                   ('bsd_mau_in_tb_tt', 'Thông báo thanh toán'),
                                   ('bsd_mau_in_tb_tt_dot_cuoi_html', 'Thông báo thanh toán đợt cuối (html)')],
                                  string="Mẫu in", required=True,
                                  default='bsd_mau_in_tb_tt_html')

    def action_in(self):
        tai_khoan = self.bsd_tb_tt_id.bsd_du_an_id.bsd_tk_ng_ids
        tai_khoan = tai_khoan.filtered(lambda t: t.bsd_tk_chinh)
        if not tai_khoan:
            raise UserError("Dự án chưa cấu hình tài khoản chính.\nVui lòng chọn tài khoản chính cho dự án.")
        if len(tai_khoan) > 1:
            raise UserError("Dự án cấu hình nhiều hơn 1 tài khoản chính.\nVui lòng kiểm tra lại thông tin.")
        data = {
            'ids': self.bsd_tb_tt_id.ids,
            'model': self.bsd_tb_tt_id._name,
        }
        self.bsd_tb_tt_id.write({
            'bsd_ngay_in': datetime.datetime.now(),
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdTBTTNN(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_tt_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.tb_tt'].browse(data['ids'])
        tai_khoan = doc.bsd_du_an_id.bsd_tk_ng_ids
        tai_khoan = tai_khoan.filtered(lambda t: t.bsd_tk_chinh)
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': doc,
            'ngay_ht': ngay_ht,
            'chu_tk': tai_khoan.acc_holder_name,
            'so_tk': tai_khoan.acc_number,
            'ngan_hang': tai_khoan.bank_id.name,
            'chi_nhanh': tai_khoan.bsd_chi_nhanh,
        }


class ReportBsdTBTTNNDotCuoi(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_tt_dot_cuoi_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.tb_tt'].browse(data['ids'])
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': doc,
            'ngay_ht': ngay_ht,
        }