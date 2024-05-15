from odoo import models, fields, api

class stock_location(models.Model):
    _inherit = "stock.picking"
    
    driver_id = fields.Many2one('res.partner',string="Driver",related="sale_id.driver_id",store=True,readonly=False)
    driver_status = fields.Selection([
        ('Assigned', 'Assigned'),
        ('In-Transit', 'In-Transit'),
        ('Delivered', 'Delivered'),
        ('Delivered with Return', 'Delivered with Return'),
        ('Cancelled', 'Cancelled'),
    ], string='Driver Status')

    is_driver_confirm = fields.Boolean(string='Driver Confirm')


    