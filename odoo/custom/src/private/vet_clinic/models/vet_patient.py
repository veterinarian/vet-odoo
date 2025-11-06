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

    # Age input fields (inverse computation)
    age_years = fields.Integer(string='Age (Years)', compute='_compute_age_fields', inverse='_inverse_age_fields', store=False)
    age_months = fields.Integer(string='Age (Months)', compute='_compute_age_fields', inverse='_inverse_age_fields', store=False)

    color = fields.Char(string='Color/Markings')
    microchip_number = fields.Char(string='Microchip Number')

    # Weight stored internally in kg
    weight = fields.Float(string='Weight (internal kg)', tracking=True, groups='base.group_no_one')
    weight_unit = fields.Selection([
        ('kg', 'Kilograms (kg)'),
        ('lbs', 'Pounds (lbs)'),
    ], string='Weight Unit', default='kg', required=True, tracking=True)
    weight_display = fields.Float(string='Weight', compute='_compute_weight_display', inverse='_inverse_weight_display',
                                   digits=(6, 2), tracking=True, store=True)

    neutered = fields.Boolean(string='Spayed/Neutered', default=False, tracking=True)

    appointment_ids = fields.One2many('vet.appointment', 'patient_id', string='Appointments')
    appointment_count = fields.Integer(string='Number of Appointments', compute='_compute_appointment_count')

    allergies = fields.Text(string='Known Allergies')
    medical_notes = fields.Text(string='Medical Notes')

    image = fields.Binary(string='Photo', attachment=True)

    active = fields.Boolean(default=True)

    @api.depends('birth_date')
    def _compute_age(self):
        """Compute human-readable age string from birth date"""
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

    @api.depends('birth_date')
    def _compute_age_fields(self):
        """Compute age_years and age_months from birth date"""
        from datetime import date
        for patient in self:
            if patient.birth_date:
                today = date.today()
                delta = today - patient.birth_date
                patient.age_years = delta.days // 365
                patient.age_months = (delta.days % 365) // 30
            else:
                patient.age_years = 0
                patient.age_months = 0

    def _inverse_age_fields(self):
        """Calculate birth date from age_years and age_months"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        for patient in self:
            if patient.age_years or patient.age_months:
                today = date.today()
                years = patient.age_years or 0
                months = patient.age_months or 0
                patient.birth_date = today - relativedelta(years=years, months=months)

    @api.depends('weight', 'weight_unit')
    def _compute_weight_display(self):
        """Convert weight from kg to display unit"""
        for patient in self:
            if patient.weight:
                if patient.weight_unit == 'lbs':
                    # Convert kg to lbs (1 kg = 2.20462 lbs)
                    patient.weight_display = patient.weight * 2.20462
                else:
                    patient.weight_display = patient.weight
            else:
                patient.weight_display = 0.0

    def _inverse_weight_display(self):
        """Convert weight from display unit to kg for storage"""
        for patient in self:
            if patient.weight_display:
                if patient.weight_unit == 'lbs':
                    # Convert lbs to kg (1 lb = 0.453592 kg)
                    patient.weight = patient.weight_display * 0.453592
                else:
                    patient.weight = patient.weight_display
            else:
                patient.weight = 0.0

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for patient in self:
            patient.appointment_count = len(patient.appointment_ids)
