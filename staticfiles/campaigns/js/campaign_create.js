/**
 * Campaign Creation Form JavaScript
 * Handles all form functionality, contact management, and UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // ============================================================================
    // FORM AUTO-SAVE & DRAFT MANAGEMENT
    // ============================================================================
    
    const form = document.querySelector('form');
    const formData = new FormData(form);

    // Save form data to localStorage every 30 seconds
    setInterval(function() {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            if (key !== 'csrfmiddlewaretoken') {
                if (key === 'days_of_week') {
                    if (!data[key]) data[key] = [];
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            }
        }
        localStorage.setItem('campaign_draft', JSON.stringify(data));
    }, 30000);

    // Load draft data on page load
    const draft = localStorage.getItem('campaign_draft');
    if (draft && !document.querySelector('input[name="name"]').value) {
        try {
            const data = JSON.parse(draft);
            for (let key in data) {
                if (key === 'days_of_week' && Array.isArray(data[key])) {
                    data[key].forEach(value => {
                        const checkbox = document.querySelector(`input[name="${key}"][value="${value}"]`);
                        if (checkbox) checkbox.checked = true;
                    });
                } else {
                    const field = document.querySelector(`[name="${key}"]`);
                    if (field) {
                        if (field.type === 'checkbox') {
                            field.checked = data[key] === 'on' || data[key] === true;
                        } else {
                            field.value = data[key];
                        }
                    }
                }
            }
        } catch (e) {
            console.error('Error loading draft:', e);
        }
    }

    // Clear draft when form is submitted
    form.addEventListener('submit', function() {
        localStorage.removeItem('campaign_draft');
    });

    // ============================================================================
    // CHANNEL & VOICE CONFIGURATION
    // ============================================================================
    
    const channelSelect = document.querySelector('select[name="channel"]');
    const voiceSection = document.querySelector('select[name="voice_id"]').closest('.form-control');
    
    function toggleVoiceSection() {
        if (channelSelect.value === 'voice') {
            voiceSection.style.display = 'block';
        } else {
            voiceSection.style.display = 'none';
        }
    }
    
    channelSelect.addEventListener('change', toggleVoiceSection);
    toggleVoiceSection(); // Initial state

    // ============================================================================
    // SCRIPT TEMPLATE HANDLING
    // ============================================================================
    
    const scriptTemplateSelect = document.querySelector('select[name="script_template"]');
    const scriptPreview = document.getElementById('script-preview');
    const scriptContent = document.getElementById('script-content');
    const scriptVariables = document.getElementById('script-variables');
    const scriptLanguage = document.getElementById('script-language');
    const scriptChannel = document.getElementById('script-channel');
    const scriptContentTextarea = document.querySelector('textarea[name="script_content"]');
    
    // Hardcoded script templates data
    const scriptTemplates = {
        'hr_screening_general': {
            script: `Hello {{first_name}}, this is {{agent_name}} calling from {{company_name}} regarding your recent application for the {{position}} role.

We'd like to schedule a brief screening call to discuss your background and experience. The call will take about 15-20 minutes.

Are you available for a call this week? We can accommodate your schedule.`,
            variables: ['first_name', 'agent_name', 'company_name', 'position'],
            language: 'English',
            channel: 'Voice'
        },
        'hr_screening_technical': {
            script: `Hi {{first_name}}, this is {{agent_name}} from {{company_name}} HR department.

We're calling about your application for the {{position}} position. Before we proceed to the technical interview, we need to verify a few details about your experience with {{technologies}}.

Could you confirm your years of experience with these technologies? Also, are you comfortable with {{work_requirements}}?`,
            variables: ['first_name', 'agent_name', 'company_name', 'position', 'technologies', 'work_requirements'],
            language: 'English',
            channel: 'Voice'
        },
        'collections_reminder': {
            script: `Good {{time_of_day}}, {{customer_name}}. This is {{agent_name}} calling from {{company_name}} regarding your account {{account_number}}.

We're calling to remind you that you have an outstanding balance of {{amount_due}} that was due on {{due_date}}.

We understand that sometimes unexpected expenses arise. Would you like to discuss payment options or set up a payment plan?`,
            variables: ['time_of_day', 'customer_name', 'agent_name', 'company_name', 'account_number', 'amount_due', 'due_date'],
            language: 'English',
            channel: 'Voice'
        },
        'collections_negotiation': {
            script: `Hello {{customer_name}}, this is {{agent_name}} from {{company_name}} collections department.

I'm calling about your account {{account_number}} with a balance of {{amount_due}}. I see you've been a customer for {{customer_years}} years, and we value your business.

Given your situation, we'd like to work with you. We can offer a {{discount_percentage}}% discount if you can pay {{settlement_amount}} by {{settlement_date}}. Would this work for you?`,
            variables: ['customer_name', 'agent_name', 'company_name', 'account_number', 'amount_due', 'customer_years', 'discount_percentage', 'settlement_amount', 'settlement_date'],
            language: 'English',
            channel: 'Voice'
        },
        'sales_cold_call': {
            script: `Hi {{prospect_name}}, this is {{agent_name}} calling from {{company_name}}.

I noticed that {{company_name}} helps businesses like yours with {{solution_benefit}}. We've been working with companies in {{industry}} to {{value_proposition}}.

I'd love to share a quick case study about how we helped {{similar_company}} achieve {{results}}. Would you be interested in a 15-minute conversation about this?`,
            variables: ['prospect_name', 'agent_name', 'company_name', 'solution_benefit', 'industry', 'value_proposition', 'similar_company', 'results'],
            language: 'English',
            channel: 'Voice'
        },
        'sales_follow_up': {
            script: `Hello {{prospect_name}}, this is {{agent_name}} following up from {{company_name}}.

We spoke {{days_ago}} about {{solution_name}} and how it could help with {{pain_point}}. You mentioned you were interested in {{specific_feature}}.

I wanted to check in and see if you've had a chance to review the proposal I sent. Do you have any questions about {{pricing}} or {{implementation_timeline}}?`,
            variables: ['prospect_name', 'agent_name', 'company_name', 'days_ago', 'solution_name', 'pain_point', 'specific_feature', 'pricing', 'implementation_timeline'],
            language: 'English',
            channel: 'Voice'
        },
        'appointment_reminder': {
            script: `Good {{time_of_day}}, {{patient_name}}. This is {{agent_name}} calling from {{clinic_name}} to remind you of your appointment tomorrow at {{appointment_time}}.

Your appointment is with Dr. {{doctor_name}} for {{procedure_type}}. Please arrive {{arrival_time}} minutes early to complete any necessary paperwork.

If you need to reschedule or have any questions, please call us at {{phone_number}}. We look forward to seeing you tomorrow.`,
            variables: ['time_of_day', 'patient_name', 'agent_name', 'clinic_name', 'appointment_time', 'doctor_name', 'procedure_type', 'arrival_time', 'phone_number'],
            language: 'English',
            channel: 'Voice'
        },
        'customer_survey': {
            script: `Hello {{customer_name}}, this is {{agent_name}} calling from {{company_name}}.

We value your feedback and would like to conduct a brief customer satisfaction survey about your recent experience with us. The survey will take about 5 minutes.

Your responses help us improve our services. Would you be willing to participate? We can call you back at a more convenient time if needed.`,
            variables: ['customer_name', 'agent_name', 'company_name'],
            language: 'English',
            channel: 'Voice'
        },
        'custom': {
            script: `[Custom script content will be entered below]`,
            variables: ['custom_variables'],
            language: 'Custom',
            channel: 'Custom'
        }
    };
    
    function updateScriptPreview() {
        const selectedTemplate = scriptTemplateSelect.value;
        if (selectedTemplate && scriptTemplates[selectedTemplate]) {
            const template = scriptTemplates[selectedTemplate];
            
            // Show script preview
            scriptContent.textContent = template.script;
            scriptVariables.textContent = template.variables.join(', ');
            scriptLanguage.textContent = template.language;
            scriptChannel.textContent = template.channel;
            scriptPreview.style.display = 'block';
            
            // Auto-fill script content textarea
            if (selectedTemplate !== 'custom') {
                scriptContentTextarea.value = template.script;
            } else {
                scriptContentTextarea.value = '';
            }
        } else {
            scriptPreview.style.display = 'none';
            scriptContentTextarea.value = '';
        }
    }
    
    scriptTemplateSelect.addEventListener('change', updateScriptPreview);

    // ============================================================================
    // CONTACT MANAGEMENT
    // ============================================================================
    
    const addContactBtn = document.getElementById('add-contact-btn');
    const clearContactsBtn = document.getElementById('clear-contacts-btn');
    const exportContactsBtn = document.getElementById('export-contacts-btn');
    const contactList = document.getElementById('contact-list');
    const contactCount = document.getElementById('contact-count');
    const contactsDataInput = document.getElementById('contacts-data');
    
    let contacts = [];
    
    function addContact() {
        const phone = document.querySelector('input[name="manual_phone"]').value.trim();
        const firstName = document.querySelector('input[name="manual_first_name"]').value.trim();
        const lastName = document.querySelector('input[name="manual_last_name"]').value.trim();
        
        if (!phone) {
            alert('Please enter a phone number');
            return;
        }
        
        // Check for duplicates
        const cleanPhone = cleanPhoneNumber(phone);
        const isDuplicate = contacts.some(c => c.phone === cleanPhone);
        
        if (isDuplicate) {
            showDuplicateError([{
                phone: cleanPhone,
                name: `${firstName} ${lastName}`.trim() || 'Unknown'
            }]);
            return;
        }
        
        const contact = {
            id: Date.now(),
            phone: cleanPhone,
            first_name: firstName,
            last_name: lastName
        };
        
        contacts.push(contact);
        updateContactDisplay();
        updateContactsData();
        
        // Clear input fields
        document.querySelector('input[name="manual_phone"]').value = '';
        document.querySelector('input[name="manual_first_name"]').value = '';
        document.querySelector('input[name="manual_last_name"]').value = '';
        
        // Show success message
        showSuccessMessage('Contact added successfully');
    }
    
    function removeContact(id) {
        console.log('removeContact called with ID:', id, 'Type:', typeof id);
        console.log('Contacts before removal:', contacts);
        console.log('Contact IDs:', contacts.map(c => ({ id: c.id, type: typeof c.id })));
        
        // Ensure id is a number for comparison
        const numericId = typeof id === 'string' ? parseInt(id) : id;
        console.log('Numeric ID for comparison:', numericId);
        
        contacts = contacts.filter(contact => {
            const contactId = typeof contact.id === 'string' ? parseInt(contact.id) : contact.id;
            return contactId !== numericId;
        });
        
        console.log('Contacts after removal:', contacts);
        updateContactDisplay();
        updateContactsData();
    }
    
    function updateContactDisplay() {
        if (contacts.length === 0) {
            contactList.innerHTML = `
                <div class="text-center text-base-content/50 py-4">
                    <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                    <p>No contacts added yet</p>
                    <p class="text-sm">Add contacts manually or upload a file</p>
                </div>
            `;
        } else {
            // Create a grid layout for contacts
            const contactsHtml = contacts.map(contact => `
                <div class="bg-base-100 p-3 rounded-lg border border-base-300 hover:border-primary/30 transition-colors" data-contact-id="${contact.id}">
                    <div class="flex items-start justify-between">
                        <div class="flex-1 min-w-0">
                            <div class="font-medium truncate">${contact.first_name} ${contact.last_name}</div>
                            <div class="text-sm text-base-content/70 font-mono">${contact.phone}</div>
                        </div>
                        <button type="button" class="remove-contact-btn btn btn-ghost btn-xs text-error hover:bg-error/10 ml-2 flex-shrink-0" data-contact-id="${contact.id}" onclick="removeContact(${contact.id})">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            `).join('');
            
            // Wrap contacts in a responsive grid
            contactList.innerHTML = `
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                    ${contactsHtml}
                </div>
            `;
        }
        
        contactCount.textContent = contacts.length;
    }
    
    function updateContactsData() {
        contactsDataInput.value = JSON.stringify(contacts);
    }
    
    function clearContacts() {
        if (confirm('Are you sure you want to clear all contacts?')) {
            contacts = [];
            updateContactDisplay();
            updateContactsData();
        }
    }
    
    function exportContacts() {
        if (contacts.length === 0) {
            alert('No contacts to export');
            return;
        }
        
        const csvContent = [
            ['Phone', 'First Name', 'Last Name'],
            ...contacts.map(contact => [contact.phone, contact.first_name, contact.last_name])
        ].map(row => row.join(',')).join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'campaign_contacts.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    }
    
    // Event listeners
    addContactBtn.addEventListener('click', addContact);
    clearContactsBtn.addEventListener('click', clearContacts);
    exportContactsBtn.addEventListener('click', exportContacts);
    
    // Event delegation for remove contact buttons (backup method)
    contactList.addEventListener('click', function(e) {
        // Check if the clicked element or its parent is the remove button
        let removeButton = e.target;
        if (e.target.classList.contains('remove-contact-btn')) {
            removeButton = e.target;
        } else if (e.target.closest('.remove-contact-btn')) {
            removeButton = e.target.closest('.remove-contact-btn');
        } else {
            return; // Not a remove button click
        }
        
        const contactId = parseInt(removeButton.getAttribute('data-contact-id'));
        removeContact(contactId);
    });

    // ============================================================================
    // ADDRESS BOOK FUNCTIONALITY
    // ============================================================================
    
    const openAddressBookBtn = document.getElementById('open-address-book-btn');
    const addressBookModal = document.getElementById('address-book-modal');
    const closeAddressBookBtn = document.getElementById('close-address-book-btn');
    const addressBookContacts = document.getElementById('address-book-contacts');
    const addressBookSearch = document.getElementById('address-book-search');
    const addressBookFilter = document.getElementById('address-book-filter');
    const selectAllBtn = document.getElementById('select-all-btn');
    const clearSelectionBtn = document.getElementById('clear-selection-btn');
    const addSelectedBtn = document.getElementById('add-selected-btn');
    const selectedCount = document.getElementById('selected-count');
    
    // Sample address book data
    const addressBookData = [
        { id: 'ab_1', type: 'person', first_name: 'Ahmed', last_name: 'Al-Rashid', phone: '+97335000001', email: 'ahmed.alrashid@email.com', company: 'TechCorp Bahrain' },
        { id: 'ab_2', type: 'person', first_name: 'Fatima', last_name: 'Hassan', phone: '+97335000002', email: 'fatima.hassan@email.com', company: 'Digital Solutions' },
        { id: 'ab_3', type: 'person', first_name: 'Omar', last_name: 'Khalil', phone: '+97335000003', email: 'omar.khalil@email.com', company: 'Innovation Hub' },
        { id: 'ab_4', type: 'person', first_name: 'Layla', last_name: 'Mahmoud', phone: '+97335000004', email: 'layla.mahmoud@email.com', company: 'Future Systems' },
        { id: 'ab_5', type: 'person', first_name: 'Yusuf', last_name: 'Ibrahim', phone: '+97335000005', email: 'yusuf.ibrahim@email.com', company: 'Smart Tech' },
        { id: 'ab_6', type: 'company', name: 'Bahrain Tech Solutions', phone: '+97335000006', email: 'info@bts.bh', contact_person: 'Sarah Johnson' },
        { id: 'ab_7', type: 'company', name: 'Gulf Innovation Group', phone: '+97335000007', email: 'hello@gig.bh', contact_person: 'Michael Chen' },
        { id: 'ab_8', type: 'person', first_name: 'Noor', last_name: 'Al-Zahra', phone: '+97335000008', email: 'noor.alzahra@email.com', company: 'Creative Agency' },
        { id: 'ab_9', type: 'person', first_name: 'Khalid', last_name: 'Rashid', phone: '+97335000009', email: 'khalid.rashid@email.com', company: 'Data Dynamics' },
        { id: 'ab_10', type: 'company', name: 'Middle East Digital', phone: '+97335000010', email: 'contact@med.bh', contact_person: 'Emily Rodriguez' },
        { id: 'ab_11', type: 'person', first_name: 'Zainab', last_name: 'Saleh', phone: '+97335000011', email: 'zainab.saleh@email.com', company: 'Cloud Solutions' },
        { id: 'ab_12', type: 'person', first_name: 'Hassan', last_name: 'Ali', phone: '+97335000012', email: 'hassan.ali@email.com', company: 'AI Innovations' },
        { id: 'ab_13', type: 'company', name: 'Bahrain Digital Hub', phone: '+97335000013', email: 'info@bdh.bh', contact_person: 'David Thompson' },
        { id: 'ab_14', type: 'person', first_name: 'Aisha', last_name: 'Mohammed', phone: '+97335000014', email: 'aisha.mohammed@email.com', company: 'Tech Pioneers' },
        { id: 'ab_15', type: 'person', first_name: 'Rashid', last_name: 'Al-Mansouri', phone: '+97335000015', email: 'rashid.almansouri@email.com', company: 'Digital Future' }
    ];
    
    let filteredAddressBookData = [...addressBookData];
    let selectedAddressBookContacts = new Set();
    
    function renderAddressBookContacts() {
        const contactsHtml = filteredAddressBookData.map(contact => {
            const isSelected = selectedAddressBookContacts.has(contact.id);
            const displayName = contact.type === 'person' 
                ? `${contact.first_name} ${contact.last_name}`
                : contact.name;
            const displayCompany = contact.type === 'person' 
                ? contact.company 
                : `Contact: ${contact.contact_person}`;
            
            return `
                <div class="flex items-center justify-between bg-base-100 p-3 rounded-lg border border-base-300 hover:border-primary/30 transition-colors">
                    <div class="flex items-center gap-3">
                        <input type="checkbox" class="checkbox checkbox-primary" 
                               value="${contact.id}" ${isSelected ? 'checked' : ''} />
                        <div>
                            <div class="font-medium">${displayName}</div>
                            <div class="text-sm text-base-content/70">${displayCompany}</div>
                            <div class="text-xs text-base-content/50 font-mono">${contact.phone}</div>
                        </div>
                    </div>
                    <div class="badge badge-${contact.type === 'person' ? 'primary' : 'secondary'} badge-sm">
                        ${contact.type === 'person' ? 'Person' : 'Company'}
                    </div>
                </div>
            `;
        }).join('');
        
        addressBookContacts.innerHTML = contactsHtml;
        updateSelectedCount();
    }
    
    function updateSelectedCount() {
        selectedCount.textContent = selectedAddressBookContacts.size;
    }
    
    function filterAddressBookContacts() {
        const searchTerm = addressBookSearch.value.toLowerCase();
        const filterType = addressBookFilter.value;
        
        filteredAddressBookData = addressBookData.filter(contact => {
            const matchesSearch = contact.first_name?.toLowerCase().includes(searchTerm) ||
                                 contact.last_name?.toLowerCase().includes(searchTerm) ||
                                 contact.name?.toLowerCase().includes(searchTerm) ||
                                 contact.company?.toLowerCase().includes(searchTerm) ||
                                 contact.phone.includes(searchTerm) ||
                                 contact.email.toLowerCase().includes(searchTerm);
            
            const matchesFilter = !filterType || contact.type === filterType;
            
            return matchesSearch && matchesFilter;
        });
        
        renderAddressBookContacts();
    }
    
    function addSelectedContactsToCampaign() {
        const selectedContacts = addressBookData.filter(contact => selectedAddressBookContacts.has(contact.id));
        const addedContacts = [];
        const duplicates = [];
        
        selectedContacts.forEach(contact => {
            const newContact = {
                id: Math.floor(Date.now() + Math.random() * 1000),
                phone: contact.phone,
                first_name: contact.type === 'person' ? contact.first_name : contact.name,
                last_name: contact.type === 'person' ? contact.last_name : ''
            };
            
            // Check for duplicates
            const isDuplicate = contacts.some(c => c.phone === newContact.phone);
            if (!isDuplicate) {
                contacts.push(newContact);
                addedContacts.push(newContact);
            } else {
                duplicates.push({
                    phone: contact.phone,
                    name: contact.type === 'person' ? `${contact.first_name} ${contact.last_name}` : contact.name
                });
            }
        });
        
        updateContactDisplay();
        updateContactsData();
        
        // Close modal and reset
        closeAddressBookModal();
        
        // Show success message
        if (addedContacts.length > 0) {
            const successMsg = `Added ${addedContacts.length} contacts from address book`;
            showSuccessMessage(successMsg);
        }
        
        // Show duplicates if any
        if (duplicates.length > 0) {
            showDuplicateError(duplicates);
        }
    }
    
    // Address Book event listeners
    openAddressBookBtn.addEventListener('click', () => {
        addressBookModal.style.display = 'block';
        addressBookModal.classList.add('modal-open');
        // Prevent body scrolling when modal is open
        document.body.style.overflow = 'hidden';
        renderAddressBookContacts();
        console.log('Address book opened'); // Debug log
    });
    
    function closeAddressBookModal() {
        addressBookModal.style.display = 'none';
        addressBookModal.classList.remove('modal-open');
        // Restore body scrolling
        document.body.style.overflow = '';
        selectedAddressBookContacts.clear();
        renderAddressBookContacts();
    }
    
    closeAddressBookBtn.addEventListener('click', closeAddressBookModal);
    
    // Close modal when clicking outside
    addressBookModal.addEventListener('click', (e) => {
        if (e.target === addressBookModal) {
            closeAddressBookModal();
        }
    });
    
    addressBookSearch.addEventListener('input', filterAddressBookContacts);
    addressBookFilter.addEventListener('change', filterAddressBookContacts);
    
    selectAllBtn.addEventListener('click', () => {
        filteredAddressBookData.forEach(contact => selectedAddressBookContacts.add(contact.id));
        renderAddressBookContacts();
    });
    
    clearSelectionBtn.addEventListener('click', () => {
        selectedAddressBookContacts.clear();
        renderAddressBookContacts();
    });
    
    addSelectedBtn.addEventListener('click', addSelectedContactsToCampaign);
    
    // Handle checkbox changes in address book
    addressBookContacts.addEventListener('change', function(e) {
        if (e.target.type === 'checkbox') {
            const contactId = e.target.value;
            if (e.target.checked) {
                selectedAddressBookContacts.add(contactId);
            } else {
                selectedAddressBookContacts.delete(contactId);
            }
            updateSelectedCount();
        }
    });
    
    // Ensure scroll restoration on page unload
    window.addEventListener('beforeunload', function() {
        document.body.style.overflow = '';
    });
    
    // Ensure scroll restoration if modal is somehow left open
    window.addEventListener('focus', function() {
        if (addressBookModal.style.display === 'none') {
            document.body.style.overflow = '';
        }
    });

    // ============================================================================
    // FILE UPLOAD & CSV PROCESSING
    // ============================================================================
    
    const fileInput = document.querySelector('input[name="contact_file"]');
    const csvErrors = document.getElementById('csv-errors');
    const errorDetails = document.getElementById('error-details');
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            processCSVFile(file);
        }
    });
    
    function processCSVFile(file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                const csvContent = e.target.result;
                const lines = csvContent.split('\n');
                const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
                
                // Find column indices
                const phoneIndex = headers.findIndex(h => h.includes('phone') || h.includes('number') || h.includes('tel'));
                const firstNameIndex = headers.findIndex(h => h.includes('first') || h.includes('name'));
                const lastNameIndex = headers.findIndex(h => h.includes('last') || h.includes('surname'));
                
                if (phoneIndex === -1) {
                    showCSVError(['No phone number column found. Please ensure your CSV has a column with "phone", "number", or "tel" in the header.']);
                    return;
                }
                
                const newContacts = [];
                const errors = [];
                const duplicates = [];
                
                // Process each line (skip header)
                for (let i = 1; i < lines.length; i++) {
                    const line = lines[i].trim();
                    if (!line) continue; // Skip empty lines
                    
                    const values = parseCSVLine(line);
                    
                    if (values.length < Math.max(phoneIndex, firstNameIndex, lastNameIndex) + 1) {
                        errors.push(`Row ${i + 1}: Insufficient columns`);
                        continue;
                    }
                    
                    const phone = values[phoneIndex]?.trim();
                    const firstName = firstNameIndex >= 0 ? values[firstNameIndex]?.trim() || '' : '';
                    const lastName = lastNameIndex >= 0 ? values[lastNameIndex]?.trim() || '' : '';
                    
                    // Validate phone number
                    if (!phone) {
                        errors.push(`Row ${i + 1}: Missing phone number`);
                        continue;
                    }
                    
                    // Basic phone validation (E.164 format or common formats)
                    const cleanPhone = cleanPhoneNumber(phone);
                    if (!isValidPhoneNumber(cleanPhone)) {
                        errors.push(`Row ${i + 1}: Invalid phone number "${phone}" (cleaned: "${cleanPhone}")`);
                        continue;
                    }
                    
                    // Check for duplicate phone numbers
                    const isDuplicate = contacts.some(c => c.phone === cleanPhone) || 
                                      newContacts.some(c => c.phone === cleanPhone);
                    
                    if (isDuplicate) {
                        duplicates.push({
                            row: i + 1,
                            phone: cleanPhone,
                            name: `${firstName} ${lastName}`.trim() || 'Unknown'
                        });
                        continue;
                    }
                    
                    newContacts.push({
                        id: Date.now() + i,
                        phone: cleanPhone,
                        first_name: firstName,
                        last_name: lastName
                    });
                }
                
                // Add valid contacts
                if (newContacts.length > 0) {
                    contacts.push(...newContacts);
                    updateContactDisplay();
                    updateContactsData();
                    
                    // Show success message
                    const successMsg = `Successfully added ${newContacts.length} contacts from "${file.name}"`;
                    showSuccessMessage(successMsg);
                }
                
                // Show errors if any
                if (errors.length > 0) {
                    showCSVError(errors);
                }
                
                // Show duplicates if any
                if (duplicates.length > 0) {
                    showDuplicateError(duplicates);
                }
                
                // Clear file input
                fileInput.value = '';
                
            } catch (error) {
                showCSVError([`Error processing file: ${error.message}`]);
                fileInput.value = '';
            }
        };
        
        reader.onerror = function() {
            showCSVError(['Error reading file. Please try again.']);
            fileInput.value = '';
        };
        
        reader.readAsText(file);
    }
    
    function parseCSVLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;
        
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                result.push(current);
                current = '';
            } else {
                current += char;
            }
        }
        
        result.push(current);
        return result;
    }
    
    function cleanPhoneNumber(phone) {
        // Remove all non-digit characters except + at the beginning
        let cleaned = phone.replace(/[^\d+]/g, '');
        
        // If it starts with +, keep it (E.164 format)
        if (cleaned.startsWith('+')) {
            return cleaned;
        }
        
        // If it's 10 digits, assume US number and add +1
        if (cleaned.length === 10) {
            return '+1' + cleaned;
        }
        
        // If it's 11 digits and starts with 1, add +
        if (cleaned.length === 11 && cleaned.startsWith('1')) {
            return '+' + cleaned;
        }
        
        // If it's 12 digits and starts with 1, add +
        if (cleaned.length === 12 && cleaned.startsWith('1')) {
            return '+' + cleaned;
        }
        
        // Handle international numbers without + (like 97335000001 for Bahrain)
        // Most international numbers are 11-15 digits total
        if (cleaned.length >= 11 && cleaned.length <= 15) {
            // Common country code patterns:
            // 1 digit: US/Canada (+1)
            // 2 digits: Most countries (+44 UK, +33 France, +49 Germany, etc.)
            // 3 digits: Some countries (+973 Bahrain, +966 Saudi Arabia, etc.)
            // 4 digits: Very few countries
            
            // If it's 11-15 digits and doesn't start with 1 (US), it's likely international
            if (!cleaned.startsWith('1') || cleaned.length > 11) {
                return '+' + cleaned;
            }
        }
        
        return cleaned;
    }
    
    function isValidPhoneNumber(phone) {
        // Must start with + and have 7-15 digits
        const phoneRegex = /^\+[1-9]\d{6,14}$/;
        return phoneRegex.test(phone);
    }

    // ============================================================================
    // MESSAGE DISPLAY FUNCTIONS
    // ============================================================================
    
    function showCSVError(errors) {
        errorDetails.innerHTML = errors.map(error => 
            `<div class="text-sm">• ${error}</div>`
        ).join('');
        csvErrors.style.display = 'block';
    }
    
    function showDuplicateError(duplicates) {
        const duplicateErrors = document.getElementById('duplicate-errors');
        const duplicateDetails = document.getElementById('duplicate-details');
        
        duplicateDetails.innerHTML = duplicates.map(duplicate => 
            `<div class="text-sm">• ${duplicate.name} (${duplicate.phone})</div>`
        ).join('');
        
        duplicateErrors.style.display = 'block';
    }
    
    function showSuccessMessage(message) {
        // Create temporary success message with close button
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success mb-4 relative';
        successDiv.innerHTML = `
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>${message}</span>
            <button type="button" onclick="this.parentElement.remove()" class="btn btn-ghost btn-xs text-white hover:bg-white/20 absolute top-2 right-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
        
        // Insert after the file upload section
        const fileUploadSection = fileInput.closest('.form-control');
        fileUploadSection.parentNode.insertBefore(successDiv, fileUploadSection.nextSibling);
    }

    // ============================================================================
    // GLOBAL FUNCTION EXPORTS (for inline onclick handlers)
    // ============================================================================
    
    // Make functions globally accessible for inline onclick handlers
    window.removeContact = removeContact;
});
