/**
 * Navigation Module
 * Handles smooth scrolling and active tab management for navigation
 */

export class NavigationManager {
    constructor(options = {}) {
        this.options = {
            headerOffset: 160,
            scrollOffset: 180,
            scrollBehavior: 'smooth',
            throttleDelay: 10,
            ...options
        };
        
        this.tabs = [];
        this.sections = [];
        this.scrollTimeout = null;
        
        this.init();
    }

    init() {
        this.setupElements();
        this.addClickHandlers();
        this.addScrollListener();
    }

    /**
     * Setup tab and section elements
     */
    setupElements() {
        this.tabs = Array.from(document.querySelectorAll('a[data-section]'));
        this.sections = Array.from(document.querySelectorAll('[id$="-section"]'));
    }

    /**
     * Add click handlers for navigation tabs
     */
    addClickHandlers() {
        this.tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleTabClick(tab);
            });
        });
    }

    /**
     * Handle tab click with smooth scrolling
     * @param {HTMLElement} tab - The clicked tab element
     */
    handleTabClick(tab) {
        // Update active styling
        this.updateActiveTab(tab);
        
        // Get target section and scroll
        const targetId = tab.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            this.scrollToElement(targetElement);
        }
    }

    /**
     * Scroll to specific element with offset
     * @param {HTMLElement} element - Target element to scroll to
     */
    scrollToElement(element) {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - this.options.headerOffset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: this.options.scrollBehavior
        });
    }

    /**
     * Update active tab styling
     * @param {HTMLElement} activeTab - The tab to mark as active
     */
    updateActiveTab(activeTab = null) {
        // Remove active styling from all tabs
        this.tabs.forEach(tab => {
            tab.classList.remove('text-white', 'border-b-2', 'border-white', 'font-medium');
            tab.classList.add('text-neutral-content/70');
            
            // Special handling for Advanced tab
            if (tab.textContent.trim() === 'Advanced') {
                tab.classList.remove('text-neutral-content/70');
                tab.classList.add('text-amber-400');
            }
        });
        
        // Add active styling to current tab
        if (activeTab) {
            activeTab.classList.remove('text-neutral-content/70', 'text-amber-400');
            activeTab.classList.add('text-white', 'border-b-2', 'border-white', 'font-medium');
        }
    }

    /**
     * Update active tab based on scroll position
     */
    updateActiveTabFromScroll() {
        const scrollPosition = window.scrollY + this.options.scrollOffset;
        
        this.sections.forEach((section, index) => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionBottom = sectionTop + sectionHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                if (this.tabs[index]) {
                    this.updateActiveTab(this.tabs[index]);
                }
            }
        });
    }

    /**
     * Add throttled scroll listener for performance
     */
    addScrollListener() {
        window.addEventListener('scroll', () => {
            if (this.scrollTimeout) {
                clearTimeout(this.scrollTimeout);
            }
            this.scrollTimeout = setTimeout(() => {
                this.updateActiveTabFromScroll();
            }, this.options.throttleDelay);
        });
    }

    /**
     * Programmatically navigate to a section
     * @param {string} sectionId - ID of the section to navigate to
     */
    navigateToSection(sectionId) {
        const targetElement = document.getElementById(sectionId);
        const matchingTab = this.tabs.find(tab => 
            tab.getAttribute('href') === `#${sectionId}`
        );
        
        if (targetElement && matchingTab) {
            this.handleTabClick(matchingTab);
        }
    }

    /**
     * Destroy the navigation manager and cleanup listeners
     */
    destroy() {
        if (this.scrollTimeout) {
            clearTimeout(this.scrollTimeout);
        }
        
        // Remove event listeners if needed
        // (Note: Modern browsers handle this automatically when elements are removed)
    }
}
