/**
 * database-service.js - Centralized database operations for the entire application
 * Provides a unified interface for all database interactions
 */

// Make the class available globally
window.DatabaseService = class DatabaseService {
    constructor() {
        this.apiBasePath = '/api';
    }

    /**
     * Get CSRF token from cookies
     * @returns {string} - CSRF token
     * @private
     */
    _getCsrfToken() {
        // Try to get token from the form first
        const tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (tokenElement) return tokenElement.value;
        
        // Fallback to cookie parsing
        const name = 'csrftoken';
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

    /**
     * Get default headers for API requests
     * @param {boolean} includeContentType - Whether to include Content-Type header
     * @returns {Object} - Headers object
     * @private
     */
    _getDefaultHeaders(includeContentType = true) {
        const headers = {
            'X-CSRFToken': this._getCsrfToken(),
            'Accept': 'application/json'
        };
        
        if (includeContentType) {
            headers['Content-Type'] = 'application/json';
        }
        
        return headers;
    }

    /**
     * Process API response
     * @param {Response} response - Fetch API response
     * @returns {Promise<Object>} - Processed response data
     * @private
     */
    async _processResponse(response) {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            
            if (!response.ok) {
                const error = new Error(data.message || data.error || 'An error occurred');
                error.status = response.status;
                error.data = data;
                throw error;
            }
            
            return data;
        } else {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            return await response.text();
        }
    }

    /**
     * Make an API request
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {Object|null} data - Request data
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Response data
     * @private
     */
    async _apiRequest(endpoint, method = 'GET', data = null, options = {}) {
        const url = endpoint.startsWith('http') || endpoint.startsWith('/') 
            ? endpoint 
            : `${this.apiBasePath}/${endpoint}`;
        
        const requestOptions = {
            method,
            headers: this._getDefaultHeaders(!!data),
            ...options
        };
        
        if (data) {
            requestOptions.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, requestOptions);
            return await this._processResponse(response);
        } catch (error) {
            console.error(`API ${method} request to ${url} failed:`, error);
            throw error;
        }
    }

    /**
     * Create a new project in the database
     * @param {Object} projectData - Project data to save
     * @returns {Promise<Object>} - Response object
     */
    async createProject(projectData) {
        return await this._apiRequest('projects/create/', 'POST', projectData);
    }

    /**
     * Get a project by ID
     * @param {number|string} projectId - Project ID
     * @returns {Promise<Object>} - Project data
     */
    async getProject(projectId) {
        return await this._apiRequest(`projects/${projectId}/`);
    }

    /**
     * Update an existing project
     * @param {number|string} projectId - Project ID
     * @param {Object} projectData - Updated project data
     * @returns {Promise<Object>} - Response object
     */
    async updateProject(projectId, projectData) {
        return await this._apiRequest(`projects/${projectId}/update/`, 'PUT', projectData);
    }

    /**
     * Delete a project
     * @param {number|string} projectId - Project ID
     * @returns {Promise<Object>} - Response object
     */
    async deleteProject(projectId) {
        return await this._apiRequest(`projects/${projectId}/delete/`, 'DELETE');
    }

    /**
     * List projects with optional filtering
     * @param {Object} filters - Filter parameters
     * @param {number} page - Page number
     * @param {number} pageSize - Page size
     * @returns {Promise<Object>} - Paginated project list
     */
    async listProjects(filters = {}, page = 1, pageSize = 20) {
        const queryParams = new URLSearchParams({
            page,
            page_size: pageSize,
            ...filters
        }).toString();
        
        return await this._apiRequest(`projects/?${queryParams}`);
    }

    /**
     * Search projects by keyword
     * @param {string} keyword - Search keyword
     * @param {Object} options - Additional search options
     * @returns {Promise<Object>} - Search results
     */
    async searchProjects(keyword, options = {}) {
        const queryParams = new URLSearchParams({
            q: keyword,
            ...options
        }).toString();
        
        return await this._apiRequest(`projects/search/?${queryParams}`);
    }

    /**
     * Batch import projects
     * @param {Array<Object>} projects - Array of project data
     * @returns {Promise<Object>} - Import results
     */
    async batchImportProjects(projects) {
        return await this._apiRequest('projects/batch-import/', 'POST', { projects });
    }

    /**
     * Export projects to CSV/Excel
     * @param {Array<number|string>} projectIds - Array of project IDs to export
     * @param {string} format - Export format ('csv' or 'excel')
     * @returns {Promise<Blob>} - File blob
     */
    async exportProjects(projectIds, format = 'csv') {
        const response = await fetch(`${this.apiBasePath}/projects/export/`, {
            method: 'POST',
            headers: this._getDefaultHeaders(),
            body: JSON.stringify({ project_ids: projectIds, format })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Export failed');
        }
        
        return await response.blob();
    }

    /**
     * Get database statistics
     * @returns {Promise<Object>} - Database statistics
     */
    async getDatabaseStats() {
        return await this._apiRequest('statistics/');
    }

    /**
     * Run a custom query
     * @param {string} query - Custom query string
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} - Query results
     */
    async runCustomQuery(query, params = {}) {
        return await this._apiRequest('custom-query/', 'POST', { query, params });
    }

    /**
     * Handle database transactions
     * @param {Function} callback - Transaction callback
     * @returns {Promise<Object>} - Transaction result
     */
    async transaction(callback) {
        try {
            // Start transaction
            const txnId = await this._apiRequest('transaction/begin/', 'POST');
            
            // Execute callback within transaction context
            const result = await callback(this, txnId);
            
            // Commit transaction
            await this._apiRequest('transaction/commit/', 'POST', { transaction_id: txnId });
            
            return result;
        } catch (error) {
            // Rollback transaction on error
            if (error.txnId) {
                await this._apiRequest('transaction/rollback/', 'POST', { transaction_id: error.txnId });
            }
            throw error;
        }
    }
} 