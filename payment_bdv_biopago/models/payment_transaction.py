import logging
import pprint
import json
import requests

from odoo.http import request
from werkzeug import urls
from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_bdv_biopago import utils as bdv_utils

_logger = logging.getLogger(__name__)

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
        if self.provider_code != 'BDV' or self.operation == 'online_token' and self.operation in ['online_redirect', 'validation']:
            return{
            'transaction_key': bdv_utils.get_bdv_transaction_key(self.provider_id)
            }
        return res
        
    
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
