from odoo import api, fields, models


class VetRoom(models.Model):
    _name = "vet.room"
    _description = "Veterinary Room"
    _order = "sequence, name"

    name = fields.Char(string="Room Name", required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text()
    resource_id = fields.Many2one(
        "resource.resource",
        string="Resource",
        ondelete="cascade",
        help="Linked resource for booking system",
    )

    _sql_constraints = [("name_unique", "unique(name)", "Room name must be unique!")]

    @api.model_create_multi
    def create(self, vals_list):
        """Create linked resource when creating a room"""
        rooms = super().create(vals_list)
        for room in rooms:
            if not room.resource_id:
                resource = self.env["resource.resource"].create(
                    {
                        "name": room.name,
                        "resource_type": "material",
                        "active": room.active,
                    }
                )
                room.resource_id = resource
        return rooms

    def write(self, vals):
        """Sync changes to linked resource"""
        result = super().write(vals)
        for room in self:
            if room.resource_id:
                resource_vals = {}
                if "name" in vals:
                    resource_vals["name"] = room.name
                if "active" in vals:
                    resource_vals["active"] = room.active
                if resource_vals:
                    room.resource_id.write(resource_vals)
        return result

    def unlink(self):
        """Delete linked resources when deleting rooms"""
        resources = self.mapped("resource_id")
        result = super().unlink()
        resources.unlink()
        return result
