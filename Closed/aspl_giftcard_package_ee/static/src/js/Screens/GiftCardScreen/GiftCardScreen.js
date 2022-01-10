odoo.define('aspl_giftcard_package_ee.GiftCardScreen', function(require) {
    'use strict';

    const { debounce } = owl.utils;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    class GiftCardScreen extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('click-extend', () => this.extendExpireDate());
            useListener('click-recharge', () => this.rechargeGiftCard());
            useListener('click-exchange', () => this.ChangeCardGiftCard());
            useListener('click-change-owner', () => this.ChangeCardOwner());
            useListener('search', this._onSearch);
            this.searchDetails = {};
            this.filter = null;
            this._initializeSearchFieldConstants();
            this.state = {
                query: null,
                selectedCard: this.props.gift_card,
                detailIsShown: false,
                showGiftCreate: false,
                showGiftPaymentControlBtn:true,
            }
        }
        async reloadNewGiftCard() {
            var self = this;
            var params = {
                model: 'gift.card',
                method: 'search_read',
                domain: [['is_active', '=', true]],
            }
            rpc.query(params, {async: false}).then(function(result){
                self.env.pos.set('gift_card_order_list', result);
                self.render()
            })
        }
        close(){
            this.showScreen('ProductScreen');
        }
        orderIsEmpty(order) {
            var self = this;
            var lines_ids = []
            if(!order.is_empty()) {
                let lines_ids = _.pluck(order.get_orderlines(), 'id');
                _.each(lines_ids,function(id){
                    order.remove_orderline(order.get_orderline(id));
                });
            }
        }
        async ChangeCardOwner() {
            var self = this;
            const { confirmed, payload: selectedCardOwner } = await this.showPopup('giftCardChangeOwnerPopup', {
                title: this.env._t('Change Gift Card Owner'),
                selectedCard: this.state.selectedCard,
            }); 
            if(confirmed){
                var card_owner = selectedCardOwner;
                var params = {
                    model: 'gift.card',
                    method: 'write_gift_card_owner_from_ui',
                    args: [[Number(this.state.selectedCard.id)], selectedCardOwner],
                }
                rpc.query(params, {async: false}).then(function(result){
                    if (result){
                        self.state.selectedCard.customer_id = result
                    }
                    self.render();
                });
                    
            }
        }
        async ChangeCardGiftCard() {
            var self = this;
            const { confirmed, payload: selectedCard } = await this.showPopup('giftCardExchangePopup', {
                title: this.env._t('Exchange Gift Card'),
                selectedCard: this.state.selectedCard,
            }); 
            if(confirmed){
                var card_number = selectedCard.NewCardNumber;
                var params = {
                    model: 'gift.card',
                    method: 'write_gift_card_from_ui',
                    args: [[Number(this.state.selectedCard.id)], selectedCard.NewCardNumber],
                }
                rpc.query(params, {async: false}).then(function(result){
                    if (result){
                        self.state.selectedCard.card_no = result
                    }
                    self.render();
                });
                this.render();
            }
        }

        async rechargeGiftCard(){
            const { confirmed, payload: selectedCard } = await this.showPopup('giftCardRechargePopup', {
                title: this.env._t('Recharge Card'),
                selectedCard: this.state.selectedCard,
            }); 
            if(confirmed){
                var self = this;
                var order = self.env.pos.get_order();
                var card_details = this.state.selectedCard;
                if(!order.get_client()){
                    order.set_client(self.env.pos.db.get_partner_by_id(card_details.customer_id[0]));
                }
                var recharge_amount = this.env.pos.db.thousandsDecimalChanger(selectedCard.amount);
                if( 0 < Number(recharge_amount) ){
                    var vals = {
                        'recharge_card_id': card_details.id,
                        'recharge_card_no': card_details.card_no,
                        'recharge_card_amount':recharge_amount,
                        'card_customer_id': card_details.customer_id[0] || false,
                        'customer_name': card_details.customer_id[1],
                        'total_card_amount':recharge_amount + card_details.card_value,
                        'expire_date': card_details.expire_date,
                    }
                    var get_recharge = order.get_recharge_giftcard();
                    var product = self.env.pos.db.get_product_by_id(self.env.pos.config.gift_card_product_id[0]);
                    if (self.env.pos.config.gift_card_product_id[0]){
                        self.orderIsEmpty(order);
                        order.set_is_rounding(false);
                        order.add_product(product,{
                            price: recharge_amount,
                            extras: {
                                price_manually_set: true,
                            },
                        });
                        order.set_recharge_giftcard(vals);
                        this.showScreen('PaymentScreen',{'showGiftButton': false });
                    }
                }else{
                    self.env.pos.db.notification('danger',_t('Please enter valid amount.'));
                }
            }
        }

        async extendExpireDate() {
            const { confirmed, payload: selectedCard } = await this.showPopup('giftCardEditExpirePopup', {
                title: this.env._t('Extend Expire Date'),
                selectedCard: this.state.selectedCard,
            }); 
            var card_id = this.state.selectedCard.id;
            if (confirmed){
                if(selectedCard.new_expire_date){
                    if(this.state.selectedCard.card_no){
                        var EditCardPromise = new Promise(function(resolve, reject){
                            var params = {
                                model: "gift.card",
                                method: "write",
                                args: [card_id ,{'expire_date': moment(selectedCard.new_expire_date).locale('en').format('YYYY-MM-DD')}]
                            }
                            rpc.query(params, {async: false}).then(function(result){
                                if(result){
                                    resolve(result);
                                }
                            }).catch(function(){
                                reject(self.pos.db.notification('danger',"Connection lost"));
                            });
                        });
                    }else{
                        self.pos.db.notification('danger',_t('Please enter valid card no.'));
                    }
                }else{
                    self.pos.db.notification('danger',_t('Please select date.'));
                }
            }
        }

        clickCard(event) {
            let card = event.detail.card;
            this.state.selectedCard = this.state.selectedCard === card ? null : card;
            this.render();
        }

        back() {
            if(this.state.detailIsShown) {
                this.state.detailIsShown = false;
                this.render();
            } else {
                this.trigger('close-screen');
            }
        }

        orderIsEmpty(order) {
            var self = this;
            var currentOrderLines = order.get_orderlines();
            var lines_ids = []
            if(!order.is_empty()) {
                _.each(currentOrderLines,function(item) {
                    lines_ids.push(item.id);
                });
                _.each(lines_ids,function(id) {
                    order.remove_orderline(order.get_orderline(id));
                });
            }
            
        }

        async createNewGiftCard(event) {
            const { isNewGiftCard } = event.detail;
            const { confirmed,payload } = await this.showTempScreen('giftCardCreateScreen');
            if (confirmed) {
                if (this.env.pos.config.msg_before_card_pay){
                    var customer = this.env.pos.db.get_partner_by_id(Number(payload["customer_id"]))
                    var card_type_name = ''
                    payload["card_value"] = this.env.pos.db.thousandsDecimalChanger(payload["card_value"])
                    payload["expire_date"] = moment(payload["expire_date"]).locale('en').format('YYYY-MM-DD');
                    _.each(this.env.pos.card_type, function(result){
                        if(result['id'] == Number(payload["card_type"])){
                            card_type_name = result['name']
                        }
                    });
                    const { confirmed,getConfirmPayload } = await this.showPopup('giftCardCreatePopupConform', {
                        title: this.env._t('Confirm'),
                        CardNumber: payload["card_no"],
                        SelectCustomer: customer.name,
                        ExpireDate :payload["expire_date"],
                        Amount: payload["card_value"],
                        SelectCardType: card_type_name,
                    });
                    if (confirmed) {
                        var product_id = this.env.pos.config.gift_card_product_id[0];
                        var customer_id = Number(payload["customer_id"]);
                        payload["expire_date"] = moment(payload["expire_date"]).locale('en').format('YYYY-MM-DD');
                        this.env.pos.get_order().set_is_rounding(false);
                        var order = this.env.pos.get_order();
                        var lines = order.get_orderlines();
                        if(lines.length > 0){
                            this.orderIsEmpty(order);
                        }
                        var product = this.env.pos.db.get_product_by_id(product_id);
                        var gift_card = this.env.pos.get_order().set_giftcard(payload);
                        var customer = this.env.pos.db.get_partner_by_id(customer_id);
                        var amount = payload["card_value"];
                        this.env.pos.get_order().set_client(customer);
                        this.env.pos.get_order().add_product(product, {
                            price: amount,
                            extras: {
                                price_manually_set: true,
                            },
                        });
                        this.render();
                        this.state.showGiftPaymentControlBtn = false;
                        this.showScreen('PaymentScreen',{'showGiftButton': false });
                    }
                }else{
                    this.env.pos.get_order().set_is_rounding(false);
                    var order = this.env.pos.get_order();
                    var lines = order.get_orderlines();
                    if(lines.length > 0){
                        this.orderIsEmpty(order);
                    }
                    var product = this.env.pos.db.get_product_by_id(this.env.pos.config.gift_card_product_id[0]);
                    var customer = this.env.pos.db.get_partner_by_id(Number(payload["customer_id"]));
                    payload["card_value"] = this.env.pos.db.thousandsDecimalChanger(payload["card_value"])
                    payload["expire_date"] = moment(payload["expire_date"]).locale('en').format('YYYY-MM-DD');
                    var amount = payload["card_value"];
                    var gift_card = this.env.pos.get_order().set_giftcard(payload);
                    this.env.pos.get_order().set_client(customer);
                    this.env.pos.get_order().add_product(product, {
                        price: amount,
                        extras: {
                            price_manually_set: true,
                        },
                    });
                    this.render();
                    this.showScreen('PaymentScreen');
                }
            }
        }
        get GiftCardList() {
            return this.env.pos.get('gift_card_order_list');
        }
        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }
        get filteredGiftCardList() {
            const filterCheck = (order) => {
                if (this.filter && this.filter !== 'All Gift Card') {
                    const screen = this.env.pos.get('gift_card_order_list');
                    return this.filter === this.constants.screenToStatusMap[screen.name];
                }
                return true;
            };
            const { fieldValue, searchTerm } = this.searchDetails;
            const fieldAccessor = this._searchFields[fieldValue];
            const searchCheck = (order) => {
                if (!fieldAccessor) return true;
                const fieldValue = fieldAccessor(order);
                if (fieldValue === null) return true;
                if (!searchTerm) return true;
                return fieldValue && fieldValue.toString().toLowerCase().includes(searchTerm.toLowerCase());
            };
            const predicate = (order) => {
                return filterCheck(order) && searchCheck(order);
            };
            return this.GiftCardList.filter(predicate);
        }
        get searchBarConfig() {
            return {
                searchFields: this.constants.searchFieldNames,
                filter: { show: true, options: this.filterOptions },
            };
        }
        get filterOptions() {
            return ['All Card'];
        }
        get _searchFields() {
            var fields = {
                'Card Number': (order) => order.card_no,
                'Issue Date(YYYY-MM-DD hh:mm A)': (order) => moment(order.issue_date).locale('en').format('YYYY-MM-DD hh:mm A'),
                'Expire Date(YYYY-MM-DD hh:mm A)': (order) => moment(order.expire_date).locale('en').format('YYYY-MM-DD hh:mm A'),
                 Customer: (order) => order.customer_id[1],
            };
            return fields;
        }
        _initializeSearchFieldConstants() {
            this.constants = {};
            Object.assign(this.constants, {
                searchFieldNames: Object.keys(this._searchFields),
            });
        }
    }
    GiftCardScreen.template = 'GiftCardScreen';

    Registries.Component.add(GiftCardScreen);

    return GiftCardScreen;
});
