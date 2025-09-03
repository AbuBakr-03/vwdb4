from django.db import migrations, models


def convert_phones_to_phone(apps, schema_editor):
    """Convert phones JSONField to single phone field."""
    Contact = apps.get_model('people', 'Contact')
    
    for contact in Contact.objects.all():
        # Get the first phone number from the phones array, or empty string if none
        if hasattr(contact, 'phones') and contact.phones:
            # Extract first phone number from JSON array
            if isinstance(contact.phones, list) and len(contact.phones) > 0:
                contact.phone = str(contact.phones[0]) if contact.phones[0] else ''
            else:
                contact.phone = ''
        else:
            contact.phone = ''
        contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_contact_unique_tenant_external_id_and_more'),
    ]

    operations = [
        # Add the new phone field
        migrations.AddField(
            model_name='contact',
            name='phone',
            field=models.CharField(default='', max_length=20, help_text='Phone number in E.164 format'),
        ),
        
        # Convert data from phones to phone
        migrations.RunPython(convert_phones_to_phone, reverse_code=migrations.RunPython.noop),
        
        # Remove the old phones field
        migrations.RemoveField(
            model_name='contact',
            name='phones',
        ),
    ]
