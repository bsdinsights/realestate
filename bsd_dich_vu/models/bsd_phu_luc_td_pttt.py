# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime, calendar
import logging
_logger = logging.getLogger(__name__)


class BsdPLPTTT(models.Model):
    _name = 'bsd.pl_pttt'
    _description = "Phụ lục thay đổi phương thức thanh toán"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma'

    bsd_ma = fields.Char(string="Mã", help="Mã phụ lục hợp đồng thay đổi phương thức thanh toán",
                         required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phụ lục hợp đồng đã tồn tại !'),
    ]
    bsd_ngay = fields.Datetime(string="Ngày", help="Ngày tạo phụ lục hợp đồng thay đổi phương thức thanh toán",
                               required=True,
                               default=lambda self: fields.Datetime.now(),
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Tên khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng mua bán", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_cs_tt_ht_id = fields.Many2one('bsd.cs_tt', string="PTTT hiện tại", readonly=True, required=True)
    bsd_ltt_ht_ids = fields.Many2many('bsd.lich_thanh_toan', relation='lich_ht_rel', string="Lịch thanh toán ht", readonly=True)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd(self):
        self.bsd_du_an_id = self.bsd_hd_ban_id.bsd_du_an_id
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
        self.bsd_cs_tt_ht_id = self.bsd_hd_ban_id.bsd_cs_tt_id
        self.update({'bsd_ltt_ht_ids': [(5,), (6, 0, self.bsd_hd_ban_id.bsd_ltt_ids.ids)]})

    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án",
                                   help="Tên dự án", required=True, readonly=True)
    bsd_unit_id = fields.Many2one('product.product',
                                  string="Sản phẩm", help="Tên Sản phẩm",
                                  required=True, readonly=True)
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_ky_pl = fields.Date(string="Ngày ký PL", help="Ngày ký phụ lục thay đổi PTTT", readonly=True)
    bsd_nguoi_xn_ky_id = fields.Many2one('res.users', string="Người xác nhận ký",
                                         help="Người xác nhận ký phụ lục hợp đồng", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", help="Ngày duyệt phụ lục hợp đồng", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True)
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", help="Ngày xác nhận phụ lục hợp đồng", readonly=True)
    bsd_nguoi_huy_id = fields.Many2one('res.users', string="Người hủy", readonly=True)
    bsd_ngay_huy = fields.Date(string="Ngày hủy", help="Ngày hủy phụ lục hợp đồng", readonly=True)
    bsd_ly_do_huy = fields.Char(string="Lý do hủy", help="Lý do hủy phụ lục", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),('duyet', 'Duyệt'),
                              ('dk_pl', 'Đã ký phụ lục'), ('huy', 'Hủy')],
                             string="Trạng thái", help="Trạng thái", required=True, default="nhap", tracking=1)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="PTTT mới", help="Phương thức thanh toán mới",
                                   required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})

    bsd_ltt_ids = fields.Many2many('bsd.lich_thanh_toan', relation='lich_moi_rel', string="Lịch thanh toán",
                                   readonly=True)
    bsd_ly_do = fields.Char(string="Lý do không duyệt", readonly=True, tracking=2)

    def action_tao_pl(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phụ lục thay đổi PTTT',
            'res_model': 'bsd.pl_pttt',
            'res_id': self.id,
            'target': 'current',
            'view_mode': 'form'
        }

    # Xác nhận phụ lục hợp đồng
    def action_xac_nhan(self):
        if not self.bsd_ltt_ids:
            raise UserError(_("Chưa tạo lịch thanh toán mới.\nVui lòng kiểm tra lại thông tin."))
        self.write({
            'state': 'xac_nhan',
            'bsd_nguoi_xn_id': self.env.uid,
            'bsd_ngay_xn': fields.Date.today(),
        })

    def action_tao_lich_tt(self):
        # Xóa đợt chưa thanh toán để tạo lại lịch
        self.bsd_ltt_ids.filtered(lambda x: x.bsd_thanh_toan == 'chua_tt').unlink()
        # kiểm tra các đợt đã và đang thanh toán có nhiều hơn lịch thanh toán hiện tại hay ko
        # Lấy các đợt đã thanh toán tiền của lịch cũ
        old_paid = self.bsd_hd_ban_id.bsd_ltt_ids.filtered(lambda x: x.bsd_thanh_toan != 'chua_tt')
        # số đợt thanh toán của lịch thanh toán mới
        tong_dot_new = 0
        for dot in self.bsd_cs_tt_id.bsd_ct_ids:
            if dot.bsd_cach_tinh != 'td':
                tong_dot_new += 1
            else:
                if dot.bsd_lap_lai == '0':
                    tong_dot_new += 1
                else:
                    tong_dot_new += dot.bsd_so_dot
        if len(old_paid) > tong_dot_new:
            raise UserError(_("Tổng số đợt thanh toán mới nhỏ hơn số đợt đã thanh toán hiện tại.\n"
                              "Vui lòng kiểm tra lại phương thức thanh toán."))
        else:
            for dot in old_paid:
                self.write({
                    'bsd_ltt_ids': [(4, dot.id)]
                })
            # tính lại tổng tiền còn phải thanh toán cho các đợt thanh toán
            tong_tien_da_tt = sum(old_paid.mapped('bsd_tien_dot_tt'))
            tong_tien_phai_tt = self.bsd_hd_ban_id.bsd_tong_gia - self.bsd_hd_ban_id.bsd_tien_pbt
            lich_tt = self._tinh_lich_tt()
            tien_da_phan_bo = 0
            for dot_tt in lich_tt[len(old_paid):]:
                if dot_tt != lich_tt[-1]:
                    tien_dot_tt = tong_tien_phai_tt * dot_tt['bsd_tl_tt'] / 100
                    tien_dot_tt = tien_dot_tt - (tien_dot_tt % 1000)
                    dot_tt['bsd_tien_dot_tt'] = tien_dot_tt
                    tien_da_phan_bo += tien_dot_tt
                else:
                    dot_tt['bsd_tien_dot_tt'] = tong_tien_phai_tt - tien_da_phan_bo - tong_tien_da_tt
                self.write({
                    'bsd_ltt_ids': [(4, self.bsd_ltt_ids.create(dot_tt).id)]
                })
            # Cập nhật phương thức thanh toán mới cho hợp đồng
            self.bsd_hd_ban_id.write({'bsd_cs_tt_id': self.bsd_cs_tt_id.id})

    # Ký phụ lục hợp đồng
    def action_ky_pl(self):
        if self.state == 'duyet':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_ky_pl_pttt_action').read()[0]
            return action

    def thay_doi_pttt(self):
        # Lấy các đợt chưa thanh toán ra khỏi hợp đồng
        self.bsd_ltt_ht_ids.filtered(lambda x: x.bsd_thanh_toan == 'chua_tt').write({'bsd_hd_ban_id': False})
        # Thêm các đợt mới vào hợp đồng
        self.bsd_ltt_ids\
            .filtered(lambda x: x.bsd_thanh_toan == 'chua_tt')\
            .write({'bsd_hd_ban_id': self.bsd_hd_ban_id.id})
        # Lấy đợt thu phí quản lý bàn giao từ đợt cũ sang đợt mới
        dot_thu_pbt = self.bsd_ltt_ids.filtered(lambda x: x.bsd_tinh_pbt)
        dot_thu_pql = self.bsd_ltt_ids.filtered(lambda x: x.bsd_tinh_pql)
        self.bsd_hd_ban_id.bsd_dot_pbt_ids.write({'bsd_parent_id': dot_thu_pbt.id})
        self.bsd_hd_ban_id.bsd_dot_pql_ids.write({'bsd_parent_id': dot_thu_pql.id})

    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ngay_duyet': fields.Date.today(),
                'state': 'duyet',
            })

    # Hủy phụ lục hợp đồng
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            return self.env.ref('bsd_dich_vu.bsd_wizard_huy_pl_pttt_action').read()[0]

    # Không duyệt phụ lục hợp đồng
    def action_khong_duyet(self):
        if self.state == 'xac_nhan':
            action = self.env.ref('bsd_dich_vu.bsd_wizard_khong_duyet_pl_pttt_action').read()[0]
            return action

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có quy định mã phụ lục thay đổi phương thức thanh toán.\n'
                              'Vui lòng kiểm tra lại thanh tin.'))
        vals['bsd_ma'] = sequence.next_by_id()
        res = super(BsdPLPTTT, self).create(vals)
        return res

    # hàm tính đợt thanh toán
    def _cb_du_lieu_dtt(self, stt, ma_dtt, dot_tt, lai_phat, ngay_hh_tt, cs_tt, tl_tt, tinh_pql, tinh_pbt):
        res = {}
        if ngay_hh_tt:
            ngay_ah_cd = ngay_hh_tt + datetime.timedelta(days=lai_phat.bsd_an_han)
        else:
            ngay_ah_cd = False
        res.update({
            'bsd_stt': stt,
            'bsd_ma_dtt': ma_dtt,
            'bsd_ten_dtt': 'Đợt ' + str(stt),
            'bsd_ngay_hh_tt': ngay_hh_tt,
            'bsd_tl_tt': tl_tt,
            'bsd_tinh_pql': tinh_pql,
            'bsd_tinh_pbt': tinh_pbt,
            'bsd_ngay_ah': ngay_ah_cd,
            'bsd_tinh_phat': lai_phat.bsd_tinh_phat,
            'bsd_lai_phat': lai_phat.bsd_lai_phat,
            'bsd_tien_td': lai_phat.bsd_tien_td,
            'bsd_tl_td': lai_phat.bsd_tl_td,
            'bsd_cs_tt_id': cs_tt.id,
            'bsd_cs_tt_ct_id': dot_tt.id,
            'bsd_dot_ky_hd': dot_tt.bsd_dot_ky_hd,
            'bsd_tien_dc': 0,
            'bsd_loai': 'dtt'
        })
        return res

    # Tạo lịch thanh toán
    def _tinh_lich_tt(self):
        lich_tt = []

        # hàm cộng tháng
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year, month, day)

        # tạo biến cục bộ
        stt = 0  # Đánh số thứ tự record đợt thanh toán
        ngay_hh_tt = datetime.datetime.now()  # Ngày giá trị mặc đính tính ngày hết hạn thanh toán
        cs_tt = self.bsd_cs_tt_id
        dot_tt_ids = cs_tt.bsd_ct_ids
        lai_phat = cs_tt.bsd_lai_phat_tt_id
        # dùng để tính tiền đợt thanh toán cuối
        tong_tien_dot_tt = 0
        # Kiểm tra chính sách thanh toán chi tiết
        if len(dot_tt_ids.filtered(lambda x: x.bsd_cach_tinh == 'dkbg')) > 1:
            raise UserError(_("Chính sách thanh toán chi tiết có nhiều hơn 1 đợt dự kiến bàn giao."))
        if len(dot_tt_ids.filtered(lambda x: x.bsd_dot_cuoi)) > 1:
            raise UserError(_("Chính sách thanh toán chi tiết có nhiều hơn 1 đợt dự thanh toán cuối."))
        # Tạo các đợt thanh toán
        for dot in dot_tt_ids.sorted('bsd_stt'):
            # Tạo dữ liệu đợt cố định
            if dot.bsd_cach_tinh == 'cd' and not dot.bsd_dot_cuoi:
                dot_cd = dot
                stt += 1
                # cập nhật lại ngày hết hạn thanh toán
                ngay_hh_tt = dot_cd.bsd_ngay_cd
                lich_tt.append(self._cb_du_lieu_dtt(stt, 'CD', dot_cd, lai_phat, ngay_hh_tt, cs_tt, dot.bsd_tl_tt,
                               dot_cd.bsd_tinh_pql, dot_cd.bsd_tinh_pbt))
            # Tạo dữ liệu đợt tự động
            elif dot.bsd_cach_tinh == 'td':
                dot_td = dot
                ngay_hh_tt_td = ngay_hh_tt
                list_ngay_hh_tt_td = []
                if dot_td.bsd_lap_lai == '1':
                    for dot_i in range(0, dot_td.bsd_so_dot):
                        if dot_td.bsd_tiep_theo == 'ngay':
                            ngay_hh_tt_td += datetime.timedelta(days=dot_td.bsd_so_ngay)
                        else:
                            ngay_hh_tt_td = add_months(ngay_hh_tt_td, dot_td.bsd_so_thang)
                        list_ngay_hh_tt_td.append(ngay_hh_tt_td)
                else:
                    if dot_td.bsd_tiep_theo == 'ngay':
                        ngay_hh_tt_td += datetime.timedelta(days=dot_td.bsd_so_ngay)
                    else:
                        ngay_hh_tt_td = add_months(ngay_hh_tt_td, dot_td.bsd_so_thang)
                    list_ngay_hh_tt_td.append(ngay_hh_tt_td)
                # cộng thời gian gia hạn cuối của đợt tự động
                list_ngay_hh_tt_td[-1] += datetime.timedelta(days=dot_td.bsd_ngay_gh)
                # Gán lại ngày cuối cùng tự động thanh toán
                ngay_hh_tt = list_ngay_hh_tt_td[-1]
                # Kiểm tra nếu đợt tự động có tích chọn thu phí quản lý hoặc phí bảo trì
                # thì gắn vào đợt tự động đầu tiên
                da_tao_pql = False
                da_tao_pbt = False
                for ngay in list_ngay_hh_tt_td:
                    stt += 1
                    if dot_td.bsd_ngay_thang > 0:
                        last_day = calendar.monthrange(ngay.year, ngay.month)[1]

                        if dot_td.bsd_ngay_thang > last_day:
                            ngay = ngay.replace(day=last_day)
                        else:
                            ngay = ngay.replace(day=dot_td.bsd_ngay_thang)
                    if dot_td.bsd_tinh_pql and not dot_td.bsd_tinh_pbt and not da_tao_pql:
                        lich_tt.append(
                            self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay, cs_tt, dot.bsd_tl_tt, True, False))
                        da_tao_pql = True
                    elif not dot_td.bsd_tinh_pql and dot_td.bsd_tinh_pbt and not da_tao_pbt:
                        lich_tt.append(
                            self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay, cs_tt, dot.bsd_tl_tt, False, True))
                        da_tao_pbt = True
                    elif dot_td.bsd_tinh_pql and dot_td.bsd_tinh_pbt and not da_tao_pbt and not da_tao_pql:
                        lich_tt.append(
                            self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay, cs_tt, dot.bsd_tl_tt, True, True))
                        da_tao_pql = True
                        da_tao_pbt = True
                    else:
                        lich_tt.append(
                            self._cb_du_lieu_dtt(stt, 'TD', dot_td, lai_phat, ngay, cs_tt, dot.bsd_tl_tt, False, False))

            # Tạo đợt thanh toán theo dự kiến bàn giao
            elif dot.bsd_cach_tinh == 'dkbg':
                dot_dkbg = dot
                ngay_hh_tt_dkbg = self.bsd_unit_id.bsd_ngay_dkbg or self.bsd_unit_id.bsd_du_an_id.bsd_ngay_dkbg or False
                stt += 1
                # cập nhật lại ngày hết hạn thanh toán
                ngay_hh_tt = ngay_hh_tt_dkbg
                lich_tt.append(self._cb_du_lieu_dtt(stt, 'DKBG', dot_dkbg, lai_phat, ngay_hh_tt_dkbg, cs_tt,
                                                    dot.bsd_tl_tt,
                               dot_dkbg.bsd_tinh_pql, dot_dkbg.bsd_tinh_pbt))

            # Tạo đợt thanh toán cuối
            elif dot.bsd_dot_cuoi:
                dot_cuoi = dot
                stt += 1
                lich_tt.append(self._cb_du_lieu_dtt(stt, 'DBGC', dot_cuoi, lai_phat, False, cs_tt, dot.bsd_tl_tt,
                               dot_cuoi.bsd_tinh_pql, dot_cuoi.bsd_tinh_pbt))
        return lich_tt
