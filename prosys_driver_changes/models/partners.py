from odoo import models, fields, api

class Partner(models.Model):
    _inherit = "res.partner"
    
    is_driver = fields.Boolean('Is Driver?')
    driver_user_id = fields.Many2one('res.users',string="Driver")

    