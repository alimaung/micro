/**
 * Allocation Data Utilities
 * 
 * This module provides utilities for saving and loading allocation data
 * to avoid localStorage quota issues with large datasets.
 */

/**
 * Get CSRF token for Django requests
 */
function getCsrfToken() {
    const tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (tokenElement) return tokenElement.value;
    
    const name = 'csrftoken=';
    const cookies = document.cookie.split(';');
    for (const c of cookies) {
        const v = c.trim();
        if (v.startsWith(name)) return decodeURIComponent(v.substring(name.length));
    }
    return null;
}

/**
 * Get project ID from various sources
 */
function getProjectId() {
    // Try URL parameters first
    const urlParams = new URLSearchParams(window.location.search);
    let projectId = urlParams.get('id');
    
    if (projectId) return projectId;
    
    // Try from localStorage project state
    try {
        const projectState = localStorage.getItem('microfilmProjectState');
        if (projectState) {
            const parsed = JSON.parse(projectState);
            if (parsed.projectId) return parsed.projectId;
        }
    } catch (error) {
        console.warn('Error getting project ID from localStorage:', error);
    }
    
    return null;
}

/**
 * Save allocation data to project .data folder
 * 
 * @param {Object} allocationData - The allocation data to save
 * @param {string} projectId - Optional project ID (will auto-detect if not provided)
 * @returns {Promise<boolean>} - Success status
 */
async function saveAllocationDataToProject(allocationData, projectId = null) {
    try {
        projectId = projectId || getProjectId();
        
        if (!projectId) {
            console.error('[AllocationUtils] No project ID available for saving allocation data');
            return false;
        }
        
        // Get project state for destination path
        let projectState = null;
        try {
            const projectStateJSON = localStorage.getItem('microfilmProjectState');
            if (projectStateJSON) {
                projectState = JSON.parse(projectStateJSON);
            }
        } catch (error) {
            console.warn('[AllocationUtils] Could not get project state:', error);
        }
        
        // Prepare data to save
        const dataToSave = {
            allocationResults: allocationData,
            lastUpdated: new Date().toISOString(),
            projectId: projectId,
            completed: true
        };
        
        // Include project state if available for path resolution
        if (projectState) {
            dataToSave.projectState = projectState;
        }
        
        const response = await fetch(`/api/allocation/${projectId}/save-data/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(dataToSave)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('[AllocationUtils] Saved allocation data to project folder:', result.path);
            
            // Store a small reference in localStorage instead of full data
            localStorage.setItem('microfilmAllocationData', JSON.stringify({
                __dataFolder: true,
                projectId: projectId,
                lastUpdated: new Date().toISOString(),
                completed: true,
                savedToPath: result.path
            }));
            
            return true;
        } else {
            const error = await response.json();
            console.error('[AllocationUtils] Failed to save allocation data:', error.message);
            return false;
        }
        
    } catch (error) {
        console.error('[AllocationUtils] Error saving allocation data to project:', error);
        return false;
    }
}

/**
 * Load allocation data from project .data folder or localStorage
 * 
 * @param {string} projectId - Optional project ID (will auto-detect if not provided)
 * @returns {Promise<Object|null>} - The allocation data or null if not found
 */
async function loadAllocationData(projectId = null) {
    try {
        projectId = projectId || getProjectId();
        
        if (!projectId) {
            console.error('[AllocationUtils] No project ID available for loading allocation data');
            return null;
        }
        
        // First check localStorage for reference
        const localData = localStorage.getItem('microfilmAllocationData');
        if (localData) {
            const parsed = JSON.parse(localData);
            
            // If it's a reference to .data folder, load from API
            if (parsed.__dataFolder && parsed.projectId === projectId) {
                console.log('[AllocationUtils] Loading allocation data from project .data folder');
                
                const response = await fetch(`/api/allocation/${projectId}/load-data/`);
                if (response.ok) {
                    const result = await response.json();
                    return result.data;
                } else {
                    console.warn('[AllocationUtils] Could not load from project folder, trying fallbacks');
                }
            } else if (parsed.allocationResults) {
                // It's actual data in localStorage (small projects or old format)
                console.log('[AllocationUtils] Loading allocation data from localStorage');
                return parsed;
            }
        }
        
        // Fallback: try RegisterStorage service
        if (window.RegisterStorage) {
            console.log('[AllocationUtils] Trying RegisterStorage service');
            try {
                const data = await window.RegisterStorage.loadKey(projectId, 'microfilmAllocationData');
                if (data) {
                    return data;
                }
            } catch (error) {
                console.warn('[AllocationUtils] RegisterStorage failed:', error);
            }
        }
        
        console.warn('[AllocationUtils] No allocation data found');
        return null;
        
    } catch (error) {
        console.error('[AllocationUtils] Error loading allocation data:', error);
        return null;
    }
}

/**
 * Check if allocation data exists for the current project
 * 
 * @param {string} projectId - Optional project ID (will auto-detect if not provided)
 * @returns {Promise<boolean>} - Whether allocation data exists
 */
async function hasAllocationData(projectId = null) {
    const data = await loadAllocationData(projectId);
    return data !== null && data.allocationResults !== undefined;
}

/**
 * Get allocation data synchronously from localStorage (for backward compatibility)
 * This should only be used when async loading is not possible
 * 
 * @returns {Object|null} - The allocation data or null if not found
 */
function getAllocationDataSync() {
    try {
        const localData = localStorage.getItem('microfilmAllocationData');
        if (localData) {
            const parsed = JSON.parse(localData);
            
            // If it's a reference to .data folder, we can't load synchronously
            if (parsed.__dataFolder) {
                console.warn('[AllocationUtils] Allocation data is in project folder, use loadAllocationData() instead');
                return null;
            }
            
            return parsed;
        }
        return null;
    } catch (error) {
        console.error('[AllocationUtils] Error getting allocation data synchronously:', error);
        return null;
    }
}

// Export functions for use in other modules
if (typeof window !== 'undefined') {
    window.AllocationDataUtils = {
        saveAllocationDataToProject,
        loadAllocationData,
        hasAllocationData,
        getAllocationDataSync,
        getProjectId,
        getCsrfToken
    };
}
