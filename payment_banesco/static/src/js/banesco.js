/** @odoo-module */

import checkoutForm from 'payment.checkout_form';
import manageForm from 'payment.manage_form';


const BanescoPayment = {
    /**
     * 
     *
     * @override method from payment.payment_form_mixin
     * @private
     * @param {string} code - The code of the payment option
     * @param {number} providerId - The id of the payment option handling the transaction
     * @param {object} processingValues - The processing values of the transaction
     * @return {object}
     */
    _processRedirectPayment: function (code, providerId, processingValues) { 
        const BanescoApi = require('tax_customer.receiptPaymentBanesco');
        if (code !== 'banesco') {
            return this._super(...arguments);
        }
        //Valores que se le pasan a la funcion para su funcionamiento//
        let apikey = processingValues.banesco_API_key
        let valor1 = ""; //---- cedula del pagador
        let valor2 = processingValues.amount //---- monto
        let valor3 = "mundo"; //---- Campo dinámico
        let valor4 = processingValues.reference; //---- ID de la transacción
        let valor5 = processingValues.reference+'fecha'; //---- Descripción o concepto del trámite
        // Este valor será proporcionado por el banco junto con el ApiKey
        // let secret = processingValues.banesco_secret_key;
        // let firmar = apikey+valor1+valor2+valor3+valor4;
        //  convercion de la firma Solicitada//
        let firma = processingValues.sign
        var params = "?valor1=" + valor1;
        params += "&valor2=" + valor2;
        params += "&valor3=" + valor3;
        params += "&valor4=" + valor4;
        params += "&valor5=" + valor5;
        params += "&apikey=" + apikey;
        params += "&firma=" + firma;
        var url="https://qa-botondepago.banescopagos.com";
        // ----------------------------------------------------------------//
        // BanescoApi.Banesco_boton(url, valor1, valor2, valor4, valor5, valor5, apikey, firma, '')
        BanescoApi.Banesco_open_win(url, 
                                    valor1, 
                                    valor2, 
                                    valor4, 
                                    valor5, 
                                    valor5, 
                                    apikey, 
                                    firma, 
                                    1)
        // Banesco_open_win(url, cedula, monto, idtramite, comprobante, concepto, apikey, firma, tipo)
        // location.href  = href;
        //-----------------------------------//
        
        // async function hmacSha256(message, secret) {
        //     // codificar como UTF-8
        //     const msgBuffer = new TextEncoder().encode(message);
        //     const keyBuffer = new TextEncoder().encode(secret);
        //     // importar la clave secreta
        //     const key = await crypto.subtle.importKey('raw', keyBuffer, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
        //     // encriptar el mensaje
        //     const signature = await crypto.subtle.sign('HMAC', key, msgBuffer);
        //     // convertir ArrayBuffer a Array
        //     const hashArray = Array.from(new Uint8Array(signature));
        //     // convertir bytes a cadena hexadecimal
        //     const hashHex = hashArray.map(b => ('00' + b.toString(16)).slice(-2)).join('');
        //     return hashHex;}
    },
};

checkoutForm.include(BanescoPayment);
manageForm.include(BanescoPayment);
