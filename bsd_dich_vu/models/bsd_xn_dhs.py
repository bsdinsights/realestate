# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdXacNhanDHS(models.Model):
    _name = 'bsd.xn_dhs'
    _description = "Xác nhận đủ hồ sơ làm giấy tờ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten'

    bsd_ma = fields.Char(string="Mã", help="Mã xác nhận đủ hồ sơ làm giấy tờ", required=True,
                         readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã xác nhận đủ hồ sơ làm giấy tờ đã tồn tại !')
    ]
    bsd_ten = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày", required=True, default=lambda self: fields.Date.today(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True, readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngay_xn = fields.Date(string="Ngày xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True, help="Người xác nhận")
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", help="Ngày duyệt", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'), ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string='Trạng thái', help="Trạng thái",
                             required=True, readonly=True, default='nhap', tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", help="Lý do", readonly=True, tracking=2)
    bsd_ct_ids = fields.One2many('bsd.xn_dhs_unit', 'bsd_xn_dhs_id', string="Cập nhật NDC chi tiết",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})

    def action_nhap_sp(self):
        action = {
            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {
                'model': 'bsd.xn_dhs_unit',
                'context': self._context,
            }
        }
        return action

    # tính năng thêm sản phẩm
    def action_them_sp(self):
        action = self.env.ref('bsd_dich_vu.bsd_xn_dhs_unit_action_popup').read()[0]
        action['context'] = {'default_bsd_xn_dhs_id': self.id,
                             'default_bsd_du_an_id': self.bsd_du_an_id.id}
        return action

    def action_xac_nhan(self):
        if not self.bsd_ct_ids.filtered(lambda x: x.state == 'nhap'):
            raise UserError("Không có sản phẩm cập nhật giá trị QSDĐ.\nVui lòng kiểm tra lại thông tin.")
        message = ''
        ct_ids = self.bsd_ct_ids.filtered(lambda x: x.state == 'xac_nhan')
        _logger.debug(ct_ids)
        # Lọc các hợp đồng đã bị thanh lý
        hop_dong_da_tl = ct_ids.mapped('bsd_hd_ban_id').filtered(lambda h: h.state == 'thanh_ly')
        if hop_dong_da_tl:
            message += "<ul><li>Những hợp đồng đã bị thanh lý: {}</li>".format(','.join(hop_dong_da_tl.mapped('bsd_ma_hd_ban')))

        # Lọc các hợp đồng chưa nộp giấy cmnd
        ct_no_cmnd = ct_ids.filtered(lambda x: not x.bsd_cmnd_hc)
        if ct_no_cmnd:
            message += "<ul><li>Những sản phẩm chưa nộp giấy CMND/ Hộ chiếu: {}</li>"\
                .format(','.join(ct_no_cmnd.mapped('bsd_hd_ban_id').mapped('bsd_ma_hd_ban')))

        # Lọc các hợp đồng chưa nộp Hộ khẩu/ Thẻ thường trú
        ct_no_hk = ct_ids.filtered(lambda x: not x.bsd_hk_ttt)
        if ct_no_hk:
            message += "<ul><li>Những sản phẩm chưa nộp hộ khẩu/ thẻ thường trú: {}</li>"\
                .format(','.join(ct_no_hk.mapped('bsd_hd_ban_id').mapped('bsd_ma_hd_ban')))

        # Lọc các hợp đồng chưa nộp hợp đồng mua bán
        ct_no_hd = ct_ids.filtered(lambda x: not x.bsd_hdmb)
        if ct_no_hd:
            message += "<ul><li>Những sản phẩm chưa nộp hợp đồng mua bán: {}</li>"\
                .format(','.join(ct_no_hd.mapped('bsd_hd_ban_id').mapped('bsd_ma_hd_ban')))

        # Lọc các hợp đồng chưa nộp hóa đơn thuế VAT
        ct_no_vat = ct_ids.filtered(lambda x: not x.bsd_hd_vat)
        if ct_no_vat:
            message += "<ul><li>Những sản phẩm chưa nộp hóa đơn thuế VAT: {}</li>"\
                .format(','.join(ct_no_vat.mapped('bsd_hd_ban_id').mapped('bsd_ma_hd_ban')))

        # Lọc các hợp đồng chưa nộp giấy xác nhận tình trạng hôn nhân
        ct_no_tthn = ct_ids.filtered(lambda x: not x.bsd_tt_hn)
        if ct_no_tthn:
            message += "<ul><li>Những sản phẩm chưa nộp giấy xác nhận tình trạng hôn nhân: {}</li>"\
                .format(','.join(ct_no_tthn.mapped('bsd_hd_ban_id').mapped('bsd_ma_hd_ban')))

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

    @api.model
    def create(self, vals):
        sequence = None
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã xác nhận đủ hồ sơ.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdXacNhanDHS, self).create(vals)


class BsdXacNhanDHSChiTiet(models.Model):
    _name = 'bsd.xn_dhs_unit'
    _description = 'Xác nhận đủ hồ sơ từng sản phẩm'
    _rec_name = 'bsd_unit_id'

    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Date.today(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_xn_dhs_id = fields.Many2one('bsd.xn_dhs', string="XN.ĐHS", help="Xác nhận đủ hồ sơ (chính)",
                                    ondelete='cascade', index=True, copy=False)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_stt = fields.Integer(related='bsd_unit_id.bsd_stt', store=True)
    bsd_cmnd_hc = fields.Boolean(string='CMND/ Hộ chiếu', help="Đã nhận CMND hoặc hộ chiếu")
    bsd_hk_ttt = fields.Boolean(string='Hộ khẩu/ Thẻ TT', help="Đã nhận hộ khẩu hoặc thẻ thường trú")
    bsd_hdmb = fields.Boolean(string='Hợp đồng', help="Đã nhận hợp đồng mua bán")
    bsd_hd_vat = fields.Boolean(string="HĐ thuế VAT", help="Hóa đơn thuế VAT")
    bsd_tt_hn = fields.Boolean(string="Giấy XN.TTHN", help="Giấy xác nhận tình trạng hôn nhân")
    bsd_hs_ids = fields.Many2many('bsd.hs_gt', string="Giấy tờ khác", help="Hồ sơ/ giấy tờ khác")
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)

    # Tên hiện thị record
    def name_get(self):
        res = []
        for xn in self:
            ma_xn_dkbg = xn.bsd_xn_dhs_id.bsd_ma
            ma_unit = xn.bsd_unit_id.bsd_ma_unit
            res.append((xn.id, "{0} - {1}".format(ma_xn_dkbg, ma_unit)))
        return res

    def action_tao(self):
        pass

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        _logger.debug("Onchange")
        hd_ban = self.bsd_unit_id.bsd_hd_ban_id
        if hd_ban:
            dot_tt = hd_ban.bsd_ltt_ids.filtered(lambda x: x.bsd_ma_dtt == 'DBGC')[0]
        else:
            dot_tt = False
        self.bsd_hd_ban_id = hd_ban
        self.bsd_dot_tt_id = dot_tt
