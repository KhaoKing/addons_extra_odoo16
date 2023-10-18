# -*- coding: utf-8 -*
import odoo.api as api
from odoo.api import SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})  
    rule = env['ir.rule'].search([('name', '=', 'res.partner.rule.private.employee')])
    rule.write({'active': False})

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rule = env['ir.rule'].search([('name', '=', 'res.partner.rule.private.employee')])
    rule['active'] = True