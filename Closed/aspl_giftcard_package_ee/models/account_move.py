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

from odoo import models, fields, api, _
import json
from odoo.tools import float_is_zero
from datetime import datetime


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def reconcile(self):
        res = super(AccountMoveLine, self).reconcile()
        move_id = self.mapped('move_id').filtered(lambda move: move.payment_state in ('paid', 'in_payment'))
        gift_card_line_id = move_id.invoice_line_ids.filtered(lambda line: line.product_id.id == self.env.company.gift_card_product_id.id)
        if gift_card_line_id and move_id.new_gift_card_id and move_id.new_gift_card_id.state == 'draft':
            move_id.new_gift_card_id.state = 'confirm'
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    new_gift_card_id = fields.Many2one('gift.card',string="Gift Card")
    # is_paid_gift_card = fields.Boolean("Is Paid Gift Card")
    is_paid_gift_card = fields.Boolean("Is Paid Gift Card", compute="_confirm_gift_card_partial_payment")

    @api.depends('invoice_line_ids', 'new_gift_card_id')
    def _confirm_gift_card_partial_payment(self):
        gift_card_line_id = self.invoice_line_ids.filtered(lambda line: line.product_id.id == self.env.company.gift_card_product_id.id)
        paid_amount = self.amount_total - self.amount_residual
        if gift_card_line_id and self.new_gift_card_id and self.new_gift_card_id.state == 'draft' and self.amount_residual > 0 and paid_amount >= gift_card_line_id.price_subtotal:
            self.is_paid_gift_card = True
        else:
            self.is_paid_gift_card = False

    def action_register_gift_card_payment(self):
        if self.new_gift_card_id and self.new_gift_card_id.state == 'draft':
            self.new_gift_card_id.state = 'confirm'

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        payment_obj = self.env['account.payment']
        sale_order_id = self.env['sale.order'].search([('name', '=', vals.get("invoice_origin"))])
        company_journal_id = self.env.company.gc_journal_id
        if sale_order_id and sale_order_id.gift_card_use_ids and company_journal_id:
            for line in sale_order_id.gift_card_use_ids:
                values = {
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': res.partner_id.id,
                    'amount': line.amount,
                    'ref': line.card_id.card_no,
                    'currency_id': res.company_id.currency_id.id,
                    'reference_invoice_id': res.id,
                    'journal_id': company_journal_id.id,
                    'date': datetime.today(),
                    'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                }
                payment = payment_obj.sudo().create(values)
                payment.sudo().action_post()
        return res

    def action_post(self):
        res = super(AccountMove, self).action_post()
        payment_ids = self.env['account.payment'].search([('reference_invoice_id', '=', self.id)])
        for line in payment_ids:
            move_line = self.env['account.move.line'].search([('payment_id', '=', line.id),
                                                              ('account_id', '=',
                                                               line.partner_id.property_account_receivable_id.id)])
            self.js_assign_outstanding_line(move_line.id)
        return res


class AccountPayment(models.Model):
    _inherit = "account.payment"

    reference_invoice_id = fields.Many2one("account.move", string="Reference Invoice")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
