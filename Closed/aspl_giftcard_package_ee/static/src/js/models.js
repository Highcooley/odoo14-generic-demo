odoo.define('aspl_giftcard_package_ee.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;
    var utils = require('web.utils');
    var session = require('web.session');

    var round_pr = utils.round_precision;
    var QWeb = core.qweb;

    models.load_fields("pos.payment.method", ['allow_for_gift_card'])
    models.load_fields("res.company", ['gift_card_account_id', 'default_exp_month', 'menual_card_number'])

    var _super_paymentline = models.Paymentline.prototype;
    var _super_Order = models.Order.prototype;

    models.PosModel.prototype.models.push({
        model:  'gift.card.type',
        fields: ['name'],
        loaded: function(self,card_type){
            self.card_type = card_type;
        },
    },{
        model: 'gift.card',
        domain: [['is_active', '=', true]],
        loaded: function(self,gift_cards){
            self.set({'gift_card_order_list' : gift_cards});
        },
    },{
        model:  'res.users',
        fields: ['name','company_id', 'id', 'groups_id', 'lang'],
        domain: function(self){ return [['company_ids', 'in', self.config.company_id[0]],'|', ['groups_id','=', self.config.group_pos_manager_id[0]],['groups_id','=', self.config.group_pos_user_id[0]]]; },
        loaded: function(self,users){
            users.forEach(function(user) {
                user.role = 'cashier';
                user.admin_role = 'user';
                user.groups_id.some(function(group_id) {
                    if (group_id === self.config.group_admin_user_id[0]) {
                        user.admin_role = 'admin';
                        if (group_id === self.config.group_pos_manager_id[0]) {
                            user.role = 'manager';
                            return true;
                        }
                        return true;
                    }   
                    if (group_id === self.config.group_pos_manager_id[0]) {
                        user.role = 'manager';
                        return true;
                    }
                });
                if (user.id === self.session.uid) {
                    self.user = user;
                    self.employee.name = user.name;
                    self.employee.role = user.role;
                    self.employee.user_id = [user.id, user.name];
                }
            });
            self.users = users;
            self.employees = [self.employee];
            self.set_cashier(self.employee);
        },
    });

    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            var res = _super_Order.initialize.apply(this, arguments);
            this.set({
                rounding: true,
            });
            this.redeem = false;
            this.recharge = false;
            this.giftcard = [];
            this.if_gift_card = false;
            this.to_gift_card = this.to_gift_card || false;
            return this;
        },
        init_from_JSON: function(json){
            _super_Order.init_from_JSON.apply(this,arguments);
            this.to_gift_card = json.to_gift_card;
        },
        getOrderReceiptEnv: function() {
            // Formerly get_receipt_render_env defined in ScreenWidget.
            var res = _super_Order.getOrderReceiptEnv.call(this);
            var barcode_val = this.get_giftcard();
            var barcode_recharge_val = this.get_recharge_giftcard();
            var barcode_redeem_val = this.get_redeem_giftcard();
            if( barcode_val && barcode_val[0]) {
                var barcode = barcode_val[0].card_no;
            }else if(barcode_recharge_val){
                var barcode = barcode_recharge_val.recharge_card_no;
            }else if(barcode_redeem_val){
                var barcode = barcode_redeem_val.redeem_card;
            }
            if(barcode){
                var img = new Image();
                img.id = "test-barcode";
                $(img).JsBarcode(barcode.toString());
                res.receipt['barcode'] = $(img)[0] ? $(img)[0].src : false;
            }
            return res;
        },
        set_gift_card_payment: function(to_gift_card){
            this.to_gift_card = to_gift_card;
            this.trigger('change',this);
        },
        get_is_gift_card_payment: function(){
            return this.to_gift_card;
        },
        set_is_rounding: function(rounding) {
            this.set('rounding', rounding);
        },
        get_is_rounding: function() {
            return this.get('rounding');
        },
        set_giftcard: function(giftcard) {
            this.giftcard.push(giftcard);
        },
        get_giftcard: function() {
            return this.giftcard;
        },
        set_recharge_giftcard: function(recharge) {
            this.recharge = recharge;
        },
        get_recharge_giftcard: function(){
            return this.recharge;
        },
        set_redeem_giftcard: function(redeem) {
            this.redeem = redeem;
        },
        get_redeem_giftcard: function() {
            return this.redeem;
        },
        get_rounding_applied: function() {
            var rounding_applied = _super_Order.get_rounding_applied.call(this);
            var rounding = this.get_is_rounding();
            if(this.pos.config.cash_rounding && !rounding && rounding_applied != 0) {
                rounding_applied = 0
                return rounding_applied;
            }
            return rounding_applied;
        },
        has_not_valid_rounding: function() {
            var rounding_applied = _super_Order.has_not_valid_rounding.call(this);
            var rounding = this.get_is_rounding();
            var line_rounding = true;
            if(!this.pos.config.cash_rounding)
                return false;
            if (this.pos.config.cash_rounding && !rounding)
                return false;
            var lines = this.paymentlines.models;

            for(var i = 0; i < lines.length; i++) {
                var line = lines[i];
                if (line.payment_method.allow_for_gift_card){
                    line_rounding = false;
                    break
                }else{
                    line_rounding = true;
                }
            }
            if (!line_rounding){
                return false;
            }else{
                if(!utils.float_is_zero(line.amount - round_pr(line.amount, this.pos.cash_rounding[0].rounding), 6))
                return line;
            }
            return false;
        },
        // send detail in backend order
        export_as_JSON: function() {
            var orders = _super_Order.export_as_JSON.call(this);
            orders.giftcard = this.get_giftcard() || false;
            orders.recharge = this.get_recharge_giftcard() || false;
            orders.redeem = this.get_redeem_giftcard() || false;
            orders.to_gift_card = this.get_is_gift_card_payment() || false;
            return orders;
        },
        // send detail in report
        export_for_printing: function(){
            var orders = _super_Order.export_for_printing.call(this);
            orders.giftcard = this.get_giftcard() || false;
            orders.recharge = this.get_recharge_giftcard() || false;
            orders.redeem = this.get_redeem_giftcard() || false;
            return orders;
        },
    });

});
