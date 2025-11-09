from odoo import api, fields, models


class ResourceBooking(models.Model):
    _inherit = "resource.booking"

    # Override to disable auto-assignment by default for vet workflow
    combination_auto_assign = fields.Boolean(default=False)

    # Vet-specific fields
    patient_id = fields.Many2one(
        "vet.patient",
        string="Patient",
        tracking=True,
        help="The patient (animal) for this appointment",
    )
    owner_id = fields.Many2one(
        "vet.owner",
        string="Owner",
        related="patient_id.owner_id",
        store=True,
        help="The owner of the patient",
    )

    @api.onchange("patient_id", "provider_id")
    def _onchange_attendees(self):
        """Auto-populate attendees with owner and provider"""
        attendees = self.env["res.partner"]

        # Add owner as attendee
        if self.owner_id and self.owner_id.partner_id:
            attendees |= self.owner_id.partner_id

        # Add provider as attendee
        if self.provider_id and self.provider_id.partner_id:
            attendees |= self.provider_id.partner_id

        if attendees:
            self.partner_ids = attendees

    # Medical information
    reason = fields.Text(
        string="Reason for Visit",
        help="Primary reason for the appointment",
    )
    diagnosis = fields.Text(
        help="Diagnosis determined during the appointment",
    )
    treatment = fields.Text(
        help="Treatment plan for the patient",
    )
    prescription = fields.Text(
        help="Medications prescribed",
    )
    notes = fields.Text(
        string="Additional Notes",
        help="Any additional notes about the appointment",
    )

    # Link to room and provider
    room_id = fields.Many2one(
        "vet.room",
        string="Room",
        store=True,
        help="The room where the appointment takes place",
    )
    provider_id = fields.Many2one(
        "res.users",
        string="Provider",
        store=True,
        domain=[("is_provider", "=", True)],
        help="The staff member providing the service",
    )

    @api.onchange("room_id", "provider_id")
    def _onchange_room_provider(self):
        """Update combination when room/provider is selected"""
        if not self.room_id and not self.provider_id:
            self.combination_id = False
            return

        # Collect resources
        resources = self.env["resource.resource"]
        if self.room_id and self.room_id.resource_id:
            resources |= self.room_id.resource_id
        if self.provider_id and self.provider_id.provider_resource_id:
            resources |= self.provider_id.provider_resource_id

        if not resources:
            self.combination_id = False
            return

        # Try to find existing combination with these exact resources
        existing_combination = self.env["resource.booking.combination"].search(
            [("resource_ids", "=", resources.ids)], limit=1
        )

        if existing_combination:
            self.combination_id = existing_combination

    def _get_or_create_combination(self, room, provider):
        """Get or create a combination for the given room and provider"""
        # Collect resources
        resources = self.env["resource.resource"]
        if room and room.resource_id:
            resources |= room.resource_id
        if provider and provider.provider_resource_id:
            resources |= provider.provider_resource_id

        if not resources:
            return False

        # Try to find existing combination with these exact resources
        existing_combination = self.env["resource.booking.combination"].search(
            [("resource_ids", "=", resources.ids)], limit=1
        )

        if existing_combination:
            return existing_combination

        # Create new combination
        new_combination = self.env["resource.booking.combination"].create(
            {
                "resource_ids": [(6, 0, resources.ids)],
            }
        )
        return new_combination

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure combination is created from room/provider on create"""
        for vals in vals_list:
            if "room_id" in vals or "provider_id" in vals:
                room = self.env["vet.room"].browse(vals.get("room_id", False))
                provider = self.env["res.users"].browse(vals.get("provider_id", False))
                combination = self._get_or_create_combination(room, provider)
                if combination:
                    vals["combination_id"] = combination.id
                    # Link to booking type if creating
                    if vals.get("type_id") and not self.env[
                        "resource.booking.type.combination.rel"
                    ].search(
                        [
                            ("type_id", "=", vals["type_id"]),
                            ("combination_id", "=", combination.id),
                        ]
                    ):
                        self.env["resource.booking.type.combination.rel"].create(
                            {
                                "type_id": vals["type_id"],
                                "combination_id": combination.id,
                                "sequence": 10,
                            }
                        )

        bookings = super().create(vals_list)

        # Auto-generate name for each booking
        for booking in bookings:
            if not booking.name or booking.name == "New":
                booking.name = booking._generate_name()

        return bookings

    def write(self, vals):
        """Ensure combination is updated from room/provider on write"""
        if "room_id" in vals or "provider_id" in vals:
            for booking in self:
                room = (
                    self.env["vet.room"].browse(vals["room_id"])
                    if "room_id" in vals
                    else booking.room_id
                )
                provider = (
                    self.env["res.users"].browse(vals["provider_id"])
                    if "provider_id" in vals
                    else booking.provider_id
                )
                combination = self._get_or_create_combination(room, provider)
                if combination:
                    vals["combination_id"] = combination.id
                    # Link to booking type if not already linked
                    if booking.type_id and not self.env[
                        "resource.booking.type.combination.rel"
                    ].search(
                        [
                            ("type_id", "=", booking.type_id.id),
                            ("combination_id", "=", combination.id),
                        ]
                    ):
                        self.env["resource.booking.type.combination.rel"].create(
                            {
                                "type_id": booking.type_id.id,
                                "combination_id": combination.id,
                                "sequence": 10,
                            }
                        )

        result = super().write(vals)

        # Regenerate name if key fields changed
        if any(key in vals for key in ["patient_id", "type_id", "start"]):
            for booking in self:
                booking.name = booking._generate_name()

        return result

    @api.depends("patient_id", "owner_id", "type_id", "start")
    def _compute_display_name(self):
        """Override display name to show patient and owner"""
        res = super()._compute_display_name()
        for booking in self:
            if booking.patient_id and booking.owner_id:
                booking.display_name = (
                    f"{booking.patient_id.name} - {booking.owner_id.name}"
                )
        return res

    def _generate_name(self):
        """Auto-generate a meaningful name for the booking"""
        self.ensure_one()
        parts = []

        if self.patient_id:
            parts.append(self.patient_id.name)

        if self.type_id:
            parts.append(self.type_id.name)

        if self.start:
            # Format: YYYY-MM-DD HH:MM
            parts.append(self.start.strftime("%Y-%m-%d %H:%M"))

        return " - ".join(parts) if parts else "Appointment"
