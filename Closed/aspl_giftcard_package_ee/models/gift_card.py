# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
import time
import logging
import base64
from base64 import b64encode, b64decode

from odoo import models, fields, api, _
from simplecrypt import encrypt, decrypt
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class GiftCard(models.Model):
    _name = "gift.card"
    _rec_name = "card_no"
    _description = "Gift Card"

    def random_cardno(self):
        # if not self.env.company.menual_card_number:
        return int(time.time())
        # else:
        #     return ""

    card_no = fields.Char(string="Card No", default=random_cardno)
    card_value = fields.Float(string="Amount")
    # customer_id = fields.Many2one('res.partner', string="Customer")
    customer_id = fields.Many2one('res.partner', string="Customer", domain=lambda self: "['|',('company_id', '=', %s), ('company_id', '=', False)]" % self.env.company.id)
    issue_date = fields.Date(string="Issue Date", default=datetime.now().date())
    expire_date = fields.Date(string="Expire Date", compute="_default_expire_date_cal")
    pin_no = fields.Char(string="Pin", copy=False)
    is_active = fields.Boolean('Active', default=True)
    card_type = fields.Many2one('gift.card.type', string="Card Type")
    used_line = fields.One2many('gift.card.use', 'card_id', string="Used Line")
    # recharge_line = fields.One2many('gift.card.recharge', 'card_id', string="Recharge Line", oncascade='delete')
    encrypted_id = fields.Char(string='Encrypted')
    email = fields.Char(string="Email")
    user_name = fields.Char(string="User Name")
    order_id = fields.Many2one("sale.order", string="Order")
    usage_count_sale = fields.Integer(string="Sale Usage", compute="_compute_count_usage")
    usage_count_pos = fields.Integer(string="POS Usage", compute="_compute_count_usage")
    recharge_count = fields.Integer(string="Recharge", compute="_compute_count_usage")
    change_owner_count = fields.Integer(string="Change Owner", compute="_compute_count_usage")
    usage_amount = fields.Float("Amount Used", compute="_compute_balance")
    balance = fields.Float("Balance", compute="_compute_balance")
    recharge_line = fields.One2many('gift.card.recharge', 'card_id', string="Recharge Line")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    menual_card_number = fields.Boolean(related="company_id.menual_card_number")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancelled', 'Cancelled')
        ], readonly=True, copy=False, default='draft')

    _sql_constraints = [
        ('card_no_uniq', 'unique (card_no)', "Gift Card already exists !"),
    ]

    @api.depends('issue_date')
    def _default_expire_date_cal(self):
        for each in self:
            default_month = 1
            if self.env.company.default_exp_month > 0:
                default_month = self.env.company.default_exp_month
            date_after_month =  each.issue_date + relativedelta(months=default_month)
            each.expire_date = date_after_month

    def _compute_count_usage(self):
        for each in self:
            each.usage_count_sale = self.env['gift.card.use'].search_count([('card_id','=',each.id), ('pos_order_id', '=', False)])
            each.usage_count_pos = self.env['gift.card.use'].search_count([('card_id','=',each.id), ('order_id', '=', False)])
            each.recharge_count = self.env['gift.card.recharge'].search_count([('card_id','=',each.id)])
            each.change_owner_count = self.env['gift.owner.history'].search_count([('card_id','=',each.id)])

    def _compute_balance(self):
        for each in self:
            for line in each.used_line:
                each.usage_amount += line.amount
            each.balance = each.card_value - each.usage_amount

    @api.model
    def create(self, vals):
        # if vals.get('card_value') > 0:
        res = super(GiftCard, self).create(vals)
        MASTER_KEY = "Some-long-base-key-to-use-as-encyrption-key"
        message = str(res['id'])
        cipher = encrypt(MASTER_KEY, message)
        encoded_cipher = b64encode(cipher)
        res['encrypted_id'] = encoded_cipher
        template_id = self.env['ir.model.data'].get_object_reference('aspl_giftcard_package_ee',
                                                                     'email_template__buy_card')
        if template_id and template_id[1]:
            template_obj = self.env['mail.template'].browse(template_id[1])
            template_obj.send_mail(res.id, force_send=True)
        return res
        # else:
        #     raise ValidationError(_('Card Amount should be greater than 0'))
        # return res

    def gift_card_usage_sale(self):
        return {
            'name': _('Sale Gift Card Use'),
            'view_mode': 'tree',
            'res_model': 'gift.card.use',
            'type': 'ir.actions.act_window',
            'domain': [('card_id','=',self.id), ('pos_order_id', '=', False)],
            'target': 'current',
        }

    def gift_card_owner_change_history(self):
        return {
            'name': _('Gift Card Owner History'),
            'view_mode': 'tree',
            'res_model': 'gift.owner.history',
            'type': 'ir.actions.act_window',
            'domain': [('card_id','=',self.id)],
            'target': 'current',
        }

    def gift_card_usage_pos(self):
        return {
            'name': _('POS Gift Card Use'),
            'view_mode': 'tree',
            'res_model': 'gift.card.use',
            'type': 'ir.actions.act_window',
            'domain': [('card_id','=',self.id), ('order_id', '=', False)],
            'target': 'current',
        }

    def gift_card_recharge(self):
        return {
            'name': _('Gift Card Recharge'),
            'view_mode': 'tree',
            'res_model': 'gift.card.recharge',
            'type': 'ir.actions.act_window',
            'domain': [('card_id','=',self.id)],
            'target': 'current',
        }

    # def assing_payment(self):
    #     if self.customer_id and self.card_value > 0:
    #         order_vals = {
    #             'partner_id': self.customer_id.id,
    #             'order_line': [(0, 0, {
    #                 'name':'New Gift Card ',
    #                 'product_id': self.env.company.gift_card_product_id.id,
    #                 'product_uom_qty': 1,
    #                 'qty_delivered': 1,
    #                 'price_unit': self.card_value})]
    #         }
    #         sale_order_id = self.env['sale.order'].create(order_vals)
    #         sale_order_id.action_confirm()
    #         invoice_id = sale_order_id._create_invoices()
    #         invoice_id.action_post()
    #         payment_vals = {
    #             'payment_type': 'inbound',
    #             'partner_type': 'customer',
    #             'partner_id': invoice_id.partner_id.id,
    #             'amount': self.card_value,
    #             'ref': invoice_id.name,
    #             'currency_id': invoice_id.currency_id.id,
    #             'date': datetime.today(),
    #             'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
    #         }
    #         payment_id = self.env['account.payment'].sudo().create(payment_vals)
    #         payment_id.sudo().action_post()
    #         move_line_ids = self.env['account.move.line'].search([('payment_id', '=', payment_id.id),
    #                                                           ('account_id', '=', payment_id.partner_id.property_account_receivable_id.id)])
    #         invoice_id.js_assign_outstanding_line(move_line_ids.id)
    #         self.state = 'confirm'
    #     else:
    #         raise ValidationError(_('Gift Card amount is more than 0.'))
        
    def cancel_card(self):
        self.state = 'cancelled'

    @api.model
    def _send_mail_balance_and_expired_coupon(self, expired=False, balance=False):
        today = fields.Date.today()
        this_week_end_date = fields.Date.to_string(fields.Date.from_string(today) + datetime.timedelta(days=7))
        gift_card_ids = self.search([('expire_date', '=', this_week_end_date)])
        template_id = self.env['ir.model.data'].get_object_reference('aspl_giftcard_package_ee',
                                                                     'email_template_for_coupon_expire_7')
        balance_template_id = self.env['ir.model.data'].get_object_reference('aspl_giftcard_package_ee',
                                                                             'email_template_regarding_balance1')
        if expired:
            if template_id and template_id[1]:
                for gift_card in gift_card_ids:
                    try:
                        template_obj1 = self.env['mail.template'].browse(template_id[1])
                        template_obj1.send_mail(gift_card.id, force_send=True, raise_exception=False)
                    except Exception as e:
                        _logger.error('Unable to send email for order %s', e)
        if balance:
            if balance_template_id and balance_template_id[1]:
                for gift_card in self.search([]):
                    try:
                        template_obj2 = self.env['mail.template'].browse(balance_template_id[1])
                        template_obj2.send_mail(gift_card.id, force_send=True, raise_exception=False)
                    except Exception as e:
                        _logger.error('Unable to send email for order %s', e)

    def write_gift_card_from_ui(self, new_card_no):
        old_card_no = self.card_no
        self.write({'card_no': new_card_no})
        self.env['gift.card.exchange.history'].create({
            'old_card_no': old_card_no, 'new_card_no': new_card_no,
            'customer_id': self.customer_id.id
        })
        try:
            template_id = self.env['ir.model.data'].get_object_reference('aspl_giftcard_package_ee',
                                                                         'email_template_exchange_number')
            if template_id and template_id[1]:
                template_obj = self.env['mail.template'].browse(template_id[1])
                template_obj.send_mail(self.id, force_send=True, raise_exception=False)
        except Exception as e:
            _logger.error('Unable to send email for order %s', e)
        return new_card_no

    def write_gift_card_owner_from_ui(self, new_owner_id):
        history_vals = {
            'customer_id': self.customer_id.id,
            'card_id': self.id,
            'new_customer_id': int(new_owner_id.get('new_owner')),
            'user_id': self.env.user.id,
            'card_amount': self.balance,
        }
        self.env['gift.owner.history'].create(history_vals)
        self.customer_id = int(new_owner_id.get('new_owner'))
        return [self.customer_id.id, self.customer_id.name]


class GiftCardUse(models.Model):
    _name = 'gift.card.use'
    _description = "Gift Card Use"

    card_id = fields.Many2one('gift.card', string="Card", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer")
    order_id = fields.Many2one("sale.order", string="Sale Order")
    pos_order_id = fields.Many2one("pos.order", string="POS Order")
    order_date = fields.Date(string="Order Date")
    amount = fields.Float(string="Amount")
    journal_id = fields.Many2one('account.journal', 'Journal')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        res = super(GiftCardUse, self).create(vals)
        if res.pos_order_id:
            try:
                template_id = self.env['ir.model.data'].get_object_reference('aspl_giftcard_package_ee', 'email_template_regarding_card_use')
                if template_id and template_id[1]:
                    template_obj = self.env['mail.template'].browse(template_id[1])
                    template_obj.send_mail(res.id, force_send=True, raise_exception=False)
            except Exception as e:
                _logger.error('Unable to send email for order %s', e)
        return res


class GiftOwnerHistory(models.Model):
    _name = 'gift.owner.history'
    _description = 'Used to Store Gift Card Owner History.'
    _order = 'id desc'

    card_id = fields.Many2one('gift.card', string="Card")
    customer_id = fields.Many2one('res.partner', string="Customer")
    new_customer_id = fields.Many2one('res.partner', string="New Customer")
    user_id = fields.Many2one('res.users', string="User")
    card_amount = fields.Float(string="Amount")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)


class GiftCardRecharge(models.Model):
    _name = 'gift.card.recharge'
    _rec_name = 'amount'
    _description = 'Used to Store Gift Card Recharge History.'
    _order = 'id desc'

    card_id = fields.Many2one('gift.card', string="Card")
    customer_id = fields.Many2one('res.partner', string="Customer")
    recharge_date = fields.Date(string="Recharge Date")
    user_id = fields.Many2one('res.users', string="User")
    amount = fields.Float(string="amount")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        res = super(GiftCardRecharge, self).create(vals)
        template_id = self.env['ir.model.data'].get_object_reference('aspl_giftcard_package_ee',
                                                                     'email_template_recharge_card')
        if template_id and template_id[1]:
            template_obj = self.env['mail.template'].browse(template_id[1])
            template_obj.send_mail(res.id, force_send=True)

        return res

class GiftCardType(models.Model):
    _name = 'gift.card.type'
    _rec_name = 'name'
    _description = 'Used to Store Gift Card Type.'

    name = fields.Char(string="Name")
    code = fields.Char(string=" Code")


class GiftCardExchangeHistory(models.Model):
    _name = 'gift.card.exchange.history'
    _description = 'Used to Store Gift Card Exchange History.'

    customer_id = fields.Many2one('res.partner', string="Customer")
    old_card_no = fields.Char(string="Old Card No.", readonly=True)
    new_card_no = fields.Char(string="New Card No.", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)


class GiftCardValue(models.Model):
    _name = 'gift.card.value'
    _description = "Gift Card Value"

    active = fields.Boolean(string="Active", default=True)
    amount = fields.Float(string="Amount")
    sequence = fields.Integer(string="Sequence")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
