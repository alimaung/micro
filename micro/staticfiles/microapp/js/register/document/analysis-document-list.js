/**
 * Document Analysis Document List Module
 * 
 * Handles document list management:
 * - Adding documents to the list
 * - Clearing the document list
 * - Updating the document list with new data
 */

/**
 * Clear the document list
 */
function clearDocumentList() {
    if (!analysisState.documentList) return;
    
    // Check if documentList is a DOM element or an array
    if (typeof analysisState.documentList.innerHTML === 'undefined') {
        // It's not a DOM element, might be an array
        console.log('[Analysis] documentList is not a DOM element, cannot clear');
        return;
    }
    
    // Clear the list
    analysisState.documentList.innerHTML = '';
    
    // Add empty message
    const emptyMessage = document.createElement('div');
    emptyMessage.className = 'empty-list-message';
    emptyMessage.textContent = 'No documents analyzed yet';
    analysisState.documentList.appendChild(emptyMessage);
}

/**
 * Add a document to the list
 * @param {Object} docData - Document object to add
 */
function addDocumentToList(docData) {
    if (!analysisState.documentList) return;
    
    // Remove empty message if it exists
    const emptyMessage = analysisState.documentList.querySelector('.empty-list-message');
    if (emptyMessage) {
        analysisState.documentList.removeChild(emptyMessage);
    }
    
    // Get document name for display and fallback ID
    const docDisplayName = docData.fileName || docData.name || 'Unknown Document';
    
    // Create document item
    const docItem = document.createElement('div');
    docItem.className = 'document-item';
    // Use id if available, otherwise use name or fileName as the identifier
    docItem.setAttribute('data-doc-id', docData.id || docData.name || docData.fileName || 'doc-' + Math.random().toString(36).substr(2, 9));
    
    // Create document name
    const docName = document.createElement('div');
    docName.className = 'doc-name';
    docName.textContent = docDisplayName;
    
    // Create pages count
    const docPages = document.createElement('div');
    docPages.className = 'doc-pages';
    docPages.textContent = docData.pages;
    
    // Create oversized count
    const docOversized = document.createElement('div');
    docOversized.className = 'doc-oversized';
    // Use oversizedPages if available, fall back to totalOversized property
    docOversized.textContent = docData.oversizedPages || docData.totalOversized || 0;
    
    // Create status
    const docStatus = document.createElement('div');
    docStatus.className = 'doc-status';
    
    // Create badge
    const badge = document.createElement('span');
    badge.className = 'document-badge';
    
    if (docData.hasOversized) {
        badge.classList.add('badge-oversized');
        badge.textContent = 'Oversized';
    } else {
        badge.classList.add('badge-standard');
        badge.textContent = 'Standard';
    }
    
    // Assemble document item
    docStatus.appendChild(badge);
    docItem.appendChild(docName);
    docItem.appendChild(docPages);
    docItem.appendChild(docOversized);
    docItem.appendChild(docStatus);
    
    // Add to list
    analysisState.documentList.appendChild(docItem);
}

/**
 * Update document list with new documents
 * @param {Array} documents - Array of document objects
 */
function updateDocumentList(documents) {
    console.log('[Analysis DocumentList] updateDocumentList called with', documents ? documents.length : 0, 'documents');
    
    if (!documents || documents.length === 0) {
        console.log('[Analysis DocumentList] No documents provided, skipping update');
        return;
    }
    
    // Log the first document for debugging
    if (documents.length > 0) {
        console.log('[Analysis DocumentList] First document sample:', documents[0]);
    }
    
    // Clear current list
    clearDocumentList();
    
    // Sort documents naturally by name/filename
    const naturalSort = (a, b) => {
        // Get document names to compare
        const aName = a.fileName || a.name || '';
        const bName = b.fileName || b.name || '';
        
        // Extract numbers from document names if present
        const aNum = /^(\d+)/.exec(aName);
        const bNum = /^(\d+)/.exec(bName);
        
        // If both names start with numbers, compare them numerically
        if (aNum && bNum) {
            return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
        }
        
        // Otherwise, fall back to standard string comparison
        return aName.localeCompare(bName);
    };
    
    // Create a sorted copy of the documents array
    const sortedDocuments = [...documents].sort(naturalSort);
    
    // Add each document
    sortedDocuments.forEach(docData => {
        addDocumentToList(docData);
    });
    
    console.log('[Analysis DocumentList] Document list updated with', documents.length, 'documents');
}

// Export functions for use in other modules
window.clearDocumentList = clearDocumentList;
window.addDocumentToList = addDocumentToList;
window.updateDocumentList = updateDocumentList; 