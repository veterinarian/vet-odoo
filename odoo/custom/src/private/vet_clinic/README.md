# Veterinary Clinic Module

## Overview

This module provides comprehensive veterinary clinic management functionality for Odoo 17.

## Features

### Patient Management
- Comprehensive patient (animal) profiles
- Multiple species support (dogs, cats, birds, reptiles, etc.)
- Medical history tracking
- Photo support
- Microchip number tracking
- Allergy tracking
- Age calculation

### Owner Management
- Pet owner contact information
- Address management
- Multiple pets per owner
- Activity tracking

### Appointment Management
- Calendar-based appointment scheduling
- Multiple appointment types (checkup, vaccination, surgery, emergency, follow-up)
- Appointment workflow (scheduled → confirmed → in progress → done)
- Veterinarian assignment
- Diagnosis and treatment recording
- Prescription management

### Security
- Two security groups: User and Manager
- Granular access rights per model

### Pre-loaded Data
- Common pet species (Dog, Cat, Bird, Rabbit, Horse, etc.)
- Appointment numbering sequence

## Installation

1. Place this module in your Odoo addons path
2. Update the app list
3. Install "Veterinary Clinic"

## Usage

### Creating a New Patient

1. Go to Veterinary → Patients
2. Click "Create"
3. Fill in patient details (name, owner, species, etc.)
4. Add medical information in the Medical Information tab
5. Save

### Scheduling an Appointment

1. Go to Veterinary → Appointments
2. Click "Create" or use the "New Appointment" button from a patient form
3. Select patient, date, and appointment type
4. Fill in the reason for visit
5. Assign a veterinarian
6. Confirm the appointment

### Managing Appointments

- Use the calendar view to see appointments by week/month
- Filter appointments by status (scheduled, confirmed, in progress, done)
- Update diagnosis, treatment, and prescriptions during the appointment
- Complete the appointment when done

## Technical Details

### Models

- `vet.patient` - Veterinary patients (animals)
- `vet.owner` - Pet owners
- `vet.species` - Animal species
- `vet.appointment` - Appointments and visits

### Dependencies

- `base` - Base Odoo functionality
- `mail` - Chatter and activity tracking
- `calendar` - Calendar view support

## Testing

Run tests with:
```bash
odoo-bin -c config.conf -d test_db --test-enable -i vet_clinic --stop-after-init
```

## License

AGPL-3.0-or-later

## Author

veterinarian

## Version

17.0.1.0.0
