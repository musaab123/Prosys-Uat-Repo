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
from odoo.addons.portal.controllers.mail import PortalChatter

from werkzeug import urls
from werkzeug.exceptions import NotFound, Forbidden

from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.tools import consteq, plaintext2html
from odoo.addons.mail.controllers import mail
from odoo.exceptions import AccessError



from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime
from odoo.tools import groupby as groupbyelem
from odoo.exceptions import AccessError, MissingError, ValidationError,RedirectWarning, UserError
import base64
import json
import math
import re
from werkzeug import urls



DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')

def _check_special_access(res_model, res_id, token='', _hash='', pid=False):
    record = request.env[res_model].browse(res_id).sudo()
    if _hash and pid:  # Signed Token Case: hash implies token is signed by partner pid
        return consteq(_hash, record._sign_token(pid))
    elif token:  # Token Case: token is the global one of the document
        token_field = request.env[res_model]._mail_post_token_field
        return (token and record and consteq(record[token_field], token))
    else:
        raise Forbidden()


def _message_post_helper_sudo(res_model, res_id, message, token='', _hash=False, pid=False, nosubscribe=True, **kw):
    """ Generic chatter function, allowing to write on *any* object that inherits mail.thread. We
        distinguish 2 cases:
            1/ If a token is specified, all logged in users will be able to write a message regardless
            of access rights; if the user is the public user, the message will be posted under the name
            of the partner_id of the object (or the public user if there is no partner_id on the object).

            2/ If a signed token is specified (`hash`) and also a partner_id (`pid`), all post message will
            be done under the name of the partner_id (as it is signed). This should be used to avoid leaking
            token to all users.

        Required parameters
        :param string res_model: model name of the object
        :param int res_id: id of the object
        :param string message: content of the message

        Optional keywords arguments:
        :param string token: access token if the object's model uses some kind of public access
                             using tokens (usually a uuid4) to bypass access rules
        :param string hash: signed token by a partner if model uses some token field to bypass access right
                            post messages.
        :param string pid: identifier of the res.partner used to sign the hash
        :param bool nosubscribe: set False if you want the partner to be set as follower of the object when posting (default to True)

        The rest of the kwargs are passed on to message_post()
    """
    record = request.env[res_model].sudo().browse(res_id)

    # check if user can post with special token/signed token. The "else" will try to post message with the
    # current user access rights (_mail_post_access use case).
    if token or (_hash and pid):
        pid = int(pid) if pid else False
        if _check_special_access(res_model, res_id, token=token, _hash=_hash, pid=pid):
            record = record.sudo()
        else:
            raise Forbidden()
    else:  # early check on access to avoid useless computation
        record.check_access_rights('read')
        record.check_access_rule('read')

    # deduce author of message
    author_id = request.env.user.partner_id.id if request.env.user.partner_id else False

    # Signed Token Case: author_id is forced
    if _hash and pid:
        author_id = pid
    # Token Case: author is document customer (if not logged) or itself even if user has not the access
    elif token:
        if request.env.user._is_public():
            # TODO : After adding the pid and sign_token in access_url when send invoice by email, remove this line
            # TODO : Author must be Public User (to rename to 'Anonymous')
            author_id = record.partner_id.id if hasattr(record, 'partner_id') and record.partner_id.id else author_id
        else:
            if not author_id:
                raise NotFound()

    email_from = None
    if author_id and 'email_from' not in kw:
        partner = request.env['res.partner'].sudo().browse(author_id)
        email_from = partner.email_formatted if partner.email else None

    message_post_args = dict(
        body=message,
        message_type=kw.pop('message_type', "comment"),
        subtype_xmlid=kw.pop('subtype_xmlid', "mail.mt_comment"),
        author_id=author_id,
        **kw
    )

    # This is necessary as mail.message checks the presence
    # of the key to compute its default email from
    if email_from:
        message_post_args['email_from'] = email_from

    return record.with_context(mail_create_nosubscribe=nosubscribe).message_post(**message_post_args)

class PortalChaterInherit(PortalChatter):

    @http.route(['/mail/chatter_post'], type='json', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, attachment_ids=None, attachment_tokens=None, **kw):
        """Create a new `mail.message` with the given `message` and/or `attachment_ids` and return new message values.

        The message will be associated to the record `res_id` of the model
        `res_model`. The user must have access rights on this target document or
        must provide valid identifiers through `kw`. See `_message_post_helper`.
        """
        if not self._portal_post_has_content(res_model, res_id, message,
                                             attachment_ids=attachment_ids, attachment_tokens=attachment_tokens,
                                             **kw):
            print("before if kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
            return


        res_id = int(res_id)

        self._portal_post_check_attachments(attachment_ids or [], attachment_tokens or [])

        result = {'default_message': message}
        # message is received in plaintext and saved in html
        if message:
            message = plaintext2html(message)
        post_values = {
            'res_model': res_model,
            'res_id': res_id,
            'message': message,
            'send_after_commit': False,
            'attachment_ids': False,  # will be added afterward
        }

        post_values.update((fname, kw.get(fname)) for fname in self._portal_post_filter_params())

        post_values['_hash'] = kw.get('hash')
        message = _message_post_helper_sudo(**post_values)
        print("after if vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")

        result.update({'default_message_id': message.id})
        print("after if vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")



        if attachment_ids:
            # sudo write the attachment to bypass the read access
            # verification in mail message
            record = request.env[res_model].browse(res_id)
            message_values = {'res_id': res_id, 'model': res_model}
            attachments = record._message_post_process_attachments([], attachment_ids, message_values)

            if attachments.get('attachment_ids'):
                message.sudo().write(attachments)

            result.update({'default_attachment_ids': message.attachment_ids.sudo().read(['id', 'name', 'mimetype', 'file_size', 'access_token'])})
        return result


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


    def _document_check_access_sudo(self, model_name, document_id, access_token=None):
        """Check if current user is allowed to access the specified record.

        :param str model_name: model of the requested record
        :param int document_id: id of the requested record
        :param str access_token: record token to check if user isn't allowed to read requested record
        :return: expected record, SUDOED, with SUPERUSER context
        :raise MissingError: record not found in database, might have been deleted
        :raise AccessError: current user isn't allowed to read requested document (and no valid token was given)
        """
        document = request.env[model_name].sudo().browse([document_id])
        document_sudo = document.with_user(SUPERUSER_ID).exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not document_sudo.access_token or not consteq(document_sudo.access_token, access_token):
                raise
        return document_sudo
    


    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    @http.route('/portal/attachment/add', type='http', auth='public', methods=['POST'], website=True)
    def attachment_add(self, name, file, res_model, res_id, access_token=None, **kwargs):
        """Process a file uploaded from the portal chatter and create the
        corresponding `ir.attachment`.

        The attachment will be created "pending" until the associated message
        is actually created, and it will be garbage collected otherwise.

        :param name: name of the file to save.
        :type name: string

        :param file: the file to save
        :type file: werkzeug.FileStorage

        :param res_model: name of the model of the original document.
            To check access rights only, it will not be saved here.
        :type res_model: string

        :param res_id: id of the original document.
            To check access rights only, it will not be saved here.
        :type res_id: int

        :param access_token: access_token of the original document.
            To check access rights only, it will not be saved here.
        :type access_token: string

        :return: attachment data {id, name, mimetype, file_size, access_token}
        :rtype: dict
        """
        try:
            self._document_check_access_sudo(res_model, int(res_id), access_token=access_token)
        except (AccessError, MissingError) as e:
            raise UserError(_("The document does not exist or you do not have the rights to access it."))

        IrAttachment = request.env['ir.attachment']
        access_token = False

        # Avoid using sudo or creating access_token when not necessary: internal
        # users can create attachments, as opposed to public and portal users.
        if not request.env.user._is_internal():
            IrAttachment = IrAttachment.sudo().with_context(binary_field_real_user=IrAttachment.env.user)
            access_token = IrAttachment._generate_access_token()

        # At this point the related message does not exist yet, so we assign
        # those specific res_model and res_is. They will be correctly set
        # when the message is created: see `portal_chatter_post`,
        # or garbage collected otherwise: see  `_garbage_collect_attachments`.
        attachment = IrAttachment.create({
            'name': name,
            'datas': base64.b64encode(file.read()),
            'res_model': 'mail.compose.message',
            'res_id': 0,
            'access_token': access_token,
        })
        return request.make_response(
            data=json.dumps(attachment.read(['id', 'name', 'mimetype', 'file_size', 'access_token'])[0]),
            headers=[('Content-Type', 'application/json')]
        )


    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    

    @http.route(['/my/delivery-orders/view/<int:picking_id>'], auth='user', type='http', website=True, csrf=True)
    def drivers_picking_create_page(self,picking_id=None,access_token=None, **kw):
        try:
            delevery_sudo =self._document_check_access_sudo('stock.picking', picking_id, access_token=access_token)
       
        except (AccessError, MissingError) as test:
            print("dddddddddddddddddddddddddddddddddddddd",test)
            return 
        
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

   


   