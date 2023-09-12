# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    street = fields.Char(readonly=True, string='Street')
    street2 = fields.Char(readonly=True, string='Street 2')
    phone_number = fields.Char(readonly=True, string='Phone')
    country_id = fields.Many2one('res.country',readonly=True, string='Country')
    vat = fields.Char(readonly=True, string='VAT')
    partner_name = fields.Char(string='Client', readonly=True)

    def _get_info(self):
        partner_id = self.partner_id
        if partner_id:
            street = self.partner_id.street
            vat = self.partner_id._get_vat() 
            print (street)
            print (vat)   
            if not street or not vat:
                raise UserError (_("Ops! This client doesn't have an Address or VAT defined. Check the information of Contact"))
            self.write({
                'partner_name': partner_id.name,
                'country_id': self.partner_id.country_id.id if self.partner_id.country_id else False,
                'street': street,
                'street2': self.partner_id.street2,
                'phone_number': self.partner_id.phone,
                'vat': vat,
            })

    @api.onchange('partner_id')
    def _onchange_contact_info(self):
        self._get_info()

    @api.model
    def create (self, vals):
        create_onchange = super(AccountMove, self).create(vals)
        create_onchange._onchange_contact_info()
        return create_onchange