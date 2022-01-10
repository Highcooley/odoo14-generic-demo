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
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
from datetime import datetime


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    gift_card_journal = fields.Boolean("Is Gift Card", copy=False)
    payment_debit_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        help="Incoming payments entries triggered by invoices/refunds will be posted on the Outstanding Receipts Account "
             "and displayed as blue lines in the bank reconciliation widget. During the reconciliation process, concerned "
             "transactions will be reconciled with entries on the Outstanding Receipts Account instead of the "
             "receivable account.", string='Outstanding Receipts Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                             ('user_type_id.type', 'not in', ('receivable', 'payable')), \
                             '|', ('user_type_id', '=', %s), ('id', 'in', [default_account_id, %s])]" % (self.env.ref('account.data_account_type_current_assets').id, self.env.company.gift_card_account_id.id))
    payment_credit_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        help="Outgoing payments entries triggered by bills/credit notes will be posted on the Outstanding Payments Account "
             "and displayed as blue lines in the bank reconciliation widget. During the reconciliation process, concerned "
             "transactions will be reconciled with entries on the Outstanding Payments Account instead of the "
             "payable account.", string='Outstanding Payments Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                             ('user_type_id.type', 'not in', ('receivable', 'payable')), \
                             '|', ('user_type_id', '=', %s), ('id', 'in', [default_account_id, %s])]" % (self.env.ref('account.data_account_type_current_assets').id, self.env.company.gift_card_account_id.id))

    @api.onchange('gift_card_journal')
    def _onchange_gift_card_journal(self):
        if self.gift_card_journal:
            gift_card_journal_id = self.search_count([('company_id', '=', self.company_id.id), ('gift_card_journal', '=', True)])
            if gift_card_journal_id > 0:
                self.gift_card_journal = False
                raise ValidationError(_('Gift Card journal already exist for this company.'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
