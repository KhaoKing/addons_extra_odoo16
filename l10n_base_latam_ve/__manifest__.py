# -*- coding: utf-8 -*-
{
    'name':"Localización LATAM VE",

    'summary': """Add module extra for 'Localization Base Latam'""",

    'description': """
        This module is for can select another way to register a DNI of any person or gobernement entity.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['l10n_latam_base', 'account', 'base'],

    # always loaded
    'data': [
        'data/identification_type.xml',
        'data/l10n_latam.identification.type.csv',
        'views/account_move_view.xml'
    ],
}
