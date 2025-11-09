from odoo import api, fields, models


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
    provider_resource_id = fields.Many2one(
        "resource.resource",
        string="Provider Resource",
        ondelete="set null",
        help="Linked resource for booking system",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Create linked resource for providers"""
        users = super().create(vals_list)
        for user in users:
            user._ensure_provider_resource()
        return users

    def write(self, vals):
        """Sync changes to linked resource"""
        result = super().write(vals)
        # Check if provider status changed
        if "provider_type_id" in vals or "name" in vals:
            for user in self:
                user._ensure_provider_resource()
        return result

    def _ensure_provider_resource(self):
        """Ensure provider has a linked resource if they are a provider"""
        self.ensure_one()
        if self.is_provider and not self.provider_resource_id:
            # Create resource for this provider
            resource = self.env["resource.resource"].create(
                {
                    "name": self.name,
                    "resource_type": "user",
                    "user_id": self.id,
                    "active": self.active,
                }
            )
            self.provider_resource_id = resource
        elif self.is_provider and self.provider_resource_id:
            # Update existing resource
            self.provider_resource_id.write(
                {
                    "name": self.name,
                    "active": self.active,
                }
            )
        elif not self.is_provider and self.provider_resource_id:
            # Remove resource if no longer a provider
            self.provider_resource_id.unlink()
            self.provider_resource_id = False
