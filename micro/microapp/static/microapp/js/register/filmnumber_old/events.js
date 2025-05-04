/**
 * Film Number Allocation Events Module
 * 
 * This module handles all event binding and event handling for the film number allocation step.
 */

import { getState, startFilmNumberAllocation, resetFilmNumberAllocation } from './core.js';
import * as FilmNumberUI from './ui.js';

/**
 * Bind all event listeners
 */
export function bindEvents() {
    const dom = FilmNumberUI.getDomElements();
    
    // Start film number allocation button
    if (dom.startFilmNumberBtn) {
        dom.startFilmNumberBtn.addEventListener('click', startFilmNumberAllocation);
    }
    
    // Reset button
    if (dom.resetFilmNumberBtn) {
        dom.resetFilmNumberBtn.addEventListener('click', resetFilmNumberAllocation);
    }
    
    // Navigation buttons
    if (dom.backBtn) {
        dom.backBtn.addEventListener('click', navigateToAllocation);
    }
    
    if (dom.toNextStepBtn) {
        dom.toNextStepBtn.addEventListener('click', navigateToNextStep);
    }
    
    // Copy and export buttons
    const copyBtn = document.getElementById('copy-filmnumber-data');
    if (copyBtn) {
        copyBtn.addEventListener('click', copyFilmNumberData);
    }
    
    const exportBtn = document.getElementById('export-filmnumber-data');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportFilmNumberData);
    }
    
    // Add event listeners for index table pagination and filtering
    const searchInput = document.getElementById('index-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            filterIndexTable(this.value);
        }, 300));
    }
    
    // Add event listeners for final index table pagination and filtering
    const finalSearchInput = document.getElementById('final-index-search');
    if (finalSearchInput) {
        finalSearchInput.addEventListener('input', debounce(function() {
            filterFinalIndexTable(this.value);
        }, 300));
    }
}

/**
 * Navigate back to allocation
 */
function navigateToAllocation() {
    const state = getState();
    window.location.href = `/register/allocation/?id=${state.projectId}&flow=${state.workflowType}`;
}

/**
 * Navigate to the next step
 */
function navigateToNextStep() {
    const state = getState();
    window.location.href = `/register/indexgen/?id=${state.projectId}&flow=${state.workflowType}`;
}

/**
 * Copy film number data to clipboard
 */
function copyFilmNumberData() {
    const dom = FilmNumberUI.getDomElements();
    if (dom.filmNumberDetailsJson) {
        const text = dom.filmNumberDetailsJson.textContent;
        navigator.clipboard.writeText(text)
            .then(() => {
                // Show success message
                const copyBtn = document.getElementById('copy-filmnumber-data');
                if (copyBtn) {
                    const originalTitle = copyBtn.getAttribute('title');
                    copyBtn.setAttribute('title', 'Copied!');
                    copyBtn.classList.add('success');
                    
                    // Reset after short delay
                    setTimeout(() => {
                        copyBtn.setAttribute('title', originalTitle);
                        copyBtn.classList.remove('success');
                    }, 2000);
                }
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
            });
    }
}

/**
 * Export film number data as JSON file
 */
function exportFilmNumberData() {
    const state = getState();
    
    if (!state.filmNumberResults) return;
    
    // Prepare data
    const data = JSON.stringify(state.filmNumberResults, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Create download link
    const a = document.createElement('a');
    a.href = url;
    a.download = `film_number_allocation_${state.projectId}_${new Date().toISOString().slice(0, 10)}.json`;
    
    // Trigger download
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 0);
}

/**
 * Filter index table based on search term
 * 
 * @param {string} searchTerm - Search term to filter by
 */
function filterIndexTable(searchTerm) {
    const state = getState();
    if (!state.indexData) return;
    
    const tableBody = document.getElementById('index-table-body');
    if (!tableBody) return;
    
    // Clear the table
    tableBody.innerHTML = '';
    
    // Get entries
    let entries = [];
    if (state.indexData.index && Array.isArray(state.indexData.index)) {
        entries = state.indexData.index;
    } else if (Array.isArray(state.indexData)) {
        entries = state.indexData;
    } else {
        console.error('Unknown index data format:', state.indexData);
        return;
    }
    
    // Filter entries if search term provided
    let filteredEntries = entries;
    if (searchTerm && searchTerm.trim() !== '') {
        const term = searchTerm.trim().toLowerCase();
        filteredEntries = entries.filter(entry => {
            // Search in doc ID and COM ID
            const docId = String(entry[0]).toLowerCase();
            const comId = String(entry[1]).toLowerCase();
            
            return docId.includes(term) || comId.includes(term);
        });
    }
    
    // Sort entries by document ID (natural sort)
    const sortedEntries = [...filteredEntries].sort((a, b) => {
        const aId = String(a[0]);
        const bId = String(b[0]);
        
        // Extract numbers from document IDs if present
        const aNum = /^(\d+)/.exec(aId);
        const bNum = /^(\d+)/.exec(bId);
        
        // If both IDs start with numbers, compare them numerically
        if (aNum && bNum) {
            return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
        }
        
        // Otherwise, fall back to standard string comparison
        return aId.localeCompare(bId);
    });
    
    // Limit display for performance
    const displayLimit = 100;
    const displayEntries = sortedEntries.slice(0, displayLimit);
    
    // Add rows for each index entry
    displayEntries.forEach(entry => {
        const docId = entry[0];
        const comId = entry[1];
        const initialIndex = entry[2] || [0, 0, 0];
        const finalIndex = entry[3] || 'Pending';
        
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
        tableInfo.textContent = `Showing ${displayEntries.length} of ${filteredEntries.length} entries`;
    }
}

/**
 * Filter final index table based on search term
 * 
 * @param {string} searchTerm - Search term to filter by
 */
function filterFinalIndexTable(searchTerm) {
    const state = getState();
    if (!state.updatedIndexData) return;
    
    const tableBody = document.getElementById('final-index-table-body');
    if (!tableBody) return;
    
    // Clear the table
    tableBody.innerHTML = '';
    
    // Get entries
    let entries = [];
    if (state.updatedIndexData.index && Array.isArray(state.updatedIndexData.index)) {
        entries = state.updatedIndexData.index;
    } else if (Array.isArray(state.updatedIndexData)) {
        entries = state.updatedIndexData;
    } else {
        console.error('Unknown index data format:', state.updatedIndexData);
        return;
    }
    
    // Filter entries if search term provided
    let filteredEntries = entries;
    if (searchTerm && searchTerm.trim() !== '') {
        const term = searchTerm.trim().toLowerCase();
        filteredEntries = entries.filter(entry => {
            // Search in doc ID, COM ID, and film number
            const docId = String(entry[0]).toLowerCase();
            const comId = String(entry[1]).toLowerCase();
            const rollId = entry[2] ? String(entry[2][0]).toLowerCase() : '';
            const finalIndex = entry[3] ? String(entry[3]).toLowerCase() : '';
            
            return docId.includes(term) || comId.includes(term) || 
                   rollId.includes(term) || finalIndex.includes(term);
        });
    }
    
    // Sort entries by document ID (natural sort)
    const sortedEntries = [...filteredEntries].sort((a, b) => {
        const aId = String(a[0]);
        const bId = String(b[0]);
        
        // Extract numbers from document IDs if present
        const aNum = /^(\d+)/.exec(aId);
        const bNum = /^(\d+)/.exec(bId);
        
        // If both IDs start with numbers, compare them numerically
        if (aNum && bNum) {
            return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
        }
        
        // Otherwise, fall back to standard string comparison
        return aId.localeCompare(bId);
    });
    
    // Limit display for performance
    const displayLimit = 100;
    const displayEntries = sortedEntries.slice(0, displayLimit);
    
    // Add rows for each index entry
    displayEntries.forEach(entry => {
        // Try to find film number for this roll
        const rollId = entry[2] ? entry[2][0] : null;
        let filmNumber = "Not assigned";
        
        // If we have film number results, look up the film number
        if (state.filmNumberResults && rollId) {
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
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${entry[0]}</td>
            <td>${entry[1]}</td>
            <td>${rollId || '-'}</td>
            <td>${filmNumber}</td>
            <td>${entry[3] || 'Pending'}</td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Update table info
    const finalTableInfo = document.getElementById('final-table-info');
    if (finalTableInfo) {
        finalTableInfo.textContent = `Showing ${displayEntries.length} of ${filteredEntries.length} entries`;
    }
}

/**
 * Debounce function to limit how often a function is called
 * 
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait between calls
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
} 