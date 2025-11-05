from odoo import models, fields, api


class VetPatient(models.Model):
    _name = 'vet.patient'
    _description = 'Veterinary Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Patient Name', required=True, tracking=True)
    owner_id = fields.Many2one('vet.owner', string='Owner', required=True, tracking=True)
    species_id = fields.Many2one('vet.species', string='Species', required=True, tracking=True)
    breed = fields.Char(string='Breed', tracking=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('unknown', 'Unknown'),
    ], string='Gender', default='unknown', tracking=True)

    birth_date = fields.Date(string='Date of Birth', tracking=True)
    age = fields.Char(string='Age', compute='_compute_age', store=False)

    color = fields.Char(string='Color/Markings')
    microchip_number = fields.Char(string='Microchip Number')

    weight = fields.Float(string='Weight (kg)', tracking=True)

    neutered = fields.Boolean(string='Spayed/Neutered', default=False, tracking=True)

    appointment_ids = fields.One2many('vet.appointment', 'patient_id', string='Appointments')
    appointment_count = fields.Integer(string='Number of Appointments', compute='_compute_appointment_count')

    allergies = fields.Text(string='Known Allergies')
    medical_notes = fields.Text(string='Medical Notes')

    image = fields.Binary(string='Photo', attachment=True)

    active = fields.Boolean(default=True)

    @api.depends('birth_date')
    def _compute_age(self):
        from datetime import date
        for patient in self:
            if patient.birth_date:
                today = date.today()
                delta = today - patient.birth_date
                years = delta.days // 365
                months = (delta.days % 365) // 30
                if years > 0:
                    patient.age = f"{years} year(s), {months} month(s)"
                else:
                    patient.age = f"{months} month(s)"
            else:
                patient.age = ''

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for patient in self:
            patient.appointment_count = len(patient.appointment_ids)
