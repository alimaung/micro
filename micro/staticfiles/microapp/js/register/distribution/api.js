/**
 * API Module - Handles all server communications for distribution functionality
 * Uses Fetch API for AJAX requests
 */

const MicroDistributionAPI = (function() {
    'use strict';

    // Private properties
    let config = {
        baseUrl: '/api/distribution/',
        projectId: null,
        csrfToken: null
    };

    /**
     * Initialize the API module
     * @param {Object} options - Configuration options
     */
    function init(options = {}) {
        // Merge options with defaults
        config = Object.assign(config, options);
        
        // Get CSRF token for POST requests
        config.csrfToken = getCsrfToken();
        
        // Return public interface
        return publicInterface();
    }

    /**
     * Get the distribution status for the current project
     * @returns {Promise} Promise that resolves with the status response
     */
    function getDistributionStatus() {
        const url = `${config.baseUrl}status/${config.projectId}/`;
        return fetchWithErrorHandling(url);
    }

    /**
     * Start the distribution process
     * @param {Object} options - Distribution options
     * @returns {Promise} Promise that resolves with the distribution response
     */
    function startDistribution(options = {}) {
        const url = `${config.baseUrl}distribute/${config.projectId}/`;
        return fetchWithErrorHandling(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify(options)
        });
    }

    /**
     * Generate reference sheets for the current project
     * @param {Object} options - Reference sheet options
     * @returns {Promise} Promise that resolves with the reference sheets response
     */
    function generateReferenceSheets(options = {}) {
        const url = `${config.baseUrl}generate-references/${config.projectId}/`;
        return fetchWithErrorHandling(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify(options)
        });
    }

    /**
     * Process a single document during distribution
     * @param {Object} document - Document data
     * @returns {Promise} Promise that resolves with the processing response
     */
    function processDocument(document) {
        const url = `${config.baseUrl}process-document/${config.projectId}/`;
        return fetchWithErrorHandling(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({ document })
        });
    }

    /**
     * Complete the distribution process
     * @param {Object} summary - Distribution summary data
     * @returns {Promise} Promise that resolves with the completion response
     */
    function completeDistribution(summary) {
        const url = `${config.baseUrl}complete/${config.projectId}/`;
        return fetchWithErrorHandling(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({ summary })
        });
    }

    /**
     * Reset the distribution for the current project
     * @returns {Promise} Promise that resolves with the reset response
     */
    function resetDistribution() {
        const url = `${config.baseUrl}reset/${config.projectId}/`;
        return fetchWithErrorHandling(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({})
        });
    }

    /**
     * Wrapper for fetch with consistent error handling
     * @param {String} url - The URL to fetch
     * @param {Object} options - Fetch options
     * @returns {Promise} Promise that resolves with the JSON response
     */
    function fetchWithErrorHandling(url, options = {}) {
        console.log(`API request to: ${url}`, options);
        
        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    console.error(`API error: ${response.status} ${response.statusText}`, response);
                    return response.json().then(errorData => {
                        throw new Error(errorData.message || `HTTP error ${response.status}`);
                    }).catch(err => {
                        // If JSON parsing fails, throw the original HTTP error
                        throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .catch(error => {
                console.error(`Fetch error:`, error);
                throw error;
            });
    }

    /**
     * Get CSRF token from cookies
     * @returns {String} CSRF token
     */
    function getCsrfToken() {
        const name = 'csrftoken';
        const cookieValue = document.cookie.split(';')
            .map(cookie => cookie.trim())
            .find(cookie => cookie.startsWith(name + '='));
            
        if (cookieValue) {
            return cookieValue.substring(name.length + 1);
        }
        
        // Fallback to meta tag if cookie not found
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : '';
    }

    /**
     * Get the current project ID
     * @returns {Number} Project ID
     */
    function getProjectId() {
        return config.projectId;
    }

    /**
     * Set the base URL for API requests
     * @param {String} url - New base URL
     */
    function setBaseUrl(url) {
        config.baseUrl = url;
    }

    /**
     * Set the project ID for API requests
     * @param {Number} id - Project ID
     */
    function setProjectId(id) {
        config.projectId = id;
    }

    /**
     * Return public interface for this module
     */
    function publicInterface() {
        return {
            init,
            getProjectId,
            getDistributionStatus,
            startDistribution,
            generateReferenceSheets,
            processDocument,
            completeDistribution,
            resetDistribution,
            setBaseUrl,
            setProjectId
        };
    }

    // Return public interface
    return {
        init: init
    };
})();