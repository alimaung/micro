/**
 * Reference Sheet Calculation Module
 * 
 * Provides functionality to:
 * - Calculate reference sheet positions
 * - Group oversized pages into ranges
 * - Determine optimal reference sheet placement
 */

/**
 * Calculate reference sheets positions for a document
 * @param {Object} document - Document data with oversized page information
 * @returns {Object} - The same document with reference sheet information added
 */
function calculateDocumentReferences(document) {
    // Skip documents with no oversized pages
    if (!document.hasOversized || !document.oversizedPages || document.oversizedPages.length === 0) {
        document.referencePages = [];
        document.totalReferences = 0;
        document.adjusted_ranges = [];
        return document;
    }
    
    // Sort oversized pages
    const sortedPages = [...document.oversizedPages].sort((a, b) => a - b);
    
    // Group consecutive pages into ranges
    const ranges = [];
    let currentRange = [sortedPages[0]];
    
    for (let i = 1; i < sortedPages.length; i++) {
        const currentPage = sortedPages[i];
        const prevPage = sortedPages[i - 1];
        
        // If pages are consecutive, add to current range
        if (currentPage === prevPage + 1) {
            currentRange.push(currentPage);
        } else {
            // Otherwise, finish current range and start a new one
            ranges.push([...currentRange]);
            currentRange = [currentPage];
        }
    }
    
    // Add the last range
    if (currentRange.length > 0) {
        ranges.push([...currentRange]);
    }
    
    // Calculate reference page positions (one reference page per range)
    const referencePages = ranges.map(range => range[0]);
    
    // Update document with reference information
    document.referencePages = referencePages;
    document.referenceRanges = ranges.map(range => ({
        start: range[0],
        end: range[range.length - 1],
        pages: range.length
    }));
    document.totalReferences = referencePages.length;
    
    // Calculate adjusted ranges (accounting for inserted reference sheets)
    const adjusted_ranges = [];
    let shift = 0; // Track how many reference sheets have been inserted
    
    for (let i = 0; i < ranges.length; i++) {
        const range = ranges[i];
        const start = range[0];
        const end = range[range.length - 1];
        
        // Adjust the range start and end based on previously inserted reference sheets
        const adjusted_start = start + shift;
        const adjusted_end = end + shift;
        
        // Store the adjusted range
        adjusted_ranges.push({
            original: [start, end],
            adjusted: [adjusted_start, adjusted_end],
            reference_page: referencePages[i] + shift // The reference page also needs adjustment
        });
        
        // Increment shift for next ranges
        shift += 1;
    }
    
    document.adjusted_ranges = adjusted_ranges;
    
    return document;
}

/**
 * Calculate reference sheets for all documents in the analysis results
 * @param {Array} documents - Array of document analysis results
 * @returns {Object} - Object with reference statistics and updated documents
 */
function calculateAllReferences(documents) {
    if (!documents || documents.length === 0) {
        return {
            totalReferences: 0,
            totalPagesWithRefs: 0,
            documents: [],
            hasReferences: false
        };
    }
    
    // Calculate references for each document
    const updatedDocuments = documents.map(calculateDocumentReferences);
    
    // Calculate total references
    const totalReferences = updatedDocuments.reduce(
        (total, doc) => total + (doc.totalReferences || 0), 
        0
    );
    
    // Calculate total pages including references
    const totalOriginalPages = updatedDocuments.reduce(
        (total, doc) => total + (doc.pages || 0), 
        0
    );
    
    // Check if any document has references
    const hasReferences = totalReferences > 0;
    
    return {
        totalReferences: totalReferences,
        totalPagesWithRefs: totalOriginalPages + totalReferences,
        documents: updatedDocuments,
        hasReferences: hasReferences
    };
}

/**
 * Save reference sheet calculations to project state
 * @param {Object} referenceData - The calculated reference data
 */
function saveReferenceData(referenceData) {
    try {
        // Get current workflow state
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        
        // Update with reference information
        workflowState.referenceData = referenceData;
        workflowState.totalReferences = referenceData.totalReferences;
        workflowState.totalPagesWithRefs = referenceData.totalPagesWithRefs;
        
        // Save back to localStorage
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
        
        // Also save in the step-specific data
        if (typeof saveStepData === 'function') {
            saveStepData('references', referenceData);
        }
        
    } catch (error) {
        console.error('[References] Error saving reference data to localStorage:', error);
    }
}

// Export functions for use in other modules
window.calculateDocumentReferences = calculateDocumentReferences;
window.calculateAllReferences = calculateAllReferences;
window.saveReferenceData = saveReferenceData; 