# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
import logging
from num2words import num2words
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportGiuCho(models.TransientModel):
    _name = 'bsd.giu_cho.report.wizard'
    _description = 'Chọn mẫu in giữ chỗ'

    def _get_giu_cho(self):
        giu_cho = self.env['bsd.giu_cho'].browse(self._context.get('active_ids', []))
        return giu_cho

    bsd_giu_cho_id = fields.Many2one('bsd.giu_cho', string="Giữ chỗ", default=_get_giu_cho, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_giu_cho_chuan', 'Giữ chỗ'),
                                   ('bsd_mau_in_giu_cho_chuan_html', 'Giữ chỗ (html)')], string="Mẫu in",
                                  required=True,
                                  default='bsd_mau_in_giu_cho_chuan')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_giu_cho_id.ids,
            'model': self.bsd_giu_cho_id._name,
        }
        ref_id = 'bsd_kinh_doanh.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdGiuCho(models.AbstractModel):
    _name = 'report.bsd_kinh_doanh.bsd_giu_cho_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        giu_cho = self.env['bsd.giu_cho'].browse(data['ids'])
        tien_giu_cho = num2words(giu_cho.bsd_tien_gc, lang='vi_VN') + ' ' + 'đồng'
        ngay_hien_tai = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_hien_tai = ngay_hien_tai.replace(tzinfo=from_zone)
        ngay_hien_tai = ngay_hien_tai.astimezone(to_zone)
        _logger.debug(ngay_hien_tai)
        tai_khoan = giu_cho.bsd_khach_hang_id.bank_ids
        tai_khoan = tai_khoan.filtered(lambda t: t.bsd_tk_chinh)
        if not tai_khoan:
            raise UserError("Khách hàng chưa cấu hình tài khoản chính.\nVui lòng chọn tài khoản chính cho khách hàng.")
        if len(tai_khoan) > 1:
            raise UserError("Khách hàng cấu hình nhiều hơn 1 tài khoản chính.\nVui lòng kiểm tra lại thông tin.")
        # Không có tên tài khoản sẽ lấy tên chủ tk
        chu_tk = tai_khoan.acc_holder_name if tai_khoan.acc_holder_name else tai_khoan.partner_id.display_name
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': giu_cho,
            'tien_giu_cho_chu': tien_giu_cho,
            'ngay_hien_tai': ngay_hien_tai.strftime("%d/%m/%y"),
            'chu_tk': chu_tk,
            'so_tk': tai_khoan.acc_number,
            'ngan_hang': tai_khoan.bank_id.name,
            'chi_nhanh': tai_khoan.bsd_chi_nhanh
        }