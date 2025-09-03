"""
Django management command to seed sample contacts for testing.
"""

from django.core.management.base import BaseCommand
from people.models import Contact, Segment
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Seed sample contacts for testing campaigns functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            default='zain_bh',
            help='Client ID for the contacts'
        )

    def handle(self, *args, **options):
        client_id = options['client_id']
        
        try:
            self.stdout.write('Seeding sample contacts...')
            
            # Get or create a user for created_by
            user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            # Create segments
            segments = []
            segment_data = [
                {'name': 'VIP Customers', 'description': 'High-value customers', 'color': 'badge-primary'},
                {'name': 'New Leads', 'description': 'Recently acquired leads', 'color': 'badge-success'},
                {'name': 'Returning Customers', 'description': 'Repeat customers', 'color': 'badge-info'},
                {'name': 'Technical Support', 'description': 'Customers needing support', 'color': 'badge-warning'},
            ]
            
            for seg_data in segment_data:
                segment, created = Segment.objects.get_or_create(
                    name=seg_data['name'],
                    defaults={
                        'description': seg_data['description'],
                        'color': seg_data['color'],
                        'created_by': user
                    }
                )
                segments.append(segment)
                if created:
                    self.stdout.write(f'✅ Created segment: {segment.name}')
                else:
                    self.stdout.write(f'⚠️ Segment already exists: {segment.name}')
            
            # Create sample contacts
            contacts_data = [
                {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com',
                    'phone': '+1 555 123 4567',
                    'company': 'Tech Solutions Inc',
                    'segments': [segments[0].id, segments[1].id]  # VIP + New Lead
                },
                {
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'email': 'jane.smith@example.com',
                    'phone': '+1 555 234 5678',
                    'company': 'Marketing Pro',
                    'segments': [segments[1].id]  # New Lead
                },
                {
                    'first_name': 'Ahmed',
                    'last_name': 'Al-Rashid',
                    'email': 'ahmed@dubai-corp.com',
                    'phone': '+971 50 123 4567',
                    'company': 'Dubai Corporation',
                    'segments': [segments[0].id, segments[2].id]  # VIP + Returning
                },
                {
                    'first_name': 'Sarah',
                    'last_name': 'Johnson',
                    'email': 'sarah.j@saudi-tech.com',
                    'phone': '+966 50 987 6543',
                    'company': 'Saudi Tech Solutions',
                    'segments': [segments[2].id]  # Returning Customer
                },
                {
                    'first_name': 'Bob',
                    'last_name': 'Wilson',
                    'email': 'bob.wilson@acme.com',
                    'phone': '+1 555 345 6789',
                    'company': 'Acme Corporation',
                    'segments': [segments[3].id]  # Technical Support
                },
                {
                    'first_name': 'Alice',
                    'last_name': 'Brown',
                    'email': 'alice.brown@design.com',
                    'phone': '+44 20 7946 0958',
                    'company': 'Design Studio UK',
                    'segments': [segments[1].id, segments[3].id]  # New Lead + Support
                },
                {
                    'first_name': 'Carlos',
                    'last_name': 'Rodriguez',
                    'email': 'carlos@spanish-tech.com',
                    'phone': '+34 91 123 4567',
                    'company': 'Spanish Tech Solutions',
                    'segments': [segments[2].id]  # Returning Customer
                },
                {
                    'first_name': 'Yuki',
                    'last_name': 'Tanaka',
                    'email': 'yuki.tanaka@japan-tech.com',
                    'phone': '+81 3 1234 5678',
                    'company': 'Japan Technology Corp',
                    'segments': [segments[0].id]  # VIP Customer
                }
            ]
            
            # Create contacts
            for contact_data in contacts_data:
                contact, created = Contact.objects.get_or_create(
                    external_id=f"TEST_{contact_data['first_name']}_{contact_data['last_name']}",
                    defaults={
                        'first_name': contact_data['first_name'],
                        'last_name': contact_data['last_name'],
                        'email': contact_data['email'],
                        'phone': contact_data['phone'],
                        'company': contact_data['company'],
                        'segments': contact_data['segments'],
                        'tenant_id': client_id,
                        'created_by': user
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created contact: {contact.display_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Contact already exists: {contact.display_name}')
                    )
            
            # Summary
            total_contacts = Contact.objects.filter(tenant_id=client_id).count()
            total_segments = Segment.objects.count()
            
            self.stdout.write('\n=== Contact Seeding Summary ===')
            self.stdout.write(f'Total contacts: {total_contacts}')
            self.stdout.write(f'Total segments: {total_segments}')
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully seeded contacts for client: {client_id}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error seeding contacts: {str(e)}')
            )
            raise

