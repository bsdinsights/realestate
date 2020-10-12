# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdChinhSachThanhToan(models.Model):
    _name = 'bsd.cs_tt'
    _rec_name = 'bsd_ten_cstt'
    _description = "Thông tin chính sách thanh toán"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_cstt = fields.Char(string="Mã", help="Mã chính sách thanh toán", required=True,
                              readonly=True,
                              states={'nhap': [('readonly', False)]})
    _sql_constraints = [
        ('bsd_ma_cstt_unique', 'unique (bsd_ma_cstt)',
         'Mã chính sách thanh toán đã tồn tại !'),
    ]
    bsd_ten_cstt = fields.Char(string="Tên", help="Tên chính sách thanh toán", required=True,
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
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
    bsd_lai_phat_tt_id = fields.Many2one('bsd.lai_phat_tt', string="Lãi phạt", required=True,
                                         help="Phương thức tính lãi suất trong trường hợp chậm thanh toán",
                                         readonly=True,
                                         states={'nhap': [('readonly', False)]})

    bsd_phat_thd = fields.Float(string="Phạt trước hợp đồng", required=True,
                                help="""Phần trăm phí phạt (theo giá trị hợp đồng)
                                        trong trường hợp chấm dứt giao dịch trước khi ký hợp đồng
                                """,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_phat_shd = fields.Float(string="Phạt sau hợp đồng", required=True,
                                help="""Phần trăm phí phạt (theo giá trì hợp đồng) 
                                        trong trường hợp chấm dứt giao dịch sau khi ký hợp đồng
                                """,
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tb_tt = fields.Integer(string="Thông báo thanh toán",
                               help="Số ngày (trước khi đến hạn thanh toán) để gửi thông tin thanh toán",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})

    bsd_tl_hd = fields.Integer(string="Số ngày trễ",
                               help="Tổng số ngày trễ tối đa để thanh lý hợp đồng",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_qh_tt = fields.Integer(string="Số ngày trễ/ Đợt", help="Số ngày trễ tối đa của mỗi đợt thanh toán",
                               readonly=True,
                               states={'nhap': [('readonly', False)]})
    bsd_canh_bao1 = fields.Integer(string="Cảnh báo 1",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 1",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_canh_bao2 = fields.Integer(string="Cảnh báo 2",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 2",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_canh_bao3 = fields.Integer(string="Cảnh báo 3",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 3",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_canh_bao4 = fields.Integer(string="Cảnh báo 4",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 4",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_canh_bao5 = fields.Integer(string="Cảnh báo 5",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 5",
                                   readonly=True,
                                   states={'nhap': [('readonly', False)]})
    bsd_tl_cb1 = fields.Boolean(string="Thiết lập cảnh báo 1",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tl_cb2 = fields.Boolean(string="Thiết lập cảnh báo 2",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tl_cb3 = fields.Boolean(string="Thiết lập cảnh báo 3",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tl_cb4 = fields.Boolean(string="Thiết lập cảnh báo 4",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    bsd_tl_cb5 = fields.Boolean(string="Thiết lập cảnh báo 5",
                                readonly=True,
                                states={'nhap': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.cs_tt_ct', 'bsd_cs_tt_id', string="Chi tiết",
                                 readonly=True,
                                 states={'nhap': [('readonly', False)]})
    active = fields.Boolean(default=True)
    bsd_ly_do = fields.Char(string="Lý do", help="Lý do không duyệt phương thức thanh toán", tracking=2)
    state = fields.Selection([('nhap', 'Nháp'), ('xac_nhan', 'Xác nhận'),
                              ('duyet', 'Duyệt'), ('het_han', 'Hết hạn'), ('huy', 'Hủy')],
                             string="Trạng thái", required=True, default='nhap', tracking=1)

    # Xác nhận phương thúc thanh toán
    def action_xac_nhan(self):
        if self.state == 'nhap':
            self.write({
                'state': 'xac_nhan'
            })

    # Duyệt phương thức thanh toán
    def action_duyet(self):
        if self.state == 'xac_nhan':
            self.write({
                'state': 'duyet',
            })

    # Không duyệt phương thức thanh toán
    def action_khong_duyet(self):
        action = self.env.ref('bsd_danh_muc.bsd_wizard_cs_tt_action').read()[0]
        return action

    # Hủy phương thức thanh toán
    def action_huy(self):
        if self.state in ['nhap', 'xac_nhan']:
            self.write({
                'state': 'huy',
            })


class BsdChinhSachThanhToanChiTiet(models.Model):
    _name = 'bsd.cs_tt_ct'
    _description = 'Thông tin chi tiết chính sách thanh toán'
    _rec_name = "bsd_dot_tt"

    bsd_stt = fields.Integer(string="Số thứ tự", help="Số thứ tự sắp xếp", required=True)
    bsd_dot_tt = fields.Char(string="Đợt thanh toán", help="Tên đợt thanh toán", required=True)
    bsd_cach_tinh = fields.Selection([('cd', 'Cố định'),
                                      ('td', 'Tự động'),
                                      ('dkbg', 'Dự kiến bàn giao')], string="Cách tính",
                                     help="""
                                        Phương pháp tính hạn thanh toán dựa trên ngày cố định, tự động hay ngày
                                        bàn giao
                                     """)
    bsd_ngay_cd = fields.Date(string="Ngày cố định",
                              help="Ngày thanh toán của đợt thanh toán theo cách tính: ngày cố định")

    bsd_dot_cuoi = fields.Boolean(string="Đợt thanh toán cuối", default=False)

    bsd_tl_tt = fields.Float(string="Tỷ lệ thanh toán", help="Tỷ lệ thanh toán theo từng đợt bàn giao", required=True)

    bsd_bg_tam = fields.Boolean(string="Bàn giao tạm", help="Có bàn giao tạm thời theo đợt thanh toán hay không?",
                                default=False)

    bsd_dien_giai = fields.Char(string="Diễn giải", help="Diễn giải")
    bsd_tinh_pbt = fields.Boolean(string="Phí bảo trì", help="Có tính phí bảo trì trong đợt thanh toán hay không?",
                                  default=False)
    bsd_tinh_pql = fields.Boolean(string="Phí quản lý", help="Có tính phí quản lý trong đợt thanh toán hay không?",
                                  default=False)
    bsd_tu_nc = fields.Boolean(string="Từ ngày cọc",
                               help="""Thông tin quy định: hạn thanh toán của đợt thanh toán tính
                                theo ngày cọc hay ngày ký hợp đồng""", default=False)
    bsd_tiep_theo = fields.Selection([('ngay', 'Theo ngày'), ('thang', 'Theo tháng')], string="Đợt tiếp theo", default='ngay',
                                     help="""Cách xác định hạn thanh toán của đợt tiếp theo, được tính
                                     theo số ngày hoặc số tháng
                                     """)
    bsd_so_ngay = fields.Integer(string="Số ngày", help="""Số ngày được sử dụng để tính hạn thanh toán
                                                    của đợt thanh toán tiếp theo""")
    bsd_so_thang = fields.Integer(string="Số tháng", help="""Số tháng được sử dụng để tính hạn thanh toán
                                                    của đợt thanh toán tiếp theo""")
    bsd_ngay_tbvn = fields.Integer(string="Ngày thông báo VN", help="""Số ngày được cộng thêm khi tính hạn thanh toán
                                                                        của mỗi đợt thanh toán đối với khách hàng 
                                                                        trong nước""")
    bsd_ngay_tbnn = fields.Integer(string="Ngày thông báo NN", help="""Số ngày được cộng thêm khi tính hạn thanh toán
                                                                        của mỗi đợt thanh toán đối với khách hàng 
                                                                        nước ngoài""")
    bsd_lap_lai = fields.Selection([('0', 'Không'), ('1', 'Có')], string="Lặp lại",
                                   default="0", help="Cách tính của đợt thanh toán có được lặp lại hay không")

    bsd_ngay_thang = fields.Integer(string="Ngày hàng tháng", help="Thanh toán vào ngày cố định của mỗi tháng")

    bsd_so_dot = fields.Integer(string="Số đợt thanh toán", help="Số đợt thanh toán được lặp lại ")

    bsd_ngay_gh = fields.Integer(string="Ngày gia hạn", help="""Ngày được cộng thêm khi tính hạn thanh toán của đợt 
                                                                thanh toán. Trong trường hợp đợt thanh toán tự động được
                                                                 lặp lại nhiều lần, thì chỉ cộng ngày gia hạn vào đợt 
                                                                 tính tự động cuối cùng.
                                                            """)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="Chính sách thanh toán")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Không sử dụng')],
                             string="Trạng thái", default='active', required=True)
    # bsd_gd_tt = fields.Selection([('dat_coc', 'Đặt cọc'), ('hop_dong', 'Hợp đồng')],
    #                              string="Giai đoạn thanh toán", help="Thanh toán trước hay sau làm hợp đồng",
    #                              default="dat_coc", required=True)
    bsd_dot_ky_hd = fields.Boolean(string="Đợt ký hợp đồng", help="Đánh dấu đợt thanh toán là đợt ký hợp đồng")

    @api.onchange('bsd_dot_cuoi')
    def _onchange_bsd_dot_cuoi(self):
        _logger.debug("debug tại đây")
        self.bsd_cach_tinh = None
