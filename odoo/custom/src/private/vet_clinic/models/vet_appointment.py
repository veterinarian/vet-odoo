from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VetAppointment(models.Model):
    _name = "vet.appointment"
    _description = "Veterinary Appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "appointment_date desc"

    name = fields.Char(
        string="Appointment Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
        index=True,
    )
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
    )

    patient_id = fields.Many2one(
        "vet.patient", string="Patient", required=True, tracking=True
    )
    owner_id = fields.Many2one(
        "vet.owner", string="Owner", related="patient_id.owner_id", store=True
    )

    appointment_date = fields.Datetime(
        string="Appointment Date", required=True, tracking=True
    )
    duration = fields.Float(string="Duration (hours)", default=0.5)

    appointment_type = fields.Selection(
        [
            ("checkup", "Regular Checkup"),
            ("vaccination", "Vaccination"),
            ("surgery", "Surgery"),
            ("emergency", "Emergency"),
            ("followup", "Follow-up"),
            ("other", "Other"),
        ],
        string="Appointment Type",
        default="checkup",
        required=True,
        tracking=True,
    )

    veterinarian_id = fields.Many2one("res.users", string="Veterinarian", tracking=True)
    provider_id = fields.Many2one(
        "res.users",
        string="Provider",
        required=True,
        tracking=True,
        help="The staff member providing the service",
    )
    room_id = fields.Many2one("vet.room", string="Room", required=True, tracking=True)

    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="scheduled",
        required=True,
        tracking=True,
    )

    reason = fields.Text(string="Reason for Visit", required=True)
    diagnosis = fields.Text(string="Diagnosis")
    treatment = fields.Text(string="Treatment")
    prescription = fields.Text(string="Prescription")

    notes = fields.Text(string="Additional Notes")

    has_overlap = fields.Boolean(
        string="Has Overlap",
        compute="_compute_has_overlap",
        compute_sudo=False,
        store=True,
    )
    overlap_warning = fields.Html(
        string="Overlap Warning",
        compute="_compute_has_overlap",
        compute_sudo=False,
        store=False,
    )

    @api.depends("patient_id", "owner_id", "appointment_date")
    def _compute_display_name(self):
        """Compute display name showing patient and owner"""
        for appointment in self:
            if appointment.patient_id and appointment.owner_id:
                date_str = ""
                if appointment.appointment_date:
                    date_str = appointment.appointment_date.strftime("%Y-%m-%d %H:%M")
                appointment.display_name = (
                    f"{appointment.patient_id.name} - {appointment.owner_id.name}"
                    + (f" ({date_str})" if date_str else "")
                )
            else:
                appointment.display_name = appointment.name or _("New")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "vet.appointment"
                ) or _("New")
        return super().create(vals_list)

    @api.depends("appointment_date", "duration", "provider_id", "room_id", "state")
    def _compute_has_overlap(self):
        """Check for overlapping appointments with the same provider or room"""
        from datetime import timedelta

        for appointment in self:
            if (
                not appointment.appointment_date
                or not appointment.duration
                or not (appointment.provider_id or appointment.room_id)
            ):
                appointment.has_overlap = False
                appointment.overlap_warning = False
                continue

            # Calculate end time
            start_time = appointment.appointment_date
            end_time = start_time + timedelta(hours=appointment.duration)

            # Build domain to find overlapping appointments
            domain = [
                ("state", "not in", ["cancelled", "done"]),
                ("appointment_date", "<", end_time),
            ]

            # Exclude current appointment if it has a real ID (not a new record)
            if appointment.id and isinstance(appointment.id, int):
                domain.append(("id", "!=", appointment.id))

            # Search for overlaps
            overlapping = self.env["vet.appointment"].search(domain)

            provider_overlaps = []
            room_overlaps = []

            for other in overlapping:
                other_end_time = other.appointment_date + timedelta(
                    hours=other.duration
                )

                # Check if times actually overlap
                if other_end_time > start_time:
                    # Check provider overlap
                    if (
                        appointment.provider_id
                        and other.provider_id == appointment.provider_id
                    ):
                        provider_overlaps.append(other)

                    # Check room overlap
                    if appointment.room_id and other.room_id == appointment.room_id:
                        room_overlaps.append(other)

            appointment.has_overlap = bool(provider_overlaps or room_overlaps)

            # Build warning message
            if appointment.has_overlap:
                warnings = []
                if provider_overlaps:
                    warnings.append("<strong>Provider Overlap:</strong>")
                    for other in provider_overlaps:
                        date_str = other.appointment_date.strftime("%Y-%m-%d %H:%M")
                        msg = f"  • {other.name} - {date_str}"
                        msg += f" ({other.patient_id.name})"
                        warnings.append(msg)

                if room_overlaps:
                    warnings.append("<strong>Room Overlap:</strong>")
                    for other in room_overlaps:
                        date_str = other.appointment_date.strftime("%Y-%m-%d %H:%M")
                        msg = f"  • {other.name} - {date_str}"
                        msg += f" ({other.patient_id.name})"
                        warnings.append(msg)

                appointment.overlap_warning = (
                    '<div class="alert alert-warning">'
                    + "<br/>".join(warnings)
                    + "</div>"
                )
            else:
                appointment.overlap_warning = False

    @api.constrains("appointment_date")
    def _check_appointment_date(self):
        for appointment in self:
            if (
                appointment.appointment_date
                and appointment.appointment_date < fields.Datetime.now()
            ):
                if appointment.state == "scheduled":
                    raise ValidationError(_("Appointment date cannot be in the past."))

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancelled"})
