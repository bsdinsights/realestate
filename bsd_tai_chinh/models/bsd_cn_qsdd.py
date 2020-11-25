# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BsdCapNhatGTQSDD(models.Model):
    _name = 'bsd.cn_qsdd'
    _description = "Cập nhật giá trị QSDĐ"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten'

    bsd_ma = fields.Char(string="Mã", help="Mã danh sách cập nhật giá trị QSDĐ", required=True, readonly=True,
                                 copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã cập nhật giá trị QSDĐ đã tồn tại !')
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
    bsd_ngay_xn = fields.Datetime(string="Ngày xác nhận", readonly=True, help="Ngày xác nhận")
    bsd_nguoi_xn_id = fields.Many2one('res.users', string="Người xác nhận", readonly=True, help="Người xác nhận")
    bsd_ngay_duyet = fields.Datetime(string="Ngày duyệt", readonly=True, help="Ngày duyệt")
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", help="Người duyệt", readonly=True)

    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('huy', 'Hủy')],
                             string="Trạng thái", default="nhap", required=True, readonly=True, tracking=1)
    bsd_ly_do = fields.Html(string="Lý do", readonly=True, tracking=2)
    bsd_ct_ids = fields.One2many('bsd.cn_qsdd_unit', 'bsd_cn_qsdd_id', string="Cập nhật QSDĐ chi tiết")

    # tính năng import dự liệu
    def action_nhap_sp(self):
        action = {
            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {
                'model': 'bsd.cn_qsdd_unit'
            }
        }
        return action

    # tính năng thêm sản phẩm
    def action_them_sp(self):
        action = self.env.ref('bsd_tai_chinh.bsd_cn_qsdd_unit_action_popup').read()[0]
        action['context'] = {'default_bsd_cn_qsdd_id': self.id,
                             'default_bsd_du_an_id': self.bsd_du_an_id.id}
        return action

    # Xác nhận cập nhật giá trị QSDĐ
    def action_xac_nhan(self):
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
            # Cập nhật giá QSDĐ/ m2 và tạo phụ lục nếu giá trị mới khác giá trị hiện tại
            for ct in ct_ids:
                # tạo phụ lục với hợp đồng
                if ct.bsd_hd_ban_id:
                    hd_ban = ct.bsd_hd_ban_id
                    self.env['bsd.pl_qsdd'].create({
                        'bsd_khach_hang_id': hd_ban.bsd_khach_hang_id.id,
                        'bsd_hd_ban_id': hd_ban.id,
                        'bsd_du_an_id': hd_ban.bsd_du_an_id.id,
                        'bsd_unit_id': hd_ban.bsd_unit_id.id,
                        'bsd_dt_sd': hd_ban.bsd_dt_sd,
                        'bsd_cs_tt_ht_id': hd_ban.bsd_cs_tt_id.id,
                        'bsd_ltt_ht_ids': [(5,), (6, 0, hd_ban.bsd_ltt_ids.ids)],
                        'bsd_gia_ban_ht': hd_ban.bsd_gia_ban,
                        'bsd_tien_ck_ht': hd_ban.bsd_tien_ck,
                        'bsd_tien_bg_ht': hd_ban.bsd_tien_bg,
                        'bsd_gia_truoc_thue_ht': hd_ban.bsd_gia_truoc_thue,
                        'bsd_tien_qsdd_ht': hd_ban.bsd_tien_qsdd,
                        'bsd_tien_thue_ht': hd_ban.bsd_tien_thue,
                        'bsd_tien_pbt_ht': hd_ban.bsd_tien_pbt,
                        'bsd_tong_gia_ht': hd_ban.bsd_tong_gia,
                        'bsd_tien_da_tt': hd_ban.bsd_tien_tt_hd,
                        'bsd_thue_suat': hd_ban.bsd_thue_suat,
                        'bsd_qsdd_m2_ht': ct.bsd_qsdd_m2_ht,
                        'bsd_qsdd_m2_moi': ct.bsd_qsdd_m2_moi,
                        'bsd_dot_ct_id': hd_ban.bsd_ltt_ids.filtered(lambda d: d.bsd_ma_dtt == 'DBGC').id,
                    })
                ct.bsd_unit_id.write({'bsd_qsdd_m2': ct.bsd_qsdd_m2_moi})

    # Không duyệt cập nhật giá trị QSDĐ
    def action_khong_duyet(self):
        action = self.env.ref('bsd_tai_chinh.bsd_wizard_khong_duyet_cn_qsdd_action').read()[0]
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
            raise UserError(_('Dự án chưa có mã cập nhật giá trị QSDĐ.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdCapNhatGTQSDD, self).create(vals)

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


class BsdCapNhatGTQSDDUnit(models.Model):
    _name = 'bsd.cn_qsdd_unit'
    _description = "Cập nhật điều kiện bàn giao sản phẩm"
    _order = 'bsd_stt'
    _rec_name = 'bsd_unit_id'

    bsd_cn_qsdd_id = fields.Many2one('bsd.cn_qsdd', ondelete='cascade',
                                     string="Cập nhật QSDĐ",
                                     help="Tên cập nhật giá trị QSDĐ", required=True,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_ngay = fields.Date(string="Ngày tạo", required=True, default=lambda self: fields.Datetime.now(),
                           readonly=True,
                           states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", readonly=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_stt = fields.Integer(related='bsd_unit_id.bsd_stt', store=True)
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", readonly=True)
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
    bsd_qsdd_m2_ht = fields.Monetary(string="QSDĐ/ m2 hiện tại", help="Giá trị QSDĐ/ m2 hiện tại", readonly=True)
    bsd_qsdd_m2_moi = fields.Monetary(string="QSDĐ/ m2 mới", help="Giá trị QSDĐ/ m2 mới", readonly=True,
                                      states={'nhap': [('readonly', False)]}, required=True)
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
        if self.bsd_qsdd_m2_moi < 0:
            raise UserError("Giá trị QSDĐ không thể nhỏ hơn 0")

    @api.model
    def create(self, vals):
        res = super(BsdCapNhatGTQSDDUnit, self).create(vals)
        res.write({
            'bsd_du_an_id': res.bsd_unit_id.bsd_du_an_id.id,
            'bsd_hd_ban_id': res.bsd_unit_id.bsd_hd_ban_id.id,
            'bsd_qsdd_m2_ht': res.bsd_unit_id.bsd_qsdd_m2,
            'bsd_unit_state': res.bsd_unit_id.state,
        })
        return res
