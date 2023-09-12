/** @odoo-module */

export class BanescOptions {
    /**
     * Prepare the options to init the Stripe JS Object.
     *
     * This method serves as a hook for modules that would fully implement Stripe Connect.
     *
     * @param {object} processingValues
     * @return {object}
     */
    _prepareBanescOptions(processingValues) {
        return {};
    };
}
