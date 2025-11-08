from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    provider_type_id = fields.Many2one(
        "vet.provider.type",
        string="Provider Type",
        help="The type of provider (Doctor, Tech, Groomer, etc.)",
    )
    is_provider = fields.Boolean(
        string="Is Provider",
        related="provider_type_id.is_provider",
        store=True,
        readonly=True,
        help="Whether this user can provide services to patients",
    )
