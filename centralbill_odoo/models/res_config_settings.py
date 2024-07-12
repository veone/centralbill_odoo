import re    
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dev_domain = fields.Char(string="Domaine Dev")
    prod_domain = fields.Char(string="Domaine Prod")
    
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

    def set_values(self):
        "Set config values"
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].set_param('centralbill_odoo.dev_domain', self.dev_domain)
        self.env['ir.config_parameter'].set_param('centralbill_odoo.prod_domain', self.prod_domain)

    @api.model
    def get_values(self):
        "Get config values"
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(dev_domain=params.get_param('centralbill_odoo.dev_domain'))
        res.update(prod_domain=params.get_param('centralbill_odoo.prod_domain'))
    
        return res