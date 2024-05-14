from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    team_id = fields.Many2one('crm.team', 'Sales Team')
    

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_id = fields.Many2one('sale.order', 'Sale Order')
    custom_team_id = fields.Many2one("crm.team", related="sale_id.team_id", string="Sale Team")



class ResCompany(models.Model):
    _inherit = 'res.company'
    date_creation = fields.Datetime('Created Date', invisible=True, default=fields.Datetime.now)

