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

    arabic_name = fields.Char('Arabic Name')
    arabic_street = fields.Char('Arabic Street')
    arabic_street2 = fields.Char('Arabic Street2')
    arabic_city = fields.Char('Arabic City')
    arabic_state = fields.Char('Arabic State')
    arabic_country = fields.Char('Arabic Country')
    arabic_zip = fields.Char('Arabic Zip')
    arabic_web = fields.Char('Arabic Website')
    arabic_company_dis = fields.Char('Arabic  Company description')
    date_creation = fields.Datetime('Created Date', invisible=True, default=fields.Datetime.now)

