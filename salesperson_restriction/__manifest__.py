# -*- coding: utf-8 -*-
{
    'name': "Salesperson Restriction",
    'summary': """
        Seller restriction. You cannot see other clients if they are not yours.""",
    'author': "Leonardo Khaoim",
    'version': '1.0',
    'depends': ['base', 'sale_management'],
    'data': [
        'security/sale_security.xml'
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}