# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Provider: Centralbill',
    'version': '2.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "An Ivorian payment provider.",
    'depends': ['payment'],
    'data': [
        'views/centralbill_odoo_templates.xml',
        'views/payment_provider_views.xml',
        'views/res_config_settings.xml',
        
        'data/payment_icon_data.xml',
        'data/payment_provider_data.xml',
    ],
    'application': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}