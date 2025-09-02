from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from people.models import Contact
import json


class DuplicatePreventionTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create a test contact
        self.existing_contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            external_id='EMP001',
            phone='12345678',
            tenant_id='zain_bh',
            created_by=self.user
        )

    def test_duplicate_email_prevention(self):
        """Test that contacts with duplicate emails are prevented."""
        # Try to create a contact with the same email
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',  # Same email
            'external_id': 'EMP002',
            'phone': '87654321',
            'tenant_id': 'zain_bh'
        }
        
        response = self.client.post(
            reverse('people:contact_create'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should fail due to duplicate email
        self.assertEqual(response.status_code, 400)
        
        # Verify only one contact exists
        self.assertEqual(Contact.objects.count(), 1)

    def test_duplicate_external_id_prevention(self):
        """Test that contacts with duplicate external IDs are prevented."""
        # Try to create a contact with the same external ID
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'external_id': 'EMP001',  # Same external ID
            'phone': '87654321',
            'tenant_id': 'zain_bh'
        }
        
        response = self.client.post(
            reverse('people:contact_create'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should fail due to duplicate external ID
        self.assertEqual(response.status_code, 400)
        
        # Verify only one contact exists
        self.assertEqual(Contact.objects.count(), 1)

    def test_duplicate_name_allowed(self):
        """Test that contacts with duplicate names are allowed."""
        # Try to create a contact with the same name
        data = {
            'first_name': 'John',
            'last_name': 'Doe',  # Same name
            'email': 'john.doe2@example.com',
            'external_id': 'EMP002',
            'phone': '87654321',
            'tenant_id': 'zain_bh'
        }
        
        response = self.client.post(
            reverse('people:contact_create'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should succeed - names are not unique
        self.assertEqual(response.status_code, 200)
        
        # Verify two contacts exist
        self.assertEqual(Contact.objects.count(), 2)

    def test_duplicate_phone_prevention(self):
        """Test that contacts with duplicate phone numbers are prevented."""
        # Try to create a contact with the same phone
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'external_id': 'EMP002',
            'phone': '12345678',  # Same phone
            'tenant_id': 'zain_bh'
        }
        
        response = self.client.post(
            reverse('people:contact_create'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should fail due to duplicate phone
        self.assertEqual(response.status_code, 400)
        
        # Verify only one contact exists
        self.assertEqual(Contact.objects.count(), 1)

    def test_successful_contact_creation(self):
        """Test that unique contacts can be created successfully."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'external_id': 'EMP002',
            'phone': '87654321',
            'tenant_id': 'zain_bh'
        }
        
        response = self.client.post(
            reverse('people:contact_create'),
            data=json.dumps(data),
            content_type='application/json'
        )
        

        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        
        # Verify two contacts exist
        self.assertEqual(Contact.objects.count(), 2)
    
    def test_phone_number_required(self):
        """Test that phone number is required for contact creation."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'external_id': 'EMP002',
            'phone': '',  # No phone number
            'tenant_id': 'zain_bh'
        }
        
        response = self.client.post(
            reverse('people:contact_create'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should fail due to missing phone number
        self.assertEqual(response.status_code, 400)
        self.assertIn('Phone number is required', response.json()['message'])
        
        # Verify only one contact exists (the original one)
        self.assertEqual(Contact.objects.count(), 1)

    def test_find_duplicates_method(self):
        """Test the find_duplicates model method."""
        # Test finding duplicates by email
        duplicates = Contact.find_duplicates(
            email='john.doe@example.com',
            tenant_id='zain_bh'
        )
        self.assertEqual(duplicates.count(), 1)
        self.assertEqual(duplicates.first(), self.existing_contact)
        
        # Test finding duplicates by external ID
        duplicates = Contact.find_duplicates(
            external_id='EMP001',
            tenant_id='zain_bh'
        )
        self.assertEqual(duplicates.count(), 1)
        self.assertEqual(duplicates.first(), self.existing_contact)
        

        
        # Test finding duplicates by phone
        duplicates = Contact.find_duplicates(
            phone='12345678',
            tenant_id='zain_bh'
        )
        self.assertEqual(duplicates.count(), 1)
        self.assertEqual(duplicates.first(), self.existing_contact)

    def test_tenant_isolation(self):
        """Test that duplicate checking is isolated by tenant."""
        # Create a contact in a different tenant
        other_tenant_contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            external_id='EMP001',
            phone='12345678',
            tenant_id='other_tenant',
            created_by=self.user
        )
        
        # Should be able to create a contact with same data in different tenant
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'external_id': 'EMP001',
            'phone': '12345678',
            'tenant_id': 'other_tenant'
        }
        
        response = self.client.post(
            reverse('people:contact_create'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should fail due to duplicate in same tenant
        self.assertEqual(response.status_code, 400)
        
        # But we should have 2 contacts total (different tenants)
        self.assertEqual(Contact.objects.count(), 2)
