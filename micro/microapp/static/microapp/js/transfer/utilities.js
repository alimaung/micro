/**
 * utilities.js - Helper functions for the Transfer module
 * Contains utility functions for formatting, path manipulation, etc.
 */

// Make the class available globally
window.Utilities = class Utilities {
    /**
     * Format file size to human-readable format
     * @param {number} bytes - Size in bytes
     * @returns {string} - Formatted size string
     */
    formatSize(bytes) {
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }
    
    /**
     * Format time to human-readable format
     * @param {number} seconds - Time in seconds
     * @returns {string} - Formatted time string
     */
    formatTime(seconds) {
        if (isNaN(seconds) || !isFinite(seconds)) {
            return 'Unknown';
        }
        
        if (seconds < 60) {
            return `${Math.ceil(seconds)} seconds`;
        }
        
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) {
            return `${minutes} minute${minutes > 1 ? 's' : ''}`;
        }
        
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return `${hours} hour${hours > 1 ? 's' : ''} ${remainingMinutes} minute${remainingMinutes > 1 ? 's' : ''}`;
    }
    
    /**
     * Extract folder name from path
     * @param {string} path - Full path
     * @returns {string} - Folder name
     */
    extractFolderName(path) {
        const pathParts = path.split('\\');
        return pathParts[pathParts.length - 1];
    }
    
    /**
     * Ensure path ends with backslash
     * @param {string} path - Path to check
     * @returns {string} - Path with trailing backslash
     */
    ensureTrailingSlash(path) {
        return path.endsWith('\\') ? path : path + '\\';
    }
    
    /**
     * Normalize a file path to use consistent separators
     * @param {string} path - Path to normalize 
     * @returns {string} - Normalized path
     */
    normalizePath(path) {
        return path.replace(/\//g, '\\');
    }
};
