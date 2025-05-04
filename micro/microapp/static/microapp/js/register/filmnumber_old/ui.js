/**
 * Film Number Allocation UI Module
 * 
 * This module handles all UI operations for the film number allocation step.
 * It imports functions from the UI part files to avoid token limitations.
 */

import { getState, CAPACITY_16MM, CAPACITY_35MM, getLocalStorageData } from './core.js';

// Cache DOM elements
let domElements = {};

/**
 * Get DOM elements for UI manipulation
 */
export function getDomElements() {
    if (Object.keys(domElements).length === 0) {
        // Initialize dom element cache
        domElements = {
            // Status and controls
            statusBadge: document.getElementById('filmnumber-status-badge'),
            startFilmNumberBtn: document.getElementById('start-filmnumber'),
            resetFilmNumberBtn: document.getElementById('reset-filmnumber'),
            toNextStepBtn: document.getElementById('to-step-6'),
            backBtn: document.getElementById('back-to-allocation'),
            
            // Project info
            projectId: document.getElementById('project-id'),
            documentCount: document.getElementById('document-count'),
            totalPages: document.getElementById('total-pages'),
            workflowType: document.getElementById('workflow-type'),
            oversizedCount: document.getElementById('oversized-count'),
            
            // Film sections
            film16mmSection: document.getElementById('film-16mm-section'),
            film35mmSection: document.getElementById('film-35mm-section'),
            
            // Roll counts and containers
            rollCount16mm: document.getElementById('roll-count-16mm'),
            pagesAllocated16mm: document.getElementById('pages-allocated-16mm'),
            utilization16mm: document.getElementById('utilization-16mm'),
            filmRolls16mm: document.getElementById('film-rolls-16mm'),
            
            rollCount35mm: document.getElementById('roll-count-35mm'),
            pagesAllocated35mm: document.getElementById('pages-allocated-35mm'),
            utilization35mm: document.getElementById('utilization-35mm'),
            filmRolls35mm: document.getElementById('film-rolls-35mm'),
            
            // Split documents
            splitDocumentsPanel: document.getElementById('split-documents-panel'),
            splitDocumentsTable: document.getElementById('split-documents-table'),
            
            // Details
            filmNumberDetailsJson: document.getElementById('filmnumber-details-json'),
            
            // Progress modal
            progressModal: document.getElementById('filmnumber-progress-modal'),
            progressBar: document.getElementById('filmnumber-progress-bar'),
            progressText: document.getElementById('filmnumber-progress-text')
        };
    }
    return domElements;
}

// Import all UI functions from part files

// Part 1: Basic UI functions
export function updateWorkflowTypeUI() {
    const state = getState();
    const dom = getDomElements();
    
    // Update workflow type display
    if (dom.workflowType) {
        dom.workflowType.textContent = state.workflowType === 'hybrid' ? 'Hybrid (16mm + 35mm)' : 'Standard (16mm only)';
    }
    
    // Show/hide 35mm section based on workflow type
    if (dom.film35mmSection) {
        if (state.workflowType === 'hybrid') {
            dom.film35mmSection.classList.remove('hidden');
        } else {
            dom.film35mmSection.classList.add('hidden');
        }
    }
}

export function updateProjectInfo() {
    const state = getState();
    const dom = getDomElements();
    
    if (!state.analysisResults) {
        return;
    }
    
    // Update project ID
    if (dom.projectId) {
        dom.projectId.textContent = state.projectId || '-';
    }
    
    // Get analysis results
    const analysisResults = state.analysisResults.analysisResults || state.analysisResults;
    
    // Update document count
    if (dom.documentCount) {
        dom.documentCount.textContent = analysisResults.totalDocuments || 
                                        analysisResults.documents?.length || '0';
    }
    
    // Update total pages
    if (dom.totalPages) {
        dom.totalPages.textContent = analysisResults.totalPages || '0';
    }
    
    // Update oversized count
    if (dom.oversizedCount) {
        dom.oversizedCount.textContent = analysisResults.oversizedPages || '0';
    }
}

export function updateAllocationSummary() {
    const state = getState();
    const dom = getDomElements();
    
    if (!state.allocationResults) {
        return;
    }
    
    // Get the allocation results, handling different structure possibilities
    let allocationResults;
    
    // Handle the specific allocationData structure from your application
    if (state.allocationResults.allocationResults && state.allocationResults.allocationResults.results) {
        // This matches the structure in your sample data
        allocationResults = state.allocationResults.allocationResults.results;
    } else if (state.allocationResults.results) {
        allocationResults = state.allocationResults.results;
    } else {
        allocationResults = state.allocationResults;
    }
    
    console.log('Using allocation results structure:', allocationResults);
    
    // Update 16mm summary
    if (dom.rollCount16mm && allocationResults.total_rolls_16mm !== undefined) {
        dom.rollCount16mm.textContent = allocationResults.total_rolls_16mm;
    }
    
    if (dom.pagesAllocated16mm && allocationResults.total_pages_16mm !== undefined) {
        dom.pagesAllocated16mm.textContent = allocationResults.total_pages_16mm;
    }
    
    if (dom.utilization16mm) {
        const utilization = calculateUtilization(
            allocationResults.total_pages_16mm, 
            allocationResults.total_rolls_16mm,
            CAPACITY_16MM
        );
        dom.utilization16mm.textContent = `${utilization}%`;
    }
    
    // Update 35mm summary if in hybrid mode
    if (state.workflowType === 'hybrid') {
        if (dom.rollCount35mm && allocationResults.total_rolls_35mm !== undefined) {
            dom.rollCount35mm.textContent = allocationResults.total_rolls_35mm;
        }
        
        if (dom.pagesAllocated35mm && allocationResults.total_pages_35mm !== undefined) {
            dom.pagesAllocated35mm.textContent = allocationResults.total_pages_35mm;
        }
        
        if (dom.utilization35mm) {
            const utilization = calculateUtilization(
                allocationResults.total_pages_35mm,
                allocationResults.total_rolls_35mm,
                CAPACITY_35MM
            );
            dom.utilization35mm.textContent = `${utilization}%`;
        }
    }
}

// Calculate utilization percentage
function calculateUtilization(pagesUsed, rollCount, capacity) {
    if (!rollCount || rollCount === 0 || !capacity) return 0;
    
    const totalCapacity = rollCount * capacity;
    return Math.round((pagesUsed / totalCapacity) * 100);
}

// From UI part 2
export { 
    updateFilmNumberResults,
    clearRollContainers,
    clearFilmNumberResults
} from './ui_part2.js';

// From UI part 3
export {
    updateStatusBadge,
    showProgressModal,
    hideProgressModal,
    updateProgress,
    updateProgressText,
    showError,
    prePopulateFromAllocation,
    showToast
} from './ui_part3.js';

// From UI part 4
export {
    initIndexTable,
    updateFinalIndexTable,
    exportIndexToCsv,
    generateCsvFromIndexData,
    exportIndexToJson,
    downloadFile
} from './ui_part4.js'; 