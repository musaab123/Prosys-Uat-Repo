from odoo import api,fields, models, _
from odoo.tools import check_barcode_encoding, groupby

class CrmTeam(models.Model):
    _inherit = 'stock.picking' 
    sale_id = fields.Many2one('sale.order')
    date_creation = fields.Datetime('Created Date', invisible=True, default=fields.Datetime.now)
    team_id = fields.Many2one(
        comodel_name='crm.team',
        string="Sales Team",
        related='sale_id.team_id'
       
       )
    
    packages_number = fields.Char(string="Number of packages")
    

    






    
