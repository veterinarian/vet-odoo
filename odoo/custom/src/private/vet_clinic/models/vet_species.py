from odoo import fields, models


class VetSpecies(models.Model):
    _name = "vet.species"
    _description = "Animal Species"
    _order = "name"

    name = fields.Char(string="Species Name", required=True, translate=True)
    code = fields.Char(size=10)
    description = fields.Text()
    active = fields.Boolean(default=True)
