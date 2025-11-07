from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VetAppointment(models.Model):
    _name = 'vet.appointment'
    _description = 'Veterinary Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc'

    name = fields.Char(string='Appointment Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    patient_id = fields.Many2one('vet.patient', string='Patient', required=True, tracking=True)
    owner_id = fields.Many2one('vet.owner', string='Owner', related='patient_id.owner_id', store=True)

    appointment_date = fields.Datetime(string='Appointment Date', required=True, tracking=True)
    duration = fields.Float(string='Duration (hours)', default=0.5)

    appointment_type = fields.Selection([
        ('checkup', 'Regular Checkup'),
        ('vaccination', 'Vaccination'),
        ('surgery', 'Surgery'),
        ('emergency', 'Emergency'),
        ('followup', 'Follow-up'),
        ('other', 'Other'),
    ], string='Appointment Type', default='checkup', required=True, tracking=True)

    veterinarian_id = fields.Many2one('res.users', string='Veterinarian', tracking=True)

    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='scheduled', required=True, tracking=True)

    reason = fields.Text(string='Reason for Visit', required=True)
    diagnosis = fields.Text(string='Diagnosis')
    treatment = fields.Text(string='Treatment')
    prescription = fields.Text(string='Prescription')

    notes = fields.Text(string='Additional Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vet.appointment') or _('New')
        return super().create(vals_list)

    @api.constrains('appointment_date')
    def _check_appointment_date(self):
        from datetime import datetime
        for appointment in self:
            if appointment.appointment_date and appointment.appointment_date < fields.Datetime.now():
                if appointment.state == 'scheduled':
                    raise ValidationError(_('Appointment date cannot be in the past.'))

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
