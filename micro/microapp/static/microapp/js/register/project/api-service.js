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
        // Return a mock result indicating transfer functionality has been removed
        if (progressCallback) {
            // Simulate some basic progress to ensure logs are working
            progressCallback({
                file: "Transfer functionality removed",
                fileCompleted: true,
                fileProgress: 1.0,
                overallProgress: 1.0,
                bytesTransferred: 0,
                filesTransferred: 0,
                totalFiles: files ? files.length : 0,
                speed: 0
            });
        }
        
        // Return a completed status after a short delay to simulate response
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            status: 'completed',
            filesTransferred: 0,
            bytesTransferred: 0,
            errors: [{message: 'Transfer functionality has been removed'}]
        };
    }
    
    /**
     * Poll the transfer progress endpoint until the transfer is complete
     * This is a stub method since transfer functionality has been removed
     * @param {string} transferId - ID of the transfer
     * @param {Function} progressCallback - Progress callback
     * @param {number} totalBytes - Total bytes to transfer
     * @param {number} startTime - Start time of the transfer
     * @returns {Promise<Object>} - Transfer result
     */
    async _pollTransferProgress(transferId, progressCallback, totalBytes, startTime) {
        // Just return a completed status immediately
        if (progressCallback) {
            progressCallback({
                file: "Transfer functionality removed",
                fileCompleted: true,
                fileProgress: 1.0,
                overallProgress: 1.0,
                bytesTransferred: 0,
                filesTransferred: 0,
                totalFiles: 0,
                speed: 0,
                timeRemaining: 0
            });
        }
        
        // Return a completed status
        return {
            status: 'completed',
            filesTransferred: 0,
            bytesTransferred: 0,
            errors: [{message: 'Transfer functionality has been removed'}]
        };
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
