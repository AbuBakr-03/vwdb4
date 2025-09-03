/**
 * Assistants Page Main Script
 * Coordinates all interactive functionality for the assistants page
 */

import { CollapsibleManager } from './modules/collapsible.js';
import { NavigationManager } from './modules/navigation.js';
import { initPerformanceOptimizations, loadModuleWhenIdle } from './modules/performance.js';

class AssistantsPage {
    constructor() {
        this.collapsibleManager = null;
        this.navigationManager = null;
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Initialize performance optimizations first
        initPerformanceOptimizations();
        
        // Initialize modules
        this.collapsibleManager = new CollapsibleManager();
        this.navigationManager = new NavigationManager({
            headerOffset: 160,
            scrollOffset: 180
        });

        // Setup any page-specific interactions
        this.setupPageSpecific();
    }

    setupPageSpecific() {
        // Add any assistants page specific functionality here
        this.setupMetricTileInteractions();
        this.setupSearchFunctionality();
        this.setupKeyboardShortcuts();
    }

    /**
     * Setup metric tile click interactions for future drawer functionality
     */
    setupMetricTileInteractions() {
        const metricTiles = document.querySelectorAll('[data-metric]');
        metricTiles.forEach(tile => {
            tile.addEventListener('click', (e) => {
                const metricType = tile.dataset.metric;
                console.log(`Metric tile clicked: ${metricType}`);
                // Future: Open metric drawer
            });
        });
    }

    /**
     * Setup search functionality
     */
    setupSearchFunctionality() {
        const searchInputs = document.querySelectorAll('input[type="text"][placeholder*="Search"]');
        searchInputs.forEach(input => {
            input.addEventListener('input', this.debounce((e) => {
                const query = e.target.value.trim();
                if (query.length > 2) {
                    console.log(`Search query: ${query}`);
                    // Future: Implement search functionality
                }
            }, 300));
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Cmd/Ctrl + K for search
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[placeholder*="Search"]');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
    }

    /**
     * Utility: Debounce function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Public API for external access
     */
    navigateToSection(sectionId) {
        if (this.navigationManager) {
            this.navigationManager.navigateToSection(sectionId);
        }
    }

    toggleSection(contentId) {
        const button = document.querySelector(`button[aria-controls="${contentId}"]`);
        if (button && this.collapsibleManager) {
            this.collapsibleManager.toggleCollapse(button, contentId);
        }
    }
}

// Initialize the page
const assistantsPage = new AssistantsPage();

// Export for potential external use
window.AssistantsPage = assistantsPage;
