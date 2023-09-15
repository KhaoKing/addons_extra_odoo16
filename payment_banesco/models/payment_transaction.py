import logging
import hmac
import hashlib
import time

from werkzeug import urls

from odoo import _, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment_banesco import utils as banesco_utils



_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    def _get_specific_processing_values(self, processing_values):
        '''Esta funcion sobreescribe el metodo original de _get_specific_processing_values,
        proveniente del modulo de Payment_transaction'''
        amount_key = str(self.amount)
        id_reference = self.reference
        field_dinamic = ""
        api_key = banesco_utils.get_API_key(self.provider_id)
        secret_key = banesco_utils.get_secret_key(self.provider_id)

        if self.provider_code == 'banesco' and self.operation in ['online_redirect']:
            '''Si se cumple la condicion puesta arriba, procede a crear una firma, y luego
            retorna los valores al diccionario 'processingValues'''
            sign = (f"{api_key + amount_key + field_dinamic + id_reference}")
            signature = hmac.new(secret_key.encode(), sign.encode(), hashlib.sha256).hexdigest()
            return {
                'banesco_API_key': api_key,
                'banesco_secret_key': secret_key,
                'sign':signature
            }
        

    