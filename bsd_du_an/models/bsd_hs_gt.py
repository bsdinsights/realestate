from odoo import models, fields, api


class BsdHoSoGiayTo(models.Model):
    _name = 'bsd.hs_gt'
    _description = "Danh sách hồ sơ giấy tờ"
    _rec_name = 'bsd_ten'

    bsd_ten = fields.Char(string="Tên", help="Tên hồ sơ giấy tờ", required=True)