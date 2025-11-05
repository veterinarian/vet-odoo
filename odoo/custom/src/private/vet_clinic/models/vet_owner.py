from odoo import models, fields, api


class VetOwner(models.Model):
    _name = 'vet.owner'
    _description = 'Pet Owner'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Owner Name', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    mobile = fields.Char(string='Mobile', tracking=True)
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country')

    patient_ids = fields.One2many('vet.patient', 'owner_id', string='Patients')
    patient_count = fields.Integer(string='Number of Pets', compute='_compute_patient_count')

    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    @api.depends('patient_ids')
    def _compute_patient_count(self):
        for owner in self:
            owner.patient_count = len(owner.patient_ids)
