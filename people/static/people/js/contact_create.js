/**
 * Contact Creation Form JavaScript
 * Handles form functionality, tab switching, and CSV import
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
    // PHONE NUMBER MANAGEMENT
    // ============================================================================
    
    window.addPhone = function() {
        const phoneContainer = document.getElementById('phone-numbers');
        const phoneDiv = document.createElement('div');
        phoneDiv.className = 'flex gap-2';
        phoneDiv.innerHTML = `
            <input type="tel" name="phones[]" placeholder="+1234567890" 
                   class="input input-bordered flex-1" />
            <button type="button" class="btn btn-square btn-outline btn-sm" onclick="removePhone(this)">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
        phoneContainer.appendChild(phoneDiv);
    };
    
    window.removePhone = function(button) {
        const phoneContainer = document.getElementById('phone-numbers');
        if (phoneContainer.children.length > 1) {
            button.closest('.flex').remove();
        }
    };
    
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
             if (key === 'phones[]') {
                 if (!data.phones) data.phones = [];
                 if (value.trim()) data.phones.push(value.trim());
             } else if (key === 'segments') {
                 if (!data.segments) data.segments = [];
                 if (value) data.segments.push(parseInt(value));
             } else {
                 data[key] = value;
             }
         }
         
         // Handle new segments field
         if (data.new_segments && data.new_segments.trim()) {
             const newSegmentNames = data.new_segments.split(',').map(s => s.trim()).filter(s => s);
             if (!data.new_segment_names) data.new_segment_names = [];
             data.new_segment_names = newSegmentNames;
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
        
        if (data.phones && data.phones.length > 0) {
            for (let phone of data.phones) {
                if (!isValidPhoneNumber(phone)) {
                    errors.push(`Invalid phone number: ${phone}`);
                }
            }
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
                // Reset segments
                document.querySelectorAll('input[name="segments"]').forEach(cb => cb.checked = false);
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
    // CSV IMPORT WITH PREVIEW
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
        
        // Validate phone numbers if provided
        if (contact.phones) {
            const phones = contact.phones.split(',').map(p => p.trim()).filter(p => p);
            for (let phone of phones) {
                if (!isValidPhoneNumber(cleanPhoneNumber(phone))) {
                    errors.push(`Invalid phone number: ${phone}`);
                }
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
        // Simplified duplicate check - in real implementation, this would check against the database
        // For now, we'll just check against already processed contacts in this session
        const email = contact.email ? contact.email.toLowerCase().trim() : '';
        const phones = contact.phones ? contact.phones.split(',').map(p => cleanPhoneNumber(p.trim())).filter(p => p) : [];
        
        // Check against existing valid contacts in this batch
        return validContacts.some(existing => {
            if (email && existing.email && existing.email.toLowerCase().trim() === email) {
                return true;
            }
            if (phones.length > 0 && existing.phones) {
                const existingPhones = existing.phones.split(',').map(p => cleanPhoneNumber(p.trim())).filter(p => p);
                return phones.some(phone => existingPhones.includes(phone));
            }
            return false;
        });
    }
    
    function cleanPhoneNumber(phone) {
        if (!phone) return '';
        phone = phone.trim();
        // Add + if it's missing and looks like an international number
        if (!phone.startsWith('+') && /^\d{8,15}$/.test(phone)) {
            phone = '+' + phone;
        }
        return phone;
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
                div.innerHTML = `<strong>${name}</strong> - ${duplicate.reason}`;
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
        
                 // Convert to format expected by the backend
         const contactsData = validContacts.map(contact => ({
             first_name: contact.first_name || '',
             last_name: contact.last_name || '',
             email: contact.email || '',
             phones: contact.phones ? contact.phones.split(',').map(p => cleanPhoneNumber(p.trim())).filter(p => p) : [],
             company: contact.company || '',
             segments: contact.segments ? contact.segments.split(',').map(s => s.trim()).filter(s => s) : [],
             new_segment_names: contact.segments ? contact.segments.split(',').map(s => s.trim()).filter(s => s) : [],
             timezone: contact.timezone || '',
             external_id: contact.external_id || '',
             tenant_id: contact.tenant_id || 'default'
         }));
        
        // Submit to backend (you may need to update the backend to handle batch import)
        Promise.all(contactsData.map(contactData => 
            fetch('', {
            method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(contactData)
            }).then(response => response.json())
        ))
        .then(results => {
            const successful = results.filter(r => r.success).length;
            const failed = results.filter(r => !r.success).length;
            
            if (successful > 0) {
                showMessage(`Successfully imported ${successful} contacts${failed > 0 ? ` (${failed} failed)` : ''}`, 'success');
                clearCSVData();
            } else {
                showMessage('Failed to import contacts', 'error');
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
    
    function getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    function isValidPhoneNumber(phone) {
        // Basic phone validation (E.164 format)
        const phoneRegex = /^\+[1-9]\d{6,14}$/;
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
         const csvContent = `first_name,last_name,email,phones,company,segments,timezone,tenant_id
John,Doe,john@example.com,"+1234567890,+1987654321",Acme Corp,"VIP,High Value",UTC,default
Jane,Smith,jane@example.com,+1234567890,Tech Solutions,"Sales Qualified,Active",UTC,default
Michael,Johnson,michael@tech.com,+1987654321,Tech Solutions,"Enterprise,VIP",UTC,default`;
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sample_contacts.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    };
});
