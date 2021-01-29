# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdBaoGiaLTT(models.Model):
    _inherit = 'bsd.lich_thanh_toan'

    bsd_tien_phat = fields.Monetary(string="Tiền phạt chậm tt", help="Tiền phạt chậm thanh toán",
                                    compute="_compute_tien_phat", store=True)
    bsd_tp_da_tt = fields.Monetary(string="Đã thanh toán", help="Tiền phạt đã thanh toán",
                                          compute="_compute_tien_phat", store=True)
    bsd_tp_phai_tt = fields.Monetary(string="Phải thanh toán", help="Tiền phạt phải thanh toán",
                                     compute='_compute_tien_phat', store=True)
    bsd_so_ngay_tre = fields.Integer(string="Số ngày trễ", help="Số ngày trễ của đợt",
                                     compute='_compute_tien_phat', store=True)
    bsd_tien_mg_lp = fields.Monetary(string="Miễn giảm phạt", help="Tiền miễn giảm lãi phạt chậm thanh toán",
                                     compute='_compute_tien_phat', store=True)
    bsd_lai_phat_ids = fields.One2many('bsd.lai_phat', 'bsd_dot_tt_id', string="DS lãi phạt")

    @api.depends('bsd_lai_phat_ids', 'bsd_lai_phat_ids.bsd_tien_da_tt',
                 'bsd_lai_phat_ids.bsd_tien_phat',
                 'bsd_lai_phat_ids.bsd_tien_phai_tt',
                 'bsd_lai_phat_ids.bsd_so_ngay', 'bsd_lai_phat_ids.bsd_tien_mg')
    def _compute_tien_phat(self):
        for each in self:
            each.bsd_tien_phat = sum(each.bsd_lai_phat_ids.mapped('bsd_tien_phat'))
            each.bsd_tp_da_tt = sum(each.bsd_lai_phat_ids.mapped('bsd_tien_da_tt'))
            each.bsd_tp_phai_tt = sum(each.bsd_lai_phat_ids.mapped('bsd_tien_phai_tt'))
            each.bsd_so_ngay_tre = sum(each.bsd_lai_phat_ids.mapped('bsd_so_ngay'))
            each.bsd_tien_mg_lp = sum(each.bsd_lai_phat_ids.mapped('bsd_tien_mg'))

    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     compute="_compute_tien_tt", store=True)
    bsd_tien_phai_tt = fields.Monetary(string="Phải thanh toán", help="Đã thanh toán",
                                       compute="_compute_tien_tt", store=True)
    bsd_ct_ids = fields.One2many('bsd.cong_no_ct', 'bsd_dot_tt_id', string="Công nợ chứng tự",
                                 domain=[('bsd_loai', 'in', ['pt_dtt', 'pt_pql', 'pt_pbt']),
                                         ('state', '=', 'hieu_luc')], readonly=True)
    bsd_ngay_tt = fields.Datetime(compute='_compute_tien_tt', store=True)
    bsd_thanh_toan = fields.Selection(compute='_compute_tien_tt', store=True)
    bsd_tien_mg_dot = fields.Monetary(string="Miễn giảm đợt", help="Tiền miễn giảm đợt", readonly=True)

    @api.depends('bsd_ct_ids', 'bsd_ct_ids.bsd_tien_pb', 'bsd_tien_dot_tt', 'bsd_tien_dc', 'bsd_tien_mg_dot')
    def _compute_tien_tt(self):
        for each in self:
            each.bsd_tien_da_tt = sum(each.bsd_ct_ids.mapped('bsd_tien_pb'))
            each.bsd_tien_phai_tt = each.bsd_tien_dot_tt - each.bsd_tien_da_tt - each.bsd_tien_dc - each.bsd_tien_mg_dot

            if each.bsd_tien_phai_tt == 0:
                each.bsd_thanh_toan = 'da_tt'
            elif 0 < each.bsd_tien_phai_tt < each.bsd_tien_dot_tt:
                each.bsd_thanh_toan = 'dang_tt'
            else:
                each.bsd_thanh_toan = 'chua_tt'

            if each.bsd_ct_ids:
                each.bsd_ngay_tt = max(each.bsd_ct_ids.mapped('bsd_ngay_pb'))
            else:
                each.bsd_ngay_tt = None

    # DV.01.09 Theo dõi chiết khấu thanh toán trước hạn
    def tao_ck_ttth(self, ngay_tt, tien_tt, phieu_tt):
        # Kiểm tra trạng thái của hợp đồng đã ký hoặc đang thanh toán
        if self.bsd_hd_ban_id.state not in ['05_da_ky', '06_dang_tt']:
            return
        # Lấy thông tin đợt mở bán của hợp đồng
        dot_mb = self.bsd_hd_ban_id.bsd_dot_mb_id
        # Kiểm tra hợp đồng có đọt mở bán có áp dụng chiết khấu trước hạn hay không
        if not dot_mb.bsd_ck_ttth_id:
            return
        if not self.bsd_ngay_hh_tt:
            return
        # Kiểm tra ngày thanh toán có trước ngày hết hạn hay không
        if ngay_tt.date() >= self.bsd_ngay_hh_tt:
            return
        # Lấy Item chiết khấu thanh toán trước hạn
        ck_ttth = dot_mb.bsd_ck_ttth_id.bsd_ct_ids.filtered(lambda c: c.bsd_tu_ngay <= ngay_tt.date() <= c.bsd_den_ngay)
        if not ck_ttth:
            return
        if len(ck_ttth) > 1:
            raise UserError("Tìm thấy nhiều hơn 1 chiết khấu. Vui lòng kiểm tra lại.")
        so_ngay_th = (self.bsd_ngay_hh_tt - ngay_tt.date()).days
        if ck_ttth.bsd_chiet_khau_id.bsd_cach_tinh == 'tien':
            tien_ck = so_ngay_th * ck_ttth.bsd_chiet_khau_id.bsd_tien_ck
        else:
            tien_ck = float_round(((ck_ttth.bsd_chiet_khau_id.bsd_tl_ck /100/ck_ttth.bsd_chiet_khau_id.bsd_so_ngay_nam) * so_ngay_th) * tien_tt, 0)
        # Tạo Giao dich chiết khấu
        self.env['bsd.ps_gd_ck'].create({
            'bsd_ma': ck_ttth.bsd_chiet_khau_id.bsd_ma_ck,
            'bsd_ten': ck_ttth.bsd_chiet_khau_id.bsd_ten_ck,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_du_an_id': self.bsd_hd_ban_id.bsd_du_an_id.id,
            'bsd_unit_id': self.bsd_hd_ban_id.bsd_unit_id.id,
            'bsd_loai_ps': 'ttth',
            'bsd_ltt_id': self.id,
            'bsd_sn_th': so_ngay_th,
            'bsd_tien_dot_tt': tien_tt,
            'bsd_tl_ck': ck_ttth.bsd_chiet_khau_id.bsd_tl_ck,
            'bsd_tien': ck_ttth.bsd_chiet_khau_id.bsd_tien_ck,
            'bsd_phieu_thu_id': phieu_tt.id,
            'bsd_tien_ck': tien_ck,
            'bsd_tien_nhap': tien_ck,
            'state': 'nhap',
        })

    # DV.01.09 Theo dõi chiết khấu thanh toán nhanh
    def tao_ck_ttn(self, phieu_tt=None):
        # Kiểm tra trạng thái của hợp đồng
        if self.bsd_hd_ban_id.state not in ['05_da_ky', '06_dang_tt']:
            return
        # Lấy thông tin đợt mở bán của hợp đồng
        dot_mb = self.bsd_hd_ban_id.bsd_dot_mb_id
        # Kiểm tra xem đã hưởng chiết khấu thanh toán nhanh chưa
        if self.bsd_hd_ban_id.bsd_dh_ck_ttn:
            return
        # Kiểm tra hợp đồng có đọt mở bán có áp dụng chiết khấu nhanh hay không
        if not dot_mb.bsd_ck_ttn_id:
            return
        # Lấy Item chiết khấu thanh toán nhanh
        ck_ttn = dot_mb.bsd_ck_ttn_id.bsd_ct_ids.\
            filtered(lambda c: c.bsd_tu_ngay <= self.bsd_ngay_tt.date() <= c.bsd_den_ngay)
        if not ck_ttn:
            return
        if len(ck_ttn) > 1:
            raise UserError("Tìm thấy nhiều hơn 1 chiết khấu. Vui lòng kiểm tra lại.")
        # Kiểm tra tỷ lệ thanh toán của hợp đồng
        if self.bsd_hd_ban_id.bsd_tl_tt_hd < ck_ttn.bsd_chiet_khau_id.bsd_tl_tt:
            return
        if ck_ttn.bsd_chiet_khau_id.bsd_cach_tinh == 'tien':
            tien_ck = ck_ttn.bsd_chiet_khau_id.bsd_tien_ck
        else:
            tien_ck = ck_ttn.bsd_chiet_khau_id.bsd_tl_ck / 100 * self.bsd_hd_ban_id.bsd_gia_truoc_thue
        # Tạo Giao dich chiết khấu
        self.env['bsd.ps_gd_ck'].create({
            'bsd_ma': ck_ttn.bsd_chiet_khau_id.bsd_ma_ck,
            'bsd_ten': ck_ttn.bsd_chiet_khau_id.bsd_ten_ck,
            'bsd_dat_coc_id': self.bsd_dat_coc_id.id,
            'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
            'bsd_du_an_id': self.bsd_hd_ban_id.bsd_du_an_id.id,
            'bsd_unit_id': self.bsd_hd_ban_id.bsd_unit_id.id,
            'bsd_loai_ps': 'ttn',
            'bsd_tl_ck': ck_ttn.bsd_chiet_khau_id.bsd_tl_ck,
            'bsd_tien': ck_ttn.bsd_chiet_khau_id.bsd_tien_ck,
            'bsd_phieu_thu_id': phieu_tt.id,
            'bsd_tien_ck': tien_ck,
            'bsd_tien_nhap': tien_ck,
            'state': 'nhap',
        })
        self.bsd_hd_ban_id.write({
            'bsd_dh_ck_ttn': True
        })

    # Tạo lãi phạt chậm thanh toán
    def tao_lp_tt(self,ngay_tt, tien_tt, thanh_toan):
        ngay_tt = ngay_tt.date()
        # Kiểm tra ngày làm mốc tính lãi phạt
        han_tinh_phat = self.bsd_ngay_hh_tt
        if self.bsd_tinh_phat == 'nah':
            han_tinh_phat = self.bsd_ngay_ah
        # Kiểm tra đã quá hạn thanh toán của đợt hay chưa
        if han_tinh_phat >= ngay_tt:
            return
        else:
            # Số ngày tính lãi phạt
            so_ngay_nam = self.bsd_cs_tt_id.bsd_lai_phat_tt_id.bsd_so_ngay_nam
            # Số ngày tính phạt
            so_ngay_tp = (ngay_tt - han_tinh_phat).days
            # Tính lãi phạt
            tien_phat = float_round(tien_tt * (self.bsd_lai_phat/100 / so_ngay_nam) * so_ngay_tp, 0)
            # Kiểm tra lãi phạt đã vượt lãi phạt tối đa của đợt chưa
            tong_tien_phat = self.bsd_tien_phat + tien_phat
            if self.bsd_tien_td == 0 and self.bsd_tl_td != 0:
                tien_phat_toi_da = self.bsd_tien_dot_tt * self.bsd_tl_td / 100
                if tong_tien_phat > tien_phat_toi_da:
                    tien_phat = tien_phat_toi_da - self.bsd_tien_phat
            elif self.bsd_tien_td != 0 and self.bsd_tl_td == 0:
                tien_phat_toi_da = self.bsd_tien_td
                if tong_tien_phat > tien_phat_toi_da:
                    tien_phat = tien_phat_toi_da - self.bsd_tien_phat
            elif self.bsd_tien_td != 0 and self.bsd_tl_td != 0:
                tien_phat_toi_da_1 = self.bsd_tien_dot_tt * self.bsd_tl_td / 100
                tien_phat_toi_da_2 = self.bsd_tien_td
                tien_phat_toi_da = tien_phat_toi_da_1 if tien_phat_toi_da_1 < tien_phat_toi_da_2 else tien_phat_toi_da_2
                if tong_tien_phat > tien_phat_toi_da:
                    tien_phat = tien_phat_toi_da - self.bsd_tien_phat
            # Kiểm tra nếu có tính phạt thì tạo dữ liệu
            if tien_phat != 0:
                self.env['bsd.lai_phat'].create({
                    'bsd_ngay_lp': ngay_tt,
                    'bsd_hd_ban_id': self.bsd_hd_ban_id.id,
                    'bsd_dot_tt_id': self.id,
                    'bsd_phieu_thu_id': thanh_toan.id,
                    'bsd_tien_tt': tien_tt,
                    'bsd_so_ngay': so_ngay_tp,
                    'bsd_tien_phat': tien_phat
                })

    def _get_name(self):
        dot_tt = self
        name = dot_tt.bsd_ma_ht or ''
        if self._context.get('show_info'):
            if dot_tt.bsd_loai == 'dtt':
                if dot_tt.bsd_thanh_toan == 'chua_tt':
                    tt = "Chưa TT"
                elif dot_tt.bsd_thanh_toan == 'dang_tt':
                    tt = "Đang TT"
                else:
                    tt = "Đã TT"
                name = "%s - %s - %s" % (dot_tt.bsd_ten_dtt, tt,  '{:,.0f} đ'
                                         .format(dot_tt.bsd_tien_phai_tt).replace(',', '.'))
            elif dot_tt.bsd_loai == 'pbt':

                name = "%s - %s" % (dot_tt.bsd_ten_dtt, 'Phí bảo trì')
            else:
                name = "%s - %s" % (dot_tt.bsd_ten_dtt, 'Phí quản lý')
        elif self._context.get('show_info_date'):
            if dot_tt.bsd_thanh_toan == 'chua_tt':
                tt = "Chưa TT"
            elif dot_tt.bsd_thanh_toan == 'dang_tt':
                tt = "Đang TT"
            else:
                tt = "Đã TT"
            name = "%s - %s - %s - %s" % (dot_tt.bsd_ten_dtt, tt, '{:,.0f} đ'
                                          .format(dot_tt.bsd_tien_phai_tt).replace(',', '.'),
                                          dot_tt.bsd_ngay_hh_tt.strftime("%d/%m/%Y") if dot_tt.bsd_ngay_hh_tt else 'Đợt cuối')
        return name

    def name_get(self):
        res = []
        for dot_tt in self:
            name = dot_tt._get_name()
            res.append((dot_tt.id, name))
        return res


