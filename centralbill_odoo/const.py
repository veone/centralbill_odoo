# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Mapping of transaction states to Veonepay status codes.
# See https://www.pronamic.nl/wp-content/uploads/2013/04/BPE-3.0-Gateway-HTML.1.02.pdf for the
# exhaustive list of status codes.

STATUS_CODES_MAPPING = {
    'pending': ('PENDING', 'PROCESSING', 'NEEDS_MERCHANT_VALIDATION'),
    'done': ('COMPLETED',),
    'cancel': ('CANCELED',),
    'refused': ('REFUSED','REVERSED'),
    'error': ('FAILED',),
}