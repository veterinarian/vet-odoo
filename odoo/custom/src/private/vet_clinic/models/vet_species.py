from odoo import models, fields


class VetSpecies(models.Model):
    _name = 'vet.species'
    _description = 'Animal Species'
    _order = 'name'

    name = fields.Char(string='Species Name', required=True, translate=True)
    code = fields.Char(string='Code', size=10)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
