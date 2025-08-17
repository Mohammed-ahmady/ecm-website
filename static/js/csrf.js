/**
 * CSRF Protection for AJAX Requests
 * 
 * This script ensures that all AJAX requests include the CSRF token
 * as required by Django's CSRF protection mechanism.
 */

// Function to get the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Set up CSRF token for all AJAX requests
const csrftoken = getCookie('csrftoken');

// Add CSRF token to all AJAX requests
document.addEventListener('DOMContentLoaded', function() {
    // For fetch API
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        options = options || {};
        if (options.method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method.toUpperCase())) {
            if (!options.headers) {
                options.headers = {};
            }
            
            // Convert headers object to Headers if it's not already
            if (!(options.headers instanceof Headers)) {
                options.headers = new Headers(options.headers);
            }
            
            // Add CSRF token if not already present
            if (!options.headers.has('X-CSRFToken')) {
                options.headers.append('X-CSRFToken', csrftoken);
            }
        }
        return originalFetch(url, options);
    };

    // For XMLHttpRequest (jQuery and other libraries)
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function() {
        const method = arguments[0];
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method.toUpperCase())) {
            this.addEventListener('readystatechange', function() {
                if (this.readyState === 1) { // OPENED
                    this.setRequestHeader('X-CSRFToken', csrftoken);
                }
            });
        }
        originalOpen.apply(this, arguments);
    };
});
