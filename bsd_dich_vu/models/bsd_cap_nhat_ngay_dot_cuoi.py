# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdCapNhatNDC(models.Model):
    _name = 'bsd.cn_ndc'
    _description = "Cập nhật ngày hết hạn thanh toán đợt thanh toán cuối"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_cn'

    bsd_ma_cn = fields.Char(string="Mã", help="Mã cập nhật ngayd đến hạn thanh toán đợt cuối ", required=True,
                            readonly=True,
                            copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_cn_unique', 'unique (bsd_ma_cn)',
         'Mã phiếu cập nhật DKBG đã tồn tại !')
    ]
    bsd_ten_cn = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_ngay_cn = fields.Datetime(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now(),
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True, readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", help="Ngày duyệt", readonly=True)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'), ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string='Trạng thái', help="Trạng thái",
                             required=True, readonly=True, default='nhap', tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", help="Lý do", readonly=True, tracking=2)
    bsd_ct_ids = fields.One2many('bsd.cn_ndc_ct', 'bsd_cn_ndc_id', string="Cập nhật NDC chi tiết",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})

    # DV22.01 Xác nhận cập nhật đến hạn thanh toán đợt cuối
    def action_xac_nhan(self):
        if not self.bsd_ct_ids:
            raise UserError(_('Không có Hợp đồng cần được cập nhật đến hạn thanh toán của đợt cuối'))
        else:
            ct = self.bsd_ct_ids.filtered(lambda x: x.bsd_hd_ban_id.state == 'thanh_ly')
            ct.write({
                'state': 'huy',
                'bsd_ly_do_huy': 'Hợp đồng bị thanh lý'
            })
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
            })

    # DV.22.02 Duyệt cập nhật ngày đến hạn thanh toán đợt cuối
    def action_duyet(self):
        # Kiểm tra các hợp đồng đã bị thanh lý chưa
        ct_da_tl = self.bsd_ct_ids.filtered(lambda x: x.bsd_hd_ban_id.state == 'thanh_ly')
        if ct_da_tl:
            ct_da_tl.write({
                    'state': 'huy',
                    'bsd_ly_do_huy': 'Hợp đồng đã bị thanh lý'
                })
        # Kiểm tra trạng thái thanh toán của đợt thanh toán cuối
        ct_da_tt = self.bsd_ct_ids.filtered(lambda x: x.bsd_dot_tt_id.bsd_thanh_toan != 'chua_tt')
        if ct_da_tt:
            ct_da_tt.write({
                'state': 'huy',
                'bsd_ly_do_huy': 'Đợt thanh toán đã được thanh toán'
            })
        ct_ids = self.bsd_ct_ids - ct_da_tt - ct_da_tl
        if ct_ids:
            ct_ids.write({
                'state': 'duyet',
            })
        # Cập nhật hạn thanh toán đợt cuối
        for ct in ct_ids:
            ct.bsd_dot_tt_id.write({
                'bsd_ngay_hh_tt': ct.bsd_ngay_dtt
            })
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
                'bsd_ngay_duyet': fields.Datetime.now(),
                'bsd_nguoi_duyet_id': self.env.uid
            })
        # Hiển thị thông báo các hợp đồng đã bị thanh lý hoặc đã được thanh toán
        message = ''
        # Lọc các hợp đồng đã bị thanh lý
        if ct_da_tl:
            message += "<ul><li>Những hợp đồng đã bị thanh lý: {}</li>"\
                .format(','.join(ct_da_tl.bsd_hd_ban_id.mapped('bsd_ma_hd_ban')))
        # Lọc các đặ
        if ct_da_tt:
            message += "<li>Những hợp đồng đã thanh toán đợt cuối: {}</li>"\
                .format(','.join(ct_da_tl.bsd_hd_ban_id.mapped('bsd_ma_hd_ban')))
        if message:
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

    # DV.22.03 Không duyệt cập nhật ngày đến hạn thanh toán đợt cuối
    def action_khong_duyet(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_cn_ndc_action').read()[0]
        return action

    # DV.22.04 Hủy cập nhật ngày đến hạn thanh toán cuối
    def action_huy(self):
        # Cập nhật trạng thái hủy chi tiết
        self.bsd_ct_ids.write({
            'state': 'huy'
        })
        if self.state == 'xac_nhan':
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
            raise UserError(_('Dự án chưa có mã cập nhật dự kiến bàn giao'))
        vals['bsd_ma_cn'] = sequence.next_by_id()
        return super(BsdCapNhatNDC, self).create(vals)


class BsdCapNhatNDCChiTiet(models.Model):
    _name = 'bsd.cn_ndc_ct'
    _description = 'Chi tiết cập nhật ngày đợt cuối'

    bsd_ten_ct = fields.Char(string="Tiêu đề", help="Tên chi tiết cập nhật ngày đến hạn thanh toán đợt cuối",
                             required=True)
    bsd_cn_ndc_id = fields.Many2one('bsd.cn_ndc', string="Cập nhật ĐHTT", help="Cập nhật đến hạn thanh toán cuối",
                                    required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True)
    bsd_ngay_dtt = fields.Date(string="Ngày đến hạn", help="Hạn thanh toán của đợt thanh toán cuối", required=True)
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán cuối", help="Đợt thanh toán cuối")
    bsd_ly_do_huy = fields.Char(string="Lý do hủy", help="Lý do hủy", readonly=True)
    state = fields.Selection([('duyet', 'Duyệt'), ('huy', 'Hủy')], string="Trạng thái",
                             help="Trạng thái của chi tiết", readonly=True)

    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
        self.bsd_dot_tt_id = self.bsd_hd_ban_id.filtered(lambda x: x.bsd_ma_dtt == 'DBGC')

    @api.constrains('bsd_ngay_dtt', 'bsd_dot_tt_id')
    def _constrains_ngay_dtt(self):
        stt = self.bsd_dot_tt_id.bsd_stt - 1
        dot_lien_ke = self.bsd_hd_ban_id.filtered(lambda x: x.bsd_stt == stt)
        if self.bsd_ngay_dtt < dot_lien_ke.bsd_ngay_hh_tt:
            raise UserError(_('Ngày đến hạn nhỏ hơn ngày đến hạn của đợt thanh toán liền kề'))

    @api.onchange('bsd_cn_ndc_id')
    def _onchange_cn_ndc(self):
        self.bsd_ten_ct = self.bsd_cn_ndc_id.bsd_ten_cn
