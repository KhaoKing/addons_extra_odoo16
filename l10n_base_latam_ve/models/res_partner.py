from odoo import models, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_vat(self):
        name = []
        type_id = self.l10n_latam_identification_type_id
        vat = self.vat
        if type_id and vat:
            name.append(type_id.name)
            name.append(vat)
        return ' '.join(name)

    # @api.constrains('vat')
    # def _check_vat(self):
    #     for record in self:
    #         if not record.vat:
    #             raise ValidationError(_("The VAT couldn't have null. Check it out"))
    #         if record.vat and len(record.vat) != 9:
    #             raise ValidationError(_("The VAT need 9 numbers. Check it out"))

    # @api.model
    # def create(self, vals):
    #     create_contact = super(ResPartner, self).create(vals)
    #     name = ['J','G','C','V','E','P']
    #     type_vat = self.env['res.partner'].browse(self.l10n_latam_identification_type_id)
    #     if type_vat.search([('l10n_latam_identification_type_id', 'in', name)]):
    #         return create_contact
        
# Recuerda, []= Lista, {} = Diccionario , () = Tupla