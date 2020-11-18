# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdThemUnit(models.Model):
    _name = 'bsd.them_unit'
    _description = 'Thêm Sản phẩm trong đợt phát hành'
    _rec_name = 'bsd_ma_tu'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_tu = fields.Char(string="Mã", required=True, readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_tu_unique', 'unique (bsd_ma_tu)',
         'Mã Phiếu thêm unit đã tồn tại !'),
    ]
    bsd_ngay_tu = fields.Date(string="Ngày", help="Ngày thực hiện", required=True,
                              readonly=True,default=lambda self: fields.Date.today(),
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
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", help="Ngày duyệt yêu cầu", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt yêu cầu",
                                      readonly=True)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái",
                             tracking=1, required=True, default='nhap')
    bsd_cb_ids = fields.One2many('bsd.them_unit_cb', 'bsd_them_unit_id', string="Chuẩn bị",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ph_ids = fields.One2many('bsd.dot_mb_unit', 'bsd_them_unit_id', string="Phát hành", readonly=True)

    # KD.04.05.01 - Chuẩn bị Sản phẩm
    def action_chuan_bi(self):
        if not self.bsd_cb_ids:
            raise UserError("Chưa có Sản phẩm được chọn. Vui lòng kiểm tra lại thông tin !")
        self.write({
            'state': 'xac_nhan',
        })

    def action_xac_nhan(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phiếu thêm SP',
            'res_model': 'bsd.them_unit',
            'res_id': self.id,
            'target': 'current',
            'view_mode': 'form'
        }

    # KD.04.05.02 - Phát hành thêm Sản phẩm
    def action_phat_hanh(self):
        # kiểm tra đợt mở bán
        if self.bsd_dot_mb_id.state != 'ph' or self.bsd_dot_mb_id.bsd_den_ngay < datetime.date.today():
            raise UserError("Vui lòng kiểm tra lại thông tin đợt mở bán!")

        # kiểm tra trạng thái record
        if self.state != 'xac_nhan':
            pass
        else:
            action = self.env.ref('bsd_kinh_doanh.bsd_wizard_ph_them_unit_action').read()[0]
            return action

    def action_phat_hanh_wizard(self, so_gio):
        # lấy tất cả unit chuẩn bị phát hành ở trạng thái chuẩn bị đặt chỗ, giữ chỗ, sẵn sàng
        units = self.bsd_cb_ids.mapped('bsd_unit_id').filtered(lambda x: x.state in ['chuan_bi',
                                                                                     'dat_cho',
                                                                                     'san_sang',
                                                                                     'giu_cho'])
        # các sản phẩm đã có giao dịch
        cb_no_state = self.bsd_cb_ids.filtered(lambda c: c.bsd_unit_id not in units)
        cb_no_state.write({
            'bsd_ly_do': 'kd_tt',
        })
        # các chuẩn bị chưa có giao dịch
        cb_state = self.bsd_cb_ids - cb_no_state

        # các chuẩn bị đúng trạng thái, đang được ưu tiên
        cb_uu = cb_state.filtered(lambda u: u.bsd_unit_id.bsd_uu_tien == '1')
        cb_uu.write({
            'bsd_ly_do': 'dd_ut',
        })
        # Lọc các sản phẩm đang ưu tiên
        cb_state_uu = cb_state - cb_uu
        # các chuẩn bị trùng với đợt mở bán khác
        cb_trung = cb_state_uu.filtered(lambda t: t.bsd_unit_id.bsd_dot_mb_id)
        cb_trung.write({
            'bsd_ly_do': 'dang_mb',
        })
        cb_state_uu_trung = cb_state_uu - cb_trung
        # Kiểm tra nếu có sản phẩm không thỏa điều kiện thì chuyển trạng thái về nháp
        if len(self.bsd_cb_ids) != len(cb_state_uu_trung):
            self.write({
                'state': 'nhap',
                'bsd_ly_do': "Danh sách chuẩn bị sản phẩm không thỏa điều kiện"
            })
        else:
            # Lấy units template
            units_template = set(cb_state_uu_trung.mapped('bsd_unit_id').mapped('product_tmpl_id').ids)
            # lấy các unit trong bảng giá đang áp dụng cho đợt mở bán
            bang_gia_units_template = set(self.bsd_bang_gia_id.item_ids.mapped('product_tmpl_id').ids)
            # lấy các unit thỏa điều kiện  không trường ưu tiên và bsd_dot_mb_id và có trong bảng giá
            phat_hanh_units_templated = list(units_template.intersection(bang_gia_units_template))
            # Các sản phẩm đã có giá trong bảng giá bán của đợt mở bán
            units_co_bang_gia = self.env['product.product'].search(
                [('product_tmpl_id', 'in', phat_hanh_units_templated)])
            # Các sản phẩm không có giá trong bảng giá bán của đợt mở bán
            units_ko_bang_gia = cb_state_uu_trung.mapped('bsd_unit_id') - units_co_bang_gia
            # phát hành các unit có bảng giá
            for unit in units_co_bang_gia:
                pricelist_item = self.env['product.pricelist.item'].search(
                    [('product_tmpl_id', '=', unit.product_tmpl_id.id)],
                    limit=1)
                self.bsd_ph_ids.create({
                    'bsd_du_an_id': unit.bsd_du_an_id.id,
                    'bsd_toa_nha_id': unit.bsd_toa_nha_id.id,
                    'bsd_tang_id': unit.bsd_tang_id.id,
                    'bsd_unit_id': unit.id,
                    'bsd_gia_ban': pricelist_item.fixed_price,
                    'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                    'bsd_them_unit_id': self.id,
                })
                # KD.04.06 Cập nhật tình trạng Sản phẩm phát hành
                if unit.state == 'chuan_bi':
                    unit.write({
                        'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                        'state': 'san_sang',
                    })
                else:
                    unit.write({
                        'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                    })
            # phát hành các unit không có trong bảng giá bán
            for unit in units_ko_bang_gia:
                cb = self.bsd_cb_ids.filtered(lambda c: c.bsd_unit_id == unit)
                # Cập nhật giá của sản phẩm vào bảng giá của đợt mở bán
                self.bsd_bang_gia_id.item_ids.create({
                    'product_tmpl_id': unit.product_tmpl_id.id,
                    'fixed_price': cb.bsd_gia_ban,
                    'bsd_them_unit_id': self.id,
                })
                unit.write({
                    'list_price': cb.bsd_gia_ban
                })
                self.bsd_ph_ids.create({
                    'bsd_du_an_id': unit.bsd_du_an_id.id,
                    'bsd_toa_nha_id': unit.bsd_toa_nha_id.id,
                    'bsd_tang_id': unit.bsd_tang_id.id,
                    'bsd_unit_id': unit.id,
                    'bsd_gia_ban': cb.bsd_gia_ban,
                    'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                    'bsd_them_unit_id': self.id,
                })
                # KD.04.06 Cập nhật tình trạng Sản phẩm phát hành
                if unit.state == 'chuan_bi':
                    unit.write({
                        'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                        'state': 'san_sang',
                    })
                else:
                    unit.write({
                        'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                    })
            # Cập nhập người duyệt ngày duyệt
            self.write({
                'state': 'duyet',
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ngay_duyet': fields.Date.today()
            })
        # Tính hạn giữ chỗ của giữ chỗ sau khi phát hành đợt mở bán
        # cập nhật đợt mở bán cho giữ chỗ
        units_ph = self.bsd_ph_ids.mapped('bsd_unit_id')
        for unit_ph in units_ph:
            giu_cho_unit = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', unit_ph.id)])
            for gc in giu_cho_unit:
                gc.write({
                    'bsd_dot_mb_id': self.bsd_dot_mb_id.id,
                    'bsd_ngay_hh_gc': gc.bsd_ngay_hh_gc + datetime.timedelta(hours=so_gio)
                })

    # KD.04.04.05 - Không duyệt thêm Sản phẩm
    def action_khong_duyet(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_wizard_them_unit_action').read()[0]
        return action

    # KD.04.04.06 - Hủy thêm Sản phẩm
    def action_huy(self):
        self.write({
            'state': 'huy',
        })

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phiếu thêm Sản phẩm đợt mở bán.'))
        vals['bsd_ma_tu'] = sequence.next_by_id()
        res = super(BsdThemUnit, self).create(vals)
        return res


class BsdDotMoBanCB(models.Model):
    _name = 'bsd.them_unit_cb'
    _description = 'Thông tin Sản phẩm chuẩn bị phiếu thêm Sản phẩm'
    _rec_name = 'bsd_unit_id'

    bsd_them_unit_id = fields.Many2one('bsd.them_unit', string="Phiếu thêm SP", required=True, ondelete='CASCADE')
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True)
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True)
    bsd_gia_ban = fields.Monetary(string="Giá bán", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ly_do = fields.Selection([('dang_mb', 'Đang mở bán'),
                                  ('dd_ut', 'Đánh dấu ưu tiên'),
                                  ('kd_tt', 'Đã có giao dịch')],
                                 string="Lý do", help="Lý do Sản phẩm không được phát hành mở bán", readonly=True)

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_gia_ban = self.bsd_unit_id.list_price

    @api.model
    def create(self, vals):
        if 'bsd_unit_id' in vals.keys() and 'bsd_them_unit_id' in vals.keys():
            if self.env['bsd.them_unit_cb'].search([('bsd_unit_id', '=', vals['bsd_unit_id']),
                                                    ('bsd_them_unit_id', '=', vals['bsd_them_unit_id'])]):
                raise UserError("Phiếu đã có sản phẩm.\nVui lòng kiểm tra lại thông tin!")
        rec = super(BsdDotMoBanCB, self).create(vals)
        return rec

    def write(self, vals):
        if 'bsd_unit_id' in vals.keys():
            if self.env['bsd.them_unit_cb'].search([('bsd_unit_id', '=', vals['bsd_unit_id']),
                                                    ('bsd_dot_mb_id', '=', self.bsd_dot_mb_id.id)]):
                raise UserError("Phiếu đã có sản phẩm.\nVui lòng kiểm tra lại thông tin.")
        rec = super(BsdDotMoBanCB, self).write(vals)
        return rec


class ProductPriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    bsd_them_unit_id = fields.Many2one('bsd.them_unit', string="Phiếu thêm SP", readonly=True)


