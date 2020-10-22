# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdChinhSachThanhToan(models.Model):
    _name = 'bsd.cs_tt'
    _rec_name = 'bsd_ten_cstt'
    _description = "Thông tin chính sách thanh toán"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_cstt = fields.Char(string="Mã", help="Mã chính sách thanh toán", required=True,
                              readonly=True, copy=False, default="/")
    _sql_constraints = [
        ('bsd_ma_cstt_unique', 'unique (bsd_ma_cstt)',
         'Mã chính sách thanh toán đã tồn tại !'),
    ]
    bsd_ten_cstt = fields.Char(string="Tên", help="Tên chính sách thanh toán", required=True,
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_search_name = fields.Char(string="Search name", compute='_compute_search_name', store=True)

    @api.depends('bsd_ma_cstt', 'bsd_ten_cstt')
    def _compute_search_name(self):
        for each in self:
            each.bsd_search_name = (each.bsd_ma_cstt or '') + ' - ' + (each.bsd_ten_cstt or '')

    bsd_dien_giai = fields.Char(string="Diễn giải",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True, help="Tên dự án",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chính sách thanh toán",
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chính sách thanh toán",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_ngay_tinh = fields.Selection([('ndc', 'Ngày đặt cọc'), ('nhd', 'Ngày hợp đồng')],
                                     string="Ngày tính", default="ndc",
                                     help="""
                                     Ngày được sử dụng để bắt đầu tính hạn thanh toán là ngày ký hợp đồng hay
                                     ngày đặt cọc
                                     """,
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_dk_hd = fields.Float(string="Điều kiện hợp đồng", help="Điều kiện thanh toán để làm hợp đồng mua bán",
                             readonly=True,
                             states={'nhap': [('readonly', False)]})
    bsd_lai_phat_tt_id = fields.Many2one('bsd.lai_phat_tt', string="Lãi phạt chậm TT", required=True,
                                         help="Phương thức tính lãi suất trong trường hợp chậm thanh toán",
                                         readonly=True,
                                         states={'nhap': [('readonly', False)]})

    bsd_phat_dc = fields.Float(string="Phạt thanh lý đặt cọc", required=True,
                               help="""Phần trăm phí phạt thanh lý đặt cọc""",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_phat_ttdc = fields.Float(string="Phạt thanh lý TTĐC", required=True,
                                 help="""Phần trăm phí phạt thanh lý thỏa thuận đặt cọc""",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    bsd_phat_hd = fields.Float(string="Phạt thanh lý HĐ", required=True,
                               help="""Phần trăm phí phạt thanh lý hợp đồng mua bán""",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_tb_tt = fields.Integer(string="Thông báo thanh toán",
                               help="Số ngày (trước khi đến hạn thanh toán) để gửi thông tin thanh toán",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_tl_hd = fields.Integer(string="Tổng số ngày TL",
                               help="Tổng số ngày trễ tối đa để thanh lý hợp đồng",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_qh_tt = fields.Integer(string="Tổng số ngày TL/ đợt", help="Số ngày trễ tối đa của mỗi đợt thanh toán",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_canh_bao1 = fields.Integer(string="Thông báo nhắc nợ 1",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 1",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_canh_bao2 = fields.Integer(string="Thông báo nhắc nợ 2",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 2",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_canh_bao3 = fields.Integer(string="Thông báo nhắc nợ 3",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 3",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_canh_bao4 = fields.Integer(string="Thông báo nhắc nợ 4",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 4",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_canh_bao5 = fields.Integer(string="Thông báo nhắc nợ 5",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 5",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_tl_cb1 = fields.Boolean(string="Thiết lập TBNN 1",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tl_cb2 = fields.Boolean(string="Thiết lập TBNN 2",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tl_cb3 = fields.Boolean(string="Thiết lập TBNN 3",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tl_cb4 = fields.Boolean(string="Thiết lập TBNN 4",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tl_cb5 = fields.Boolean(string="Thiết lập TBNN 5",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.cs_tt_ct', 'bsd_cs_tt_id', string="Chi tiết",
                                 readonly=True, copy=True,
                                 states={'nhap': [('readonly', False)]})
    active = fields.Boolean(default=True)
    bsd_ly_do = fields.Char(string="Lý do", help="Lý do không duyệt phương thức thanh toán", tracking=2)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('het_han', 'Hết hạn'), ('huy', 'Hủy')],
                             string="Trạng thái", required=True, default='nhap', tracking=1)
    bsd_nguoi_duyet_id = fields.Many2one('res.users', string="Người duyệt", readonly=True)
    bsd_ngay_duyet = fields.Date(string="Ngày duyệt", readonly=True)

    # Kiểm tra dữ liệu ngày hiệu lực
    @api.constrains('bsd_tu_ngay', 'bsd_den_ngay')
    def _constrains_ngay(self):
        for each in self:
            if each.bsd_tu_ngay:
                if not each.bsd_den_ngay:
                    raise UserError(_("Sai thông tin ngày kết thúc.\n Vui lòng kiểm tra lại thông tin."))
                elif each.bsd_den_ngay < each.bsd_tu_ngay:
                    raise UserError(_("Ngày kết thúc không thể nhỏ hơn ngày bắt đầu.\n Vui lòng kiểm tra lại thông tin."))

    # Kiểm tra tổng phần trăm của các đợt thanh toán
    @api.constrains('bsd_ct_ids')
    def _constrains_ct(self):
        if self.bsd_ct_ids:
            tong_pt = sum(self.bsd_ct_ids.filtered(lambda x: x.bsd_cach_tinh != 'td').mapped('bsd_tl_tt'))
            _logger.debug(tong_pt)
            for ct in self.bsd_ct_ids.filtered(lambda x: x.bsd_cach_tinh == 'td'):
                if ct.bsd_so_dot > 0:
                    tong_pt += (ct.bsd_tl_tt * ct.bsd_so_dot)
                else:
                    tong_pt += ct.bsd_tl_tt
            _logger.debug("Tổng phần trăm thanh toán")
            _logger.debug(tong_pt)
            if tong_pt != 100:
                raise UserError(_("Tỷ lệ của đợt thanh toán không bằng 100%.\n "
                                  "Vui lòng kiểm tra lại thông tin."))

    # Xác nhận phương thúc thanh toán
    def action_xac_nhan(self):
        if not self.bsd_ct_ids:
            raise UserError(_("Bạn chưa nhập thông tin khai báo đợt thanh toán.\n "
                              "Vui lòng kiểm tra lại thông tin."))
        else:
            dot_ky_hd = self.bsd_ct_ids.filtered(lambda d: d.bsd_dot_ky_hd)
            if not dot_ky_hd:
                raise UserError(_("Phương thức thanh toán chưa có đợt ký hợp đồng.\n"
                                  "Vui lòng kiểm tra lại thông tin"))
            if len(dot_ky_hd) > 1:
                raise UserError(_("Phương thức thanh toán có hơn 2 đọt ký hợp đồng.\n"
                                  "Vui lòng kiểm tra lại thông tin"))
            dot_cuoi = self.bsd_ct_ids.filtered(lambda d: d.bsd_dot_cuoi)
            if not dot_cuoi:
                raise UserError(_("Phương thức thanh toán chưa có đợt cuối.\n"
                                  "Vui lòng kiểm tra lại thông tin"))
            elif len(dot_cuoi) > 1:
                raise UserError(_("Phương thức thanh toán có hơn 2 đợt cuối.\n"
                                  "Vui lòng kiểm tra lại thông tin"))
            dot_pql = self.bsd_ct_ids.filtered(lambda d: d.bsd_tinh_pql)
            if not dot_pql:
                raise UserError(_("Phương thức thanh toán chưa có đợt thu phí quản lý.\n"
                                  "Vui lòng kiểm tra lại thông tin"))
            elif len(dot_pql) > 1:
                raise UserError(_("Phương thức thanh toán có hơn 2 đợt thu phí quản lý.\n"
                                  "Vui lòng kiểm tra lại thông tin"))
            dot_pbt = self.bsd_ct_ids.filtered(lambda d: d.bsd_tinh_pbt)
            if not dot_pbt:
                raise UserError(_("Phương thức thanh toán chưa có đợt thu phí bảo trì.\n"
                                  "Vui lòng kiểm tra lại thông tin"))
            elif len(dot_pbt) > 1:
                raise UserError(_("Phương thức thanh toán có hơn 2 đợt thu phí bảo trì.\n"
                                  "Vui lòng kiểm tra lại thông tin"))
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # Duyệt phương thức thanh toán
    def action_duyet(self):
        if not self.bsd_ct_ids:
            raise UserError(_("Bạn chưa nhập thông tin khai báo đợt thanh toán.\n "
                              "Vui lòng kiểm tra lại thông tin."))
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
                'bsd_ngay_duyet': fields.Date.today(),
                'bsd_nguoi_duyet_id': self.env.uid,
            })

    # Không duyệt phương thức thanh toán
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_cs_tt_action').read()[0]
        return action

    # Hủy phương thức thanh toán
    def action_huy(self):
        if self.state in ['xac_nhan']:
            self.write({
                'state': 'huy',
            })

    def action_them_dot(self):
        action = self.env.ref('bsd_danh_muc.bsd_cs_tt_ct_action_popup').read()[0]
        action['context'] = {'default_bsd_cs_tt_id': self.id}
        return action

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            if operator == 'ilike':
                args += [('bsd_search_name', operator, name)]
            elif operator == '=':
                args += [('bsd_ma_cstt', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return models.lazy_name_get(recs.with_user(access_rights_uid))

    @api.model
    def create(self, vals):
        sequence = False
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã phương thức thanh toán.'))
        vals['bsd_ma_cstt'] = sequence.next_by_id()
        return super(BsdChinhSachThanhToan, self).create(vals)


class BsdChinhSachThanhToanChiTiet(models.Model):
    _name = 'bsd.cs_tt_ct'
    _description = 'Thông tin chi tiết chính sách thanh toán'
    _rec_name = "bsd_dot_tt"

    bsd_stt = fields.Integer(string="Số thứ tự", help="Số thứ tự sắp xếp", required=True, default=1)
    bsd_dot_tt = fields.Char(string="Đợt thanh toán", help="Tên đợt thanh toán", required=True)
    bsd_cach_tinh = fields.Selection([('cd', 'Ngày cố định'),
                                      ('td', 'Ngày tự động'),
                                      ('dkbg', 'Ngày dự kiến bàn giao')], string="Cách tính",
                                     help="""
                                        Phương pháp tính hạn thanh toán dựa trên ngày cố định, tự động hay ngày
                                        bàn giao
                                     """)
    bsd_ngay_cd = fields.Date(string="Ngày cố định",
                              help="Ngày đến hạn của đợt thanh toán theo cách tính: ngày cố định")

    bsd_dot_cuoi = fields.Boolean(string="Đợt thanh toán cuối", default=False)

    bsd_tl_tt = fields.Float(string="Tỷ lệ thanh toán", help="Tỷ lệ thanh toán theo từng đợt bàn giao", required=True)

    bsd_bg_tam = fields.Boolean(string="Bàn giao tạm thời", help="Có bàn giao tạm thời theo đợt thanh toán hay không?",
                                default=False)

    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_tinh_pbt = fields.Boolean(string="Phí bảo trì", help="Có tính phí bảo trì trong đợt thanh toán hay không?",
                                  default=False)
    bsd_tinh_pql = fields.Boolean(string="Phí quản lý", help="Có tính phí quản lý trong đợt thanh toán hay không?",
                                  default=False)
    bsd_tiep_theo = fields.Selection([('ngay', 'Theo ngày'), ('thang', 'Theo tháng')], string="Loại cách tính", default='ngay',
                                     help="""Cách xác định hạn thanh toán của đợt tiếp theo, được tính
                                     theo số ngày hoặc số tháng
                                     """)
    bsd_so_ngay = fields.Integer(string="Số ngày", help="""Số ngày được sử dụng để tính hạn thanh toán
                                                    của đợt thanh toán tiếp theo""")
    bsd_so_thang = fields.Integer(string="Số tháng", help="""Số tháng được sử dụng để tính hạn thanh toán
                                                    của đợt thanh toán tiếp theo""")
    bsd_lap_lai = fields.Selection([('0', 'Không'), ('1', 'Có')], string="Lặp lại",
                                   default="0", help="Cách tính của đợt thanh toán có được lặp lại hay không")

    bsd_ngay_thang = fields.Integer(string="Ngày hàng tháng", help="Thanh toán vào ngày cố định của mỗi tháng")

    bsd_so_dot = fields.Integer(string="Số lần lặp", help="Số đợt thanh toán được lặp lại")

    bsd_ngay_gh = fields.Integer(string="Số ngày tiếp theo lần lặp cuối",
                                 help="""Ngày được cộng thêm khi tính hạn thanh toán của đợt 
                                         thanh toán. Trong trường hợp đợt thanh toán tự động được
                                         lặp lại nhiều lần, thì chỉ cộng ngày gia hạn vào đợt 
                                         tính tự động cuối cùng.
                                 """)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="Phương thức thanh toán", ondelete="cascade", required=True)
    bsd_dot_ky_hd = fields.Boolean(string="Đợt ký hợp đồng", help="Đánh dấu đợt thanh toán là đợt ký hợp đồng")

    @api.onchange('bsd_dot_cuoi')
    def _onchange_bsd_dot_cuoi(self):
        self.bsd_cach_tinh = None

    @api.onchange('bsd_tl_tt', 'bsd_so_dot')
    def _onchange_bsd_tl_tt(self):
        tong_tl_tt = 0
        for dot in self.bsd_cs_tt_id.bsd_ct_ids:
            if dot.bsd_cach_tinh != 'td':
                tong_tl_tt += dot.bsd_tl_tt
            else:
                if dot.bsd_lap_lai == '0':
                    tong_tl_tt += dot.bsd_tl_tt
                else:
                    tong_tl_tt += dot.bsd_tl_tt * dot.bsd_so_dot
        if tong_tl_tt > 100:
            return {
                'warning': {'title': _("Cảnh báo"),
                            'message': _('Tỷ lệ thanh toán đã vượt 100%, {0}%'.format(tong_tl_tt))}
            }

    @api.onchange('bsd_ngay_cd')
    def _onchange_ngay_cd(self):
        if self.bsd_ngay_cd:
            if self.bsd_ngay_cd < fields.Date.today():
                return {
                    'warning': {'title': _("Cảnh báo"),
                                'message': _('Ngày cố định không được nhỏ hơn hiện tại')}
                }

    @api.onchange('bsd_bg_tam')
    def _onchange_bg_tam(self):
        if self.bsd_bg_tam:
            self.bsd_tinh_pbt = True
            self.bsd_tinh_pql = True
        else:
            self.bsd_tinh_pbt = False
            self.bsd_tinh_pql = False

    @api.constrains('bsd_lap_lai')
    def _constrains_lap_lai(self):
        if self.bsd_lap_lai == '1':
            if self.bsd_so_dot < 1:
                raise UserError(_("Số lần lặp không được nhỏ hơn 1.\n Vui lòng kiểm tra lại thông tin."))

    @api.constrains('bsd_tl_tt')
    def _constrains_bsd_tl_tt(self):
        if self.bsd_tl_tt < 0 or self.bsd_tl_tt > 100:
            raise UserError(_("Giá trị nhập nằm ngoài khoản giới hạn"))

    @api.constrains('bsd_ngay_thang')
    def _constraint_ngay_thang(self):
        for each in self:
            if each.bsd_ngay_thang > 31:
                raise UserError(_("Ngày trong tháng không được lớn hơn 31"))

    @api.constrains('bsd_stt', 'bsd_cs_tt_id')
    def _constrains_cs_tt(self):
        list_ct = self.bsd_cs_tt_id.bsd_ct_ids.mapped('bsd_stt')
        if len(set(list_ct)) < len(list_ct):
            raise UserError(_("Sô thứ tự trùng.\n Vui lòng kiểm tra lại thông tin"))

    def action_xac_nhan(self):
        pass
