# People App - Contact Management

## Duplicate Prevention

The People app now includes comprehensive duplicate prevention to avoid creating duplicate contacts when importing CSV files or manually creating contacts.

### Duplicate Detection Criteria

The system checks for duplicates based on the following criteria:

1. **Email Address** - Exact match (case-insensitive)
2. **External ID** - Exact match (CRM/HRIS IDs)
3. **Phone Number** - Exact match for phone number

Note: Name combinations (first name + last name) are NOT considered duplicates, as multiple people can have the same name (e.g., Ahmad Mohammad).

### How It Works

1. **Frontend Validation**: When processing CSV files, the frontend checks for duplicates within the current batch
2. **Backend Validation**: When importing, the backend performs comprehensive duplicate checking against the database
3. **Automatic Skipping**: Duplicate contacts are automatically skipped during import with detailed error messages

### CSV Import Process

1. Upload CSV file
2. Click "Process CSV" to validate and check for duplicates
3. Review any validation errors or duplicate warnings
4. Click "Import Contacts" to import only unique contacts

### Cleanup Existing Duplicates

If you have existing duplicate contacts in your database, you can use the management command to clean them up:

```bash
# First, run in dry-run mode to see what would be deleted
python manage.py cleanup_duplicates --dry-run

# Then run the actual cleanup (will prompt for confirmation)
python manage.py cleanup_duplicates

# Process a specific tenant
python manage.py cleanup_duplicates --tenant=your_tenant_id
```

The cleanup command will:
- Keep the oldest contact (based on creation date)
- Delete newer duplicates
- Show detailed information about what will be deleted
- Ask for confirmation before proceeding

### CSV Format

The system expects CSV files with the following columns:

- `first_name` (required if no last_name)
- `last_name` (required if no first_name)
- `phone_number` (required, used for duplicate checking)
- `email` (optional, used for duplicate checking)
- `external_id` (optional, used for duplicate checking)
- `tenant_id` (optional, defaults to 'zain_bh')

### Best Practices

1. **Always use unique external IDs** from your CRM/HRIS system
2. **Include email addresses** when possible for better duplicate detection
3. **Use consistent phone number formatting** (8 digits for Bahrain)
4. **Review duplicate warnings** before importing
5. **Run cleanup commands** periodically to maintain data quality

### Error Handling

- **Validation Errors**: Contacts with invalid data are skipped
- **Duplicate Warnings**: Existing contacts are identified and skipped
- **Import Summary**: Detailed report of successful imports and skipped duplicates
