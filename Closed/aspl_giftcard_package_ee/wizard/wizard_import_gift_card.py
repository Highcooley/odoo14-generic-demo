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

import io
import os
import csv
import base64
import binascii
import tempfile
import xlrd, mmap, xlwt

from odoo import models,fields,api,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class ImportGiftCard(models.TransientModel):
    _name = 'import.gift.card'
    _description = 'Import Gift Card'

    name = fields.Char(string="File Name")
    csv_import_file = fields.Binary("Import csv")

    def csv_validator(self, xml_name):
        name, extension = os.path.splitext(xml_name)
        return True if extension == '.xls' or extension == '.xlsx' else False

    def import_new_gift_card(self):
        # line = keys = ['ID', 'Name', 'Created By', 'Product', 'Created on', 'Issue Date', 'Expiry Date.', 'Expiry Date', 'Original Value', 'Current Value', 'Coupon Barcode', 'Coupon Code Apply Limit', 'POS Order', 'POS Order/Coupon/Coupon Barcode', 'POS Order/Customer', 'POS Order/Cashier', 'POS Order/Coupon/Created on', 'POS Order/Coupon/Expiry Date', 'POS Order/Coupon/Issue Date', 'POS Order/Coupon/Coupon Amount', 'POS Order/Coupon/Maximum amount']
        line = keys = ['Company', 'Gift Card Type', 'Issue Date', 'Expiry Date', 'Original Value', 'Current Value', 'Card No', 'Customer']
        csv_data = base64.b64decode(self.csv_import_file)
        data_file = io.StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter=',')
        file_reader.extend(csv_reader)
        partner_id = False
        for i in range(len(file_reader)):
            field = list(map(str, file_reader[i]))
            values = dict(zip(keys, field))
            if values and i == 0:
                continue
            if values.get('Gift Card Type'):
                card_type_id = self.env['gift.card.type'].search([('name', '=', values.get('Gift Card Type'))])
            if values.get('Company'):
                company_id = self.env['res.company'].search([('name', '=', values.get('Company'))])
            if values.get('Customer'):
                partner_id = self.env['res.partner'].search([('name', '=', values.get('Customer'))])
            issue_date = datetime.strptime(values.get('Issue Date'), '%Y-%m-%d').date()
            if values.get('Original Value') and float(values.get('Original Value')) > 0:
                vals_card = {
                    'card_no': values.get('Card No'),
                    'card_value': values.get('Original Value'),
                    'issue_date': issue_date,
                    'company_id': company_id.id or self.env.company.id,
                    'card_type': card_type_id.id,
                    'state': 'confirm',
                }
                if partner_id:
                    vals_card.update({
                        'customer_id': partner_id.id or False,
                    })
                gift_card_id = self.env['gift.card'].sudo().create(vals_card)
            else:
                gift_card_id = self.env['gift.card'].sudo().create({
                    'card_no': values.get('Card No'),
                    'card_value': 1,
                    'issue_date': issue_date,
                    'customer_id': partner_id.id,
                    'company_id': company_id.id,
                    'card_type': card_type_id.id,
                    'state': 'confirm',
                })
                gift_card_id.sudo().write({
                    'card_value': 0,
                })
            if values.get('Original Value') != values.get('Current Value'):
                amount = 0
                if values.get('Current Value') == 0:
                    amount = values.get('Original Value')
                else:
                    amount = float(values.get('Original Value')) - float(values.get('Current Value'))
                card_use_id = self.env['gift.card.use'].create({
                    'card_id': gift_card_id.id,
                    'amount': amount,
                    'partner_id': gift_card_id.customer_id.id,
                })
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
