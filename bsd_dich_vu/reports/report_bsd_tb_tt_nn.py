# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
from dateutil import tz
_logger = logging.getLogger(__name__)


class BsdWizardReportThanhLy(models.TransientModel):
    _name = 'bsd.tb_tt_nn.report.wizard'
    _description = 'Chọn mẫu in thông báo thanh toán nhắc nợ'

    def _get_tb_tt_nn(self):
        tb_tt_nn = self.env['bsd.tb_tt_nn'].browse(self._context.get('active_ids', []))
        return tb_tt_nn

    bsd_tb_tt_nn_id = fields.Many2one('bsd.tb_tt_nn', string="Thông báo", default=_get_tb_tt_nn, readonly=True)
    bsd_mau_in = fields.Selection([('bsd_mau_in_tb_tt_nn_html', 'Thông báo thanh toán (html)'),
                                   ('bsd_mau_in_tb_tt_nn', 'Thông báo thanh toán'),
                                   ('bsd_mau_in_tb_nn_html', 'Thông báo nhắc nợ (html)'),
                                   ('bsd_mau_in_tb_nn', 'Thông báo nhắc nợ'),
                                   ('bsd_mau_in_tb_tt_dot_cuoi_html', 'Thông báo thanh toán đợt cuối (html)'),], string="Mẫu in", required=True,
                                  default='bsd_mau_in_tb_tt_nn_html')

    def action_in(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.bsd_tb_tt_nn_id.ids,
            'model': self.bsd_tb_tt_nn_id._name,
        }
        self.bsd_tb_tt_nn_id.write({
            'bsd_ngay_in': datetime.datetime.now(),
        })
        ref_id = 'bsd_dich_vu.' + self.bsd_mau_in
        return self.env.ref(ref_id).report_action(self, data=data)


class ReportBsdTBTTNN(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_tt_nn_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.tb_tt_nn'].browse(data['ids'])
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


class ReportBsdTBTTNNDotCuoi(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_tt_nn_dot_cuoi_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.tb_tt_nn'].browse(data['ids'])
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


#     Mẫu in thông báo nhắc nợ
class ReportBsdTBNN(models.AbstractModel):
    _name = 'report.bsd_dich_vu.bsd_tb_nn_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc = self.env['bsd.tb_tt_nn'].browse(data['ids'])
        ngay_ht = datetime.datetime.now()
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context['tz'])
        ngay_ht = ngay_ht.replace(tzinfo=from_zone)
        ngay_ht = ngay_ht.astimezone(to_zone)
        # Tính lãi phát sinh chậm thanh toán
        list_dot = []
        for dot_tt in doc.bsd_hd_ban_id.bsd_ltt_ids\
                .filtered(lambda x: x.bsd_thanh_toan != 'da_tt' and x.bsd_ngay_hh_tt < datetime.date.today()):
            # Kiểm tra đợt thanh toán còn nằm trong thời gian ân hạn hay không
            if ngay_ht < dot_tt.bsd_ngay_ah:
                so_ngay_tp = 0
            else:
                if dot_tt.bsd_tinh_phat == 'htt':
                    so_ngay_tp = int(ngay_ht - dot_tt.bsd_ngay_hh_tt)
                else:
                    so_ngay_tp = int(ngay_ht - dot_tt.bsd_ngay_ah)
            tien_phat = dot_tt.bsd_tien_phai_tt * so_ngay_tp * (dot_tt.bsd_lai_phat / 36500)
            list_dot.append({
                'ten_dot': dot_tt.bsd_ten_dtt,
                'ty_le': dot_tt.bsd_cs_tt_ct_id.bsd_tl_tt,
                'tien_chua_tt': dot_tt.bsd_tien_phai_tt,
                'ngay_den_han': dot_tt.bsd_ngay_hh_tt,
                'so_ngay_tp': so_ngay_tp,
                'lai_phat': dot_tt.bsd_lai_phat,
                'tien_phat': tien_phat,
                'tong_tien': tien_phat + dot_tt.bsd_tien_phai_tt,
                'ghi_chu': "Đã quá hạn"
            })
        res = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': doc,
            'ngay_ht': ngay_ht,
            'ngay_tinh_lp': ngay_ht.strftime("%d/%m/%Y"),
            'list_dot': list_dot

        }
        return res
