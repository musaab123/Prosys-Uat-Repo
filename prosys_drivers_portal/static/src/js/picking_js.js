odoo.define('prosys_drivers_portal.portal_stock_drivers', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.portal_stock_drivers = publicWidget.Widget.extend({
        
        selector: '.js_picking_drivers_selector',
        events: {
            'click #picking_delivered_val': '_onClickpicking_delivered_val',
            'click #picking_returned_val': '_onClickpicking_returned_val',
            'click #picking_cancelled_val': '_onClickpicking_cancelled_val',
            'click #confirm_return_val': '_onClickconfirm_return_val',
            'click #in_transit_btn_val': '_onClickin_transit_btn_val',
            'click #qty_decrement': '_onclick_qty_decrement',
            'click #qty_increment': '_onclick_qty_increment',
            'click #picking_transit_val':'_onclick_picking_transit_val',
            

            
        },
        async start() {
            await this._super(...arguments);

            console.log('start');
        },


        async _onclick_picking_transit_val(event){

            var result = {};
            var picking_length = document.getElementById('picking_length').value;
            var pickings = [];
            var empty = 0;
            for (let index = 1; index <= parseInt(picking_length); index++) {
                if ($('input[name="del_check['+index+']"]').prop("checked")){
                    pickings.push(document.getElementById('picking_id['+index+']').value);
                    empty = 1;
                }
                
            }
            if (empty == 1){
                result['pickings'] = pickings;
                ajax.jsonRpc('/make_deliveies_in_transit', 'call', result).then( function(data){
                    var error = data['error']
                    if (error){
                        alert(error);   
                    } else {
                        location.reload();   
                    }


                });
            }else{
                alert('There is no records selected!!');
                event.preventDefault(); 
                return false;
            }

        },
        async _onclick_qty_decrement(event){
            var file = event.target;
            var qty = $(file).attr('qtyid');
            var qty_val = document.getElementById('re_pro_qty['+qty+']');
            var currentValue = parseInt(qty_val.value);


            if (currentValue > 1) {
                qty_val.value = currentValue - 1;
            }            
        },

        async _onclick_qty_increment(event){
            var file = event.target;
            var qty = $(file).attr('qtyid');
            var qty_val = document.getElementById('re_pro_qty['+qty+']');
            var currentValue = parseInt(qty_val.value);

            qty_val.value = currentValue + 1;        
        },

        async _onClickpicking_delivered_val(){
            var result = {};
            var picking_id = document.getElementById('picking_id').value;
            result['picking_id'] = picking_id;

            ajax.jsonRpc('/delivery_of_picking_by_client', 'call', result).then( function(data){
                var error = data['error']
                if (error){
                    alert(error);   
                } else {
                    location.reload();   
                }


            });
        },

        async _onClickconfirm_return_val(){
            var result = {};
            var picking_id = document.getElementById('picking_id').value;
            result['picking_id'] = picking_id;
            var table_length = document.getElementById('table_length');
            var tablelength = parseInt(table_length.value);
            result['table_length'] = tablelength;
            var datas = [];
            for (let index = 0; index < tablelength; index++) {
                datas.push({
                    'product':document.getElementById('pro_id['+index+']').value,
                    'returend_qty':document.getElementById('re_pro_qty['+index+']').value,
                })
                
            }
            result['products'] = datas;



            ajax.jsonRpc('/returened_of_picking_by_client', 'call', result).then( function(data){
                var error = data['error']
                var success = data['success']
                if (error){
                    alert(error);   
                } else {
                    location.reload();   
                }


            });
        },


        async _onClickpicking_returned_val(){
            var modal_return = document.getElementById('CurrModal');
            modal_return.style.display = 'block';

            window.addEventListener("click", function(event) {
                if (event.target === modal_return) {
                    modal_return.style.display = "none";
                }
            });
        },


        

        async _onClickin_transit_btn_val(){
            var result = {};
            var picking_id = document.getElementById('picking_id').value;
            result['picking_id'] = picking_id;

            ajax.jsonRpc('/In_transit_of_picking_by_client', 'call', result).then( function(data){
                var done = data['done']
                if (done){
                    location.reload();   
                }


            });
        },


        async _onClickpicking_cancelled_val(){
            var result = {};
            var picking_id = document.getElementById('picking_id').value;
            result['picking_id'] = picking_id;

            ajax.jsonRpc('/cancellation_of_picking_by_client', 'call', result).then( function(data){
                var done = data['done']
                if (done){
                    location.reload();   
                }


            });
        },

        
       
    });
});
