/**
 * Contact Creation Form JavaScript
 * Handles form functionality, tab switching, CSV import, and phone numbers with full validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // ============================================================================
    // TAB SWITCHING
    // ============================================================================
    
    const manualTab = document.getElementById('manual-tab');
    const csvTab = document.getElementById('csv-tab');
    const manualForm = document.getElementById('manual-form');
    const csvForm = document.getElementById('csv-form');
    
    manualTab.addEventListener('click', function() {
        manualTab.classList.add('tab-active');
        csvTab.classList.remove('tab-active');
        manualForm.style.display = 'block';
        csvForm.style.display = 'none';
    });
    
    csvTab.addEventListener('click', function() {
        csvTab.classList.add('tab-active');
        manualTab.classList.remove('tab-active');
        csvForm.style.display = 'block';
        manualForm.style.display = 'none';
    });
    

    
    // ============================================================================
    // FORM SUBMISSION
    // ============================================================================
    
    const contactForm = document.getElementById('contact-form');
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = new FormData(contactForm);
        const data = {};
        
        // Handle regular fields
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Validate required fields
        const errors = validateForm(data);
        if (errors.length > 0) {
            showMessage(errors.join('<br>'), 'error');
            return;
        }
        
        // Submit form
        submitContact(data);
    });
    
    function validateForm(data) {
        const errors = [];
        
        if (!data.first_name && !data.last_name) {
            errors.push('Contact must have first name or last name');
        }
        
        // Phone number is now required
        if (!data.phone || !data.phone.trim()) {
            errors.push('Phone number is required');
        } else if (!isValidPhoneNumber(data.phone.trim())) {
            errors.push(`Invalid phone number: ${data.phone.trim()}`);
        }
        
        return errors;
    }
    
    function submitContact(data) {
        // Show loading state
        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Creating...';
        submitBtn.disabled = true;
        
        fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showMessage(result.message, 'success');
                // Reset form
                contactForm.reset();
                // Reset phone numbers to single field
                const phoneContainer = document.getElementById('phone-numbers');
                phoneContainer.innerHTML = `
                    <div class="flex gap-2">
                        <input type="tel" name="phones[]" placeholder="+1234567890" 
                               class="input input-bordered flex-1" />
                        <button type="button" class="btn btn-square btn-outline btn-sm" onclick="removePhone(this)">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                `;
                // Reset tenant_id to default
                document.querySelector('input[name="tenant_id"]').value = 'zain_bh';
            } else {
                showMessage(result.message, 'error');
            }
        })
        .catch(error => {
            showMessage('Error creating contact. Please try again.', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            // Restore button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }
    
    // ============================================================================
    // CSV IMPORT WITH PREVIEW AND FULL VALIDATION
    // ============================================================================
    
    let csvData = [];
    let validContacts = [];
    let duplicateContacts = [];
    let errorRows = [];
    
    const csvFileInput = document.getElementById('csv-file');
    const csvPreview = document.getElementById('csv-preview');
    const csvCount = document.getElementById('csv-count');
    const csvHeaders = document.getElementById('csv-headers');
    const csvBody = document.getElementById('csv-body');
    const processCsvBtn = document.getElementById('process-csv-btn');
    const importCsvBtn = document.getElementById('import-csv-btn');
    const clearCsvBtn = document.getElementById('clear-csv-btn');
    const csvErrors = document.getElementById('csv-errors');
    const csvErrorDetails = document.getElementById('csv-error-details');
    const csvDuplicateErrors = document.getElementById('csv-duplicate-errors');
    const csvDuplicateDetails = document.getElementById('csv-duplicate-details');
    
    // File input change handler
    csvFileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            if (!file.name.toLowerCase().endsWith('.csv')) {
                showMessage('Please select a valid CSV file', 'error');
                return;
            }
            parseCSVFile(file);
        }
    });
    
    // Process CSV button
    processCsvBtn.addEventListener('click', function() {
        processCSVData();
    });
    
    // Import CSV button
    importCsvBtn.addEventListener('click', function() {
        importValidContacts();
    });
    
    // Clear CSV button
    clearCsvBtn.addEventListener('click', function() {
        clearCSVData();
    });
    
    function parseCSVFile(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const text = e.target.result;
            const lines = text.split('\n').filter(line => line.trim());
            
            if (lines.length < 2) {
                showMessage('CSV file must contain headers and at least one data row', 'error');
                return;
            }
            
            // Parse CSV
            const headers = parseCSVRow(lines[0]);
            csvData = [];
            
            for (let i = 1; i < lines.length; i++) {
                if (lines[i].trim()) {
                    const rowData = parseCSVRow(lines[i]);
                    const contact = {};
                    headers.forEach((header, index) => {
                        contact[header.toLowerCase().trim()] = rowData[index] || '';
                    });
                    contact._row = i + 1; // Store row number for error reporting
                    csvData.push(contact);
                }
            }
            
            displayCSVPreview(headers, csvData);
            showProcessButton();
        };
        reader.readAsText(file);
    }
    
    function parseCSVRow(row) {
        const result = [];
        let current = '';
        let inQuotes = false;
        
        for (let i = 0; i < row.length; i++) {
            const char = row[i];
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                result.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        result.push(current.trim());
        return result;
    }
    
    function displayCSVPreview(headers, data) {
        // Show preview section
        csvPreview.style.display = 'block';
        csvCount.textContent = `${data.length} contacts found`;
        
        // Clear previous content
        csvHeaders.innerHTML = '';
        csvBody.innerHTML = '';
        
        // Add headers
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            th.className = 'text-xs font-semibold';
            csvHeaders.appendChild(th);
        });
        
        // Add rows (limit to first 10 for preview)
        const previewData = data.slice(0, 10);
        previewData.forEach(contact => {
            const tr = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = contact[header.toLowerCase().trim()] || '';
                td.className = 'text-xs';
                tr.appendChild(td);
            });
            csvBody.appendChild(tr);
        });
        
        if (data.length > 10) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = headers.length;
            td.textContent = `... and ${data.length - 10} more rows`;
            td.className = 'text-xs text-center text-base-content/50 italic';
            tr.appendChild(td);
            csvBody.appendChild(tr);
        }
    }
    
    function showProcessButton() {
        processCsvBtn.style.display = 'inline-flex';
        clearCsvBtn.style.display = 'inline-flex';
    }
    
    function processCSVData() {
        validContacts = [];
        duplicateContacts = [];
        errorRows = [];
        
        // Show loading state
        const originalText = processCsvBtn.innerHTML;
        processCsvBtn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Processing...';
        processCsvBtn.disabled = true;
        
        // Validate each contact
        csvData.forEach(contact => {
            const validation = validateCSVContact(contact);
            if (validation.isValid) {
                // Check for duplicates (simplified - checking email and phone)
                const isDuplicate = checkForDuplicate(contact);
                if (isDuplicate) {
                    duplicateContacts.push({
                        contact: contact,
                        reason: 'Email or phone already exists'
                    });
                } else {
                    validContacts.push(contact);
                }
            } else {
                errorRows.push({
                    row: contact._row,
                    contact: contact,
                    errors: validation.errors
                });
            }
        });
        
        // Display results
        displayProcessingResults();
        
        // Restore button state
        processCsvBtn.innerHTML = originalText;
        processCsvBtn.disabled = false;
        
        // Show import button if there are valid contacts
        if (validContacts.length > 0) {
            importCsvBtn.style.display = 'inline-flex';
            importCsvBtn.innerHTML = `<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>Import ${validContacts.length} Contacts`;
        }
    }
    
    function validateCSVContact(contact) {
        const errors = [];
        
        // Validate required fields
        if (!contact.first_name && !contact.last_name) {
            errors.push('Contact must have first_name or last_name');
        }
        
        // Validate phone number is required
        const phoneNumber = contact.phone_number || contact.phones; // Support both field names
        if (!phoneNumber || !phoneNumber.trim()) {
            errors.push('Phone number is required');
        } else {
            const phone = phoneNumber.trim();
            if (!isValidPhoneNumber(cleanPhoneNumber(phone))) {
                errors.push(`Invalid phone number: ${phone}`);
            }
        }
        
        // Validate email if provided
        if (contact.email && !isValidEmail(contact.email)) {
            errors.push(`Invalid email: ${contact.email}`);
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }
    
    function checkForDuplicate(contact) {
        // Check for duplicates within the current batch and provide better duplicate detection
        const email = contact.email ? contact.email.toLowerCase().trim() : '';
        const phone = (contact.phone_number || contact.phones) ? cleanPhoneNumber((contact.phone_number || contact.phones).trim()) : '';
        const externalId = contact.external_id ? contact.external_id.trim() : '';
        const firstName = contact.first_name ? contact.first_name.trim().toLowerCase() : '';
        const lastName = contact.last_name ? contact.last_name.trim().toLowerCase() : '';
        
        // Check against existing valid contacts in this batch
        const batchDuplicate = validContacts.some(existing => {
            // Check by email
            if (email && existing.email && existing.email.toLowerCase().trim() === email) {
                return true;
            }
            
            // Check by external ID
            if (externalId && existing.external_id && existing.external_id.trim() === externalId) {
                return true;
            }
            
            // Check by name combination
            if (firstName && lastName && existing.first_name && existing.last_name) {
                const existingFirstName = existing.first_name.trim().toLowerCase();
                const existingLastName = existing.last_name.trim().toLowerCase();
                if (firstName === existingFirstName && lastName === existingLastName) {
                    return true;
                }
            }
            
            // Check by phone
            if (phone) {
                const existingPhone = (existing.phone_number || existing.phones) ? cleanPhoneNumber((existing.phone_number || existing.phones).trim()) : '';
                if (phone === existingPhone) {
                    return true;
                }
            }
            
            return false;
        });
        
        if (batchDuplicate) {
            return true;
        }
        
        // Note: We can't check against database duplicates here since this is client-side
        // The backend will handle database duplicate checking when the CSV is actually imported
        return false;
    }
    
    function cleanPhoneNumber(phone) {
        if (!phone) return '';
        phone = phone.trim();
        // Ensure it's exactly 8 digits
        if (/^\d{8}$/.test(phone)) {
            return phone;
        }
        return phone; // Return as-is if not 8 digits
    }
    
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    function displayProcessingResults() {
        // Hide previous error messages
        csvErrors.style.display = 'none';
        csvDuplicateErrors.style.display = 'none';
        
        // Show processing errors if any
        if (errorRows.length > 0) {
            csvErrorDetails.innerHTML = '';
            errorRows.forEach(error => {
                const div = document.createElement('div');
                div.innerHTML = `<strong>Row ${error.row}:</strong> ${error.errors.join(', ')}`;
                csvErrorDetails.appendChild(div);
            });
            csvErrors.style.display = 'block';
        }
        
        // Show duplicate errors if any
        if (duplicateContacts.length > 0) {
            csvDuplicateDetails.innerHTML = '';
            duplicateContacts.forEach(duplicate => {
                const div = document.createElement('div');
                const name = `${duplicate.contact.first_name} ${duplicate.contact.last_name}`.trim();
                const duplicateReason = getDuplicateReason(duplicate.contact, duplicate.reason);
                div.innerHTML = `<strong>${name}</strong> - ${duplicateReason}`;
                csvDuplicateDetails.appendChild(div);
            });
            csvDuplicateErrors.style.display = 'block';
        }
        
        // Update count
        csvCount.textContent = `${validContacts.length} valid contacts, ${duplicateContacts.length} duplicates, ${errorRows.length} errors`;
    }
    
    function importValidContacts() {
        if (validContacts.length === 0) {
            showMessage('No valid contacts to import', 'warning');
            return;
        }
        
        // Show loading state
        const originalText = importCsvBtn.innerHTML;
        importCsvBtn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Importing...';
        importCsvBtn.disabled = true;
        
        // Convert contacts back to CSV format for the backend
        const csvContent = convertContactsToCSV(validContacts);
        const csvBlob = new Blob([csvContent], { type: 'text/csv' });
        const csvFile = new File([csvBlob], 'contacts.csv', { type: 'text/csv' });
        
        // Create FormData and submit to CSV import endpoint
        const formData = new FormData();
        formData.append('csv_file', csvFile);
        
        fetch('/people/contacts/import-csv/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
                clearCSVData();
            } else {
                showMessage(data.message || 'Failed to import contacts', 'error');
            }
        })
        .catch(error => {
            showMessage('Error importing contacts. Please try again.', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            // Restore button state
            importCsvBtn.innerHTML = originalText;
            importCsvBtn.disabled = false;
        });
    }
    
    function convertContactsToCSV(contacts) {
        // Create CSV header
        const headers = ['first_name', 'last_name', 'email', 'phone_number', 'external_id', 'tenant_id'];
        let csvContent = headers.join(',') + '\n';
        
        // Add each contact as a CSV row
        contacts.forEach(contact => {
            const row = [
                contact.first_name || '',
                contact.last_name || '',
                contact.email || '',
                (contact.phone_number || contact.phones) || '',
                contact.external_id || '',
                'zain_bh'
            ];
            csvContent += row.map(field => `"${field}"`).join(',') + '\n';
        });
        
        return csvContent;
    }
    
    function clearCSVData() {
        csvData = [];
        validContacts = [];
        duplicateContacts = [];
        errorRows = [];
        
        csvFileInput.value = '';
        csvPreview.style.display = 'none';
        processCsvBtn.style.display = 'none';
        importCsvBtn.style.display = 'none';
        clearCsvBtn.style.display = 'none';
        csvErrors.style.display = 'none';
        csvDuplicateErrors.style.display = 'none';
    }
    
    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================
    
    function getDuplicateReason(contact, reason) {
        // Provide more detailed duplicate reason information
        const reasons = [];
        
        if (contact.email) {
            reasons.push('email');
        }
        if (contact.external_id) {
            reasons.push('external ID');
        }
        if (contact.first_name && contact.last_name) {
            reasons.push('name');
        }
        if (contact.phone_number || contact.phones) {
            reasons.push('phone');
        }
        
        if (reasons.length > 0) {
            return `Duplicate detected by: ${reasons.join(', ')}`;
        }
        
        return reason || 'Duplicate contact detected';
    }
    
    function getCSRFToken() {
        // Try to get CSRF token from form input first
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) {
            console.log('CSRF token found in form input:', token.value ? 'Yes' : 'No');
            return token.value;
        }
        
        // Fallback to meta tag
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            console.log('CSRF token found in meta tag:', metaToken.getAttribute('content') ? 'Yes' : 'No');
            return metaToken.getAttribute('content');
        }
        
        console.warn('No CSRF token found!');
        return '';
    }
    
    function isValidPhoneNumber(phone) {
        // Basic phone validation (8 digits only)
        const phoneRegex = /^\d{8}$/;
        return phoneRegex.test(phone);
    }
    
    function showMessage(message, type = 'info') {
        const container = document.getElementById('message-container');
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} mb-4 shadow-lg`;
        alertDiv.innerHTML = `
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                ${getAlertIcon(type)}
            </svg>
            <span>${message}</span>
            <button type="button" onclick="this.parentElement.remove()" class="btn btn-ghost btn-xs">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
        `;
        
        container.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    function getAlertIcon(type) {
        switch (type) {
            case 'success':
                return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>';
            case 'error':
                return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>';
            case 'warning':
                return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path>';
            default:
                return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>';
        }
    }
    
    // ============================================================================
    // SAMPLE CSV DOWNLOAD
    // ============================================================================
    
    window.downloadSampleCSV = function() {
        const csvContent = `first_name,last_name,email,phone_number,external_id
John,Doe,john@example.com,12345678,EMP001
Jane,Smith,jane@example.com,87654321,EMP002
Michael,Johnson,michael@tech.com,98765432,EMP003
Sarah,Wilson,sarah@example.com,11223344,EMP004
David,Brown,david@example.com,55667788,EMP005`;
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sample_contacts.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    };
});
