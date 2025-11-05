{
    'name': 'Veterinary Clinic',
    'version': '17.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Veterinary clinic management system',
    'description': """
        Veterinary Clinic Management
        =============================

        This module provides functionality for managing a veterinary clinic:
        * Patient (animal) management
        * Pet owners management
        * Appointments scheduling
        * Medical history tracking
        * Treatment plans
        * Medication prescriptions
    """,
    'author': 'veterinarian',
    'website': 'https://github.com/veterinarian/vet-odoo',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
        'calendar',
    ],
    'data': [
        'security/vet_clinic_security.xml',
        'security/ir.model.access.csv',
        'views/vet_patient_views.xml',
        'views/vet_owner_views.xml',
        'views/vet_appointment_views.xml',
        'views/vet_menu.xml',
        'data/vet_species_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
