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
    // PARTY TYPE SWITCHING
    // ============================================================================
    
    const partyTypeRadios = document.querySelectorAll('input[name="party_type"]');
    const personFields = document.getElementById('person-fields');
    const companyFields = document.getElementById('company-fields');
    
    function toggleFields() {
        const selectedType = document.querySelector('input[name="party_type"]:checked').value;
        
        if (selectedType === 'person') {
            personFields.style.display = 'grid';
            companyFields.style.display = 'none';
        } else {
            personFields.style.display = 'none';
            companyFields.style.display = 'grid';
        }
    }
    
    partyTypeRadios.forEach(radio => {
        radio.addEventListener('change', toggleFields);
    });
    
    // Initial state
    toggleFields();
    
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
        
        if (!data.party_type) {
            errors.push('Contact type is required');
        }
        
        if (data.party_type === 'person') {
            if (!data.first_name && !data.last_name) {
                errors.push('Person must have first name or last name');
            }
        } else if (data.party_type === 'company') {
            if (!data.name) {
                errors.push('Company name is required');
            }
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
    // CSV IMPORT
    // ============================================================================
    
    const importCsvBtn = document.getElementById('import-csv-btn');
    const csvFileInput = document.getElementById('csv-file');
    
    importCsvBtn.addEventListener('click', function() {
        const file = csvFileInput.files[0];
        if (!file) {
            showMessage('Please select a CSV file', 'error');
            return;
        }
        
        if (!file.name.toLowerCase().endsWith('.csv')) {
            showMessage('Please select a valid CSV file', 'error');
            return;
        }
        
        importCSV(file);
    });
    
    function importCSV(file) {
        // Show loading state
        const originalText = importCsvBtn.innerHTML;
        importCsvBtn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Importing...';
        importCsvBtn.disabled = true;
        
        const formData = new FormData();
        formData.append('csv_file', file);
        
        fetch('{% url "people:contact_import_csv" %}', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showMessage(result.message, 'success');
                if (result.errors && result.errors.length > 0) {
                    showMessage(`Import completed with ${result.errors.length} errors:<br>${result.errors.join('<br>')}`, 'warning');
                }
                csvFileInput.value = '';
            } else {
                showMessage(result.message, 'error');
            }
        })
        .catch(error => {
            showMessage('Error importing CSV. Please try again.', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            // Restore button state
            importCsvBtn.innerHTML = originalText;
            importCsvBtn.disabled = false;
        });
    }
    
    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================
    
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
