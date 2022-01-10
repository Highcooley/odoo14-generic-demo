odoo.define('aspl_giftcard_package_ee.giftCardRedeemPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    class giftCardRedeemPopup extends AbstractAwaitablePopup {
        constructor(){
            super(...arguments);
            this.state = useState({ GiftCardNumber: '', GiftCardAmount:'',
                                    showCardNumberInput: true, displayAmount : '',
                                    showAmountInput: true, singleCardNumber:''});
            this.gift_card_number_ref = useRef('gift_card_number');
            this.gift_card_amount_ref = useRef('gift_card_amount');
            this.redeem = false;
        }
        mounted() {
            this._autoFillData();
            this.gift_card_number_ref.el.focus();
        }
        onInputKeyDownNumberVlidation(e) {
           if(e.which != 110 && e.which != 8 && e.which != 0 && e.key != this.env.pos.db.decimalSeparator() && e.key != this.env.pos.db.decimalSeparator() && (e.which < 48 || e.which > 57 || e.shiftKey) && (e.which < 96 || e.which > 105) && (e.which < 37 || e.which > 40)) {
                e.preventDefault();
            }
        }
        getPayload() {
            return {
                card_no: this.state.GiftCardNumber,
                card_amount: this.state.GiftCardAmount,
                redeem: this.redeem,
            };
        }
        CheckGiftCardBalance(e) {
            self = this;
            if (e.which == 13 && this.state.GiftCardNumber) {
                var today = moment().locale('en').format('YYYY-MM-DD');
                var code = this.state.GiftCardNumber;
                var get_redeems = this.env.pos.get_order().get_redeem_giftcard();
                var existing_card = _.where(get_redeems, {'redeem_card': code });
                var customer_id = this.env.pos.get_order().get_client().id;
                this.rpc({
                    model: 'gift.card',
                    method: 'search_read',
                    domain: [['card_no', '=', code],
                            ['expire_date', '>=', today],['issue_date', '<=', today],['state', '=', 'confirm']],
                }, {async: true}).then((result) => {
                    if(result.length > 0){
                        if(existing_card.length > 0){
                            res[0]['balance'] = existing_card[existing_card.length - 1]['redeem_remaining']
                        }
                        self.redeem = result[0];
                        self.state.displayAmount = self.env.pos.format_currency(result[0].balance);
                        if(result[0].customer_id[1]){
                           self.state.displayCustomer = self.env.pos.format_currency(result[0].customer_id[1]);
                        }
                        if(result[0].balance <= 0){
                            self.state.showAmountInput = false;
                        }
                    }else{
                        self.env.pos.db.notification('danger',_t('Barcode not found or gift card has been expired.'));
                    }
                })
            }
        }

        async _autoFillData(){
            var self = this;
            var today = moment().locale('en').format('YYYY-MM-DD');
            var customer_id = this.env.pos.get_order().get_client().id;
            var get_redeems = this.env.pos.get_order().get_redeem_giftcard();

             await this.rpc({
                model: 'gift.card',
                method: 'search_read',
                domain: [['customer_id', '=', customer_id], ['expire_date', '>=', today],['issue_date', '<=', today]],
            }, {async: true}).then((result) => {
                if(result.length == 1){
                    self.state.GiftCardNumber = result[0].card_no;
                    var GiftCardAmount = result[0].balance >= self.env.pos.get_order().get_due() ? self.env.pos.get_order().get_due().toFixed(2) : result[0].balance.toFixed(2);
                    self.state.GiftCardAmount = self.env.pos.format_currency_no_symbol(GiftCardAmount)
                    self.state.showCardNumberInput = false;
                        self.redeem = result[0];
                    if(result[0].customer_id){
                        self.state.displayCustomer = self.env.pos.format_currency(result[0].customer_id[1]);
                    }
                    self.state.singleCardNumber = result[0].card_no;
                    self.state.displayAmount = self.env.pos.format_currency(result[0].balance);
                    if(result[0].balance <= 0)
                        self.state.showAmountInput = false;
                } else {
                    self.state.showCardNumberInput = true;
                    self.state.showAmountInput = true;
                }
            })
        }
    }

    giftCardRedeemPopup.template = 'giftCardRedeemPopup';

    giftCardRedeemPopup.defaultProps = {
        confirmText: 'Apply',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };

    Registries.Component.add(giftCardRedeemPopup);

    return giftCardRedeemPopup;
});
