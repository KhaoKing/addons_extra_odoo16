# coding: utf-8
from werkzeug import urls
from odoo.http import request
import hashlib
import hmac
import logging
import time
import requests
import json
from unicodedata import normalize
from odoo.addons.payment import utils as payment_utils
from odoo import _, fields, models
from odoo.addons.payment.models.payment_provider import ValidationError
from odoo.tools.float_utils import float_compare, float_repr
from odoo.exceptions import UserError, ValidationError

def _get_token(id,key,url):
    token = False
    data = {
        'grant_type':'client_credentials',
        'client_id':id,
        'client_secret':key,
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*'
        }
    try:
        res = requests.post(url, data, timeout=60)
        token = json.loads(res.content)['access_token']
    except requests.exceptions.Timeout:
        raise UserError(_('Timeout: el servidor no ha respondido en 60s'))
    except (ValueError, requests.exceptions.ConnectionError):
        raise UserError(_('Servidor inaccesible, inténtelo más tarde'))
    return token

res_code = {
    0:'Pendiente',
    1:'Procesado',
    2:'En Proceso',
    3:'Cancelado',
}

    
class BDVPayment(models.Model):
    _inherit = 'payment.provider'
    
    code = fields.Selection(
        selection_add=[('bdv', "BDV")], ondelete={'bdv': 'set default'})
    bdv_transaction_key = fields.Char(
        string='BDV Nombre', required_if_provider='bdv', groups='base.group_system')
    bdv_signature_key = fields.Char(
        string='BDV API Key', required_if_provider='bdv', groups='base.group_system')
    bdv_url_token = fields.Char(
        string='URL Token', required_if_provider='bdv', groups='base.group_system')
    bdv_url_api = fields.Char(
        string='URL API', required_if_provider='bdv', groups='base.group_system')
    
    def venezuela_form_generate_values(self, values):
            self.ensure_one()
            token = _get_token(id=self.bdv_transaction_key,key=self.bdv_signature_key,url=self.bdv_url_token) or False
            vef_currency = self.env.ref('base.VEF')
            phone = values.get('partner_phone','').replace('-','').replace('+58','')
            if len(phone) == 11 and phone[0] == '0':
                phone = phone[1:]
            elif len(phone) != 10:
                raise UserError(_('Formato de Telefono incorrecto.'))
            
            letter = values.get('partner',False).vat[0] if values.get('partner',False).vat[0] in ('v','V','e','E','p','P','j','J','g','G') else False
            if not letter:
                raise UserError(_('Formato de Cedula o Rif incorrecto.'))
            number = values.get('partner',False).vat.replace(' ','').replace('-','')[1:]
            amount = values.get('amount',0)
            if values.get('currency',False):
                amount = values.get('currency',False)._convert(values.get('amount',0), vef_currency, self.env.company, fields.Date.today())
            data = {
                'amount':amount,
                'currency':1,
                'reference':values.get('reference',''),
                'title':values.get('reference','').split('-')[0],
                'description':'Compra realizada a {url} con referencia {ref}'.format(url=request.httprequest.host_url, ref=values.get('reference','').split('-')[0]),
                'email':values.get('partner_email',''),
                'cellphone':phone,
                'urlToReturn':request.httprequest.host_url + 'payment/venezuela/callback'
            }
            if letter.upper() in ('V','E','P'):
                data.update({
                    'letter':letter.upper(),
                    'number':number
                })
            else:
                data.update({
                    'rifLetter':letter.upper(),
                    'rifNumber':number
                })
            headers = {
                'Content-Type': 'application/json',
                'Authorization':'Bearer ' + token,
                'accept': '*/*',
            }

            try:
                res = requests.post(self.bdv_url_api,headers=headers,json=data, timeout=60)
                content = json.loads(res.content)
                response_code = content.get('responseCode') or False
                if response_code == 0:
                    return_url = json.loads(res.content)['urlPayment']
                    payment_id = json.loads(res.content)['paymentId']
                    response_description = json.loads(res.content)['responseDescription']
                else:
                    raise UserError(_(error_codes[response_code]))
            except requests.exceptions.Timeout:
                raise UserError(_('Timeout: el servidor no ha respondido en 60s'))
            except (ValueError, requests.exceptions.ConnectionError):
                raise UserError(_('Servidor inaccesible, inténtelo más tarde'))
            
            values.update({
                'urlToReturn':return_url,
                'payment_id':payment_id,
                'response_description':response_description,
                'token':token,
                })
            tx = self.env['payment.transaction'].sudo().search([('reference','=',values.get('reference'))])
            tx.acquirer_reference = payment_id
            tx.state_message = 'Respuesta de redirección: ' + response_description
            return dict(values)
    
    def venezuela_get_form_action_url(self):
        self.ensure_one()
        return request.httprequest.host_url + 'payment/venezuela/redirect'


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    def _get_specific_processing_values(self, processing_values):
        """ Override of payment to return Stripe-specific processing values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'stripe' or self.operation == 'online_token':
            return res

        if self.operation in ['online_redirect', 'validation']:
            checkout_session = self._stripe_create_checkout_session()
            return {
                'publishable_key': stripe_utils.get_publishable_key(self.provider_id),
                'session_id': checkout_session['id'],
            }
        else:  # Express checkout.
            payment_intent = self._stripe_create_payment_intent()
            self.stripe_payment_intent = payment_intent['id']
            return {
                'client_secret': payment_intent['client_secret'],
            }
    def venezuela_payments_callback(self):
        self.ensure_one()
        token = _get_token(id=self.provider_id.bdv_transaction_key,key=self.provider_id.bdv_signature_key,url=self.provider_id.bdv_url_token) or False
        if not token:
            raise UserError(_('Fallo de comunicación, favor comunicarse con un administrador.'))
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'Bearer ' + token,
            'accept': '*/*',
        }
        try:
            res = requests.get('{url}/{paymentid}'.format(url=self.provider_id.bdv_url_api,paymentid=self.provider_reference),headers=headers, timeout=60)
            status = json.loads(res.content)['status']
            amount = json.loads(res.content)['amount']
            transaction_id = json.loads(res.content)['transactionId']
            if status == 1:
                self._set_transaction_done()
                self.write({
                    'state': 'done',
                    'date': fields.Datetime.now(),
                    'state_message': json.loads(res.content)['responseDescription'],
                })
                self.payment_token_id.active = False
                self._post_process_after_done()
                return status
            else:
                raise UserError(_(res_code[status]))
        except requests.exceptions.Timeout:
            raise UserError(_('Timeout: el servidor no ha respondido en 60s'))
        except (ValueError, requests.exceptions.ConnectionError):
            raise UserError(_('Servidor inaccesible, inténtelo más tarde'))
