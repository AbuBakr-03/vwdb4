/**
 * Sidebar Utilities - Handle sidebar collapse and fixed header positioning
 * This module provides utilities for managing sidebar states and updating fixed headers accordingly.
 */

/**
 * Initialize sidebar toggle functionality for pages with fixed headers
 * @param {Object} options - Configuration options
 * @param {string} options.fixedHeaderId - ID of the fixed header element
 * @param {string} options.mainSidebarId - ID of the main sidebar (default: 'sidebar')
 * @param {string} options.secondarySidebarSelector - CSS selector for secondary sidebar
 */
function initializeSidebarToggle(options = {}) {
    const {
        fixedHeaderId = 'fixed-header',
        mainSidebarId = 'sidebar',
        secondarySidebarSelector = null
    } = options;

    const fixedHeader = document.getElementById(fixedHeaderId);
    const mainSidebar = document.getElementById(mainSidebarId);
    
    if (!fixedHeader) {
        console.warn(`Fixed header with ID '${fixedHeaderId}' not found`);
        return;
    }
    
    console.log('Initializing sidebar toggle functionality...');
    
    // Listen for sidebar toggle events from the main sidebar
    document.addEventListener('sidebarToggle', function(event) {
        const isCollapsed = event.detail.collapsed;
        console.log('Sidebar toggled, collapsed:', isCollapsed);
        updateHeaderPosition(fixedHeader, isCollapsed, secondarySidebarSelector);
    });
    
    // Set initial position based on current sidebar state
    const initialCollapsed = document.body.classList.contains('sidebar-collapsed');
    console.log('Initial sidebar state - collapsed:', initialCollapsed);
    updateHeaderPosition(fixedHeader, initialCollapsed, secondarySidebarSelector);
    
    // Monitor secondary sidebar visibility changes if selector is provided
    if (secondarySidebarSelector) {
        monitorSecondarySidebar(fixedHeader, secondarySidebarSelector);
    }
}

/**
 * Update the fixed header position based on sidebar states
 * @param {HTMLElement} fixedHeader - The fixed header element
 * @param {boolean} mainSidebarCollapsed - Whether the main sidebar is collapsed
 * @param {string} secondarySidebarSelector - CSS selector for secondary sidebar
 */
function updateHeaderPosition(fixedHeader, mainSidebarCollapsed, secondarySidebarSelector) {
    let leftPosition;
    
    // Check if secondary sidebar exists and is visible
    const secondarySidebar = secondarySidebarSelector ? document.querySelector(secondarySidebarSelector) : null;
    const hasSecondary = secondarySidebar && secondarySidebar.offsetWidth > 0;
    
    if (hasSecondary) {
        // Both main and secondary sidebars present
        if (mainSidebarCollapsed) {
            leftPosition = '400px'; // 64px (collapsed main) + 320px (secondary) = 384px, rounded to 400px for margin
        } else {
            leftPosition = '640px'; // 320px (expanded main) + 320px (secondary) = 640px
        }
    } else {
        // Only main sidebar present
        if (mainSidebarCollapsed) {
            leftPosition = '80px'; // 64px (collapsed main) + 16px margin
        } else {
            leftPosition = '336px'; // 320px (expanded main) + 16px margin
        }
    }
    
    console.log(`Updating header position to: ${leftPosition}`);
    fixedHeader.style.left = leftPosition;
}

/**
 * Monitor secondary sidebar visibility changes
 * @param {HTMLElement} fixedHeader - The fixed header element
 * @param {string} secondarySidebarSelector - CSS selector for secondary sidebar
 */
function monitorSecondarySidebar(fixedHeader, secondarySidebarSelector) {
    const secondarySidebar = document.querySelector(secondarySidebarSelector);
    
    if (!secondarySidebar) {
        console.log('Secondary sidebar not found, skipping monitoring');
        return;
    }
    
    // Use ResizeObserver to detect visibility changes
    const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            const isVisible = entry.contentRect.width > 0;
            console.log('Secondary sidebar visibility changed:', isVisible);
            
            // Get current main sidebar state and update header position
            const mainSidebarCollapsed = document.body.classList.contains('sidebar-collapsed');
            updateHeaderPosition(fixedHeader, mainSidebarCollapsed, secondarySidebarSelector);
        }
    });
    
    resizeObserver.observe(secondarySidebar);
    
    // Also monitor for DOM changes (sidebar being added/removed)
    const mutationObserver = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.type === 'childList') {
                // Check if secondary sidebar was added or removed
                const mainSidebarCollapsed = document.body.classList.contains('sidebar-collapsed');
                updateHeaderPosition(fixedHeader, mainSidebarCollapsed, secondarySidebarSelector);
            }
        });
    });
    
    mutationObserver.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
}

/**
 * Get current sidebar configuration
 * @returns {Object} Current sidebar state information
 */
function getSidebarState() {
    const mainSidebar = document.getElementById('sidebar');
    const mainCollapsed = document.body.classList.contains('sidebar-collapsed');
    
    return {
        mainSidebar: {
            element: mainSidebar,
            collapsed: mainCollapsed,
            width: mainCollapsed ? 64 : 320
        }
    };
}

// Export functions for use in other scripts
window.SidebarUtils = {
    initializeSidebarToggle,
    updateHeaderPosition,
    getSidebarState
};

// Auto-initialize if page has the required elements
document.addEventListener('DOMContentLoaded', function() {
    const fixedHeader = document.getElementById('fixed-header');
    const mainSidebar = document.getElementById('sidebar');
    
    if (fixedHeader && mainSidebar) {
        // Try to detect secondary sidebar by common patterns
        const possibleSecondarySelectors = [
            'aside.w-80:not(#sidebar)', // DaisyUI sidebar that's not the main one
            '.secondary-sidebar',
            '[data-sidebar="secondary"]'
        ];
        
        let secondarySidebarSelector = null;
        for (const selector of possibleSecondarySelectors) {
            if (document.querySelector(selector)) {
                secondarySidebarSelector = selector;
                break;
            }
        }
        
        initializeSidebarToggle({
            fixedHeaderId: 'fixed-header',
            mainSidebarId: 'sidebar',
            secondarySidebarSelector
        });
    }
});
