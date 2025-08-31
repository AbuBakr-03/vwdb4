from django.core.management.base import BaseCommand
from people.models import Contact


class Command(BaseCommand):
    help = 'Clean up test contacts from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete ALL contacts (use with caution)',
        )

    def handle(self, *args, **options):
        if options['all']:
            contacts = Contact.objects.all()
            action = 'delete ALL'
        else:
            # Delete contacts with TEST_ in external_id or international phone numbers
            contacts = Contact.objects.filter(
                external_id__startswith='TEST_'
            ) | Contact.objects.filter(
                phones__contains=['+81', '+34', '+44', '+1', '+966', '+971']
            )
            action = 'delete test/international'

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would {action} {contacts.count()} contacts')
            )
            for contact in contacts:
                self.stdout.write(f'  - {contact.display_name} ({contact.primary_phone})')
        else:
            count = contacts.count()
            contacts.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {count} contacts')
            )
