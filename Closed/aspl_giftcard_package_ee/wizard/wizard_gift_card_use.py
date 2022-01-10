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

from odoo import models,fields,api,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class UseGiftCard(models.TransientModel):
    _name = 'wizard.use.gift.card'
    _description = 'use gift card wizard'

    partner_id = fields.Many2one("res.partner", string="Partner", default=lambda self: self.env['sale.order'].browse(self.env.context.get('active_id')).partner_id.id)
    gift_card_id = fields.Many2one('gift.card',string="Card Number")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    card_pin = fields.Char(string="Pin", copy=False)
    amount = fields.Float(string="Amount")
    card_balance = fields.Float(string="Card Balance", related="gift_card_id.balance")
    order_balance = fields.Float(string="Order Amount", default=lambda self: self.env['sale.order'].browse(self.env.context.get('active_id')).amount_total)

    def add_line(self):
        if not self.env.company.gc_journal_id:
            raise ValidationError(_('Please Select Gift Card Journal in Current Company'))
        values = []
        active_id = self._context['active_id']
        sale_order = self.env['sale.order'].browse(active_id)
        gift_card_id = self.env['gift.card'].search([('card_no', '=', self.gift_card_id.card_no)])
        if gift_card_id.pin_no == self.card_pin and gift_card_id.card_no == self.gift_card_id.card_no and gift_card_id.customer_id == self.partner_id and self.amount <= self.gift_card_id.balance  and self.amount <= sale_order.amount_total:
            if self.amount <= gift_card_id.card_value:
                gift_dict = {'card_id': gift_card_id.id,
                             'amount':self.amount,
                             'partner_id': self.partner_id.id,
                             'order_id': sale_order.id,
                             'journal_id': self.env.company.gc_journal_id.id,
                             }
                values.append((0, 0, gift_dict))
                sale_order.write({'gift_card_use_ids': values})
            else:
                raise ValidationError(_('Not enough balance.'))
        else:
            if self.amount > self.gift_card_id.balance  or self.amount > sale_order.amount_total:
                raise ValidationError(_('Invalid Amount. Please Enter Valid Amount'))
            else:
                raise ValidationError(_('Invalid PIN.'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: