from odoo import api, fields, models


class VetMedicalNote(models.Model):
    _name = "vet.medical.note"
    _description = "Veterinary Medical Note"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute="_compute_name", store=True)
    patient_id = fields.Many2one(
        "vet.patient", string="Patient", required=True, ondelete="cascade", index=True
    )
    booking_id = fields.Many2one(
        "resource.booking",
        string="Related Appointment",
        ondelete="set null",
        help="Link to the appointment this note was created during",
    )
    date = fields.Datetime(required=True, default=fields.Datetime.now, tracking=True)
    author_id = fields.Many2one(
        "res.users",
        string="Author",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    note_type = fields.Selection(
        [
            ("soap", "SOAP Note"),
            ("communication", "Communication"),
            ("internal", "Internal Note"),
            ("result", "Diagnostic Result"),
            ("image", "Image/Photo"),
            ("report", "Report"),
        ],
        required=True,
        default="internal",
        tracking=True,
    )

    # SOAP fields (only used when note_type = 'soap')
    subjective = fields.Text(
        help="Subjective: What the owner reports (complaints, observations, history)"
    )
    objective = fields.Text(
        help=(
            "Objective: Observable findings from examination "
            "(vitals, physical exam, labs)"
        )
    )
    assessment = fields.Text(help="Assessment: Diagnosis or differential diagnoses")
    plan = fields.Text(
        help="Plan: Treatment plan, medications, follow-up, home care instructions"
    )

    # General content for non-SOAP notes
    content = fields.Html(help="Content for non-SOAP notes")

    # Attachments
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "vet_medical_note_attachment_rel",
        "note_id",
        "attachment_id",
        string="Attachments",
        help="PDFs, images, and other files",
    )
    attachment_count = fields.Integer(compute="_compute_attachment_count")

    # Visibility and importance
    is_private = fields.Boolean(
        string="Private",
        default=False,
        help="Private notes are only visible to clinic staff",
    )
    is_important = fields.Boolean(default=False, help="Mark as important/highlighted")

    active = fields.Boolean(default=True)

    @api.depends("note_type", "date", "patient_id")
    def _compute_name(self):
        """Auto-generate name from note type and date"""
        for note in self:
            type_name = dict(self._fields["note_type"].selection).get(
                note.note_type, "Note"
            )
            date_str = ""
            if note.date:
                date_str = note.date.strftime("%Y-%m-%d %H:%M")
            patient_name = note.patient_id.name if note.patient_id else ""
            note.name = f"{type_name} - {patient_name} - {date_str}"

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for note in self:
            note.attachment_count = len(note.attachment_ids)

    def action_view_attachments(self):
        """Action to view attachments"""
        self.ensure_one()
        return {
            "name": "Attachments",
            "type": "ir.actions.act_window",
            "res_model": "ir.attachment",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.attachment_ids.ids)],
            "context": {
                "default_res_model": self._name,
                "default_res_id": self.id,
            },
        }
