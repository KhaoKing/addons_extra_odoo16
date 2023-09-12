# -*- coding: utf-8 -*-
{
    'name': "Banesco Pagos",
    'category': 'Accounting/Payment Providers',
    'summary': 'Método de pago mediante Banesco Pagos',
    'author': "Leonardo Khaoim",
    'icon': 'payment_banesco/static/description/logo.png',
    'depends': ['payment'],
    'data': [
        'views/views_banesco.xml',
        # 'views/payment_stripe_templates.xml',
        # 'views/payment_templates.xml',  # Only load the SDK on pages with a payment form.

        'data/banesco_template_data.xml',  # Depends on views/payment_stripe_templates.xml
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_banesco/static/src/js/banesco.js',
            'payment_banesco/static/src/js/banescOptions.js',
            'payment_banesco/static/src/js/loading.js',
        ],
    },
    'license': 'OPL-1'
}