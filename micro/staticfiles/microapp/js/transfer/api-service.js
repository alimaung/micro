/**
 * api-service.js - API interactions for Transfer module
 * Handles all API calls to the server
 */

// Make the class available globally
window.ApiService = class ApiService {
    constructor() {
        // Initialize the database service
        this.dbService = new DatabaseService();
    }

    /**
     * Get file statistics from server
     * @param {string} path - Path to get statistics for
     * @returns {Promise<Object>} - Statistics object
     */
    async getFileStats(path) {
        if (!path) {
            throw new Error('No source path specified');
        }
        
        try {
            // Make API call to get file statistics
            const apiEndpoint = '/get-file-statistics/?path=' + encodeURIComponent(path);
            
            const response = await fetch(apiEndpoint, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to get file statistics. Status: ' + response.status);
            }
            
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            
            return {
                fileCount: data.fileCount,
                totalSize: data.totalSize,
                files: data.files
            };
        } catch (error) {
            console.error('Error getting file statistics:', error);
            throw error;
        }
    }
    
    /**
     * Get folder structure from server
     * @param {string} path - Path to get structure for
     * @param {boolean} scanSubdirectories - Whether to scan subdirectories
     * @returns {Promise<Object>} - Folder structure object
     */
    async getFolderStructure(path, scanSubdirectories = true) {
        if (!path) {
            throw new Error('No source path specified');
        }
        
        try {
            // Make API call to scan folder structure
            const apiEndpoint = '/list-drive-contents/?path=' + 
                encodeURIComponent(path) + 
                '&scan_subdirectories=' + (scanSubdirectories ? 'true' : 'false');
            
            const response = await fetch(apiEndpoint, {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`Failed to get folder structure: ${response.statusText}`);
            }
            
            const folderData = await response.json();
            
            return {
                folders: folderData.folders || [],
                files: folderData.files || [],
                currentPath: folderData.currentPath || path,
                fullStructure: folderData.fullStructure || null
            };
        } catch (error) {
            console.error('Error getting folder structure:', error);
            throw error;
        }
    }
    
    /**
     * Transfer files from source to destination
     * @param {string} sourcePath - Source path
     * @param {string} destinationPath - Destination path
     * @param {Array} files - Array of files to transfer
     * @param {Function} progressCallback - Progress callback
     * @returns {Promise<Object>} - Transfer result object
     */
    async transferFiles(sourcePath, destinationPath, files, progressCallback) {
        if (!sourcePath || !destinationPath || !files || !files.length) {
            throw new Error('Invalid transfer parameters');
        }
        
        // Create a formatted list of files for the backend
        const filesList = files.map(file => ({
            path: file.path || `${sourcePath}\\${file.name}`,
            name: file.name,
            size: file.size,
            relPath: file.relPath || ''
        }));
        
        // Set up progress tracking variables
        let totalBytes = files.reduce((total, f) => total + f.size, 0);
        let bytesTransferred = 0;
        let filesTransferred = 0;
        let startTime = Date.now();
        
        try {
            // Call backend API to initiate transfer
            const response = await fetch('/transfer-files/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.dbService._getCsrfToken()
                },
                body: JSON.stringify({
                    sourcePath,
                    destinationPath,
                    files: filesList
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Transfer failed');
            }
            
            // Start polling for progress
            const transferId = await response.json();
            
            // Poll for transfer progress until complete
            return await this._pollTransferProgress(
                transferId.id,
                progressCallback,
                totalBytes,
                startTime
            );
        } catch (error) {
            console.error('Transfer files error:', error);
            throw error;
        }
    }
    
    /**
     * Poll the transfer progress endpoint until the transfer is complete
     * @param {string} transferId - ID of the transfer
     * @param {Function} progressCallback - Progress callback
     * @param {number} totalBytes - Total bytes to transfer
     * @param {number} startTime - Start time of the transfer
     * @returns {Promise<Object>} - Transfer result
     */
    async _pollTransferProgress(transferId, progressCallback, totalBytes, startTime) {
        let completed = false;
        
        while (!completed) {
            try {
                // Wait a bit before polling again
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Get progress update
                const response = await fetch(`/transfer-progress/?id=${transferId}`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to get transfer progress');
                }
                
                const progress = await response.json();
                
                // Update UI with progress
                if (progressCallback) {
                    const elapsedSeconds = (Date.now() - startTime) / 1000;
                    const bytesPerSecond = progress.bytesTransferred / elapsedSeconds;
                    const timeRemaining = (totalBytes - progress.bytesTransferred) / bytesPerSecond;
                    
                    progressCallback({
                        file: progress.currentFile,
                        fileProgress: progress.fileProgress,
                        overallProgress: progress.bytesTransferred / totalBytes,
                        bytesTransferred: progress.bytesTransferred,
                        filesTransferred: progress.filesTransferred,
                        totalFiles: progress.totalFiles,
                        speed: bytesPerSecond,
                        timeRemaining: timeRemaining
                    });
                }
                
                // Check if transfer is complete
                if (progress.status === 'completed' || 
                    progress.status === 'error' || 
                    progress.status === 'cancelled') {
                    completed = true;
                    
                    return {
                        status: progress.status,
                        filesTransferred: progress.filesTransferred,
                        bytesTransferred: progress.bytesTransferred,
                        errors: progress.errors || []
                    };
                }
            } catch (error) {
                console.error('Error polling transfer progress:', error);
                throw error;
            }
        }
    }
    
    /**
     * Create a new project in the database
     * @param {Object} projectData - Project data to save
     * @returns {Promise<Object>} - Response object
     */
    async createProject(projectData) {
        try {
            // Use the DatabaseService to create the project
            return await this.dbService.createProject(projectData);
        } catch (error) {
            console.error('Error creating project:', error);
            throw error;
        }
    }
}
