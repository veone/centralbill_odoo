# Part of Odoo. See LICENSE file for full copyright and licensing details.

# The codes of the payment methods to activate when Centralbill is activated.
DEFAULT_PAYMENT_METHODS_CODES = [
    'centralbill',
]

# Mapping of payment method codes to Centralbill codes.
PAYMENT_METHODS_MAPPING = {
    'alipay': 'Alipay',
    'apple_pay': 'applepay',
    'bancontact': 'bancontactmrcash',
    'billink': 'Billink',
    'in3': 'Capayable',
    'kbc': 'KBCPaymentButton',
    'bank_reference': 'PayByBank',
    'p24': 'Przelewy24',
    'sepa_direct_debit': 'SepaDirectDebit',
    'sofort': 'sofortueberweisung',
    'tinka': 'Tinka',
    'trustly': 'Trustly',
    'wechat_pay': 'WeChatPay',
    'klarna': 'klarnakp',
    'afterpay_riverty': 'afterpay',
}

# Mapping of transaction states to Centralbill status codes.
# See https://www.pronamic.nl/wp-content/uploads/2013/04/BPE-3.0-Gateway-HTML.1.02.pdf for the
# exhaustive list of status codes.

STATUS_CODES_MAPPING = {
    'pending': ('PENDING', 'PROCESSING', 'NEEDS_MERCHANT_VALIDATION'),
    'done': ('COMPLETED',),
    'cancel': ('CANCELED',),
    'refused': ('REFUSED','REVERSED'),
    'error': ('FAILED',),
}

# The currencies supported by Centralbill, in ISO 4217 format.
# See https://support.centralbill.eu/frequently-asked-questions
# Last seen online: 7 November 2022.
SUPPORTED_CURRENCIES = [
    'XOF'
]
