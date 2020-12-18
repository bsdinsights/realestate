# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdAssignKH(models.TransientModel):
    _name = 'bsd.wizard.assign_kh'
    _description = 'Assign khách hàng cho nhân viên kinh doanh khác'


