"""
Django management command to test assistant creation.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import seed_example_assistant


class Command(BaseCommand):
    help = 'Test assistant creation by seeding an example assistant'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            default='test-client-001',
            help='Client ID for the assistant'
        )

    def handle(self, *args, **options):
        client_id = options['client_id']
        
        try:
            # Get or create a superuser for testing
            owner, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'is_superuser': True,
                    'is_staff': True,
                }
            )
            
            if created:
                owner.set_password('admin123')
                owner.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created superuser: {owner.username}')
                )
            
            # Create example assistant
            assistant = seed_example_assistant(client_id=client_id, owner=owner)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created assistant: {assistant.name} '
                    f'(ID: {assistant.id}, Status: {assistant.status})'
                )
            )
            
            # Print configuration summary
            self.stdout.write('\nConfiguration Summary:')
            self.stdout.write(f'- Model: {assistant.model_config.provider} {assistant.model_config.model_name}')
            self.stdout.write(f'- Voice: {assistant.voice_config.voice.name if assistant.voice_config.voice else "None"}')
            self.stdout.write(f'- STT: {assistant.stt_config.provider} {assistant.stt_config.model_name}')
            self.stdout.write(f'- External ID: {assistant.external_id}')
            self.stdout.write(f'- Slug: {assistant.slug}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating assistant: {str(e)}')
            )
            raise
