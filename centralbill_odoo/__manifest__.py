# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Provider: Centralbill',
    'version': '2.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "An ivorian payment provider covering west african countries.",
    'website': 'http://www.veone.net',
    'author': 'VEONE',
    'depends': ['payment'],
    'data': [
        'views/centralbill_odoo_templates.xml',
        'views/payment_provider_views.xml',
        'views/res_config_setting.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'images': [
        'static/description/centralbill.png',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
