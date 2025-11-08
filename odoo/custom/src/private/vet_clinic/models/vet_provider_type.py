from odoo import fields, models


class VetProviderType(models.Model):
    _name = "vet.provider.type"
    _description = "Veterinary Provider Type"
    _order = "sequence, name"

    name = fields.Char(string="Type Name", required=True, translate=True)
    sequence = fields.Integer(string="Sequence", default=10)
    is_provider = fields.Boolean(
        string="Is Provider",
        default=False,
        help=(
            "Check this if this type can provide services "
            "(e.g., Doctor, Tech, Groomer)"
        ),
    )
    active = fields.Boolean(string="Active", default=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ("name_unique", "unique(name)", "Provider type name must be unique!")
    ]
