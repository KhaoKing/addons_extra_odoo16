# -*- coding: utf-8 -*-
{
    'name': "Banesco Pagos",
    'category': 'Accounting/Payment Providers',
    'summary': 'Método de pago mediante Banesco Pagos',
    'author': "Leonardo Khaoim",
    'icon': 'payment_banesco/static/description/logo.png',
    'depends': ['base_setup',
                'payment'],
    'data': [
        'views/views_banesco.xml',
        'data/banesco_template_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_banesco/static/src/js/loading.js',
            'payment_banesco/static/src/js/banesco_original.js',
            'payment_banesco/static/src/js/banesco.js',

        ],
    },
    'license': 'OPL-1'
}