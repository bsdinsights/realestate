# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdCapNhatDKBG(models.Model):
    _name = 'bsd.cn_dkbg'
    _description = "Cập nhật ngày dự kiến bàn giao"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten'

    bsd_ma = fields.Char(string="Mã", help="Mã cập nhật ngày dự kiến bàn giao", required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã phiếu cập nhật DKBG đã tồn tại !')
    ]
    bsd_ten = fields.Char(string="Tiêu đề", help="Tiêu đề", required=True,
                          readonly=True,
                          states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Datetime(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now(),
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
                                readonly=True, default='tat_ca',
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_ttcn = fields.Date(string="Ngày cất nóc", help="Ngày cất nóc thực tế", required=True,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_ut = fields.Date(string="Ngày ước tính", required=True,
                              help="""Ngày dùng để ước tính tiền phạt chậm thanh toán khi tạo thông báo bàn giao""",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_ngay_htt_moi = fields.Date(string="Hạn TT mới", readonly=True, states={'nhap': [('readonly', False)]},
                                   help="Ngày thanh toán đợt dự kiến bàn giao mặc định của dự án")
    bsd_co_tbnt = fields.Boolean(string="Tạo TBNT", help="Đánh dấu dùng để tạo Thông báo nghiệm thu sản phẩm",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_co_tbbg = fields.Boolean(string="Tạo TBBG", help="Đánh dấu dùng để tạo Thông báo bàn giao sản phẩm",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_ngay_xn = fields.Datetime(string="Ngày xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True, help="Người xác nhận")
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True, help="Ngày duyệt")
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt", readonly=True)
    bsd_da_tao_tbbg = fields.Boolean(string="TB bàn giao", readonly=True,
                                     help="Đánh dấu Cập nhật DKBG đã được tạo thông báo bàn giao")
    bsd_da_tao_tbnt = fields.Boolean(string="TB nghiệm thu", readonly=True,
                                     help="Đánh dấu Cập nhật DKBG đã được tạo thông báo nghiệm thu")

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Html(string="Lý do", readonly=True, tracking=2)
    bsd_ct_ids = fields.One2many('bsd.cn_dkbg_unit', 'bsd_cn_dkbg_id', string="Cập nhật DKBG chi tiết", readonly=True)

    # tính năng import dự liệu
    def action_nhap_sp(self):
        action = {
            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {
                'model': 'bsd.cn_dkbg_unit',
                'context': self._context,
            }
        }
        return action

    # tính năng thêm sản phẩm
    def action_them_sp(self):
        action = self.env.ref('bsd_dich_vu.bsd_cn_dkbg_unit_action_popup').read()[0]
        action['context'] = {'default_bsd_cn_dkbg_id': self.id,
                             'default_bsd_du_an_id': self.bsd_du_an_id.id}
        return action

    # DV.19.03 Xác nhận cập nhật DKBG
    def action_xac_nhan(self):
        if not self.bsd_ct_ids.filtered(lambda x: x.state == 'nhap'):
            raise UserError("Không có sản phẩm cập nhật ngày DKBG.\nVui lòng kiểm tra lại thông tin.")
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan',
                'bsd_ngay_xn': fields.Date.today(),
                'bsd_nguoi_xn_id': self.env.uid,
                'bsd_ly_do': '',
            })
            for ct in self.bsd_ct_ids:
                if ct.state == 'nhap':
                    ct.write({'state': 'xac_nhan'})

    # DV.19.04 Duyệt cập nhật DKBG
    def action_duyet(self):
        message = ''
        ct_xac_nhan = self.bsd_ct_ids.filtered(lambda c: c.state == 'xac_nhan')
        # Lọc các hợp đồng đã bị thanh lý
        hop_dong = self.bsd_ct_ids.mapped('bsd_hd_ban_id').filtered(lambda h: h.state == 'thanh_ly')
        if hop_dong:
            message += "<ul><li>Những hợp đồng đã bị thanh lý: {}</li>".format(','.join(hop_dong.mapped('bsd_ma_hd_ban')))
        # Lọc các unit đã bàn giao
        unit = self.bsd_ct_ids.mapped('bsd_unit_id').filtered(lambda h: h.bsd_ngay_bg)
        if unit:
            message += "<li>Những Sản phẩm đã bàn giao: {}</li>".format(','.join(unit.mapped('bsd_ten_unit')))
        if message:
            # Cập nhật trạng thái nháp
            self.write({
                'state': 'nhap',
                'bsd_ly_do': message
            })
            ct_xac_nhan.write({
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
                'bsd_nguoi_duyet_id': self.env.uid
            })
            # Cập nhật trạng thái duyệt cập nhật chi tiết đã xác nhận
            ct_xac_nhan.write({
                'state': 'duyet'
            })
            # DV.19.07 Cập nhật DKBG với loại cập nhật là sản phẩm
            if self.bsd_loai == 'san_pham':
                for ct in ct_xac_nhan:
                    ct.bsd_unit_id.write({
                        'bsd_ngay_dkbg': ct.bsd_ngay_dkbg_moi,
                        'bsd_ngay_cn': self.bsd_ngay_ttcn,
                    })
            # DV.19.08 Cập nhật DKBG với loại cập nhật là đợt thanh toán
            elif self.bsd_loai == 'dot_tt':
                for ct in ct_xac_nhan:
                    so_ngay_ah = ct.bsd_dot_tt_id.bsd_cs_tt_id.bsd_lai_phat_tt_id.bsd_an_han
                    ct.bsd_dot_tt_id.write({
                        'bsd_ngay_hh_tt': ct.bsd_ngay_htt_moi,
                        'bsd_ngay_ah': ct.bsd_ngay_htt_moi + datetime.timedelta(days=so_ngay_ah)
                    })
            # DV.19.09 Cập nhật DKBG với loại cập nhật là tất cả
            else:
                for ct in ct_xac_nhan:
                    so_ngay_ah = ct.bsd_dot_tt_id.bsd_cs_tt_id.bsd_lai_phat_tt_id.bsd_an_han
                    ct.bsd_dot_tt_id.write({
                        'bsd_ngay_hh_tt': ct.bsd_ngay_htt_moi,
                        'bsd_ngay_ah': ct.bsd_ngay_htt_moi + datetime.timedelta(days=so_ngay_ah)
                    })
                    ct.bsd_unit_id.write({
                        'bsd_ngay_dkbg': ct.bsd_ngay_dkbg_moi,
                        'bsd_ngay_cn': self.bsd_ngay_ttcn,
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
            raise UserError(_('Dự án chưa có mã cập nhật ngày dự kiến bàn giao.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdCapNhatDKBG, self).create(vals)

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


class BsdCapNhatDKBGUnit(models.Model):
    _name = 'bsd.cn_dkbg_unit'
    _description = "Cập nhật điều kiện bàn giao sản phẩm"
    _rec_name = 'bsd_unit_id'

    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Date.today(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_cn_dkbg_id = fields.Many2one('bsd.cn_dkbg',
                                     string="Cập nhật DKBG",
                                     help="Tên chứng từ cập nhật dự kiến bàn giao", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_stt = fields.Integer(related='bsd_unit_id.bsd_stt', store=True)
    bsd_unit_state = fields.Selection([('chuan_bi', 'Chuẩn bị'),
                                      ('san_sang', 'Sẵn sàng'),
                                      ('dat_cho', 'Đặt chỗ'),
                                      ('giu_cho', 'Giữ chỗ'),
                                      ('dat_coc', 'Đặt cọc'),
                                      ('chuyen_coc', 'Chuyển cọc'),
                                      ('da_tc', 'Đã thu cọc'),
                                      ('ht_dc', 'Hoàn tất đặt cọc'),
                                      ('tt_dot_1', 'Thanh toán đợt 1'),
                                      ('ky_tt_coc', 'Ký thỏa thuận cọc'),
                                      ('du_dk', 'Đủ điều kiện'),
                                      ('da_ban', 'Đã bán')], string="Trạng thái SP", readonly=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_dot_tt_id = fields.Many2one('bsd.lich_thanh_toan', string="Đợt thanh toán",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_ngay_htt = fields.Date(string="Hạn TT hiện tại", help="Hạn thanh toán hiện tại của đợt dự kiến bàn giao",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_ngay_htt_moi = fields.Date(string="Hạn TT mới", help="Hạn thanh mới của đợt dự kiến bàn giao",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})

    bsd_ngay_dkbg_ht = fields.Date(string="Ngày DKBG hiện tại", help="Ngày dự kiến bàn giao hiện tại",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ngay_dkbg_moi = fields.Date(string="Ngày DKBG mới", help="Ngày dự kiến bàn giao mới", required=True,
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_so_tb = fields.Integer(string="Số lần TB", help="Số lần hoàn thành thông báo bàn giao",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    # Tên hiện thị record
    def name_get(self):
        res = []
        for ct in self:
            ma_cn_dkbg = ct.bsd_cn_dkbg_id.bsd_ma
            ma_unit = ct.bsd_unit_id.bsd_ma_unit
            res.append((ct.id, "{0} - {1}".format(ma_cn_dkbg, ma_unit)))
        return res

    @api.onchange('bsd_unit_id')
    def _onchange_unit(self):
        hd_ban = self.bsd_unit_id.bsd_hd_ban_id
        if hd_ban:
            dot_tt = hd_ban.bsd_ltt_ids.filtered(lambda x: x.bsd_ma_dtt == 'DKBG')[0]
        else:
            dot_tt = False
        self.bsd_hd_ban_id = hd_ban

        self.bsd_dot_tt_id = dot_tt
        if dot_tt:
            self.bsd_ngay_htt = dot_tt.bsd_ngay_hh_tt
        self.bsd_ngay_dkbg_ht = self.bsd_unit_id.bsd_ngay_dkbg
        self.bsd_unit_state = self.bsd_unit_id.state

    # DV.19.02 Hủy chi tiết Cập nhật DkBG
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy',
            })

    @api.constrains('bsd_ngay_dkbg_moi', 'bsd_ngay_htt_moi')
    def _constraint_ngay_dkbg(self):
        if self.bsd_ngay_htt_moi:
            if self.bsd_ngay_dkbg_moi < self.bsd_ngay_htt_moi:
                raise UserError("Ngày DKBG mới không thể nhỏ hơn hạn thanh toán mới Đợt DKBG.\n"
                                "Vui lòng kiểm tra lại thông tin.")

    @api.constrains('bsd_so_tb')
    def _constraint_so_tb(self):
        if self.bsd_so_tb < 0 or self.bsd_so_tb > 10:
            raise UserError(_("Nhập sai số lần hoàn thành thông báo bàn giao.\nVui lòng kiểm tra lại thông tin."))

    def action_tao(self):
        pass

    @api.model
    def create(self, vals):
        _logger.debug("tạo chi tiết")
        if not vals['bsd_ngay_htt_moi']:
            if 'bsd_cn_dkbg_id' in vals:
                cn_dkbg = self.env['bsd.cn_dkbg'].browse(vals['bsd_cn_dkbg_id'])
                if cn_dkbg.bsd_ngay_htt_moi:
                    vals['bsd_ngay_htt_moi'] = cn_dkbg.bsd_ngay_htt_moi
                else:
                    vals['bsd_ngay_htt_moi'] = vals['bsd_ngay_dkbg_moi']
        res = super(BsdCapNhatDKBGUnit, self).create(vals)
        if res.bsd_unit_id.bsd_hd_ban_id:
            hd_ban = res.bsd_unit_id.bsd_hd_ban_id
            dot_dkbg = hd_ban.bsd_ltt_ids.filtered(lambda x: x.bsd_ma_dtt == 'DKBG')[0]
        else:
            dot_dkbg = False
            hd_ban = False
        res.write({
            'bsd_du_an_id': res.bsd_unit_id.bsd_du_an_id.id,
            'bsd_hd_ban_id': hd_ban.id if hd_ban else None,
            'bsd_dot_tt_id': dot_dkbg.id if dot_dkbg else None,
            'bsd_ngay_dkbg_ht': res.bsd_unit_id.bsd_ngay_dkbg,
            'bsd_unit_state': res.bsd_unit_id.state,
        })
        return res
