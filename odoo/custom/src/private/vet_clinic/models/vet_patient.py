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
    birth_date_approximate = fields.Boolean(string='Approximate Birth Date', default=False, tracking=True,
                                             help='Indicates if birth date was calculated from age rather than provided exactly')
    age = fields.Char(string='Age', compute='_compute_age', store=False)

    # Age input fields (stored, updated via onchange)
    age_years = fields.Integer(string='Age (Years)', default=0)
    age_months = fields.Integer(string='Age (Months)', default=0)

    color = fields.Char(string='Color/Markings')
    microchip_number = fields.Char(string='Microchip Number')

    # Weight stored internally in kg
    weight = fields.Float(string='Weight (kg)', tracking=True)
    weight_unit = fields.Selection([
        ('kg', 'Kilograms (kg)'),
        ('lbs', 'Pounds (lbs)'),
    ], string='Weight Unit', default='kg', required=True, tracking=True)
    weight_display = fields.Float(string='Weight', compute='_compute_weight_display', inverse='_inverse_weight_display',
                                   digits=(6, 2), store=False)

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

    @api.onchange('age_years', 'age_months')
    def _onchange_age_fields(self):
        """When age is entered, calculate birth date and mark as approximate"""
        if self.age_years or self.age_months:
            from datetime import date
            from dateutil.relativedelta import relativedelta
            today = date.today()
            years = self.age_years or 0
            months = self.age_months or 0
            self.birth_date = today - relativedelta(years=years, months=months)
            self.birth_date_approximate = True

    @api.onchange('birth_date')
    def _onchange_birth_date(self):
        """When birth date is manually entered, update age fields and mark as exact"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            delta = today - self.birth_date
            self.age_years = delta.days // 365
            self.age_months = (delta.days % 365) // 30
            # Mark as exact since user entered birth date directly
            self.birth_date_approximate = False

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
