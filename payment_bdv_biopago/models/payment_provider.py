import logging
import uuid
import json
import requests

from werkzeug.urls import url_encode, url_join, url_parse
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.http import request
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

error_codes = {
    0:'Peticion procesada con éxito.',
    2:'Letra de cédula inválida.',
    3:'Número de cédula inválido.',
    4:'Moneda inválido.',
    5:'Título inválido.',
    6:'Código de referencia inválido.',
    7:'Monto inválido.',
    8:'Se supero la cantidad máxima de sms solicitados.',
    9:'Pago no encontrado.',
    12:'Fecha actual menor a la fecha de la transacción.',
    13:'Fecha de pago expiró.',
    14:'Instrumento inválido.',
    15:'Error financiero.',
    16:'Máximo número de intentos sobre el mismo token excedido.',
    17:'Token de autenticación inválido.',
    18:'Número de teléfono inválido.',
    19:'Código de seguridad inválido.',
    20:'Número de tarjeta inválido.',
    21:'Fecha de vencimiento inválida.',
    22:'Token sms expiró.',
    23:'El campo Descripcion es muy largo.',
    24:'Email incorrecto.',
    25:'No se encuenra la entidad involucrada.',
    26:'No se encontró el SMS.',
    27:'No se encontró metodo de pago.',
    29:'Error enviando el token para confirmar el pago.',
    30:'No se encuentra el grupo de pago.',
    31:'Método de autenticación inexistente.',
    32:'Transacción no encontrada.',
    34:'Token no está disponible.',
    99:'Error desconocido.',
}

class PaymentProvider(models.Model):
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

    def _get_bdv_signature_key(self):
        """ Return the publishable key of the provider.

        This getter allows fetching the publishable key from a QWeb template and through Stripe's
        utils.

        Note: `self.ensure_one()

        :return: The publishable key.
        :rtype: str
        """
        self.ensure_one()

        return bdv_utils.get_bdv_signature_key(self.sudo())