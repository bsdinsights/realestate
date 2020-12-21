# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError
import datetime


class BsdCapNhatDTTT(models.Model):
    _name = 'bsd.cn_dttt'
    _description = "Cập nhật diện tích thông thủy"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten'

    bsd_ma = fields.Char(string="Mã", help="Mã cập nhật diện tích thông thủy thực tế", required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã cập nhật diện tích thông thủy thực tế đã tồn tại !')
    ]
    bsd_ten = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Date.today(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True, help="Người xác nhận")
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True, help="Ngày duyệt")
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt", readonly=True)

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Html(string="Lý do", readonly=True, tracking=2)
    bsd_ct_ids = fields.One2many('bsd.cn_dttt_unit', 'bsd_cn_dttt_id', string="Cập nhật diện tích thông thủy chi tiết")

    # tính năng import dự liệu
    def action_nhap_sp(self):
        action = {
            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {
                'model': 'bsd.cn_dttt_unit'
            }
        }
        return action

    # tính năng thêm sản phẩm
    def action_them_sp(self):
        action = self.env.ref('bsd_dich_vu.bsd_cn_dttt_unit_action_popup').read()[0]
        action['context'] = {'default_bsd_cn_dttt_id': self.id,
                             'default_bsd_du_an_id': self.bsd_du_an_id.id}
        return action

    # Xác nhận cập nhật giá trị QSDĐ
    def action_xac_nhan(self):
        if not self.bsd_ct_ids.filtered(lambda x: x.state == 'nhap'):
            raise UserError("Không có sản phẩm cập nhật giá trị DTTT.\nVui lòng kiểm tra lại thông tin.")
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
                'bsd_ngay_xn': fields.Date.today(),
                'bsd_nguoi_xn_id': self.env.uid,
            })
            for ct in self.bsd_ct_ids:
                if ct.state == 'nhap':
                    ct.write({'state': 'xac_nhan'})

    # Duyệt cập nhật diện tích thông thủy
    def action_duyet(self):
        message = ''
        ct_ids = self.bsd_ct_ids.filtered(lambda x: x.state == 'xac_nhan')
        # Lọc các hợp đồng đã bị thanh lý
        hop_dong = ct_ids.mapped('bsd_hd_ban_id').filtered(lambda h: h.state == 'thanh_ly')
        if hop_dong:
            message += "<ul><li>Những hợp đồng đã bị thanh lý: {}</li>".format(','.join(hop_dong.mapped('bsd_ma_hd_ban')))
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
            for ct in ct_ids:
                pass

    # Không duyệt cập nhật DTTT
    def action_khong_duyet(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_cn_dttt_action').read()[0]
        return action

    # Hủy cập nhật DTTT
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
            raise UserError(_('Dự án chưa có mã cập nhật diện tích thông thủy.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdCapNhatDTTT, self).create(vals)

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


class BsdCapNhatDTTTDUnit(models.Model):
    _name = 'bsd.cn_dttt_unit'
    _description = "Chi tiết cập nhật diện tích thông thủy thực tế"
    _order = 'bsd_stt'
    _rec_name = 'bsd_unit_id'

    bsd_cn_dttt_id = fields.Many2one('bsd.cn_dttt', ondelete='cascade',
                                     string="Cập nhật DTTT",
                                     help="Tên cập nhật diện tích thông thủy", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", readonly=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", readonly=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_stt = fields.Integer(related='bsd_unit_id.bsd_stt', store=True)
    bsd_dt_tt_tt = fields.Float(string="DT thực tế", help="Diện tích thông thủy thực tế", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_dt_tt_tk = fields.Float(string="DT thiết kế",
                                help="Diện tích thông thủy thiết kế", readonly=True)
    bsd_cl_tt = fields.Float(string="CL thực tế", help="Phầm trăm chênh lệch thực tế sau khi đo đạt",
                             readonly=True, digits=(2, 2))
    bsd_cl_cp = fields.Float(string="CL cho phép", help="Phần trăm chênh lệch cho phép của sản phẩm",
                             readonly=True)

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_dt_tt_tk = self.bsd_unit_id.bsd_dt_sd
        self.bsd_cl_cp = self.bsd_unit_id.bsd_dt_cl
        self.bsd_hd_ban_id = self.bsd_unit_id.bsd_hd_ban_id

    @api.onchange('bsd_dt_tt_tt', 'bsd_dt_tt_tk')
    def _onchange_dt(self):
        if self.bsd_dt_tt_tk:
            self.bsd_cl_tt = float_round((self.bsd_dt_tt_tt - self.bsd_dt_tt_tk) / self.bsd_dt_tt_tk * 100, 2)

    bsd_loai = fields.Selection([('td_tt', 'PL thay đổi thông tin hợp đồng'),
                                 ('td_dt', 'PL cập nhật diện tích thông thủy thực tế'),
                                 ('tb_kq', 'Thư thông báo kết quả')],
                                string="Xử lý", readonly=True)
    bsd_tien_cl = fields.Monetary(string="Tiền chênh lệch",
                                  help="Tiền chênh lệch khi cập nhật diện tích thông thủy thực tế")
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    def action_huy(self):
        if self.state == 'nhap':
            self.write({'state': 'huy'})

    def action_tao(self):
        pass

    @api.model
    def create(self, vals):
        res = super(BsdCapNhatDTTTDUnit, self).create(vals)
        res.write({
            'bsd_du_an_id': res.bsd_unit_id.bsd_du_an_id.id,
            'bsd_hd_ban_id': res.bsd_unit_id.bsd_hd_ban_id.id,
            'bsd_dt_tt_tk': res.bsd_unit_id.bsd_dt_sd,
            'bsd_cl_cp': res.bsd_unit_id.bsd_dt_cl,
        })
        if res.bsd_dt_tt_tt <= 0:
            raise UserError(_("Diện tích thực tế không thể nhỏ hơn hoặc bằng 0"))
        else:
            res.write({
                'bsd_cl_tt': float_round((res.bsd_dt_tt_tt - res.bsd_dt_tt_tk) / res.bsd_dt_tt_tk * 100, 2)
            })
        return res
