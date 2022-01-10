odoo.define('aspl_giftcard_package_ee.giftCardCreateScreen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useRef, useState } = owl.hooks;
    var core = require('web.core');
    var _t = core._t;


    class giftCardCreateScreen extends PosComponent {
        guidGenerator() {
            return Math.floor(Math.pow(10, 12-1) + Math.random() * (Math.pow(10, 12) - Math.pow(10, 12-1) - 1));
        }
        expDateCal() {
            var date = new Date();
            if (this.env.pos.company.default_exp_month <= 0) {
                date.setMonth(date.getMonth() + 1);
            }else{
                date.setMonth(date.getMonth() + this.env.pos.company.default_exp_month);
            }
            var new_date = date.getFullYear()+ "/" +(date.getMonth() + 1)+ "/" +date.getDate();
            moment(date).format('MM/DD/yyyy')
            return moment(date).format('MM/DD/YYYY')
        }
        constructor(){
            super(...arguments);
            if (this.env.pos.company.menual_card_number){
                this.state = useState({CardNumber:'', SelectCustomer:'', ExpireDate:this.expDateCal(), Amount:"", SelectCardType:"", Paid:''});
            }else{
                this.state = useState({CardNumber:this.guidGenerator(), SelectCustomer:'', ExpireDate:this.expDateCal(), Amount:"", SelectCardType:"", Paid:''});
            }
            this.card_no = useRef('CardNumber');
            this.select_customer = useRef('SelectCustomer');
            this.text_expire_date = useRef('ExpireDate');
            this.text_amount = useRef('Amount');
            this.SelectCardType = useRef('SelectCardType');
            this.Paid = useRef('Paid');
            this.partner_id = false;
        }
        autoCompletePartner(ev){
            var self = this;
            $(ev.currentTarget).autocomplete({
                source: function(request, response) {
                    self.partner_id = false;
                    var results = $.ui.autocomplete.filter(self.env.pos.db.partner_list, request.term);
                    response(results.slice(0, 7));
                },
                select: function(event, ui) {
                    self.state.SelectCustomer = ui.item.value;
                    self.partner_id = ui.item.id;
                },
            })
        }
        onInputKeyDownNumberValidation(e) {
           if(e.which != 190 && e.which != 110 && e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57) && (e.which < 96 || e.which > 105) && (e.which < 37 || e.which > 40)) {
                e.preventDefault();
           }
        }
        onInputKeyDownAmountValidation(e) {
            if(e.which != 110 && e.which != 8 && e.which != 0 && e.key != this.env.pos.db.decimalSeparator() && e.key != this.env.pos.db.decimalSeparator() && (e.which < 48 || e.which > 57 || e.shiftKey) && (e.which < 96 || e.which > 105) && (e.which < 37 || e.which > 40)) {
                e.preventDefault();
            }
        }
        back() {
            this.trigger('close-temp-screen');
        }
        isCardExist(code){
            return this.rpc({
                model: 'gift.card',
                method: 'search_read',
                domain: [['card_no', '=', code]],
            }, {async: true}).then((result) => {
                if(result && result.length > 0){
                    return true;
                }else{
                    return;
                }
            })
        }
        checkPartnerId(){
            if (!this.partner_id){
                this.state.SelectCustomer = ''
                this.env.pos.db.notification('danger', _t('This Customer does not exist!'));
            }
        }
        async confirm(){
            var SelectedCustomer = $('option[value="'+$('#select_customer').val()+'"]').attr('id')
            if(this.state.CardNumber && this.state.CardNumber.toString().length >= 5){
                let cardExist = await this.isCardExist(this.state.CardNumber);
                if(cardExist !== undefined){
                    this.env.pos.db.notification('danger', _t('Card Number Already Exist!'));
                    return;
                }
            }
            if(!this.state.CardNumber || this.state.CardNumber && this.state.CardNumber.toString().length < 5){
                this.env.pos.db.notification('danger', _t('Card Number Should be 5 Digit!'));
                return;
            }else if(this.state.SelectCustomer == ''){
                this.env.pos.db.notification('danger', _t('Please Select Customer!'));
                return;
            }else if(!SelectedCustomer){
                this.state.SelectCustomer = ''
                this.env.pos.db.notification('danger', _t('This Customer does not exist!'));
                return;
            }if(!this.state.Amount || this.state.Amount == 0){
                this.env.pos.db.notification('danger', _t('Amount Should be greater than 0!'));
                return;
            }else {
                this.props.resolve({confirmed: true,
                                    payload:{card_no: this.state.CardNumber,
                                            customer_id: Number(SelectedCustomer),
                                            expire_date: this.state.ExpireDate,
                                            card_value: this.state.Amount,
                                            card_type: this.state.SelectCardType}
                                            });

                this.trigger('close-temp-screen');
            }
        }
        clickNext() {
            this.confirm();
        }
    }

    giftCardCreateScreen.template = 'giftCardCreateScreen';

    Registries.Component.add(giftCardCreateScreen);

    return giftCardCreateScreen;
});
