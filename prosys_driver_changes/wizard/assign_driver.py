from dateutil.relativedelta import relativedelta
from dateutil import relativedelta
from datetime import datetime, timedelta , date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
import calendar
import re

class WizardAssignDriver(models.TransientModel):
    _name = 'wizard.assign.driver'

    driver_id = fields.Many2one('res.partner','Driver')


    def action_assign_driver(self):
        pickings = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        if any(picking.state != 'done' for picking in pickings):
            raise UserError('There is one of the orders selected is not in done state.\nPlease check and review selected orders.')
        elif any(picking.driver_id for picking in pickings):
            raise UserError('There is one of the orders selected is already having assigned driver.\nPlease check and review selected orders.')
        else:
            for picking in pickings:
                picking.write({'driver_id':self.driver_id.id,'driver_status':'Assigned'})
