# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import http, _,SUPERUSER_ID
from operator import itemgetter
from pytz import timezone, UTC
from odoo.addons.resource.models.resource import float_to_time
from collections import OrderedDict
from collections import namedtuple
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime
from odoo.tools import groupby as groupbyelem
from odoo.exceptions import AccessError, MissingError, ValidationError,RedirectWarning, UserError


DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')


class PortalProductSales(CustomerPortal):
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'drivers_count' in counters:

            sales = request.env['stock.picking'].sudo().search([('driver_id', '=', request.env.user.partner_id.id),('driver_status','=','Assigned')])
            values['drivers_count'] = len(sales)
        return values

    def _get_searchbar_drivers_inputs(self):
        return {
            'all': {'input': 'all', 'label': _('Search in All')},
            'name': {'input': 'name', 'label': _('Search in Ref Name')},
            'scheduled_date': {'input': 'scheduled_date', 'label': _('Search with Schedule Date')},
        }

    def _get_search_drivers_domain(self, search_in, search):
        search_domain = []
        if search_in in ('name', 'all'):
            search_domain = OR([search_domain, [('name', 'ilike', search)]])
        if search_in in ('name', 'all'):
            search_domain = OR([search_domain, [('name', 'ilike', search)]])
        if search_in in ('scheduled_date', 'all'):
            search_domain = OR([search_domain, [('scheduled_date', 'ilike', search)]])
        return search_domain

    def _get_searchbar_drivers_sortings(self):
        return {
            'name': {'label': _('Name'), 'order': 'name asc', 'sequence': 1},
        }

    def _get_searchbar_drivers_groupby(self):
        values = {
            'none': {'input': 'none', 'label': _('None'), 'order': 1},
            'name': {'input': 'name', 'label': _('Name'), 'order': 2},
        }
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_groupby_drivers_mapping(self):
        return {
            'name': 'name',
        }

    def _get_order(self, order, groupby):
        groupby_mapping = self._get_groupby_drivers_mapping()
        field_name = groupby_mapping.get(groupby, '')
        if not field_name:
            return order
        return '%s, %s' % (field_name, order)

    @http.route(['/my/delivery-orders', '/my/delivery-orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_drivers_delivery_orders(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        pickings = request.env['stock.picking'].sudo()
        _items_per_page = 20

        # if request.env.user._is_admin():
        #     domain = []
        # else:
        domain = [('driver_id', '=', request.env.user.partner_id.id),('state','=','done'),('is_driver_confirm','=', False),('picking_type_id.code', '=', 'outgoing')]
        searchbar_sortings = self._get_searchbar_drivers_sortings()
        searchbar_groupby = self._get_searchbar_drivers_groupby()
        searchbar_inputs = self._get_searchbar_drivers_inputs()
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': domain},
        }

        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain += searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        if not groupby:
            groupby = 'none'

        if search and search_in:
            domain += self._get_search_drivers_domain(search_in, search)

        drivers_count = pickings.search_count(domain)

        pager = portal_pager(
            url="/my/delivery-orders",
            url_args={'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby, 'sortby': sortby},
            total=drivers_count,
            page=page,
            step=_items_per_page
        )

        order = self._get_order(order, groupby)
        picking_list = pickings.search(domain, order=order, limit=_items_per_page, offset=pager['offset'])
        # request.session['my_leave_history'] = saless.ids[:100]
        pickinglength = len(picking_list)
        groupby_mapping = self._get_groupby_drivers_mapping()
        group = groupby_mapping.get(groupby)
        if group:
            grouped_deliveries = [pickings.concat(*g) for k, g in groupbyelem(picking_list, itemgetter(group))]
        else:
            grouped_deliveries = [picking_list]
        # raise UserError(grouped_salesmen)
        values.update({
            'grouped_deliveries': grouped_deliveries,
            'page_name': 'driver_delivery',
            'pager': pager,
            'default_url': '/my/delivery-orders',
            'search_in': search_in,
            'search': search,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'picking_list':picking_list,
            'searchbar_inputs': searchbar_inputs,
            'pickinglength':pickinglength,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("prosys_drivers_portal.portal_my_driver_delivery_list", values)
    
    


    @http.route(['/make_deliveies_in_transit'], type='json', auth="none", website=True)
    def make_deliveies_in_transit(self,  **kw):
        pickings =  kw['pickings'] if kw['pickings'] else False
        for pick in pickings:
            
            picking =  request.env['stock.picking'].sudo().browse(int(pick))
        
            picking.sudo().write({'driver_status':'In-Transit'})
        
        return {
            'done':True,
        }




    @http.route(['/my/delivery-orders/view/<int:picking_id>'], auth='user', type='http', website=True, csrf=True)
    def drivers_picking_create_page(self,picking_id=None,access_token=None, **kw):
        try:
            delevery_sudo = self._document_check_access('stock.picking', picking_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        user = request.env.user
        is_driver = user.partner_id.is_driver
        pickings = request.env['stock.picking'].sudo().browse(picking_id)
        return http.request.render('prosys_drivers_portal.portal_edit_in_picking_details', {
            'yg_user': user,
            'object': delevery_sudo,
            'is_driver': is_driver,
            'page_name': 'picking_details',
            'pickings':pickings,
        })
        
    @http.route(['/In_transit_of_picking_by_client'], type='json', auth="none", website=True)
    def In_transit_of_picking_by_client(self,  **kw):
        picking_id =  int(kw['picking_id']) if kw['picking_id'] else False
        picking =  request.env['stock.picking'].sudo().browse(picking_id)
        
        picking.sudo().write({'driver_status':'In-Transit'})
        
        return {
            'done':True,
        }
        
    @http.route(['/cancellation_of_picking_by_client'], type='json', auth="none", website=True)
    def cancellation_of_picking_by_client(self,  **kw):
        picking_id =  int(kw['picking_id']) if kw['picking_id'] else False
        picking =  request.env['stock.picking'].sudo().browse(picking_id)
        
        # picking.sudo().action_cancel()
        picking.sudo().write({'driver_status':'Cancelled'})
        
        return {
            'done':True,
        }
    


    # @http.route(['/returened_of_picking_by_client'], type='json', auth="none", website=True)
    # def returened_of_picking_by_client(self, **kw):
    #     picking_id = int(kw['picking_id']) if kw['picking_id'] else False
    #     table_length = int(kw['table_length']) if kw['table_length'] else 0
    #     picking = request.env['stock.picking'].sudo().browse(picking_id)
    #     products = kw['products']

    #     try:
    #         picking_id = request.env['stock.return.picking'].sudo().create({'picking_id': picking.id})
    #         vals = []
    #         for move in picking.move_ids_without_package:
    #             print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx---->",move)

            
    #             for pro in products:
    #                 returned_qty = float(pro['returend_qty'])
    #                 print("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq --->",returned_qty)
                                    
    #                 move_vals = {
    #                         'product_id': move.product_id.id,
    #                         'quantity': returned_qty,
    #                         'wizard_id': picking_id.id,
    #                         'move_id': move.id,
    #                         'to_refund': True,
    #                     }
    #                 vals.append(move_vals)
                    
    #         picking_line_id = request.env['stock.return.picking.line'].sudo().with_user(SUPERUSER_ID).create(vals)
            
    #         new_picking, pick_type_id = picking_id.with_user(SUPERUSER_ID)._create_returns()
    #         picking_n = request.env['stock.picking'].sudo().browse(new_picking)
    #         picking.sudo().write({'driver_status': 'Delivered with Return'})
    #         picking_n.sudo().write({'driver_status': 'Delivered with Return'})
            
    #         return {'success': True, 'error': False}
    #     except Exception as e:
    #         return {'success': False, 'error': f'Return confirmation failed: {str(e)}'}

            
    @http.route(['/returened_of_picking_by_client'], type='json', auth="none", website=True)
    def returened_of_picking_by_client(self,  **kw):
        picking_id =  int(kw['picking_id']) if kw['picking_id'] else False
        table_length =  int(kw['table_length']) if kw['table_length'] else 0
        picking =  request.env['stock.picking'].sudo().browse(picking_id)
        products = kw['products']
        # for rec in products:
        
        try:
            picking_id =  request.env['stock.return.picking'].sudo().create({'picking_id':picking.id})
            vals = []
            for move in picking.move_ids_without_package:
                
                for pro in products:
                    if move.product_id.id == int(pro['product']):
                        move_vals = {
                            'product_id':move.product_id.id,
                            'quantity':float(pro['returend_qty']),
                            'wizard_id':picking_id.id,
                            'move_id':move.id,
                            'to_refund':True,
                        }
                        vals.append(move_vals)
            picking_line_id =  request.env['stock.return.picking.line'].sudo().with_user(SUPERUSER_ID).create(vals)
            
            new_picking, pick_type_id = picking_id.with_user(SUPERUSER_ID)._create_returns()
            picking_n = request.env['stock.picking'].sudo().browse(new_picking)
            picking.sudo().write({'driver_status':'Delivered with Return'})
            picking_n.sudo().write({'driver_status':'Delivered with Return'})
            
            return {'success': True, 'error': False}

        except Exception as e:
            return {'success': False, 'error': f'Return confirmation failed: {str(e)}'}
        
        
    @http.route(['/delivery_of_picking_by_client'], type='json', auth="none", website=True)
    def delivery_of_picking_by_client(self,  **kw):
        picking_id =  int(kw['picking_id']) if kw['picking_id'] else False
        picking =  request.env['stock.picking'].sudo().browse(picking_id)
        
        # try:
        #     picking.action_confirm()
        # except UserError as e:
        #     return {'error': e.name}

        # Process the transfer
        try:
            # if picking.state == 'draft':
            #     picking.with_user(SUPERUSER_ID).action_confirm()
            #     if picking.state != 'assigned':
            #         picking.with_user(SUPERUSER_ID).action_assign()
            # picking.with_user(SUPERUSER_ID).move_ids.sudo()._set_quantities_to_reservation()
            # picking.with_user(SUPERUSER_ID).with_context(skip_immediate=True).button_validate()
            picking.sudo().write({'driver_status':'Delivered'})
            
        except UserError as e:
            return {'error': e.name}
        
        return {'error':False}

   


   