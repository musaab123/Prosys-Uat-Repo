from odoo import fields, models, api, _
from odoo.exceptions import ValidationError,UserError
from odoo.exceptions import UserError
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_update_stock_confirm(self):
        list_ids = []
        for rec in self:
            list_ids.append(rec.id)

        return {
            'name': _("Set Confirmition"),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.confirm.driver',
            'view_mode': 'form,tree',
            'view_type': 'form',
            'context': {'default_confirm_ids': list_ids},
            'target': 'new',
        }


class ChangeConfirmWizard(models.TransientModel):
    _name = 'wizard.confirm.driver'

    is_driver_confirm = fields.Boolean(default=False, tracking=True ,string="Active") 


    driver_status = fields.Selection([
        ('Assigned', 'Assigned'),
        ('In-Transit', 'In-Transit'),
        ('Delivered', 'Delivered'),
        ('Delivered with Return', 'Delivered with Return'),
        ('Cancelled', 'Cancelled'),
    ], string='Driver Status')

    @api.model
    def default_get(self, fields):
        defaults = super(ChangeConfirmWizard, self).default_get(fields)
        defaults['is_driver_confirm'] = False
        return defaults

    def action_confirm_driver(self):
        list_ids = self.env.context.get('default_confirm_ids')
        invoice_id = self.env['stock.picking']
        if self.env.context.get('default_confirm_ids'):
            invoice_id = self.env['stock.picking'].search([('id', 'in', list_ids)])

        for rec in invoice_id:
            if rec.driver_status in ['Delivered', 'Delivered with Return']:
                rec.write({ 'is_driver_confirm': self.is_driver_confirm})

            else :
                raise UserError("I apologiz Driver Not Done His Jop")



