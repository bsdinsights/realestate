# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdChinhSachThanhToan(models.Model):
    _name = 'bsd.cs_tt'
    _rec_name = 'bsd_ten_cstt'
    _description = "Thông tin chính sách thanh toán"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bsd_ma_cstt = fields.Char(string="Mã", help="Mã chính sách thanh toán", required=True)
    _sql_constraints = [
        ('bsd_ma_cstt_unique', 'unique (bsd_ma_cstt)',
         'Mã chính sách thanh toán đã tồn tại !'),
    ]
    bsd_ten_cstt = fields.Char(string="Tên", help="Tên chính sách thanh toán", required=True)
    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_du_an_id = fields.Many2one('bsd.du_an', string="Dự án", required=True, help="Tên dự án")
    bsd_tu_ngay = fields.Date(string="Từ ngày", help="Ngày bắt đầu áp dụng chính sách thanh toán")
    bsd_den_ngay = fields.Date(string="Đến ngày", help="Ngày kết thúc áp dụng chính sách thanh toán")
    bsd_ngay_tinh = fields.Selection([('ndc', 'Ngày đặt cọc'), ('nhd', 'Ngày hợp đồng')],
                                     string="Ngày tính", default="ndc",
                                     help="""
                                     Ngày được sử dụng để bắt đầu tính hạn thanh toán là ngày ký hợp đồng hay
                                     ngày đặt cọc
                                     """)
    bsd_dk_hd = fields.Float(string="Điều kiện hợp đồng", help="Điều kiện thanh toán để làm hợp đồng mua bán")
    bsd_lai_phat_tt_id = fields.Many2one('bsd.lai_phat_tt', string="Lãi phạt", required=True,
                                         help="Phương thức tính lãi suất trong trường hợp chậm thanh toán")

    bsd_phat_thd = fields.Float(string="Phạt trước hợp đồng", required=True,
                                help="""Phần trăm phí phạt (theo giá trị hợp đồng)
                                        trong trường hợp chấm dứt giao dịch trước khi ký hợp đồng
                                """)
    bsd_phat_shd = fields.Float(string="Phạt sau hợp đồng", required=True,
                                help="""Phần trăm phí phạt (theo giá trì hợp đồng) 
                                        trong trường hợp chấm dứt giao dịch sau khi ký hợp đồng
                                """)
    bsd_tb_tt = fields.Integer(string="Thông báo thanh toán",
                               help="Số ngày (trước khi đến hạn thanh toán) để gửi thông tin thanh toán")

    bsd_tl_hd = fields.Integer(string="Thanh lý hợp đồng",
                               help="Tổng số ngày trễ tối đa để thanh lý hợp đồng")
    bsd_qh_tt = fields.Integer(string="Quá hạn thanh toán", help="Số ngày trễ tối đa của mỗi đợt thanh toán")
    bsd_canh_bao1 = fields.Integer(string="Cảnh báo 1",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 1")
    bsd_canh_bao2 = fields.Integer(string="Cảnh báo 2",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 2")
    bsd_canh_bao3 = fields.Integer(string="Cảnh báo 3",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 3")
    bsd_canh_bao4 = fields.Integer(string="Cảnh báo 4",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 4")
    bsd_canh_bao5 = fields.Integer(string="Cảnh báo 5",
                                   help="Số ngày (sau khi đến hạn thanh toán) để gửi cảnh báo quá hạn thanh toán lần 5")

    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True, tracking=1, help="Trạng thái")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_ct_ids = fields.One2many('bsd.cs_tt_ct', 'bsd_cs_tt_id', string="Chi tiết")


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
                                     """, default='cd')
    bsd_ngay_cd = fields.Date(string="Ngày cố định",
                              help="Ngày thanh toán của đợt thanh toán theo cách tính: ngày cố định")

    bsd_dot_cuoi = fields.Boolean(string="Đợt bàn giao cuối", default=False)

    bsd_tl_tt = fields.Float(string="Tỷ lệ thanh toán", help="Tỷ lệ thanh toán theo từng đợt bàn giao", required=True)

    bsd_bg_tam = fields.Boolean(string="Bàn giao tạm", help="Có bàn giao tạm thời theo đợt thanh toán hay không?",
                                default=False)

    bsd_dien_giai = fields.Char(string="Diễn giải")
    bsd_tinh_pbt = fields.Boolean(string="Phí bảo trì", help="Có tính phí bảo trì trong đợt thanh toán hay không?",
                                default=False)
    bsd_tinh_pql = fields.Boolean(string="Phí quản lý", help="Có tính phí quản lý trong đợt thanh toán hay không?",
                                default=False)
    bsd_tu_nc = fields.Boolean(string="Từ ngày cọc",
                               help="""Thông tin quy định: hạn thanh toán của đợt thanh toán tính
                                theo ngày cọc hay ngày ký hợp đồng""", default=False)
    bsd_tiep_theo = fields.Selection([('ngay', 'Ngày'), ('thang', 'Tháng')], string="Đợt tiếp theo", default='ngay',
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

    bsd_ngay_gh = fields.Integer(string="Ngày gia hạn", help="""Ngày được công thêm khi tính hạn thanh toán
                                                                của đợt thanh toán tự động được lặp lại nhiều lần, thì
                                                                chỉ cộng ngày gia hạn vào đợt tính tự động cuối cùng
                                                            """)
    bsd_cs_tt_id = fields.Many2one('bsd.cs_tt', string="Chính sách thanh toán")
    state = fields.Selection([('active', 'Đang sử dụng'),
                              ('inactive', 'Ngưng sử dụng')],
                             string="Trạng thái", default='active', required=True)

    @api.onchange('bsd_dot_cuoi')
    def _onchange_bsd_dot_cuoi(self):
        _logger.debug("debug tại đây")
        self.bsd_cach_tinh = None
