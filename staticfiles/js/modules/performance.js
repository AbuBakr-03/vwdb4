/**
 * Performance Optimization Module
 * Handles lazy loading, resource preloading, and other performance enhancements
 */

/**
 * Preload SVG sprite for better icon performance
 */
export function preloadSVGSprite() {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = '/static/icons/sprite.svg';
  link.as = 'image';
  link.type = 'image/svg+xml';
  document.head.appendChild(link);
}

/**
 * Lazy load images with Intersection Observer
 */
export function initLazyLoading() {
  if (!('IntersectionObserver' in window)) {
    // Fallback for older browsers
    return;
  }

  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove('lazy');
        imageObserver.unobserve(img);
      }
    });
  });

  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
  });
}

/**
 * Optimize JavaScript loading with requestIdleCallback
 */
export function loadModuleWhenIdle(moduleFunction) {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(moduleFunction);
  } else {
    // Fallback for browsers without requestIdleCallback
    setTimeout(moduleFunction, 1);
  }
}

/**
 * Debounce function for scroll/resize events
 */
export function debounce(func, wait, immediate) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func(...args);
  };
}

/**
 * Throttle function for high-frequency events
 */
export function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Initialize performance optimizations
 */
export function initPerformanceOptimizations() {
  // Preload critical resources
  preloadSVGSprite();
  
  // Initialize lazy loading
  loadModuleWhenIdle(initLazyLoading);
  
  // Add performance marks for monitoring
  if ('performance' in window && 'mark' in performance) {
    performance.mark('performance-optimizations-loaded');
  }
}

/**
 * Resource hints for critical resources
 */
export function addResourceHints() {
  const hints = [
    { rel: 'dns-prefetch', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true },
  ];

  hints.forEach(hint => {
    const link = document.createElement('link');
    Object.keys(hint).forEach(key => {
      if (key === 'crossorigin') {
        link.setAttribute('crossorigin', hint[key]);
      } else {
        link[key] = hint[key];
      }
    });
    document.head.appendChild(link);
  });
}

// Initialize optimizations when module loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPerformanceOptimizations);
} else {
  initPerformanceOptimizations();
}
