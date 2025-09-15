/**
 * Film Number UI Index Table Functions - Part 4
 */

import { getState, getLocalStorageData } from './core.js';

/**
 * Initialize index table functionality
 */
export function initIndexTable() {
    const state = getState();
    
    // Try to load index data from localStorage
    const indexData = getLocalStorageData('microfilmIndexData');
    if (indexData && indexData.indexData) {
        console.log('Found index data in localStorage:', indexData);
        state.indexData = indexData.indexData;
        
        // Update the initial index table
        updateIndexTable(state.indexData);
    } else {
        console.log('No index data found in localStorage');
        // Show message in the index panel
        const tableBody = document.getElementById('index-table-body');
        if (tableBody) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="5" style="text-align: center; padding: 1rem;">
                    <i class="fas fa-info-circle"></i> No index data available. Please complete the index generation step first.
                </td>
            `;
            tableBody.appendChild(row);
        }
    }
    
    // Bind events for export buttons
    bindIndexExportEvents();
}

/**
 * Update the index table with data
 * 
 * @param {Object} indexData - The index data to display
 */
function updateIndexTable(indexData) {
    const tableBody = document.getElementById('index-table-body');
    if (!tableBody) return;
    
    // Clear the table
    tableBody.innerHTML = '';
    
    // Handle different index data formats
    let entries = [];
    if (indexData.index && Array.isArray(indexData.index)) {
        entries = indexData.index;
    } else if (Array.isArray(indexData)) {
        entries = indexData;
    } else {
        console.error('Unknown index data format:', indexData);
        return;
    }
    
    // Helper function for natural sorting of document IDs
    const naturalSort = (a, b) => {
        // Sort by docId (first element in entry array)
        const aId = a[0];
        const bId = b[0];
        
        // Extract numbers from document IDs if present
        const aNum = /^(\d+)/.exec(aId);
        const bNum = /^(\d+)/.exec(bId);
        
        // If both IDs start with numbers, compare them numerically
        if (aNum && bNum) {
            return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
        }
        
        // Otherwise, fall back to standard string comparison
        return aId.localeCompare(bId);
    };
    
    // Sort entries naturally by document ID
    const sortedEntries = [...entries].sort(naturalSort);
    
    // Limit display for performance
    const displayLimit = 100;
    const displayEntries = sortedEntries.slice(0, displayLimit);
    
    // Add rows for each index entry
    displayEntries.forEach(entry => {
        const docId = entry[0];
        const comId = entry[1];
        const initialIndex = entry[2] || [0, 0, 0];
        const finalIndex = entry[3] || 'Pending';
        const docIndex = entry[4] || 1;
        
        const rollId = initialIndex[0];
        const frameStart = initialIndex[1];
        const frameEnd = initialIndex[2];
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${docId}</td>
            <td>${comId}</td>
            <td>${rollId}</td>
            <td>${frameStart}-${frameEnd}</td>
            <td>${finalIndex}</td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Update table info
    const tableInfo = document.getElementById('table-info');
    if (tableInfo) {
        tableInfo.textContent = `Showing ${displayEntries.length} of ${entries.length} entries`;
    }
}

/**
 * Update the final index table with film numbers
 */
export function updateFinalIndexTable() {
    const state = getState();
    const tableBody = document.getElementById('final-index-table-body');
    if (!tableBody || !state.indexData) return;
    
    // Clear the table
    tableBody.innerHTML = '';
    
    // Clone the index data to avoid modifying the original
    const updatedIndexData = JSON.parse(JSON.stringify(state.indexData));
    
    // Handle different index data formats
    let entries = [];
    if (updatedIndexData.index && Array.isArray(updatedIndexData.index)) {
        entries = updatedIndexData.index;
    } else if (Array.isArray(updatedIndexData)) {
        entries = updatedIndexData;
    } else {
        console.error('Unknown index data format:', updatedIndexData);
        return;
    }
    
    // Update entries with film numbers
    let updatedCount = 0;
    let missingCount = 0;
    
    entries.forEach(entry => {
        // The initialIndex is the 3rd element (index 2) in the entry array
        if (entry[2]) {
            const rollId = entry[2][0];
            
            // Try to find film number for this roll
            let filmNumber = "Not assigned";
            
            // If we have film number results, look up the film number
            if (state.filmNumberResults) {
                // Check 16mm rolls
                if (state.filmNumberResults.rolls_16mm) {
                    const roll = state.filmNumberResults.rolls_16mm.find(r => r.roll_id === rollId);
                    if (roll && roll.film_number) {
                        filmNumber = roll.film_number;
                        updatedCount++;
                        
                        // Update the final index (4th element, index 3)
                        // Generate a blip-like format: filmNumber-docIndex.frameStart
                        const docIndex = entry[4] || 1;
                        const frameStart = entry[2][1] || 1;
                        entry[3] = `${filmNumber}-${docIndex.toString().padStart(4, '0')}.${frameStart.toString().padStart(5, '0')}`;
                    }
                }
                
                // Check 35mm rolls if film number still not found
                if (filmNumber === "Not assigned" && state.filmNumberResults.rolls_35mm) {
                    const roll = state.filmNumberResults.rolls_35mm.find(r => r.roll_id === rollId);
                    if (roll && roll.film_number) {
                        filmNumber = roll.film_number;
                        updatedCount++;
                        
                        // Update the final index (4th element, index 3)
                        const docIndex = entry[4] || 1;
                        const frameStart = entry[2][1] || 1;
                        entry[3] = `${filmNumber}-${docIndex.toString().padStart(4, '0')}.${frameStart.toString().padStart(5, '0')}`;
                    }
                }
            }
            
            if (filmNumber === "Not assigned") {
                missingCount++;
            }
            
            // Create row
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${entry[0]}</td>
                <td>${entry[1]}</td>
                <td>${rollId}</td>
                <td>${filmNumber}</td>
                <td>${entry[3] || 'Pending'}</td>
            `;
            
            tableBody.appendChild(row);
        }
    });
    
    // Update statistics
    const totalEntriesEl = document.getElementById('total-entries');
    const updatedEntriesEl = document.getElementById('updated-entries');
    const missingEntriesEl = document.getElementById('missing-entries');
    
    if (totalEntriesEl) {
        totalEntriesEl.textContent = entries.length;
    }
    
    if (updatedEntriesEl) {
        updatedEntriesEl.textContent = updatedCount;
    }
    
    if (missingEntriesEl) {
        missingEntriesEl.textContent = missingCount;
    }
    
    // Show the final index panel
    const finalIndexPanel = document.getElementById('final-index-panel');
    if (finalIndexPanel) {
        finalIndexPanel.classList.remove('hidden');
    }
    
    // Store the updated index data
    state.updatedIndexData = updatedIndexData;
    
    // Save to localStorage
    saveUpdatedIndexToLocalStorage(updatedIndexData);
    
    return updatedIndexData;
}

/**
 * Save updated index data to localStorage
 */
function saveUpdatedIndexToLocalStorage(updatedIndexData) {
    try {
        localStorage.setItem('microfilmUpdatedIndexData', JSON.stringify({
            projectId: getState().projectId,
            indexData: updatedIndexData,
            timestamp: new Date().toISOString()
        }));
        console.log('Updated index data saved to localStorage');
    } catch (error) {
        console.error('Error saving updated index data to localStorage:', error);
    }
}

/**
 * Bind events for index export buttons
 */
function bindIndexExportEvents() {
    // Bind event for download CSV button
    const downloadCsvBtn = document.getElementById('download-csv');
    if (downloadCsvBtn) {
        downloadCsvBtn.addEventListener('click', function() {
            exportIndexToCsv(false);
        });
    }
    
    // Bind event for download final CSV button
    const downloadFinalCsvBtn = document.getElementById('download-final-csv');
    if (downloadFinalCsvBtn) {
        downloadFinalCsvBtn.addEventListener('click', function() {
            exportIndexToCsv(true);
        });
    }
    
    // Bind event for export JSON button
    const exportJsonBtn = document.getElementById('export-json');
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', function() {
            exportIndexToJson();
        });
    }
}

/**
 * Export index to CSV
 * 
 * @param {boolean} isFinal - Whether to export the final index
 */
export function exportIndexToCsv(isFinal) {
    const state = getState();
    
    const indexData = isFinal ? state.updatedIndexData : state.indexData;
    
    if (!indexData) {
        showToast('No index data to export', 'error');
        return;
    }
    
    // Generate CSV content from index data
    const csvContent = generateCsvFromIndexData(indexData, isFinal);
    
    // Generate filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `index-${state.projectId}-${isFinal ? 'with-film-numbers' : 'initial'}-${timestamp}.csv`;
    
    // Download the file
    downloadFile(csvContent, filename, 'text/csv');
    
    // Show success message
    showToast('CSV exported successfully', 'success');
}

/**
 * Generate CSV content from index data
 * 
 * @param {Object} indexData - The index data
 * @param {boolean} isFinal - Whether to include final index
 * @returns {string} - CSV content
 */
export function generateCsvFromIndexData(indexData, isFinal) {
    // Handle different data formats
    let entries = [];
    
    if (Array.isArray(indexData)) {
        entries = indexData;
    } else if (indexData.index && Array.isArray(indexData.index)) {
        entries = indexData.index;
    } else if (indexData.data && Array.isArray(indexData.data)) {
        entries = indexData.data;
    } else if (indexData.results && Array.isArray(indexData.results)) {
        entries = indexData.results;
    } else {
        console.error('Unknown index data format:', indexData);
        return '';
    }
    
    // Generate CSV header
    let csv = isFinal 
        ? 'Document ID,COM ID,Roll ID,Film Number,Final Index\n' 
        : 'Document ID,COM ID,Roll ID,Frame Start,Frame End,Final Index\n';
    
    // Generate CSV rows
    entries.forEach(entry => {
        let docId, comId, initialIndex, finalIndex;
        
        // Handle different entry formats
        if (Array.isArray(entry)) {
            [docId, comId, initialIndex, finalIndex] = entry;
        } else {
            docId = entry.doc_id || entry.docId || '-';
            comId = entry.com_id || entry.comId || '-';
            initialIndex = entry.initial_index || entry.initialIndex || [0, 0, 0];
            finalIndex = entry.final_index || entry.finalIndex || '-';
        }
        
        // Ensure initialIndex is properly formatted
        if (!initialIndex || !Array.isArray(initialIndex)) {
            initialIndex = [0, 0, 0];
        }
        
        const rollId = initialIndex[0];
        const frameStart = initialIndex[1];
        const frameEnd = initialIndex[2];
        
        // For final index, try to get film number
        let filmNumber = "Not assigned";
        if (isFinal) {
            const state = getState();
            if (state.filmNumberResults) {
                // Check 16mm rolls
                if (state.filmNumberResults.rolls_16mm) {
                    const roll = state.filmNumberResults.rolls_16mm.find(r => r.roll_id === rollId);
                    if (roll && roll.film_number) {
                        filmNumber = roll.film_number;
                    }
                }
                
                // Check 35mm rolls if film number still not found
                if (filmNumber === "Not assigned" && state.filmNumberResults.rolls_35mm) {
                    const roll = state.filmNumberResults.rolls_35mm.find(r => r.roll_id === rollId);
                    if (roll && roll.film_number) {
                        filmNumber = roll.film_number;
                    }
                }
            }
        }
        
        if (isFinal) {
            csv += `${docId},${comId},${rollId},${filmNumber},${finalIndex}\n`;
        } else {
            csv += `${docId},${comId},${rollId},${frameStart},${frameEnd},${finalIndex}\n`;
        }
    });
    
    return csv;
}

/**
 * Export index to JSON
 */
export function exportIndexToJson() {
    const state = getState();
    
    if (!state.updatedIndexData) {
        showToast('No updated index data to export', 'error');
        return;
    }
    
    // Generate filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `index-with-film-numbers-${state.projectId}-${timestamp}.json`;
    
    // Download the file
    const jsonString = JSON.stringify(state.updatedIndexData, null, 2);
    downloadFile(jsonString, filename, 'application/json');
    
    // Show success message
    showToast('JSON exported successfully', 'success');
}

/**
 * Download a file
 * 
 * @param {string} content - The file content
 * @param {string} filename - The filename
 * @param {string} contentType - The content type
 */
export function downloadFile(content, filename, contentType) {
    const a = document.createElement('a');
    const file = new Blob([content], {type: contentType});
    
    a.href = URL.createObjectURL(file);
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(a.href);
}

// Placeholder functions that will be imported in ui.js
function showToast() {} 