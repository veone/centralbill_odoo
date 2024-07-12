import re

from odoo import models, fields, api, _

from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dev_domain = fields.Char(string="Domaine Dev", config_parameter='centralbill_odoo.dev_domain')
    prod_domain = fields.Char(string="Domaine Prod", config_parameter='centralbill_odoo.prod_domain')
    
    @api.constrains("dev_domain", "prod_domain")
    def _check_domain(self):
        for s in self:
            url_regex = r'^https:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
            if s.dev_domain:
                if not re.match(url_regex, s.dev_domain):
                    raise ValidationError(_("Veuillez mettre l'URL de développement en https."))
            
            if s.prod_domain:
                if not re.match(url_regex, s.prod_domain):
                    raise ValidationError(_("Veuillez mettre l'URL de production en https."))