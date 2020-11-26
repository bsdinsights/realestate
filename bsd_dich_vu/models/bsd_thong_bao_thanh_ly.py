from odoo import fields, models, api, _
from odoo.exceptions import UserError


class BsdTBTL(models.Model):
    _name = 'bsd.tb_tl'
    _description = 'Thông báo thanh lý'
    _rec_name = 'bsd_ma'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'bsd_ngay_tao desc'

    bsd_ma = fields.Char(string="Mã", help="Mã thông báo thanh lý", required=True, readonly=True,
                         copy=False, default='/')
    _sql_constraints = [
        ('bsd_ma_unique', 'unique (bsd_ma)',
         'Mã thông báo thanh lý đã tồn tại !')
    ]
    bsd_ngay_tao = fields.Date(string="Ngày", help="Ngày thông báo thanh lý",
                               required=True, default=lambda self: fields.Date.today(),
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    # bsd_ten = fields.Char(string="Tiêu đề", required=True, help="Tiêu đề thông báo thanh lý",
    #                       readonly=True,
    #                       states={'nhap': [('readonly', False)]})
    bsd_loai_ld = fields.Selection([('qua_han', 'Quá hạn'),
                                    ('yc_kh', 'Yêu cầu khách hàng'),
                                    ('vp_dk', 'Vi phạm điều khoản')], string="Lý do", help="Lý do", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_loai_dt = fields.Selection([('dat_coc', 'Đặt cọc'),
                                    ('hd_ban', 'Hợp đồng mua bán')], string="Đối tượng", required=True,
                                   help="Đối tượng", default='dat_coc',
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_ds_td_id = fields.Many2one('bsd.ds_td', string="Danh sách theo dõi", help="Danh sách theo dõi", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", help="Dự án", required=True,
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_dat_coc_id = fields.Many2one('bsd.dat_coc', string="Đặt cọc", help="Đặt cọc",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_hd_ban_id = fields.Many2one('bsd.hd_ban', string="Hợp đồng", help="Hợp đồng",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})
    bsd_unit_id = fields.Many2one('product.product', string="Sản phẩm", help="Sản phẩm", required=True,
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_khach_hang_id = fields.Many2one('res.partner', string="Khách hàng", help="Khách hàng", required=True,
                                        readonly=True,
                                        states={'nhap': [('readonly', False)]})
    bsd_tien_dc = fields.Monetary(string="Tiền đặt cọc", help="Tiền đặt cọc",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)]})
    bsd_ngay_ky_dc = fields.Datetime(string="Ngày ký đặt cọc", help="Ngày ký đặt cọc",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_tong_gt_hd = fields.Monetary(string="Tổng giá trị HĐ", help="Tổng giá trị hợp đồng",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_ngay_ky_ttdc = fields.Datetime(string="Ngày ký TTĐC", help="Ngày ký thỏa thuận đặt cọc",
                                       readonly=True,
                                       states={'nhap': [('readonly', False)]})
    bsd_ngay_ky_hdb = fields.Datetime(string="ngày ký hợp đồng", help="Ngày ký hợp đồng",
                                      readonly=True,
                                      states={'nhap': [('readonly', False)]})
    bsd_tien_da_tt = fields.Monetary(string="Đã thanh toán", help="Đã thanh toán",
                                     readonly=True,
                                     states={'nhap': [('readonly', False)]})
    bsd_ngay_in = fields.Datetime(string="Ngày in", help="Ngày in", readonly=True)
    bsd_ngay_gui = fields.Datetime(string="Ngày gửi", help="Ngày gửi", readonly=True)
    bsd_ngay_ht = fields.Datetime(string="Ngày hoàn thành", help="Ngày hoàn thành", readonly=True)
    bsd_nguoi_ht_id = fields.Many2one('res.users', string="Người hoàn thành", help="Người hoàn thành", readonly=True)
    state = fields.Selection([('nhap', 'Nháp'),
                              ('xac_nhan', 'Xác nhận'),
                              ('hoan_thanh', 'Hoàn thành'),
                              ('huy', 'Hủy')], string="Trạng thái", help="Trạng thái", default='nhap', tracking=1)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_tien_phat = fields.Monetary(string="Tiền phạt", help="Số tiền khách hàng bị phạt",
                                    readonly=True,
                                    states={'nhap': [('readonly', False)]})

    bsd_tien_mg = fields.Monetary(string="Miễn giảm phạt", help="Số tiền phạt được miễn giảm",
                                  readonly=True,
                                  states={'nhap': [('readonly', False)], 'xac_nhan': [('readonly', False)]})
    bsd_tong_phat = fields.Monetary(string="Tổng số tiền phạt", help="Tổng số tiền phạt sau khi được miễn giảm",
                                    readonly=True, compute="_compute_tong_phat", store=True)

    @api.depends('bsd_tien_phat', 'bsd_tien_mg')
    def _compute_tong_phat(self):
        for each in self:
            each.bsd_tong_phat = each.bsd_tien_phat - each.bsd_tien_mg

    @api.onchange('bsd_ds_td_id')
    def _onchange_ds(self):
        self.bsd_tl_phat = self.bsd_ds_td_id.bsd_tl_phat
        self.bsd_tien_phat = self.bsd_ds_td_id.bsd_tien_phat

    @api.onchange('bsd_loai_dt', 'bsd_hd_ban_id', 'bsd_dat_coc_id')
    def _onchange_tt(self):
        if self.bsd_loai_dt == 'dat_coc':
            if self.bsd_dat_coc_id:
                self.bsd_khach_hang_id = self.bsd_dat_coc_id.bsd_khach_hang_id
                self.bsd_unit_id = self.bsd_dat_coc_id.bsd_unit_id
                self.bsd_tien_dc = self.bsd_dat_coc_id.bsd_tien_dc
                self.bsd_tien_da_tt = self.bsd_dat_coc_id.bsd_tien_da_tt
                self.bsd_ngay_ky_dc = self.bsd_dat_coc_id.bsd_ngay_ky_dc
        elif self.bsd_loai_dt == 'ttdc':
            if self.bsd_hd_ban_id:
                self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id
                self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
                self.bsd_tong_gt_hd = self.bsd_hd_ban_id.bsd_tong_gia
                self.bsd_tien_da_tt = self.bsd_hd_ban_id.bsd_tien_tt_hd
                self.bsd_ngay_ky_ttdc = self.bsd_hd_ban_id.bsd_ngay_ky_ttdc
        elif self.bsd_loai_dt == 'hd_ban':
            if self.bsd_hd_ban_id:
                self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id
                self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
                self.bsd_tong_gt_hd = self.bsd_hd_ban_id.bsd_tong_gia
                self.bsd_tien_da_tt = self.bsd_hd_ban_id.bsd_tien_tt_hd
                self.bsd_ngay_ky_hdb = self.bsd_hd_ban_id.bsd_ngay_ky_hdb
        elif self.bsd_loai_dt == 'dc_cb':
            if self.bsd_hd_ban_id:
                self.bsd_khach_hang_id = self.bsd_hd_ban_id.bsd_khach_hang_id
                self.bsd_unit_id = self.bsd_hd_ban_id.bsd_unit_id
                self.bsd_tong_gt_hd = self.bsd_hd_ban_id.bsd_tong_gia
                self.bsd_tien_da_tt = self.bsd_hd_ban_id.bsd_tien_tt_hd

    # DV.17.01 - Thông báo thanh lý
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # DV.17.02 - In thông báo thanh lý
    def action_in(self):
        return self.env.ref('bsd_dich_vu.bsd_tb_tl_report_action').read()[0]

    # DV.17.03 Gửi thông báo thanh lý
    def action_gui(self):
        action = self.env.ref('bsd_dich_vu.bsd_wizard_tb_tl_action').read()[0]
        return action

    # DV.17.04 Hoàn thành thông báo
    def action_hoan_thanh(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'hoan_thanh',
                'bsd_ngay_ht': fields.Datetime.now(),
                'bsd_nguoi_ht_id': self.env.uid,
            })

    # DV.17.05 Hủy thông báo thanh lý
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy',
            })

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence']
        if 'bsd_du_an_id' in vals:
            du_an = self.env['bsd.du_an'].browse(vals['bsd_du_an_id'])
            sequence = du_an.get_ma_bo_cn(loai_cn=self._name)
        if not sequence:
            raise UserError(_('Dự án chưa có mã thông báo thanh lý.'))
        vals['bsd_ma'] = sequence.next_by_id()
        return super(BsdTBTL, self).create(vals)
