from odoo import api, fields, models


class VetOwner(models.Model):
    _name = "vet.owner"
    _description = "Pet Owner"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Owner Name", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Related Contact",
        ondelete="restrict",
        help="Linked contact for appointments and portal access",
    )
    email = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    street = fields.Char()
    street2 = fields.Char(string="Street 2")
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string="State")
    zip = fields.Char(string="ZIP")
    country_id = fields.Many2one("res.country", string="Country")

    patient_ids = fields.One2many("vet.patient", "owner_id", string="Patients")
    patient_count = fields.Integer(
        string="Number of Pets", compute="_compute_patient_count"
    )

    notes = fields.Text()
    active = fields.Boolean(default=True)

    @api.depends("patient_ids")
    def _compute_patient_count(self):
        for owner in self:
            owner.patient_count = len(owner.patient_ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Create linked partner for each owner"""
        owners = super().create(vals_list)
        for owner in owners:
            if not owner.partner_id:
                # Create a partner for this owner
                partner = self.env["res.partner"].create(
                    {
                        "name": owner.name,
                        "email": owner.email,
                        "phone": owner.phone,
                        "mobile": owner.mobile,
                        "street": owner.street,
                        "street2": owner.street2,
                        "city": owner.city,
                        "state_id": owner.state_id.id,
                        "zip": owner.zip,
                        "country_id": owner.country_id.id,
                        "comment": f"Pet Owner - {owner.name}",
                    }
                )
                owner.partner_id = partner
        return owners

    def write(self, vals):
        """Sync changes to linked partner"""
        result = super().write(vals)
        for owner in self:
            if owner.partner_id:
                partner_vals = {}
                if "name" in vals:
                    partner_vals["name"] = owner.name
                if "email" in vals:
                    partner_vals["email"] = owner.email
                if "phone" in vals:
                    partner_vals["phone"] = owner.phone
                if "mobile" in vals:
                    partner_vals["mobile"] = owner.mobile
                if "street" in vals:
                    partner_vals["street"] = owner.street
                if "street2" in vals:
                    partner_vals["street2"] = owner.street2
                if "city" in vals:
                    partner_vals["city"] = owner.city
                if "state_id" in vals:
                    partner_vals["state_id"] = owner.state_id.id
                if "zip" in vals:
                    partner_vals["zip"] = owner.zip
                if "country_id" in vals:
                    partner_vals["country_id"] = owner.country_id.id
                if partner_vals:
                    owner.partner_id.write(partner_vals)
        return result
