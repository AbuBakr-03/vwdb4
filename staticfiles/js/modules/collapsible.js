/**
 * Collapsible Module
 * Handles smooth collapsible animations for accordion-style components
 */

export class CollapsibleManager {
    constructor() {
        this.init();
    }

    init() {
        this.addEventListeners();
        this.handleResize();
    }

    /**
     * Toggle collapsible section with smooth animation
     * @param {HTMLElement} button - The trigger button
     * @param {string} contentId - ID of the content to toggle
     */
    toggleCollapse(button, contentId) {
        const content = document.getElementById(contentId);
        if (!content) return;

        const isCollapsed = content.dataset.collapsed === 'true';
        
        if (isCollapsed) {
            // Expanding
            content.style.maxHeight = content.scrollHeight + 'px';
            content.dataset.collapsed = 'false';
            button.setAttribute('aria-expanded', 'true');
            button.setAttribute('data-state', 'open');
        } else {
            // Collapsing
            content.style.maxHeight = '0px';
            content.dataset.collapsed = 'true';
            button.setAttribute('aria-expanded', 'false');
            button.setAttribute('data-state', 'closed');
        }
    }

    /**
     * Add event listeners for collapsible controls
     */
    addEventListeners() {
        // Use event delegation for better performance
        document.addEventListener('click', (e) => {
            const button = e.target.closest('button[aria-controls]');
            if (!button) return;
            
            e.preventDefault();
            const contentId = button.getAttribute('aria-controls');
            this.toggleCollapse(button, contentId);
        });
    }

    /**
     * Handle window resize to recalculate heights for expanded sections
     */
    handleResize() {
        window.addEventListener('resize', () => {
            const expandedSections = document.querySelectorAll('[data-collapsed="false"]');
            expandedSections.forEach(section => {
                section.style.maxHeight = section.scrollHeight + 'px';
            });
        });
    }
}
