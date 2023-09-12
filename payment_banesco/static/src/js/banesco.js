/** @odoo-module */

import checkoutForm from 'payment.checkout_form';
import manageForm from 'payment.manage_form';
import { BanescOptions } from '@payment_banesco/js/banescOptions';

const BanescoMixin = {

    /**
     * Redirect the customer to Stripe hosted payment page.
     *
     * @override method from payment.payment_form_mixin
     * @private
     * @param {string} code - The code of the payment option
     * @param {number} paymentOptionId - The id of the payment option handling the transaction
     * @param {object} processingValues - The processing values of the transaction
     * @return {undefined}
     */
    _processRedirectPayment: function (code, paymentOptionId, processingValues) {
        console.log (processingValues)
        console.log (processingValues)
        console.log (processingValues)
        if (code !== 'banesco') {
            return this._super(...arguments);
        }
        const banescoJS = BanescOpt(
            processingValues['banesco_API_key'],
            // Instantiate the StripeOptions class to allow patching the method and add options.
            new BanescOptions()._prepareBanescOptions(processingValues),
        );
        banescoJS.redirectToCheckout({
            sessionId: processingValues['session_id']
        })
        ;
    },
};

checkoutForm.include(BanescoMixin);
manageForm.include(BanescoMixin);
