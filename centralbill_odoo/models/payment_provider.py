# Part of Odoo. See LICENSE file for full copyright and licensing details.

from hashlib import sha256

from odoo import fields, models, _
from odoo.exceptions import ValidationError

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('centralbill', "Centralbill")], ondelete={'centralbill': 'set default'})
    centralbill_app_key = fields.Char(
        string="Application ID", help="The key solely used to identify the website with Centralbill",
        required_if_provider='centralbill')
    centralbill_app_name = fields.Char(
        string="Application Name", help="The Application name solely used to identify the website with Centralbill",
        required_if_provider='centralbill')
    centralbill_secret_key = fields.Char(
        string="Centralbill Secret Key", required_if_provider='centralbill', groups='base.group_system')

    def _centralbill_get_api_url(self):
        """ Return the API URL according to the state.

        Note: self.ensure_one()

        :return: The API URL
        :rtype: str
        """
        self.ensure_one()
        
        if self.state == 'enabled':
            prod_domain = False
            if (self.env["ir.config_parameter"].sudo().get_param("centralbill_odoo.prod_domain")):
                prod_domain = self.env["ir.config_parameter"].sudo().get_param("centralbill_odoo.prod_domain")
            if not prod_domain:
                raise ValidationError(_("Veuillez renseigner l'url de production."))   
            print(prod_domain)
            return prod_domain + '/'
        else:
            dev_domain = False
            if (self.env["ir.config_parameter"].sudo().get_param("centralbill_odoo.dev_domain")):
                dev_domain = self.env["ir.config_parameter"].sudo().get_param("centralbill_odoo.dev_domain")
            if not dev_domain:
                raise ValidationError(_("Veuillez renseigner l'url de production."))
            print(dev_domain)
            return dev_domain + '/'

    def _centralbill_generate_digital_sign(self, values, incoming=True):
        """ Generate the shasign for incoming or outgoing communications.

        :param dict values: The values used to generate the signature
        :param bool incoming: Whether the signature must be generated for an incoming (Centralbill to
                              Odoo) or outgoing (Odoo to Centralbill) communication.
        :return: The shasign
        :rtype: str
        """
        token_str = '%s,%s,%s,%s,%s,%s' % (
            values['application_id'],
            values['invoice_id'],
            values['customer_id'],
            values['total_amount_amount'],
            values['total_amount_currency'],
            values['secret']
        )
        hashed_string = sha256(token_str.encode('utf-8')).hexdigest()
        
        return hashed_string