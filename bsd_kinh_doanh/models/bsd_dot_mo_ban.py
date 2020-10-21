# -*- coding:utf-8

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class BsdDotMoBan(models.Model):
    _name = 'bsd.dot_mb'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bsd_ten_dot_mb'
    _description = 'Thông tin đợt mở bán'

    bsd_ma_dot_mb = fields.Char(string="Mã", required=True, readonly=True, copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_dot_mb_unique', 'unique (bsd_ma_dot_mb)',
         'Mã đợt mở bán đã tồn tại !'),
    ]
    bsd_ten_dot_mb = fields.Char(string="Tên", required=True,
                                 readonly=True,
                                 states={'cph': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True,
                                   readonly=True,
                                   states={'cph': [('readonly', False)]})
    bsd_bang_gia_id = fields.Many2one('product.pricelist', string="Bảng giá",
                                      readonly=True, required=True,
                                      states={'cph': [('readonly', False)]})
    bsd_ck_ch_id = fields.Many2one('bsd.ck_ch', string="CK chung",
                                   readonly=True, required=True,
                                   states={'cph': [('readonly', False)]})
    bsd_ck_nb_id = fields.Many2one('bsd.ck_nb', string="CK nội bộ",
                                   readonly=True,
                                   states={'cph': [('readonly', False)]})
    bsd_ck_ms_id = fields.Many2one('bsd.ck_ms', string="CK mua sỉ",
                                   readonly=True,
                                   states={'cph': [('readonly', False)]})
    bsd_ck_ttth_id = fields.Many2one('bsd.ck_ttth', string="CK TT trước hạn",
                                     readonly=True,
                                     states={'cph': [('readonly', False)]})
    bsd_ck_ttn_id = fields.Many2one('bsd.ck_ttn', string="CK TT nhanh",
                                    readonly=True,
                                    states={'cph': [('readonly', False)]})
    bsd_ck_cstt_id = fields.Many2one('bsd.ck_cstt', string="CK phương thức TT",
                                     readonly=True,
                                     states={'cph': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng của đợt mở bán",
                              readonly=True, required=True,
                              states={'cph': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng của đợt mở bán",
                               readonly=True, required=True,
                               states={'cph': [('readonly', False)]})
    bsd_ngay_ph = fields.Datetime(string="Ngày phát hành", help="Ngày duyệt phát hành đợt mở bán",
                                  readonly=True)
    bsd_nguoi_ph = fields.Many2one('res.users', string="Người phát hành",
                                   help="Người duyệt phát hành đợt mở bán",
                                   readonly=True)
    bsd_tu_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Từ tòa nhà",
                                        readonly=True,
                                        states={'cph': [('readonly', False)]})
    bsd_tu_tang_id = fields.Many2one('bsd.tang', string="Từ tầng",
                                     readonly=True,
                                     states={'cph': [('readonly', False)]})
    bsd_den_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Đến tòa nhà",
                                         readonly=True,
                                         states={'cph': [('readonly', False)]})
    bsd_den_tang_id = fields.Many2one('bsd.tang', string="Đến tầng",
                                      readonly=True,
                                      states={'cph': [('readonly', False)]})
    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True,
                                states={'cph': [('readonly', False)]})
    state = fields.Selection([('cph', 'Chưa phát hành'), ('ph', 'Phát hành'),
                              ('thmb', 'Thu hồi mở bán'), ('thch', 'Thu hồi Sản phẩm')],
                             string="Trạng thái", default="cph", tracking=1, required=True)
    bsd_san_gd = fields.Boolean(string="Sàn giao dịch", default=False,
                                help="""Thông tin quy định đợt mở bán chỉ cho phép các sàn giao dịch được bán, 
                                        hay cho sàn giao dịch và chủ đầu tư đều được bán""",
                                readonly=True,
                                states={'cph': [('readonly', False)]})
    bsd_sgd_ids = fields.One2many('bsd.dot_mb_sgd', 'bsd_dot_mb_id', string="Các sàn giao dịch",
                                  readonly=True,
                                  states={'cph': [('readonly', False)]})
    bsd_km_ids = fields.Many2many('bsd.khuyen_mai', string="Khuyến mãi", domain=[('state', '=', 'duyet')],
                                  readonly=True,
                                  states={'cph': [('readonly', False)]})
    bsd_dkbg_ids = fields.Many2many('bsd.dk_bg', string="Điều kiện bàn giao",
                                    readonly=True,
                                    states={'cph': [('readonly', False)]})
    bsd_cb_ids = fields.One2many('bsd.dot_mb_cb', 'bsd_dot_mb_id', string="Chuẩn bị unit",
                                 readonly=True,
                                 states={'cph': [('readonly', False)]})
    bsd_ph_ids = fields.One2many('bsd.dot_mb_unit', 'bsd_dot_mb_id', string="Phát hành unit",
                                 readonly=True,
                                 domain=[('state', '=', 'phat_hanh')],
                                 states={'cph': [('readonly', False)]})
    bsd_th_ids = fields.One2many('bsd.dot_mb_unit', 'bsd_dot_mb_id', string="Thu hồi unit",
                                 readonly=True,
                                 domain=[('state', '=', 'thu_hoi')])

    bsd_so_thu_hoi_ch = fields.Integer(string="# Thu hồi Sản phẩm", compute='_compute_thu_hoi_ch')
    bsd_so_them_ch = fields.Integer(string="# Thêm Sản phẩm", compute='_compute_them_ch')

    # Kiểm tra dữ liệu ngày hiệu lực
    @api.constrains('bsd_tu_ngay', 'bsd_den_ngay')
    def _constrains_ngay(self):
        for each in self:
            if each.bsd_tu_ngay:
                if not each.bsd_den_ngay:
                    raise UserError(_("Sai thông tin ngày kết thúc.\n Vui lòng kiểm tra lại thông tin."))
                elif each.bsd_den_ngay < each.bsd_tu_ngay:
                    raise UserError(_("Ngày kết thúc không thể nhỏ hơn ngày bắt đầu.\n Vui lòng kiểm tra lại thông tin."))

    def _compute_thu_hoi_ch(self):
        for each in self:
            thu_hoi = self.env['bsd.thu_hoi'].search([('bsd_dot_mb_id', '=', self.id)])
            each.bsd_so_thu_hoi_ch = len(thu_hoi)

    def _compute_them_ch(self):
        for each in self:
            them_unit = self.env['bsd.them_unit'].search([('bsd_dot_mb_id', '=', self.id)])
            each.bsd_so_them_ch = len(them_unit)

    def action_view_thu_hoi_ch(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_thu_hoi_action').read()[0]

        thu_hoi = self.env['bsd.thu_hoi'].search([('bsd_dot_mb_id', '=', self.id)])
        if len(thu_hoi) > 1:
            action['domain'] = [('id', 'in', thu_hoi.ids)]
        elif thu_hoi:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_thu_hoi_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = thu_hoi.id
        # Prepare the context.
        context = {
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_dot_mb_id': self.id,
        }
        action['context'] = context
        return action

    def action_view_them_ch(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_them_unit_action').read()[0]

        them_unit = self.env['bsd.them_unit'].search([('bsd_dot_mb_id', '=', self.id)])
        if len(them_unit) > 1:
            action['domain'] = [('id', 'in', them_unit.ids)]
        elif them_unit:
            form_view = [(self.env.ref('bsd_kinh_doanh.bsd_them_unit_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = them_unit.id
        # Prepare the context.
        context = {
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_dot_mb_id': self.id,
        }
        action['context'] = context
        return action

    def action_loc_unit(self):
        # gán giá trị biến nội hàm
        tu_toa_nha_id = self.bsd_tu_toa_nha_id
        den_toa_nha_id = self.bsd_den_toa_nha_id
        tu_tang_id = self.bsd_tu_tang_id
        den_tang_id = self.bsd_den_tang_id
        # Kiểm tra trạng thái record
        if self.state != 'cph':
            pass
        # Kiểm tra đầy đủ các field điều kiện lọc unit
        elif not tu_toa_nha_id or not den_toa_nha_id or not tu_tang_id:
            raise UserError("Trường điều kiện lọc sản phẩm theo tòa trống.")
        elif tu_toa_nha_id.bsd_stt > den_toa_nha_id.bsd_stt:
            raise UserError("Nhập sai số thứ tự 2 tòa nhà.")
        else:
            if not den_tang_id:
                ids_tang = []
                tu_tang_stt = tu_tang_id.bsd_stt
                den_tang_stt = den_tang_id.bsd_stt
                # nếu lọc tầng cùng tòa nhà
                if tu_toa_nha_id == den_toa_nha_id:
                    ids_tang += self.env['bsd.tang'].search([('bsd_stt', '>=', tu_tang_stt),
                                                                ('bsd_stt', '<=', den_tang_stt),
                                                                ('bsd_toa_nha_id', '=', tu_toa_nha_id.id)]).ids
                # nếu lọc tầng khác tòa nhà
                else:
                    # lọc tầng từ tòa nhà đầu
                    ids_tang += self.env['bsd.tang'].search([('bsd_stt', '>=', tu_tang_stt),
                                                             ('bsd_toa_nha_id', '=', tu_toa_nha_id.id)]).ids
                    # lọc tầng đến tòa nhà cuối
                    ids_tang += self.env['bsd.tang'].search([('bsd_stt', '<=', den_tang_stt),
                                                                ('bsd_toa_nha_id', '=', den_toa_nha_id.id)]).ids
                    # lọc tầng các tòa nhà có số thứ tự lớn hơn tòa nhà đầu và nhỏ hơn tòa nhà cuối
                    if den_toa_nha_id.bsd_stt - tu_toa_nha_id.bsd_stt > 1:
                        ids_toa_nha = self.env['bsd.toa_nha'].search([('bsd_stt', '>', tu_toa_nha_id.bsd_stt),
                                                                     ('bsd_stt', '<', den_toa_nha_id.bsd_stt),
                                                                     ('bsd_du_an_id', '=', self.bsd_du_an_id.id)]).ids
                        ids_tang += self.env['bsd.tang'].search([('bsd_toa_nha_id', 'in', ids_toa_nha)]).ids
                _logger.debug("id tầng")
                _logger.debug(ids_tang)
                # lọc unit theo các tầng đã tìm được:
                units = set(self.env['product.product'].search([('bsd_tang_id', 'in', ids_tang)]))
                # Chỉ tạo những unit chưa có trong chuẩn bị
                exist_units = set(self.bsd_cb_ids.mapped('bsd_unit_id'))
                no_units = units.difference(exist_units)
                # Tạo dữ liệu cho bảng unit chuẩn bị mở bán
                for unit in no_units:
                    self.bsd_cb_ids.create({
                        'bsd_du_an_id': unit.bsd_du_an_id.id,
                        'bsd_toa_nha_id': unit.bsd_toa_nha_id.id,
                        'bsd_tang_id': unit.bsd_tang_id.id,
                        'bsd_unit_id': unit.id,
                        'bsd_gia_ban': unit.bsd_tong_gb,
                        'bsd_dot_mb_id': self.id
                    })

    # Phát hành
    def action_phat_hanh(self):
        # kiểm tra trạng thái record
        if self.state != 'cph':
            pass
        else:
            # Nếu không có điều kiện lọc thì lấy sản phẩm trong bảng giá
            if not self.bsd_tu_toa_nha_id:
                template_ids = self.bsd_bang_gia_id.item_ids.mapped('product_tmpl_id').ids
                unit_ids = self.env['product.product'].search([('product_tmpl_id', 'in', template_ids)])
                for unit in unit_ids:
                    self.bsd_cb_ids.create({
                        'bsd_du_an_id': unit.bsd_du_an_id.id,
                        'bsd_toa_nha_id': unit.bsd_toa_nha_id.id,
                        'bsd_tang_id': unit.bsd_tang_id.id,
                        'bsd_unit_id': unit.id,
                        'bsd_gia_ban': unit.bsd_tong_gb,
                        'bsd_dot_mb_id': self.id
                    })
            # lấy tất cả unit chuẩn bị phát hành ở trạng thái chuẩn bị đặt chỗ, giữ chỗ
            units = self.bsd_cb_ids.mapped('bsd_unit_id').filtered(lambda x: x.state in ['chuan_bi', 'dat_cho',
                                                                                         'giu_cho'])
            # các chuẩn bị không đúng trạng thái
            cb_no_state = self.bsd_cb_ids.filtered(lambda c: c.bsd_unit_id not in units)
            cb_no_state.write({
                'bsd_ly_do': 'kd_tt',
            })
            # các chuẩn bị đúng trạng thái
            cb_state = self.bsd_cb_ids - cb_no_state
            # lọc các unit thỏa điều kiện trường ưu tiên là không và không có đợt mở bán
            no_uu_dot_no_mb_units = units.filtered(lambda x: x.bsd_uu_tien == '0' and not x.bsd_dot_mb_id)
            # lọc các unit thỏa điều kiện trường ưu tiên là không và có đợt mở bán
            no_uu_dot_mb_units = units.filtered(lambda x: x.bsd_uu_tien == '0' and x.bsd_dot_mb_id)

            # các chuẩn bị đúng trạng thái, đang được ưu tiên
            cb_uu = cb_state.filtered(lambda u: u.bsd_unit_id.bsd_uu_tien == '1')
            cb_uu.write({
                'bsd_ly_do': 'dd_ut',
            })
            # lọc các unit không ưu tiên có đợt mở bán chưa phát hành
            no_ph_units = no_uu_dot_mb_units.filtered(lambda x: x.bsd_dot_mb_id.state != 'ph')
            ph_units = no_uu_dot_mb_units.filtered(lambda x: x.bsd_dot_mb_id.state == 'ph')
            # kiểm tra các unit không trùng với đợt mở bán hiện tại đang phát hành
            diff_mb_units = ph_units.filtered(lambda x: (x.bsd_dot_mb_id.bsd_tu_ngay < self.bsd_tu_ngay
                                                         and x.bsd_dot_mb_id.bsd_den_ngay < self.bsd_tu_ngay)
                                                            or (x.bsd_dot_mb_id.bsd_tu_ngay > self.bsd_den_ngay
                                                                and x.bsd_dot_mb_id.bsd_den_ngay > self.bsd_den_ngay)
                                              )
            # các chuẩn bị trùng với đợt mở bán khác
            cb_trung = (cb_state - cb_uu).filtered(lambda t: t.bsd_unit_id not in diff_mb_units
                                                   and t.bsd_unit_id.bsd_dot_mb_id)
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
        if not units_ph:
            raise UserError(_('Không có sản phẩm phát hành.'))
        for unit in units_ph:
            pricelist_item = self.env['product.pricelist.item'].search([('product_tmpl_id', '=', unit.product_tmpl_id.id)],
                                                                       limit=1)
            self.bsd_ph_ids.create({
                'bsd_du_an_id': unit.bsd_du_an_id.id,
                'bsd_toa_nha_id': unit.bsd_toa_nha_id.id,
                'bsd_tang_id': unit.bsd_tang_id.id,
                'bsd_unit_id': unit.id,
                'bsd_gia_ban': pricelist_item.fixed_price,
                'bsd_dot_mb_id': self.id
            })
            # KD.04.06 Cập nhật tình trạng Sản phẩm phát hành
            if unit.state == 'chuan_bi':
                unit.write({
                    'bsd_dot_mb_id': self.id,
                    'state': 'san_sang',
                })
            else:
                unit.write({
                    'bsd_dot_mb_id': self.id,
                })
        # Cập lại lại trạng thái đợt mở bán ngày phát hình và người phát hành
        self.write({
            'state': 'ph',
            'bsd_ngay_ph': fields.Datetime.now(),
            'bsd_nguoi_ph': self.env.uid,
        })
        #  KD.04.08 Tính hạn báo giá  của giữ chỗ sau khi phát hành đợt mở bán
        units_ph = self.bsd_ph_ids.mapped('bsd_unit_id')
        for unit_ph in units_ph:
            # KD.04.09 cập nhật đợt mở bán cho giữ chỗ
            giu_cho_unit = self.env['bsd.giu_cho'].search([('bsd_unit_id', '=', unit_ph.id)])
            giu_cho_unit.write({'bsd_dot_mb_id': self.id})
        #     # lọc các giữ chỗ của unit đã thanh toán
        #     giu_cho_ids = giu_cho_unit.filtered(lambda g: g.state == 'giu_cho' and g.bsd_thanh_toan == 'da_tt')
        #     if giu_cho_ids:
        #         gc = giu_cho_ids.filtered(lambda x: not x.bsd_rap_can_id).sorted('id')
        #         gc_no_rc = zip(gc.mapped('id'), gc.mapped('bsd_ngay_tt'))
        #         gc = giu_cho_ids.filtered(lambda x: x.bsd_rap_can_id).sorted('id')
        #         gc_rc = zip(gc.mapped('id'), gc.mapped('bsd_ngay_gc'))
        #         _logger.debug("sắp xếp")
        #         gc_sorted = sorted(list(gc_rc) + list(gc_no_rc), key=lambda x: x[1])
        #         id_gc_sorted = [g[0] for g in gc_sorted]
        #         stt = 0
        #         time_gc = self.bsd_du_an_id.bsd_gc_smb
        #         ngay_ph = self.bsd_ngay_ph
        #         for giu_cho in self.env['bsd.giu_cho'].browse(id_gc_sorted):
        #             stt += 1
        #             ngay_ph += datetime.timedelta(hours=time_gc)
        #             # KD.04.07 cập nhật trạng thái giữ chỗ khi phát hành
        #             # if giu_cho.state == 'dat_cho' and giu_cho.bsd_thanh_toan == 'da_tt':
        #             #     giu_cho.write({
        #             #         'state': 'giu_cho',
        #             #     })
        #             giu_cho.write({
        #                 'bsd_stt_bg': stt,
        #                 'bsd_ngay_hh_bg': ngay_ph
        #             })

    # Thu hồi toàn bộ đợt mở bán
    def action_thu_hoi(self):
        _logger.debug('Thu hồi đợt mơt bán')
        # Kiểm tra trạng thái record
        if self.state != 'ph':
            pass
        else:
            dk = self.bsd_ph_ids.filtered(lambda p: p.bsd_unit_id.state != 'san_sang')
            _logger.debug(dk)
            if dk:
                raise UserError('Đợt mở bán đang có giao dịch.\n Vui lòng kiểm tra lại thông tin.')
            # chuyển trạng thái đợt phát hành
            self.write({
                'state': 'thmb',
            })
            # chuyển unit từ tab phát hành sang thu hồi
            self.bsd_ph_ids.write({
                'state': 'thu_hoi',
            })
            # chuyển trạng thái unit từ sẵn sàng về chuẩn bị
            _logger.debug(self.bsd_th_ids)
            self.bsd_th_ids.mapped('bsd_unit_id').write({
                'state': 'chuan_bi',
                'bsd_dot_mb_id': False
            })

    # Thu hồi Sản phẩm trong đợt mở bán
    def action_thu_hoi_can_ho(self):
        action = self.env.ref('bsd_kinh_doanh.bsd_thu_hoi_action_pop_up').read()[0]
        context = {
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_dot_mb_id': self.id,
        }
        action['context'] = context
        return action

    # Thêm Sản phẩm trong đợt mở bán
    def action_them_can_ho(self):
        context = {
            'default_bsd_du_an_id': self.bsd_du_an_id.id,
            'default_bsd_dot_mb_id': self.id,
        }
        return {
            "name": "Tạo phiếu thêm Sản phẩm",
            "res_model": 'bsd.them_unit',
            "view": [[False, 'form']],
            "type": 'ir.actions.act_window',
            "view_mode": "form",
            "context": context,
            "target": "new"
        }

    @api.model
    def create(self, vals):
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã đợt mở bán.'))
        vals['bsd_ma_dot_mb'] = sequence.next_by_id()
        res = super(BsdDotMoBan, self).create(vals)
        return res


class BsdDotMoBanSanGiaoDich(models.Model):
    _name = 'bsd.dot_mb_sgd'
    _description = 'Thông tin sàn giao dich cho đợt mở bán'
    _rec_name = 'bsd_san_gd_id'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", required=True)
    bsd_san_gd_id = fields.Many2one('res.partner', string="Tên sàn giao dịch", domain=[('is_company', '=', True)],
                                    help="Sàn giao dịch được bán các Sản phẩm trong đợt mở bán", required=True)
    bsd_san_gd_phone = fields.Char(string="Số điện thoại", related="bsd_san_gd_id.phone")
    bsd_san_gd_street = fields.Char('Đường', related="bsd_san_gd_id.street")
    bsd_san_gd_city = fields.Char('Thành phố', related="bsd_san_gd_id.city")
    bsd_san_gd_state_id = fields.Many2one("res.country.state", string='Tỉnh thành', related="bsd_san_gd_id.state_id")
    bsd_san_gd_country_id = fields.Many2one('res.country', string='Quốc gia', related="bsd_san_gd_id.country_id")


class BsdDotMoBanCB(models.Model):
    _name = 'bsd.dot_mb_cb'
    _description = 'Thông tin Sản phẩm chuẩn bị cho đợt mở bán'
    _rec_name = 'bsd_unit_id'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True)
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True)
    bsd_gia_ban = fields.Monetary(string="Giá bán", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ly_do = fields.Selection([('kc_bg', 'Không có bảng giá'),
                                  ('dang_mb', 'Đang mở bán'),
                                  ('dd_ut', 'Đánh dấu ưu tiên'),
                                  ('kd_tt', 'Không đúng trạng thái')],
                                 string="Lý do", help="Lý do Sản phẩm không được phát hành mở bán", readonly=True)

    @api.model
    def create(self, vals):
        _logger.debug("Tạo chuẩn bị")
        _logger.debug(vals)
        if 'bsd_unit_id' in vals.keys() and 'bsd_dot_mb_id' in vals.keys():
            if self.env['bsd.dot_mb_cb'].search([('bsd_unit_id', '=', vals['bsd_unit_id']),
                                                 ('bsd_dot_mb_id', '=', vals['bsd_dot_mb_id'])]):
                raise UserError("Đợt mở bán đã có sản phẩm.")
        rec = super(BsdDotMoBanCB, self).create(vals)
        return rec

    def write(self, vals):
        if 'bsd_unit_id' in vals.keys():
            if self.env['bsd.dot_mb_cb'].search([('bsd_unit_id', '=', vals['bsd_unit_id']),
                                                 ('bsd_dot_mb_id', '=', self.bsd_dot_mb_id.id)]):
                raise UserError("Đợt mở bán đã có sản phẩm.")
        rec = super(BsdDotMoBanCB, self).write(vals)
        return rec


class BsdDotMoBanUnit(models.Model):
    _name = 'bsd.dot_mb_unit'
    _description = 'Thông tin Sản phẩm phát hành cho đợt mở bán'
    _rec_name = 'bsd_unit_id'

    bsd_dot_mb_id = fields.Many2one('bsd.dot_mb', string="Đợt mở bán", required=True)
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True)
    bsd_toa_nha_id = fields.Many2one('bsd.toa_nha', string="Tòa nhà", required=True)
    bsd_tang_id = fields.Many2one('bsd.tang', string="Tầng", required=True)
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", required=True)
    bsd_gia_ban = fields.Monetary(string="Giá bán", required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    state = fields.Selection([('phat_hanh', 'Phát hành'), ('thu_hoi', 'Thu hồi')], string="Trạng thái",
                             required="True", default='phat_hanh', help="Tráng thái")
    bsd_thu_hoi_id = fields.Many2one('bsd.thu_hoi', string="Thu hồi", help="Thu hồi", readonly=True)
    bsd_them_unit_id = fields.Many2one('bsd.them_unit', string="Thêm Sản phẩm", help="Thêm Sản phẩm", readonly=True)
