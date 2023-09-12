# -*- coding: utf-8 -*-
{
    'name': "Pagos por el Banco de Venezuela",
    'category': 'eCommerce',
    'summary': 'Migración de la version 14.0 a la 16.0 para los pagos por Banco de Venezuela, ',
    'author': "Leonardo Khaoim",
    'icon': 'payment_bdv_biopago/static/src/img/logo_solo.png',
    'depends': [
        'payment'
    ],
    'data': [
        'views/view_bdv.xml',
        'views/view_template_bdv.xml',
        'data/payment_bdv_data.xml'
    ],
    'installable': True,
    'license': 'OPL-1'
}
