# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductPriceList(models.Model):
    _inherit = 'product.pricelist'
    bsd_ma_bg = fields.Char(string="Mã", help="Mã chiết khấu", required=True, readonly=True, copy=False,
                            default='/')
    _sql_constraints = [
        ('bsd_ma_bg_unique', 'unique (bsd_ma_bg)',
         'Mã bảng giá đã tồn tại !'),
    ]
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngay_bd = fields.Date(string="Ngày bắt đầu", help="Ngày bắt đầu áp dụng bảng giá", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_kt = fields.Date(string="Ngày kết thúc", help="Ngày kết thúc áp dụng bảng giá", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    name = fields.Char(string="Tên", help="Tên bảng giá bán", required=True,
                       readonly=True, states={'nhap': [('readonly', False)]})
    bsd_ly_do = fields.Char(string="Lý do", readonly=True,
                            help="Lý do không duyệt bảng giá bán", tracking=2, copy=False)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True, copy=False)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True, copy=False)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('het_han', 'Hết hạn'), ('huy', 'Hủy')],
                             string="Trạng thái", required=True, default='nhap', tracking=1)
    item_ids = fields.One2many('product.pricelist.item', 'pricelist_id', 'Pricelist Items', copy=True,
                               readonly=True,
                               states={'nhap': [('readonly', False)]})

    # Kiểm tra dữ liệu ngày hiệu lực
    @api.constrains('bsd_tu_ngay', 'bsd_den_ngay')
    def _constrains_ngay(self):
        for each in self:
            if each.bsd_tu_ngay:
                if not each.bsd_den_ngay:
                    raise UserError(_("Sai thông tin ngày kết thúc.\nVui lòng kiểm tra lại thông tin."))
                elif each.bsd_den_ngay < each.bsd_tu_ngay:
                    raise UserError(_("Ngày kết thúc không thể nhỏ hơn ngày bắt đầu.\nVui lòng kiểm tra lại thông tin."))

    # Xác nhận bảng giá
    def action_xac_nhan(self):
        if not self.item_ids:
            raise UserError(_('Bạn chưa khai báo chi tiết bảng giá.\nVui lòng kiểm tra lại'))
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # Duyệt bảng giá
    def action_duyet(self):
        if not self.item_ids:
            raise UserError(_('Bạn chưa khai báo chi tiết bảng giá.\nVui lòng kiểm tra lại'))
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
                'bsd_ngay_duyet': fields.Date.today(),
                'bsd_nguoi_duyet_id': self.env.uid,
            })
        for item in self.item_ids:
            item.product_tmpl_id.write({
                'list_price': item.fixed_price
            })

    # Không duyệt bảng giá
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_bang_gia_action').read()[0]
        return action

    # Hủy bảng giá
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy',
            })

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã bảng giá.'))
        vals['bsd_ma_bg'] = sequence.next_by_id()
        return super(ProductPriceList, self).create(vals)


class ProductPriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    bsd_ngay_duyet = fields.Date(related='pricelist_id.bsd_ngay_duyet', store=True)
    bsd_state = fields.Selection(related='pricelist_id.state', store=True)
    date_start = fields.Date(string='Ngày bắt đầu', related='pricelist_id.bsd_ngay_bd', store=True)
    date_end = fields.Date(string='Ngày kết thúc', related='pricelist_id.bsd_ngay_kt', store=True)
    applied_on = fields.Selection([
        ('3_global', 'All Products'),
        ('2_product_category', ' Product Category'),
        ('1_product', 'Product'),
        ('0_product_variant', 'Product Variant')], "Apply On",
        default='1_product', required=True, readonly=True,
        help='Pricelist Item applicable on selected option')
    compute_price = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('percentage', 'Percentage (discount)'),
        ('formula', 'Formula')], index=True, default='fixed', required=True, readonly=True)