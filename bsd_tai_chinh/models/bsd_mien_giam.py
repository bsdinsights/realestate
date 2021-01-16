# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdMienGiam(models.Model):
    _name = 'bsd.mien_giam'
    _description = "Miễn giảm tiền thanh toán giao dịch"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten'

    bsd_ma = fields.Char(string="Mã", help="Mã miễn giảm", required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã miễn giảm đã tồn tại !')
    ]
    bsd_ten = fields.Char(string="Tiêu đề", help="Tiêu đề miễn", required=True,
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Date.today(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True,
                                    readonly=True, states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True, readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", required=True, readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd(self):
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
        self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id
    bsd_ngay_xn = fields.Datetime(string="Ngày xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True, help="Người xác nhận")
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True, help="Ngày duyệt")
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt", readonly=True)

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Html(string="Lý do", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.mien_giam.ct', 'bsd_mien_giam_id', string="Miễn giảm chi tiết")

    # tính năng import dự liệu
    def action_nhap_sp(self):
        action = {
            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {
                'model': 'bsd.mien_giam.ct'
            }
        }
        return action

    # tính năng thêm sản phẩm
    def action_them_dot(self):
        action = self.env.ref('bsd_tai_chinh.bsd_mien_giam_ct_action_popup').read()[0]
        action['context'] = {'default_bsd_mien_giam_id': self.id,
                             'default_bsd_hd_ban_id': self.bsd_hd_ban_id.id}
        return action

    # Xác nhận khách hàng đã nộp đủ hồ sơ
    def action_xac_nhan(self):
        if not self.bsd_ct_ids.filtered(lambda x: x.state == 'nhap'):
            raise UserError("Không chi tiết miễn giảm.\nVui lòng kiểm tra lại thông tin.")
        message = ''
        ct_ids = self.bsd_ct_ids
        # Lọc các hợp đồng đã bị thanh lý
        hop_dong_da_tl = ct_ids.mapped('bsd_hd_ban_id').filtered(lambda h: h.state == 'thanh_ly')
        hop_dong_chua_tt = ct_ids.mapped('bsd_hd_ban_id').filtered(lambda h: h.state != 'thanh_ly')
        if hop_dong_da_tl:
            message += "<ul><li>Những hợp đồng đã bị thanh lý: {}</li>"\
                .format(','.join(hop_dong_da_tl.mapped('bsd_ma_hd_ban')))
        # Lọc các unit đã bàn giao
        unit = ct_ids.mapped('bsd_unit_id').filtered(lambda h: h.bsd_ngay_bg)
        if unit:
            message += "<li>Những Sản phẩm đã bàn giao: {}</li>".format(','.join(unit.mapped('bsd_ten_unit')))
        if message:
            # Cập nhật trạng thái nháp
            self.write({
                'bsd_ly_do': message
            })
            self.message_post(body=message)
            message_id = self.env['message.wizard'].create(
                {'message': _(message)})
            return {
                'name': _('Thông báo'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                'res_id': message_id.id,
                'target': 'new'
            }
        else:
            if self.state == 'nhap':
                self.write({
                    'state': 'xac_nhan',
                    'bsd_ngay_xn': fields.Date.today(),
                    'bsd_nguoi_xn_id': self.env.uid,
                })
                for ct in self.bsd_ct_ids:
                    if ct.state == 'nhap':
                        ct.write({'state': 'xac_nhan'})

    # Duyệt cập nhật giá trị QSDĐ
    def action_duyet(self):
        message = ''
        ct_ids = self.bsd_ct_ids.filtered(lambda x: x.state == 'xac_nhan')
        # Lọc các hợp đồng đã bị thanh lý
        hop_dong = ct_ids.mapped('bsd_hd_ban_id').filtered(lambda h: h.state == 'thanh_ly')
        if hop_dong:
            message += "<ul><li>Những hợp đồng đã bị thanh lý: {}</li>".format(','.join(hop_dong.mapped('bsd_ma_hd_ban')))
        # Lọc các unit đã bàn giao
        unit = ct_ids.mapped('bsd_unit_id').filtered(lambda h: h.bsd_ngay_bg)
        if unit:
            message += "<li>Những Sản phẩm đã bàn giao: {}</li>".format(','.join(unit.mapped('bsd_ten_unit')))
        if message:
            # Cập nhật trạng thái nháp
            self.write({
                'state': 'nhap',
                'bsd_ly_do': message
            })
            self.bsd_ct_ids.write({
                'state': 'nhap',
            })
            self.message_post(body=message)
            message_id = self.env['message.wizard'].create(
                {'message': _(message)})
            return {
                'name': _('Thông báo'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                'res_id': message_id.id,
                'target': 'new'
            }
        else:
            # Cập nhật trạng thái duyệt cập nhật
            self.write({
                'state': 'duyet',
                'bsd_ngay_duyet': fields.Datetime.now(),
                'bsd_nguoi_duyet_id': self.env.uid,
                'bsd_ly_do': ''
            })
            # Cập nhật trạng thái duyệt cập nhật chi tiết
            ct_ids.write({
                'state': 'duyet'
            })

    # Không duyệt cập nhật giá trị QSDĐ
    def action_khong_duyet(self):
        action = self.env.ref('bsd_tai_chinh.bsd_wizard_khong_duyet_mien_giam_action').read()[0]
        return action

    # Hủy cập nhật giá trị QSDĐ
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy'
            })

    @api.model
    def create(self, vals):
        sequence = None
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã miễn giảm.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdMienGiam, self).create(vals)

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            if operator == 'ilike':
                args += [('bsd_ten', operator, name)]
            elif operator == '=':
                args += [('bsd_ma', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return models.lazy_name_get(recs.with_user(access_rights_uid))


class BsdMienGiamChiTiet(models.Model):
    _name = 'bsd.mien_giam.ct'
    _description = "Chi tiết miễn giảm"
    _order = 'bsd_stt'
    _rec_name = 'bsd_dot_tt_id'

    bsd_mien_giam_id = fields.Many2one('bsd.mien_giam', ondelete='cascade',
                                       string="Miễn giảm",
                                       help="Miễn giảm", required=True,
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Date.today(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection([('dot_tt', 'Đợt thanh toán'), ('lai_phat', 'Lãi phạt chậm TT'),
                                 ('phi_ql', 'Phí quản lý')], string='Loại', readonly=True, required=True,
                                states={'nhap': [('readonly', False)]})
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán", help="Đợt thanh toán", readonly=True,
                                    states={'nhap': [('readonly', False)]}, required=True)
    bsd_stt = fields.Integer(related='bsd_dot_tt_id.bsd_stt', store=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_tien_mg = fields.Monetary(string="Tiền miễn giảm", help="Tiền miễn giảm", required=True, readonly=True,
                                  states={'nhap': [('readonly', False)]})

    @api.onchange('bsd_dot_tt_id')
    def _onchange_dot(self):
        self.bsd_tien_dot_tt = self.bsd_dot_tt_id.bsd_tien_dot_tt
        self.bsd_tien_dot_dtt = self.bsd_dot_tt_id.bsd_tien_da_tt
        self.bsd_tien_dot_ptt = self.bsd_dot_tt_id.bsd_tien_phai_tt
        self.bsd_tien_mg_dot = self.bsd_dot_tt_id.bsd_tien_mg_dot
        self.bsd_tien_phat = self.bsd_dot_tt_id.bsd_tien_phat
        self.bsd_tp_da_tt = self.bsd_dot_tt_id.bsd_tp_da_tt
        self.bsd_tp_phai_tt = self.bsd_dot_tt_id.bsd_tp_phai_tt
        self.bsd_tien_mg_lp = self.bsd_dot_tt_id.bsd_tien_mg_lp
    # Field load từ đợt thanh toán
    bsd_tien_dot_tt = fields.Monetary(string="Tiền đợt TT", help="Tiền đợt thanh toán", readonly=True)
    bsd_tien_dot_dtt = fields.Monetary(string="Tiền đợt đã TT", help="Tiền đợt đã thanh toán", readonly=True)
    bsd_tien_dot_ptt = fields.Monetary(string="Tiền đợt phải TT", help="Tiền đợt phải thanh toán", readonly=True)
    bsd_tien_mg_dot = fields.Monetary(string="Tiền đã miễn giảm đợt", help="Tiền đã miễn giảm đợt", readonly=True)
    # Field lãi phạt
    bsd_tien_phat = fields.Monetary(string="Tiền phạt chậm TT", help="Tiền phạt chậm thanh toán", readonly=True)
    bsd_tp_da_tt = fields.Monetary(string="Tiền phạt đã TT", help="Tiền phạt đã thanh toán", readonly=True)
    bsd_tp_phai_tt = fields.Monetary(string="Tiền phạt phải TT", help="Tiền phạt đã thanh toán", readonly=True)
    bsd_tien_mg_lp = fields.Monetary(string="Tiền đã miễn giảm phạt", help="Tiền đã miễn giảm thanh toán", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_hd_ban_id = self.bsd_unit_id.bsd_hd_ban_id
        self.bsd_qsdd_m2_ht = self.bsd_unit_id.bsd_qsdd_m2
        self.bsd_unit_state = self.bsd_unit_id.state

    def action_huy(self):
        if self.state == 'nhap':
            self.write({'state': 'huy'})

    def action_tao(self):
        pass

    @api.model
    def create(self, vals):
        if vals.get('bsd_dot_tt_id'):
            dot_tt = self.env['bsd.lich_thanh_toan'].browse(vals.get('bsd_dot_tt_id'))
            if not vals.get('bsd_tien_dot_tt'):
                vals['bsd_tien_dot_tt'] = dot_tt.bsd_tien_dot_tt

            if not vals.get('bsd_tien_dot_dtt'):
                vals['bsd_tien_dot_dtt'] = dot_tt.bsd_tien_da_tt

            if not vals.get('bsd_tien_dot_ptt'):
                vals['bsd_tien_dot_ptt'] = dot_tt.bsd_tien_phai_tt

            if not vals.get('bsd_tien_mg_dot'):
                vals['bsd_tien_mg_dot'] = dot_tt.bsd_tien_mg_dot

            if not vals.get('bsd_tien_phat'):
                vals['bsd_tien_phat'] = dot_tt.bsd_tien_phat

            if not vals.get('bsd_tp_da_tt'):
                vals['bsd_tp_da_tt'] = dot_tt.bsd_tp_da_tt

            if not vals.get('bsd_tp_phai_tt'):
                vals['bsd_tp_phai_tt'] = dot_tt.bsd_tp_phai_tt

            if not vals.get('bsd_tien_mg_lp'):
                vals['bsd_tien_mg_lp'] = dot_tt.bsd_tien_mg_lp

        res = super(BsdMienGiamChiTiet, self).create(vals)
        return res
