from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestVetPatient(TransactionCase):

    def setUp(self):
        super().setUp()
        # Create test data
        self.species_dog = self.env['vet.species'].create({
            'name': 'Dog',
            'code': 'DOG',
        })
        self.owner = self.env['vet.owner'].create({
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
        })

    def test_patient_creation(self):
        """Test creating a veterinary patient"""
        patient = self.env['vet.patient'].create({
            'name': 'Max',
            'owner_id': self.owner.id,
            'species_id': self.species_dog.id,
            'breed': 'Golden Retriever',
            'gender': 'male',
        })
        self.assertEqual(patient.name, 'Max')
        self.assertEqual(patient.owner_id, self.owner)
        self.assertEqual(patient.species_id, self.species_dog)

    def test_patient_age_computation(self):
        """Test age computation for patients"""
        from datetime import date, timedelta
        birth_date = date.today() - timedelta(days=730)  # 2 years ago
        patient = self.env['vet.patient'].create({
            'name': 'Bella',
            'owner_id': self.owner.id,
            'species_id': self.species_dog.id,
            'birth_date': birth_date,
        })
        # Age should be computed
        self.assertTrue(patient.age)
        self.assertIn('year', patient.age.lower())

    def test_appointment_count(self):
        """Test appointment count computation"""
        patient = self.env['vet.patient'].create({
            'name': 'Charlie',
            'owner_id': self.owner.id,
            'species_id': self.species_dog.id,
        })
        self.assertEqual(patient.appointment_count, 0)

        # Create an appointment
        self.env['vet.appointment'].create({
            'patient_id': patient.id,
            'appointment_date': '2025-12-01 10:00:00',
            'appointment_type': 'checkup',
            'reason': 'Regular checkup',
        })
        self.assertEqual(patient.appointment_count, 1)
