# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdCapNhatDKBG(models.Model):
    _name = 'bsd.cn_dkbg'
    _description = "Cập nhật điều kiện bàn giao"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_cn_dkbg'

    bsd_ma_cn_dkbg = fields.Char(string="Mã", help="Mã chứng từ ", required=True, readonly=True,
                                 copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_cn_dkbg_unique', 'unique (bsd_ma_cn_dkbg)',
         'Mã phiếu cập nhật DKBG đã tồn tại !')
    ]
    bsd_ten_cn_dkbg = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_ngay_cn_dkbg = fields.Datetime(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now(),
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection([('tat_ca', 'Tất cả'),
                                 ('san_pham', 'Sản phẩm'),
                                 ('dot_tt', 'Đợt thanh toán')], string="Loại cập nhật", required=True,
                                help="""Lựa chọn cách cập nhật ngày dự kiến bàn giao:\n
                                        1 - Tất cả: Cập nhật đồng loạt cho Sản phẩm, Hợp đồng, 
                                        Đợt thanh toán là Đợt dự kiến bàn giao. \n
                                        2 - Sản phẩm: Chỉ cập nhật cho Sản phẩm.\n
                                        3 - Đợt thanh toán: Chỉ cập nhật Đợt thanh toán là Đợt dự kiến bàn giao""",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_ttcn = fields.Date(string="Ngày cất nóc", help="Ngày cất nóc thực tế", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_ut = fields.Date(string="Ngày ước tính", required=True,
                              help="""Ngày dùng để ước tính tiền phạt chậm thanh toán khi tạo thông báo bàn giao""",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_co_tbnt = fields.Boolean(string="Tạo TBNT", help="Đánh dấu dùng để tạo Thông báo nghiệm thu sản phẩm",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_co_tbbg = fields.Boolean(string="Tạo TBBG", help="Đánh dấu dùng để tạo Thông báo bàn giao sản phẩm",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True, help="Ngày duyệt")
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt", readonly=True)
    bsd_da_tao_tbbg = fields.Boolean(string="Thông báo bàn giao", readonly=True,
                                     help="Đánh dấu Cập nhật DKBG đã được tạo thông báo bàn giao")
    bsd_da_tao_tbnt = fields.Boolean(string="Thông báo nghiệm thu", readonly=True,
                                     help="Đánh dấu Cập nhật DKBG đã được tạo thông báo nghiệm thu")

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Char(string="Lý do", readonly=True, tracking=2)
    bsd_ct_ids = fields.One2many('bsd.cn_dkbg_unit', 'bsd_cn_dkbg_id', string="Cập nhật DKBG chi tiết")

    # DV.19.03 Xác nhận cập nhật DKBG
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # DV.19.04 Duyệt cập nhật DKBG
    def action_duyet(self):
        message = ''
        # Lọc các hợp đồng đã bị thanh lý
        hop_dong = self.bsd_ct_ids.mapped('bsd_hd_ban_id').filtered(lambda h: h.state == 'thanh_ly')
        if hop_dong:
            message += "<ul><li>Những hợp đồng đã bị thanh lý: {}</li>".format(','.join(hop_dong.mapped('bsd_ma_hd_ban')))
        # Lọc các unit đã bàn giao
        unit = self.bsd_ct_ids.mapped('bsd_unit_id').filtered(lambda h: h.bsd_ngay_bg)
        if unit:
            message += "<li>Những căn hộ đã bàn giao: {}</li>".format(','.join(unit.mapped('bsd_ten_unit')))
        chi_tiet = self.bsd_ct_ids.filtered(lambda h: h.state == 'nhap')
        if chi_tiet:
            message += "<li>Những chi tiết chưa xác nhận: {}</li></ul>".format(','.join(chi_tiet.mapped('bsd_ma_cn_unit')))
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
        else:
            # Cập nhật trạng thái duyệt cập nhật
            self.write({
                'state': 'duyet',
                'bsd_ngay_duyet': fields.Datetime.now(),
                'bsd_nguoi_duyet_id': self.env.uid
            })
            # Cập nhật trạng thái duyệt cập nhật chi tiết
            self.bsd_ct_ids.write({
                'state': 'duyet'
            })

            ct_dkbg = self.bsd_ct_ids.filtered(lambda c: c.state == 'duyet')
            # DV.19.07 Cập nhật DKBG với loại cập nhật là sản phẩm
            if self.bsd_loai == 'san_pham':
                for ct in ct_dkbg:
                    ct.bsd_unit_id.write({
                        'bsd_ngay_dkbg': ct.bsd_ngay_dkbg_moi,
                    })
            # DV.19.08 Cập nhật DKBG với loại cập nhật là đợt thanh toán
            elif self.bsd_loai == 'dot_tt':
                for ct in ct_dkbg:
                    ct.bsd_dot_tt_id.write({
                        'bsd_ngay_hh_tt': ct.bsd_ngay_dkbg_moi,
                    })
            # DV.19.09 Cập nhật DKBG với loại cập nhật là tất cả
            else:
                for ct in ct_dkbg:
                    ct.bsd_dot_tt_id.write({
                        'bsd_ngay_hh_tt': ct.bsd_ngay_dkbg_moi,
                    })
                    ct.bsd_unit_id.write({
                        'bsd_ngay_dkbg': ct.bsd_ngay_dkbg_moi,
                    })
                    ct.bsd_hd_ban_id.write({
                        'bsd_ngay_dkbg': ct.bsd_ngay_dkbg_moi,
                    })

    # DV.19.05 Không duyệt cập nhật DKBG
    def action_khong_duyet(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_cn_dkbg_action').read()[0]
        return action

    # DV.19.06 Hủy cập nhật DKBG
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
            raise UserError(_('Dự án chưa có mã cập nhật dự kiến bàn giao'))
        vals['bsd_ma_cn_dkbg'] = sequence.next_by_id()
        return super(BsdCapNhatDKBG, self).create(vals)


class BsdCapNhatDKBGUnit(models.Model):
    _name = 'bsd.cn_dkbg_unit'
    _description = "Cập nhật điều kiện bàn giao sản phẩm"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ma_cn_unit'

    bsd_ma_cn_unit = fields.Char(string="Mã", help="Mã cập nhật dự kiến bàn giao chi tiết",
                                 required=True, readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_cn_unit_unique', 'unique (bsd_ma_cn_unit)',
         'Mã cập nhật dkbg sản phẩm đã tồn tại !')
    ]
    bsd_ngay_cn_unit = fields.Datetime(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now(),
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_cn_dkbg_id = fields.Many2one('bsd.cn_dkbg',
                                     string="Cập nhật DKBG",
                                     help="Tên chứng từ cập nhật dự kiến bàn giao", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_loai = fields.Selection(related="bsd_cn_dkbg_id.bsd_loai", store=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Unit", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_ngay_dkbg_ht = fields.Date(string="Ngày DKBG hiện tại", help="Ngày dự kiến bàn giao hiện tại",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngay_dkbg_moi = fields.Date(string="Ngày DKBG mới", help="Ngày dự kiến bàn giao mới",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_ngay_htt = fields.Date(string="Hạn thanh toán", help="Hạn thanh toán",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_gia_ban = fields.Monetary(related="bsd_unit_id.bsd_gia_ban")
    bsd_dk_bg = fields.Float(related="bsd_unit_id.bsd_dk_bg")
    bsd_dt_cl = fields.Float(related="bsd_unit_id.bsd_dt_cl")
    bsd_dt_xd = fields.Float(related="bsd_unit_id.bsd_dt_xd")
    bsd_dt_sd = fields.Float(related="bsd_unit_id.bsd_dt_sd")
    bsd_dt_tt = fields.Float(related="bsd_unit_id.bsd_dt_tt")
    bsd_dt_sh = fields.Float(related="bsd_unit_id.bsd_dt_sh")
    bsd_unit_state = fields.Selection(related="bsd_unit_id.state")
    bsd_ngay_xn = fields.Datetime(string="Ngày xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_ly_do = fields.Char(string="Lý do hủy", help="Lý do hủy", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    # R.01 Dự án
    @api.onchange('bsd_cn_dkbg_id')
    def _onchange_cn_dkbg(self):
        self.bsd_du_an_id = self.bsd_cn_dkbg_id.bsd_du_an_id

    # R.02 Unit
    @api.onchange('bsd_loai', 'bsd_du_an_id')
    def _onchange_loai(self):
        res = {}
        if self.bsd_loai != 'dot_tt':
            res.update({
                'domain': {'bsd_unit_id': [('bsd_du_an_id', '=', self.bsd_du_an_id.id)]}
            })
        else:
            list_id = self.env['product.product'].search([('bsd_du_an_id', '=', self.bsd_du_an_id.id),
                                                          ('bsd_hd_ban_id', '!=', False)]).ids
            res.update({
                'domain': {'bsd_unit_id': [('id', 'in', list_id)]}
            })
        return res

    # R.03 Hợp đồng
    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        self.bsd_ngay_dkbg_ht = self.bsd_unit_id.bsd_ngay_dkbg
        if self.bsd_loai != 'san_pham':
            self.bsd_hd_ban_id = self.bsd_unit_id.bsd_hd_ban_id
        else:
            self.bsd_hd_ban_id = None

    # R.04 Đợt thanh toán
    @api.onchange('bsd_hd_ban_id')
    def _onchange_hd_ban(self):
        if self.bsd_loai != 'san_pham':
            self.bsd_dot_tt_id = self.bsd_hd_ban_id.bsd_ltt_ids.filtered(lambda x: x.bsd_ma_dtt == 'DKBG')
        else:
            self.bsd_dot_tt_id = None

    # DV.19.01 Xác nhận chi tiết Cập nhật DKBG
    def action_xac_nhan(self):
        if not self.bsd_hd_ban_id:
            if self.state == 'nhap':
                self.write({
                    'state': 'xac_nhan',
                    'bsd_ngay_xn': fields.Datetime.now(),
                    'bsd_nguoi_xn_id': self.env.uid,
                })
        else:
            if self.bsd_hd_ban_id.state == 'thanh_ly':
                if self.state == 'nhap':
                    self.write({
                        'state': 'huy',
                        'bsd_ly_do': 'Hợp đồng đã bị thanh lý'
                    })
            else:
                if self.state == 'nhap':
                    self.write({
                        'state': 'xac_nhan',
                        'bsd_ngay_xn': fields.Datetime.now(),
                        'bsd_nguoi_xn_id': self.env.uid,
                    })

    # DV.19.02 Hủy chi tiết Cập nhật DkBG
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy',
            })

    @api.model
    def create(self, vals):
        sequence = None
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã cập nhật dự kiến bàn giao chi tiết'))
        vals['bsd_ma_cn_unit'] = sequence.next_by_id()
        return super(BsdCapNhatDKBGUnit, self).create(vals)