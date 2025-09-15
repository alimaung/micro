/**
 * Film Index API Module
 * 
 * This module handles server communication for film index generation.
 */
const IndexAPI = (function() {
    
    /**
     * Generate index for the project
     * 
     * @param {string} projectId - Project ID
     * @param {object} allocationResults - Allocation results from localStorage
     * @returns {Promise} - Promise that resolves with the task ID
     */
    function generateIndex(projectId, allocationResults) {
        return fetch('/api/index/initialize-index', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                projectId: projectId,
                allocationResults: allocationResults
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Error generating index');
                });
            }
            return response.json();
        });
    }
    
    /**
     * Get the status of an index generation task
     * 
     * @param {string} taskId - The task ID
     * @returns {Promise} - Promise resolving to the task status
     */
    function getTaskStatus(taskId) {
        return new Promise((resolve, reject) => {
            if (!taskId) {
                console.warn('Task ID is missing, returning default status');
                resolve({
                    status: 'in-progress',
                    progress: 50,
                    message: 'Processing...'
                });
                return;
            }
            
            const url = `/api/index/index-status?taskId=${taskId}`;
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Task status response:', data);
                resolve(data);
            })
            .catch(error => {
                console.error('Error getting task status:', error);
                reject(error);
            });
        });
    }
    
    /**
     * Get the results of an index generation task
     * 
     * @param {string} taskId - The task ID
     * @returns {Promise} - Promise resolving to the task results
     */
    function getTaskResults(taskId) {
        return new Promise((resolve, reject) => {
            if (!taskId) {
                console.warn('Task ID is missing, using project ID from URL params');
                // Try to get project ID from URL
                const urlParams = new URLSearchParams(window.location.search);
                const projectId = urlParams.get('id');
                
                if (!projectId) {
                    reject(new Error('Neither Task ID nor Project ID is available'));
                    return;
                }
                
                // Use getIndexResults instead
                return getIndexResults(projectId)
                    .then(resolve)
                    .catch(reject);
            }
            
            const url = `/api/index/index-results?projectId=${taskId}`;
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Task results response:', data);
                resolve(data);
            })
            .catch(error => {
                console.error('Error getting task results:', error);
                reject(error);
            });
        });
    }
    
    /**
     * Get the index results for a project
     * 
     * @param {string} projectId - The project ID
     * @returns {Promise} - Promise resolving to the index results
     */
    function getIndexResults(projectId) {
        return new Promise((resolve, reject) => {
            if (!projectId) {
                reject(new Error('Project ID is required'));
                return;
            }
            
            const url = `/api/index/index-results?projectId=${projectId}`;
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Index results response:', data);
                resolve(data);
            })
            .catch(error => {
                console.error('Error getting index results:', error);
                reject(error);
            });
        });
    }
    
    /**
     * Update the index with film numbers
     * 
     * @param {Object} params - Parameters for index update
     * @returns {Promise} - Promise resolving to the updated index data
     */
    function updateIndex(params) {
        return new Promise((resolve, reject) => {
            const url = '/api/index/update-index';
            const projectId = params.projectId;
            const filmNumbers = params.filmNumbers;
            
            if (!projectId) {
                reject(new Error('Project ID is required'));
                return;
            }
            
            if (!filmNumbers || !Array.isArray(filmNumbers)) {
                reject(new Error('Film numbers are required'));
                return;
            }
            
            const requestData = {
                projectId: projectId,
                filmNumbers: filmNumbers,
                indexData: params.indexData || null
            };
            
            console.log('Updating index with params:', requestData);
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Index update response:', data);
                if (data.error) {
                    reject(new Error(data.error));
                } else {
                    resolve(data);
                }
            })
            .catch(error => {
                console.error('Error updating index:', error);
                reject(error);
            });
        });
    }
    
    /**
     * Export index data to CSV
     * 
     * @param {string} projectId - The project ID
     * @param {boolean} isFinal - Whether to export the final index
     * @returns {Promise} - Promise resolving to the CSV data
     */
    function exportToCsv(projectId, isFinal = false) {
        return new Promise((resolve, reject) => {
            if (!projectId) {
                reject(new Error('Project ID is required'));
                return;
            }
            
            const url = `/api/index/export/${projectId}/csv/?is_final=${isFinal ? 1 : 0}`;
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.text();
            })
            .then(data => {
                resolve(data);
            })
            .catch(error => {
                console.error('Error exporting to CSV:', error);
                reject(error);
            });
        });
    }
    
    /**
     * Export index data to JSON
     * 
     * @param {string} projectId - The project ID
     * @returns {Promise} - Promise resolving to the JSON data
     */
    function exportToJson(projectId) {
        return new Promise((resolve, reject) => {
            if (!projectId) {
                reject(new Error('Project ID is required'));
                return;
            }
            
            const url = `/api/index/export/${projectId}/json/`;
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                resolve(data);
            })
            .catch(error => {
                console.error('Error exporting to JSON:', error);
                reject(error);
            });
        });
    }
    
    /**
     * Get CSRF token from cookie
     * 
     * @returns {string} - CSRF token
     */
    function getCsrfToken() {
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
     * Download a file with given content and filename
     * 
     * @param {string} content - The file content
     * @param {string} filename - The filename
     * @param {string} contentType - The content type
     */
    function downloadFile(content, filename, contentType) {
        const a = document.createElement('a');
        const file = new Blob([content], {type: contentType});
        
        a.href = URL.createObjectURL(file);
        a.download = filename;
        a.click();
        
        URL.revokeObjectURL(a.href);
    }
    
    // Return public API
    return {
        generateIndex,
        getTaskStatus,
        getTaskResults,
        getIndexResults,
        updateIndex,
        exportToCsv,
        exportToJson,
        downloadFile
    };
})(); 