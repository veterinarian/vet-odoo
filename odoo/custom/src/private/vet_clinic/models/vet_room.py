from odoo import fields, models


class VetRoom(models.Model):
    _name = "vet.room"
    _description = "Veterinary Room"
    _order = "sequence, name"

    name = fields.Char(string="Room Name", required=True, translate=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
    description = fields.Text(string="Description")

    _sql_constraints = [("name_unique", "unique(name)", "Room name must be unique!")]
