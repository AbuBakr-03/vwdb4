/**
 * Contact List JavaScript
 * Handles contact deletion and message display
 */

document.addEventListener('DOMContentLoaded', function() {
    // ============================================================================
    // DELETE CONTACT FUNCTIONALITY
    // ============================================================================
    
    window.deleteContact = function(contactId) {
        const modal = document.getElementById('delete-modal');
        const confirmBtn = document.getElementById('confirm-delete');
        
        // Show modal
        modal.showModal();
        
        // Handle confirmation
        confirmBtn.onclick = function() {
            deleteContactConfirmed(contactId);
            modal.close();
        };
    };
    
    function deleteContactConfirmed(contactId) {
        // Show loading state
        const confirmBtn = document.getElementById('confirm-delete');
        const originalText = confirmBtn.innerHTML;
        confirmBtn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Deleting...';
        confirmBtn.disabled = true;
        
        fetch(`/people/contacts/${contactId}/delete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showMessage(result.message, 'success');
                // Reload page to refresh the list
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showMessage(result.message, 'error');
            }
        })
        .catch(error => {
            showMessage('Error deleting contact. Please try again.', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            // Restore button state
            confirmBtn.innerHTML = originalText;
            confirmBtn.disabled = false;
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
    
    // ============================================================================
    // SEARCH ENHANCEMENTS
    // ============================================================================
    
    // Auto-submit search on Enter key
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.closest('form').submit();
            }
        });
    }
    
    // Auto-submit filters on change
    const filterSelects = document.querySelectorAll('select[name="party_type"], select[name="segment"]');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });
});
