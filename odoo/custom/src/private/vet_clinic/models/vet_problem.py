from odoo import api, fields, models


class VetProblem(models.Model):
    _name = "vet.problem"
    _description = "Master Problem List"
    _order = "status, onset_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Problem Description", required=True, tracking=True, index=True
    )
    patient_id = fields.Many2one(
        "vet.patient", string="Patient", required=True, ondelete="cascade", index=True
    )
    status = fields.Selection(
        [
            ("active", "Active"),
            ("resolved", "Resolved"),
        ],
        required=True,
        default="active",
        tracking=True,
        index=True,
    )
    onset_date = fields.Date(
        string="Date of Onset", required=True, tracking=True, index=True
    )
    resolved_date = fields.Date(tracking=True)
    diagnosis_code = fields.Char(help="ICD-10 or other diagnostic code if applicable")
    notes = fields.Text(help="Additional notes about this problem")

    # Link to related medical notes
    medical_note_ids = fields.Many2many(
        "vet.medical.note",
        "vet_problem_note_rel",
        "problem_id",
        "note_id",
        string="Related Medical Notes",
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "check_resolved_date",
            "CHECK(status = 'active' OR resolved_date IS NOT NULL)",
            "Resolved problems must have a resolution date!",
        )
    ]

    @api.onchange("status")
    def _onchange_status(self):
        """Auto-set resolved_date when status changes to resolved"""
        if self.status == "resolved" and not self.resolved_date:
            self.resolved_date = fields.Date.today()
        elif self.status == "active":
            self.resolved_date = False

    def action_mark_resolved(self):
        """Action to mark problem as resolved"""
        self.write(
            {
                "status": "resolved",
                "resolved_date": fields.Date.today(),
            }
        )

    def action_mark_active(self):
        """Action to mark problem as active again"""
        self.write(
            {
                "status": "active",
                "resolved_date": False,
            }
        )
