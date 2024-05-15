from odoo import fields, models, api, _
from odoo.exceptions import ValidationError,UserError
from odoo.exceptions import UserError
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    access_token = fields.Char()