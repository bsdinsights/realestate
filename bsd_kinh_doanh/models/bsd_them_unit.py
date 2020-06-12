# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdThuHoi(models.Model):
    _name = 'bsd.them_unit'
    _description = 'Thêm căn hộ trong đợt phát hành'
    _rec_name = 'bsd_ma_tu'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_tu = fields.Char(string="Mã", help="Mã phiếu", required=True,
                            readonly=True,
                            states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_tu_unique', 'unique (bsd_ma_tu)',
         'Mã Phiếu thêm unit đã tồn tại !'),
    ]
    bsd_ngay_tu = fields.Date(string="Ngày", help="Ngày thực hiện", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", help="Đợt mở bán", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_bang_gia_id = fields.Many2one(related="bsd_dot_mb_id.bsd_bang_gia_id")
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", help="Ngày duyệt yêu cầu", readonly=True)
    bsd_nguoi_duyet = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt yêu cầu",
                                      readonly=True)
    bsd_ly_do_khong_duyet = fields.Char(string="Lý do", readonly=True, tracking=2)
    state = fields.Selection([('nhap', 'Nháp'), ('cph', 'Chưa phát hành'),
                              ('ph', 'Phát hành'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             tracking=1, required=True, default='nhap')
    bsd_cb_ids = fields.One2many('bsd.them_unit_cb', 'bsd_them_unit_id', string="Chuẩn bị")
    bsd_ph_ids = fields.One2many('bsd.dot_mb_unit', 'bsd_them_unit_id', string="Phát hành", readonly=True)

    # KD.04.05.01 - Chuẩn bị căn hộ
    def action_chuan_bi(self):
        if not self.bsd_cb_ids:
            raise UserError("Chưa có căn hộ được chọn. Vui lòng kiểm tra lại!")
        self.write({
            'state': 'cph',
        })

    # KD.04.05.02 - Phát hành thêm căn hộ
    def action_phat_hanh(self):
        # kiểm tra đợt mở bán
        if self.bsd_dot_mb_id.state != 'ph' or self.bsd_dot_mb_id.bsd_den_ngay < datetime.date.today():
            raise UserError("Vui lòng kiểm tra lại thông tin đợt mở bán!")

        # kiểm tra trạng thái record
        if self.state != 'cph':
            pass
        else:
            # lấy tất cả unit chuẩn bị phát hành ở trạng thái chuẩn bị đặt chỗ, giữ chỗ
            units = self.bsd_cb_ids.mapped('bsd_unit_id').filtered(lambda x: x.state in ['chuan_bi', 'dat_cho',
                                                                                         'giu_cho'])
            _logger.debug("phát hành")
            units_dang_ph = self.bsd_dot_mb_id.bsd_ph_ids.mapped('bsd_unit_id')
            units = units - units_dang_ph
            _logger.debug(units)
            # các chuẩn bị không đúng trạng thái
            cb_no_state = self.bsd_cb_ids.filtered(lambda c: c.bsd_unit_id not in units)
            cb_no_state.write({
                'bsd_ly_do': 'kd_tt',
            })
            # các chuẩn bị đúng trạng thái
            cb_state = self.bsd_cb_ids - cb_no_state
            # lọc các unit thỏa điều kiện trường ưu tiên là không và không có đợt mở bán
            no_uu_dot_no_mb_units = units.filtered(lambda x: x.bsd_uu_tien == '0' and not x.bsd_dot_mb_id)
            _logger.debug('không uu tien ko đợt phát hành')
            _logger.debug(no_uu_dot_no_mb_units)
            # lọc các unit thỏa điều kiện trường ưu tiên là không và có đợt mở bán
            no_uu_dot_mb_units = units.filtered(lambda x: x.bsd_uu_tien == '0' and x.bsd_dot_mb_id)
            _logger.debug('không uu tien có đợt phát hành')
            _logger.debug(no_uu_dot_mb_units)
            # các chuẩn bị đúng trạng thái, đang được ưu tiên
            cb_uu = cb_state.filtered(lambda u: u.bsd_unit_id.bsd_uu_tien == '1')
            _logger.debug("các chuẩn bị đã ưu tiên")
            _logger.debug(cb_uu)
            cb_uu.write({
                'bsd_ly_do': 'dd_ut',
            })
            # lọc các unit không ưu tiên có đợt mở bán chưa phát hành
            no_ph_units = no_uu_dot_mb_units.filtered(lambda x: x.bsd_dot_mb_id.state != 'ph')
            _logger.debug('không uu tien có đợt mở bán chưa phát hành')
            _logger.debug(no_ph_units)
            ph_units = no_uu_dot_mb_units.filtered(lambda x: x.bsd_dot_mb_id.state == 'ph')
            # kiểm tra các unit không trùng với đợt mở bán hiện tại đang phát hành
            diff_mb_units = ph_units.filtered(lambda x: (x.bsd_dot_mb_id.bsd_tu_ngay < self.bsd_tu_ngay
                                                         and x.bsd_dot_mb_id.bsd_den_ngay < self.bsd_tu_ngay)
                                                            or (x.bsd_dot_mb_id.bsd_tu_ngay > self.bsd_den_ngay
                                                                and x.bsd_dot_mb_id.bsd_den_ngay > self.bsd_den_ngay)
                                              )
            _logger.debug('diff_mb_units')
            _logger.debug(diff_mb_units)
            # các chuẩn bị trùng với đợt mở bán khác
            cb_trung = (cb_state - cb_uu).filtered(lambda t: t.bsd_unit_id not in diff_mb_units
                                                   and t.bsd_unit_id.bsd_dot_mb_id)
            _logger.debug("các chuẩn bị trùng đợt mở bán")
            _logger.debug(cb_trung)
            cb_trung.write({
                'bsd_ly_do': 'dang_mb',
            })
            # Lấy units template
            units_template = set(no_uu_dot_no_mb_units.mapped('product_tmpl_id').ids +
                                 no_ph_units.mapped('product_tmpl_id').ids +
                                 diff_mb_units.mapped('product_tmpl_id').ids)
            # lấy các unit trong bảng giá đang áp dụng cho đợt mở báng
            bang_gia_units_template = set(self.bsd_bang_gia_id.item_ids.mapped('product_tmpl_id').ids)
            # lấy các unit thỏa điều kiện  không trường ưu tiên và bsd_dot_mb_id và có trong bảng giá
            phat_hanh_units_templated = list(units_template.intersection(bang_gia_units_template))

            units_ph = self.env['product.product'].search([('product_tmpl_id', 'in', phat_hanh_units_templated)])
            cb_no_bg = (cb_state - cb_trung - cb_uu).filtered(lambda b: b.bsd_unit_id not in units_ph)
            cb_no_bg.write({
                'bsd_ly_do': 'kc_bg',
            })
        # Xóa cb đã chuyển sang phát hành
            self.bsd_cb_ids.filtered(lambda c: c.bsd_unit_id in units_ph).unlink()
        # Tạo dự liệu trong bảng unit phát hành trong đợt mở bán
        for unit in units_ph:
            pricelist_item = self.env['product.pricelist.item'].search([('product_tmpl_id', '=', unit.product_tmpl_id.id)],
                                                                       limit=1)
            self.bsd_ph_ids.create({
                'bsd_du_an_id': unit.bsd_du_an_id.id,
                'bsd_toa_nha_id': unit.bsd_toa_nha_id.id,
                'bsd_tang_id': unit.bsd_tang_id.id,
                'bsd_unit_id': unit.id,
                'bsd_gia_ban': pricelist_item.fixed_price,
                'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                'bsd_them_unit_id': self.id
            })
            # KD.04.06 Cập nhật tình trạng căn hộ phát hành
            if unit.state == 'chuan_bi':
                unit.write({
                    'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                    'state': 'san_sang',
                })
            else:
                unit.write({
                    'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                })
        # Cập lại lại trạng thái đợt mở bán ngày phát hình và người phát hành
        self.write({
            'state': 'ph',
            'bsd_ngay_duyet': fields.Datetime.now(),
            'bsd_nguoi_duyet': self.env.uid,
        })
        #  KD.04.08 Tính hạn báo giá  của giữ chỗ sau khi phát hành đợt mở bán
        units_ph = self.bsd_ph_ids.mapped('bsd_unit_id')
        for unit_ph in units_ph:
            # cập nhật đợt mở bán cho giữ chỗ
            giu_cho_unit = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', unit_ph.id)])
            giu_cho_unit.write({'bsd_dot_mb_id': self.bsd_dot_mb_id.id})
            # lọc các giữ chỗ của unit đã thanh toán
            giu_cho_ids = giu_cho_unit.filtered(lambda g: g.state == 'giu_cho' and g.bsd_thanh_toan == 'da_tt')
            if giu_cho_ids:
                gc = giu_cho_ids.filtered(lambda x: not x.bsd_rap_can_id).sorted('id')
                gc_no_rc = zip(gc.mapped('id'), gc.mapped('bsd_ngay_tt'))
                gc = giu_cho_ids.filtered(lambda x: x.bsd_rap_can_id).sorted('id')
                gc_rc = zip(gc.mapped('id'), gc.mapped('bsd_ngay_gc'))
                _logger.debug("sắp xếp")
                gc_sorted = sorted(list(gc_rc) + list(gc_no_rc), key=lambda x: x[1])
                id_gc_sorted = [g[0] for g in gc_sorted]
                stt = 0
                time_gc = self.bsd_du_an_id.bsd_gc_smb
                ngay_ph = self.bsd_dot_mb_id.bsd_ngay_ph
                for giu_cho in self.env['bsd.giu_cho'].browse(id_gc_sorted):
                    stt += 1
                    ngay_ph += datetime.timedelta(hours=time_gc)
                    # # KD.04.07 cập nhật trạng thái giữ chỗ khi phát hành
                    # if giu_cho.state == 'dat_cho' and giu_cho.bsd_thanh_toan == 'da_tt':
                    #     giu_cho.write({
                    #         'state': 'giu_cho',
                    #     })
                    giu_cho.write({
                        'bsd_stt_bg': stt,
                        'bsd_ngay_hh_bg': ngay_ph
                    })

    # KD.04.04.05 - Không duyệt thu hồi căn hộ
    def action_khong_duyet(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_them_unit_action').read()[0]
        return action

    # KD.04.04.06 - Hủy thu hồi căn hộ
    def action_huy(self):
        self.write({
            'state': 'huy',
        })


class BsdDotMoBanCB(models.Model):
    _name = 'bsd.them_unit_cb'
    _description = 'Thông tin căn hộ chuẩn bị phiếu thêm căn hộ'
    _rec_name = 'bsd_unit_id'

    bsd_them_unit_id = fields.Many2one('bsd.them_unit', string="Phiếu thêm căn hộ", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True)
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Căn hộ", required=True)
    bsd_gia_ban = fields.Monetary(string="Giá bán", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ly_do = fields.Selection([('kc_bg', 'Không có bảng giá'),
                                  ('dang_mb', 'Đang mở bán'),
                                  ('dd_ut', 'Đánh dấu ưu tiên'),
                                  ('kd_tt', 'Không đúng trạng thái')],
                                 string="Lý do", help="Lý do căn hộ không được phát hành mở bán", readonly=True)

    @api.model
    def create(self, vals):
        if 'bsd_unit_id' in vals.keys() and 'bsd_them_unit_id' in vals.keys():
            if self.env['bsd.them_unit_cb'].search([('bsd_unit_id', '=', vals['bsd_unit_id']),
                                                 ('bsd_them_unit_id', '=', vals['bsd_them_unit_id'])]):
                raise UserError("Phiếu thêm đã có unit")
        rec = super(BsdDotMoBanCB, self).create(vals)
        return rec

    def write(self, vals):
        if 'bsd_unit_id' in vals.keys():
            if self.env['bsd.them_unit_cb'].search([('bsd_unit_id', '=', vals['bsd_unit_id']),
                                                    ('bsd_dot_mb_id', '=', self.bsd_dot_mb_id.id)]):
                raise UserError("Phiếu thêm  đã có unit")
        rec = super(BsdDotMoBanCB, self).write(vals)
        return rec





