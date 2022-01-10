odoo.define('aspl_giftcard_package_ee.PaymentScreenInherit', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { posbus } = require('point_of_sale.utils');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    var core = require('web.core');
    var _t = core._t;

    const PaymentScreenInherit = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
                this.payment_methods_config = this.env.pos.payment_methods.filter(method => this.env.pos.config.payment_method_ids.includes(method.id));
            }
            deletePaymentLine(event){
                const { cid } = event.detail;
                const line = this.paymentLines.find((line) => line.cid === cid);
                if (['waiting', 'waitingCard', 'timeout'].includes(line.get_payment_status())) {
                    line.payment_method.payment_terminal.send_payment_cancel(this.currentOrder, cid);
                }
                this.currentOrder.remove_paymentline(line);
                if(line.payment_method.allow_for_gift_card){
                    this.currentOrder.set_gift_card_payment(!this.currentOrder.get_is_gift_card_payment());
                }
                NumberBuffer.reset();
                this.render();
            }
            async useGiftCardForPayment() {
                var order = this.env.pos.get_order();
                if(order.get_is_gift_card_payment()){
                    return;
                }
                const { confirmed,payload } = await this.showPopup('giftCardRedeemPopup', {
                    title: this.env._t('Gift Card'),
                });
                if (confirmed){
                    var self = this;
                    var redeem_amount = self.env.pos.db.thousandsDecimalChanger(payload.card_amount);
                    var code = payload.card_no;
                    var redeem = payload.redeem;
                    if(order.get_due() < redeem_amount){
                        alert('Cannot Use Amount More then Due.')
                        return;
                    }
                    if(redeem_amount > 0){
                        if(redeem && redeem.balance >= redeem_amount){
                            var vals = {
                                'redeem_card_no':redeem.id,
                                'redeem_card': code,
                                'redeem_card_amount': redeem_amount,
                                'redeem_remaining':redeem.card_value - redeem_amount,
                                'card_customer_id': redeem.customer_id[0],
                                'customer_name': redeem.customer_id[1],
                                'expiry_date': redeem.expire_date,
                            };
                            var cashRegisters = null;
                            for(const payMethod of self.env.pos.payment_methods){
                                if(payMethod.id === self.env.pos.config.enable_journal_id[0]){
                                    cashRegisters = payMethod;
                                }
                            }
                            if (cashRegisters){
                                order.add_paymentline(cashRegisters);
                                order.selected_paymentline.set_amount( Math.max(redeem_amount),0 );
                                order.set_gift_card_payment(!order.get_is_gift_card_payment());
                                order.set_redeem_giftcard(vals);
                            }
                        }else{
                            self.env.pos.db.notification('danger',_t('Please enter amount below card value.'));
                        }
                    }else{
                        self.env.pos.db.notification('danger',_t('Please enter valid amount.'));
                    }
                }
            }
            async payment_back() {
                if(this.env.pos.get_order().get_orderlines().length != 0) {
                    if(this.env.pos.config.gift_card_product_id[0] && this.env.pos.get_order().get_orderlines()[0].product.id == this.env.pos.config.gift_card_product_id[0]){
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('Confirmation'),
                            body: this.env._t(
                                'Would you like to discard this order?'
                            ),
                        });
                        if (confirmed) {
                            this.env.pos.get_order().destroy({ reason: 'abandon' });
                            posbus.trigger('order-deleted');
                            this.showScreen('ProductScreen');
                        }
                    }else{
                        this.showScreen('ProductScreen');
                    }
                }else{
                    this.showScreen('ProductScreen');
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PaymentScreenInherit);

    return PaymentScreenInherit;
});
