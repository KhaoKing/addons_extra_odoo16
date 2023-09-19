/** @odoo-module */

import checkoutForm from 'payment.checkout_form';
import manageForm from 'payment.manage_form';

const BanescoApi = require('tax_customer.receiptPaymentBanesco');

const Banesco_payment = {
    /**
     * 
     *
     * @override method from payment.payment_form_mixin
     * @private
     * @param {string} code - The code of the payment option
     * @param {number} providerCode- The id of the payment option handling the transaction
     * @param {object} processingValues - The processing values of the transaction
     * @return {object}
     */
    _processRedirectPayment: function (code, providerCode, processingValues) { 
        
        if (code == 'banesco') {
            let apikey = processingValues.banesco_API_key; //Api_Key, generada por el banco. (Campo REQUERIDO)
            let valor1 = ''; //Cédula del pagador, se envia vacio, por si el valor de Odoo no coincide con la cedula del pagador. (Campo OPCIONAL)
            let valor2 = processingValues.amount; //Monto (Campo REQUERIDO)
            let valor3 = ''; //Campo Dinamico, es un vacio. (Campo OPCIONAL)
            let valor4 = processingValues.reference; //ID de la transacción
            let valor5 = ''; //Descripción o concepto del trámite
            let firma = processingValues.sign //Firma, la cual esta siendo hecha en el Backend.
            var url="https://qa-botondepago.banescopagos.com";
            // ----------------------------------------------------------------//
            // BanescoApi.Banesco_boton(url, valor1, valor2, valor4, valor5, valor5, apikey, firma, '')
            BanescoApi.Banesco_open_win(url, 
                                        valor1, 
                                        valor2, 
                                        valor4, 
                                        valor5, 
                                        valor3, 
                                        apikey, 
                                        firma, 
                                        1);
        }
        //Valores que se le pasan a la funcion para su funcionamiento//
        
        //Recuerda que los valores, falta corregir como enviarlos correctamente.
        //-----------------------------------//
    },
};
    checkoutForm.include(Banesco_payment);
    manageForm.include(Banesco_payment);
