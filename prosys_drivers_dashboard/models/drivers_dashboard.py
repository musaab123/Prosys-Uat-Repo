# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd
from pytz import utc
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import float_utils


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def get_drivers_deliveries_counts(self):
        pickings = self.env['stock.picking'].sudo().search(
            [('driver_id', '!=', False)])
        datas = [{
            'assigned_count': len(pickings.search([('driver_status' ,'=', 'Assigned') ,('picking_type_id.code', '=', 'outgoing'), ('origin', 'not ilike', 'Return')])),
            # 'unassigned_count': len(pickings.search([('driver_status' ,'!=', 'Assigned'),('state','=', 'done') ,('picking_type_id.code', '=', 'outgoing'), ('origin', 'not ilike', 'Return')])),
            'unassigned_count': len(pickings.search([('driver_status' ,'!=', 'Assigned'),
                                                      ('driver_id', '=', False),
                                                      ('state','=', 'done'),
                                                      ('picking_type_id.code', '=', 'outgoing'),
                                                      ('origin', 'not ilike', 'Return')])),
            'transit_count': len(pickings.search([('driver_status' ,'=', 'In-Transit') ,('picking_type_id.code', '=', 'outgoing'), ('origin', 'not ilike', 'Return')])),
            'delivered_count': len(pickings.search([('driver_status' ,'=', 'Delivered') ,('picking_type_id.code', '=', 'outgoing'), ('origin', 'not ilike', 'Return')])),
            'returned_count': len(pickings.search([('driver_status' ,'=', 'Delivered with Return') ,('picking_type_id.code', '=', 'incoming'), ('origin', 'ilike', 'Return')])),
            'cancelled_count': len(pickings.search([('driver_status' ,'=', 'Cancelled') ,('picking_type_id.code', '=', 'outgoing'), ('origin', 'not ilike', 'Return')])),
        }]
        return datas
    




# class StockPicking(models.Model):
#     _inherit = 'stock.picking'

#     @api.model
#     def get_unassigned_drivers_counts(self):
#         pickings = self.env['stock.picking'].sudo().search(
#             [('driver_id', '=', False)])
#         datas = [{
#             'unassigned_count': len(pickings.search([('driver_status' ,'!=', 'Assigned'),('state','=', 'done') ,('picking_type_id.code', '=', 'outgoing'), ('origin', 'not ilike', 'Return')])),
#         }]
#         return datas