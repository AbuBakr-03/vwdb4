from django.core.management.base import BaseCommand
from django.db.models import Q
from people.models import Contact
from collections import defaultdict


class Command(BaseCommand):
    help = 'Clean up duplicate contacts based on various criteria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--tenant',
            type=str,
            default='zain_bh',
            help='Tenant ID to process (default: zain_bh)',
        )

    def handle(self, *args, **options):
        tenant_id = options['tenant']
        dry_run = options['dry_run']
        
        self.stdout.write(f"Processing tenant: {tenant_id}")
        if dry_run:
            self.stdout.write("DRY RUN MODE - No contacts will be deleted")
        
        # Find duplicates by different criteria
        duplicates_found = self.find_duplicates(tenant_id)
        
        if not duplicates_found:
            self.stdout.write(self.style.SUCCESS("No duplicates found!"))
            return
        
        # Display duplicates
        self.display_duplicates(duplicates_found)
        
        if not dry_run:
            # Ask for confirmation
            confirm = input("\nDo you want to proceed with deletion? (yes/no): ")
            if confirm.lower() != 'yes':
                self.stdout.write("Operation cancelled.")
                return
            
            # Clean up duplicates
            deleted_count = self.cleanup_duplicates(duplicates_found)
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} duplicate contacts."))
        else:
            self.stdout.write(f"\nDRY RUN: Would delete {sum(len(dups) - 1 for dups in duplicates_found.values())} duplicate contacts.")

    def find_duplicates(self, tenant_id):
        """Find duplicate contacts by various criteria."""
        duplicates = defaultdict(list)
        
        # Find duplicates by email
        email_duplicates = self.find_email_duplicates(tenant_id)
        if email_duplicates:
            duplicates['email'] = email_duplicates
        
        # Find duplicates by external_id
        external_id_duplicates = self.find_external_id_duplicates(tenant_id)
        if external_id_duplicates:
            duplicates['external_id'] = external_id_duplicates
        

        
        # Find duplicates by phone numbers
        phone_duplicates = self.find_phone_duplicates(tenant_id)
        if phone_duplicates:
            duplicates['phone'] = phone_duplicates
        
        return duplicates

    def find_email_duplicates(self, tenant_id):
        """Find contacts with duplicate emails."""
        from django.db.models import Count
        
        duplicate_emails = Contact.objects.filter(
            tenant_id=tenant_id,
            email__isnull=False
        ).exclude(email='').values('email').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        duplicates = []
        for dup in duplicate_emails:
            contacts = Contact.objects.filter(
                tenant_id=tenant_id,
                email=dup['email']
            ).order_by('created_at')
            duplicates.append(list(contacts))
        
        return duplicates

    def find_external_id_duplicates(self, tenant_id):
        """Find contacts with duplicate external IDs."""
        from django.db.models import Count
        
        duplicate_ids = Contact.objects.filter(
            tenant_id=tenant_id,
            external_id__isnull=False
        ).exclude(external_id='').values('external_id').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        duplicates = []
        for dup in duplicate_ids:
            contacts = Contact.objects.filter(
                tenant_id=tenant_id,
                external_id=dup['external_id']
            ).order_by('created_at')
            duplicates.append(list(contacts))
        
        return duplicates



    def find_phone_duplicates(self, tenant_id):
        """Find contacts with duplicate phone numbers."""
        from django.db.models import Count
        
        duplicate_phones = Contact.objects.filter(
            tenant_id=tenant_id,
            phone__isnull=False
        ).exclude(phone='').values('phone').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        duplicates = []
        for dup in duplicate_phones:
            contacts = Contact.objects.filter(
                tenant_id=tenant_id,
                phone=dup['phone']
            ).order_by('created_at')
            duplicates.append(list(contacts))
        
        return duplicates

    def display_duplicates(self, duplicates):
        """Display found duplicates."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("DUPLICATE CONTACTS FOUND")
        self.stdout.write("="*60)
        
        for criteria, dup_groups in duplicates.items():
            self.stdout.write(f"\n{criteria.upper()} DUPLICATES:")
            self.stdout.write("-" * 40)
            
            for i, dup_group in enumerate(dup_groups, 1):
                self.stdout.write(f"\nGroup {i}:")
                for j, contact in enumerate(dup_group):
                    status = "KEEP" if j == 0 else "DELETE"
                    self.stdout.write(f"  {status}: {contact} (ID: {contact.id}, Created: {contact.created_at})")

    def cleanup_duplicates(self, duplicates):
        """Remove duplicate contacts, keeping the oldest one."""
        deleted_count = 0
        
        for criteria, dup_groups in duplicates.items():
            for dup_group in dup_groups:
                # Keep the first (oldest) contact, delete the rest
                contacts_to_delete = dup_group[1:]
                for contact in contacts_to_delete:
                    contact.delete()
                    deleted_count += 1
        
        return deleted_count
