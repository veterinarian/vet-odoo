{
    "name": "Veterinary Clinic",
    "version": "17.0.1.0.0",
    "category": "Healthcare",
    "summary": "Veterinary clinic management system",
    "description": """
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
    "author": "veterinarian",
    "website": "https://github.com/veterinarian/vet-odoo",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "calendar",
    ],
    "data": [
        "security/vet_clinic_security.xml",
        "security/ir.model.access.csv",
        "data/vet_species_data.xml",
        "data/vet_provider_type_data.xml",
        "data/vet_room_data.xml",
        "views/vet_provider_type_views.xml",
        "views/vet_room_views.xml",
        "views/res_users_views.xml",
        "views/vet_owner_views.xml",
        "views/vet_appointment_views.xml",
        "views/vet_patient_views.xml",
        "views/vet_menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
