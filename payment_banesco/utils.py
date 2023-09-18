# Part of Odoo. See LICENSE file for full copyright and licensing details.

def get_API_key(provider_sudo):
    return provider_sudo.banesco_API_key


def get_secret_key(provider_sudo):
    return provider_sudo.banesco_secret_key

