from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    driver_id = fields.Many2one('res.partner',string="Driver")
    
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['driver_id'] = self.driver_id.id
        return invoice_vals
    
    
class AccountMove(models.Model):
    _inherit = "account.move"
    
    driver_id = fields.Many2one('res.partner',string="Driver")

    