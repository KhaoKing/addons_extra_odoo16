import logging
import hmac
import hashlib
import time

from werkzeug import urls

from odoo import _, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment_banesco import utils as banesco_utils
from odoo.addons.payment_banesco.const import TRANSACTION_STATUS_MAPPING




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
                'sign': signature
            }
        

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of `payment` to find the transaction based on Mercado Pago data.

        :param str provider_code: The code of the provider that handled the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction if found.
        :rtype: recordset of `payment.transaction`
        :raise ValidationError: If inconsistent data were received.
        :raise ValidationError: If the data match no transaction.
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'banesco' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        if not reference:
            raise ValidationError("Banesco: " + _("Received data with missing reference."))

        tx = self.search([("reference", "=", reference),('provider_code', '=', 'banesco')])
        if not tx:
            raise ValidationError(
                "Banesco: " + _("No transaction found matching reference %s.", reference)
            )  
        return tx
    
    def _process_notification_data(self, notification_data):
        """ Override of `payment` to process the transaction based on Mercado Pago data.

        Note: self.ensure_one() from `_process_notification_data`

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data were received.
        """
        self.ensure_one()
        super()._process_notification_data(notification_data)
        if self.provider_code != 'banesco':
            return

        payment_status = notification_data.get('status')
        if not payment_status:
            raise ValidationError("Banesco: " + _("Received data with missing payment status."))
        # self.provider_reference = payment_status

        '''
        Esto lo hace el banco, creo que es la URL por donde te enviará la informacion
        # Verify the notification data.
        # verified_payment_data = self.provider_id._mercado_pago_make_request(
        #     f'/v1/payments/{self.provider_reference}', method='GET'
        # )'''

        payment_status = notification_data.get('status')
        if not payment_status:
            raise ValidationError("Banesco: " + _("Received data with missing status."))

        if payment_status in TRANSACTION_STATUS_MAPPING ['done']:
            self._set_done()
        elif payment_status in TRANSACTION_STATUS_MAPPING ['error']:
            self._set_pending()
        elif payment_status in TRANSACTION_STATUS_MAPPING ['canceled']:
            self._set_canceled()
        else:  # Classify unsupported payment status as the `error` tx state.
            _logger.warning(
                "Received data for transaction with reference %s with invalid payment status: %s",
                self.reference, payment_status
            )
            self._set_error(
                "Banesco: " + _("Received data with invalid status: %s", payment_status)
            )