"""
Django management command to test end-to-end ambient and thinking sound configuration.
"""

import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import Client
from dashboard.models import Assistant
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test end-to-end ambient and thinking sound configuration'

    def handle(self, *args, **options):
        try:
            # Get the first assistant and its owner
            assistant = Assistant.objects.first()
            user = assistant.owner if assistant else None
            
            if not assistant or not user:
                self.stdout.write(
                    self.style.ERROR('No assistant or superuser found. Run test_assistant first.')
                )
                return
            
            self.stdout.write(f'Testing audio configuration for assistant: {assistant.name}')
            
            # Test 1: Check current configuration
            vc = assistant.voice_config
            self.stdout.write('\n=== Current Configuration ===')
            self.stdout.write(f'Ambient sound enabled: {vc.ambient_sound_enabled}')
            self.stdout.write(f'Ambient sound type: {vc.ambient_sound_type}')
            self.stdout.write(f'Ambient sound volume: {vc.ambient_sound_volume}')
            self.stdout.write(f'Ambient sound URL: {vc.ambient_sound_url}')
            self.stdout.write(f'Thinking sound enabled: {vc.thinking_sound_enabled}')
            self.stdout.write(f'Thinking sound primary: {vc.thinking_sound_primary}')
            self.stdout.write(f'Thinking sound primary volume: {vc.thinking_sound_primary_volume}')
            self.stdout.write(f'Thinking sound secondary: {vc.thinking_sound_secondary}')
            self.stdout.write(f'Thinking sound secondary volume: {vc.thinking_sound_secondary_volume}')
            
            # Test 2: Simulate frontend save request
            client = Client()
            client.force_login(user)
            
            config_data = {
                "voice": {
                    "voice_id": "alloy",
                    "ambient_sound_enabled": True,
                    "ambient_sound_type": "custom",
                    "ambient_sound_volume": "50.0",
                    "ambient_sound_url": "https://example.com/rain.mp3",
                    "thinking_sound_enabled": True,
                    "thinking_sound_primary": "keyboard_typing2",
                    "thinking_sound_primary_volume": "0.9",
                    "thinking_sound_secondary": "none",
                    "thinking_sound_secondary_volume": "0.0"
                }
            }
            
            # Make the request to save assistant config
            response = client.post(
                f'/assistants/{assistant.id}/save/',
                data=json.dumps(config_data),
                content_type='application/json',
                HTTP_X_CSRFTOKEN='test-token'
            )
            
            self.stdout.write(f'\n=== Save Request Result ===')
            self.stdout.write(f'Response status: {response.status_code}')
            
            if response.status_code == 200:
                response_data = response.json()
                self.stdout.write(f'Success: {response_data.get("success", False)}')
                self.stdout.write(f'Message: {response_data.get("message", "No message")}')
                
                # Test 3: Verify the configuration was saved
                vc.refresh_from_db()
                self.stdout.write('\n=== Updated Configuration ===')
                self.stdout.write(f'Ambient sound enabled: {vc.ambient_sound_enabled}')
                self.stdout.write(f'Ambient sound type: {vc.ambient_sound_type}')
                self.stdout.write(f'Ambient sound volume: {vc.ambient_sound_volume}')
                self.stdout.write(f'Ambient sound URL: {vc.ambient_sound_url}')
                self.stdout.write(f'Thinking sound enabled: {vc.thinking_sound_enabled}')
                self.stdout.write(f'Thinking sound primary: {vc.thinking_sound_primary}')
                self.stdout.write(f'Thinking sound primary volume: {vc.thinking_sound_primary_volume}')
                self.stdout.write(f'Thinking sound secondary: {vc.thinking_sound_secondary}')
                self.stdout.write(f'Thinking sound secondary volume: {vc.thinking_sound_secondary_volume}')
                
                # Verify values match
                success = True
                success &= vc.ambient_sound_enabled == True
                success &= vc.ambient_sound_type == "custom"
                success &= vc.ambient_sound_volume == Decimal("50.0")
                success &= vc.ambient_sound_url == "https://example.com/rain.mp3"
                success &= vc.thinking_sound_enabled == True
                success &= vc.thinking_sound_primary == "keyboard_typing2"
                success &= vc.thinking_sound_primary_volume == Decimal("0.9")
                success &= vc.thinking_sound_secondary == "none"
                success &= vc.thinking_sound_secondary_volume == Decimal("0.0")
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS('\n✅ End-to-end ambient and thinking sound test PASSED!')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('\n❌ Configuration values do not match expected values!')
                    )
            else:
                response_text = response.content.decode('utf-8')
                self.stdout.write(
                    self.style.ERROR(f'Save request failed: {response_text}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during test: {str(e)}')
            )
            raise
