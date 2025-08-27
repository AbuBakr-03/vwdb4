/**
 * Segment Creation JavaScript
 * Handles segment creation form submission
 */

document.addEventListener('DOMContentLoaded', function() {
    // ============================================================================
    // FORM SUBMISSION
    // ============================================================================
    
    const segmentForm = document.getElementById('segment-form');
    
    segmentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = new FormData(segmentForm);
        const data = {};
        
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
        submitSegment(data);
    });
    
    function validateForm(data) {
        const errors = [];
        
        if (!data.name || data.name.trim() === '') {
            errors.push('Segment name is required');
        }
        
        if (!data.color) {
            errors.push('Badge color is required');
        }
        
        return errors;
    }
    
    function submitSegment(data) {
        // Show loading state
        const submitBtn = segmentForm.querySelector('button[type="submit"]');
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
                // Redirect to contact list after a short delay
                setTimeout(() => {
                    window.location.href = '/people/contacts/';
                }, 1500);
            } else {
                showMessage(result.message, 'error');
            }
        })
        .catch(error => {
            showMessage('Error creating segment. Please try again.', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            // Restore button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }
    
    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================
    
    function getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
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
});
