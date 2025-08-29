"""
Django management command to seed OpenAI and ElevenLabs voices.
"""

from django.core.management.base import BaseCommand
from dashboard.config_models import Voice
from dashboard.models import VoiceProvider


class Command(BaseCommand):
    help = 'Seed OpenAI and ElevenLabs voices for the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            default='zain_bh',
            help='Client ID for the voices'
        )

    def handle(self, *args, **options):
        client_id = options['client_id']
        
        try:
            self.stdout.write('Seeding OpenAI and ElevenLabs voices...')
            
            # OpenAI Voices
            openai_voices = [
                {
                    'name': 'Alloy',
                    'voice_id': 'alloy',
                    'description': 'OpenAI Alloy voice - versatile and natural'
                },
                {
                    'name': 'Echo',
                    'voice_id': 'echo',
                    'description': 'OpenAI Echo voice - clear and professional'
                },
                {
                    'name': 'Fable',
                    'voice_id': 'fable',
                    'description': 'OpenAI Fable voice - warm and engaging'
                },
                {
                    'name': 'Onyx',
                    'voice_id': 'onyx',
                    'description': 'OpenAI Onyx voice - deep and authoritative'
                },
                {
                    'name': 'Nova',
                    'voice_id': 'nova',
                    'description': 'OpenAI Nova voice - bright and energetic'
                },
                {
                    'name': 'Shimmer',
                    'voice_id': 'shimmer',
                    'description': 'OpenAI Shimmer voice - smooth and melodic'
                }
            ]
            
            # ElevenLabs Voices
            elevenlabs_voices = [
                {
                    'name': 'Maha',
                    'voice_id': 'NTCP1AfaTmvuDcz9dSmQ',
                    'description': 'Arabic Bahraini Accent'
                }
            ]
            
            # Create OpenAI voices
            for voice_data in openai_voices:
                voice, created = Voice.objects.get_or_create(
                    provider=VoiceProvider.OPENAI,
                    voice_id=voice_data['voice_id'],
                    defaults={
                        'client_id': client_id,
                        'name': voice_data['name'],
                        'description': voice_data['description'],
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created OpenAI voice: {voice.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ OpenAI voice already exists: {voice.name}')
                    )
            
            # Create ElevenLabs voices
            for voice_data in elevenlabs_voices:
                voice, created = Voice.objects.get_or_create(
                    provider=VoiceProvider.ELEVENLABS,
                    voice_id=voice_data['voice_id'],
                    defaults={
                        'client_id': client_id,
                        'name': voice_data['name'],
                        'description': voice_data['description'],
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created ElevenLabs voice: {voice.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ ElevenLabs voice already exists: {voice.name}')
                    )
            
            # Summary
            total_openai = Voice.objects.filter(provider=VoiceProvider.OPENAI, client_id=client_id).count()
            total_elevenlabs = Voice.objects.filter(provider=VoiceProvider.ELEVENLABS, client_id=client_id).count()
            
            self.stdout.write('\n=== Voice Seeding Summary ===')
            self.stdout.write(f'OpenAI voices: {total_openai}')
            self.stdout.write(f'ElevenLabs voices: {total_elevenlabs}')
            self.stdout.write(f'Total voices: {total_openai + total_elevenlabs}')
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully seeded voices for client: {client_id}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error seeding voices: {str(e)}')
            )
            raise
