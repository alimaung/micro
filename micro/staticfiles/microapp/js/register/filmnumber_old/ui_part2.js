/**
 * Film Number Results UI Functions - Part 2
 */

import { getState } from './core.js';

// These functions will be exported from the ui.js file
export function updateFilmNumberResults() {
    const state = getState();
    const dom = getDomElements();
    
    if (!state.filmNumberResults) {
        return;
    }
    
    // Update the allocation summary first
    updateAllocationSummary();
    
    // Clear existing roll displays
    clearRollContainers();
    
    // Update 16mm rolls
    if (state.filmNumberResults.rolls_16mm) {
        renderRolls(state.filmNumberResults.rolls_16mm, '16mm');
    }
    
    // Update 35mm rolls if in hybrid mode
    if (state.workflowType === 'hybrid' && state.filmNumberResults.rolls_35mm) {
        renderRolls(state.filmNumberResults.rolls_35mm, '35mm');
    }
    
    // Update split documents if any
    updateSplitDocuments();
    
    // Update JSON details
    if (dom.filmNumberDetailsJson) {
        dom.filmNumberDetailsJson.textContent = JSON.stringify(state.filmNumberResults, null, 2);
    }
}

/**
 * Render rolls into their containers
 */
function renderRolls(rolls, filmType) {
    const dom = getDomElements();
    const container = filmType === '16mm' ? dom.filmRolls16mm : dom.filmRolls35mm;
    
    if (!container) return;
    
    // Clear any existing empty state
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    // For each roll, create a roll card with collapsible document sections
    rolls.forEach(roll => {
        const rollCard = createRollCard(roll, filmType);
        container.appendChild(rollCard);
    });
}

/**
 * Create a roll card element with collapsible document sections
 */
function createRollCard(roll, filmType) {
    const rollCard = document.createElement('div');
    rollCard.className = 'roll-card';
    
    // Create header with film number
    const cardHeader = document.createElement('div');
    cardHeader.className = 'roll-card-header';
    
    // Add film number prominently
    const filmNumberEl = document.createElement('div');
    filmNumberEl.className = 'film-number';
    filmNumberEl.innerHTML = `<strong>Film #:</strong> ${roll.film_number || 'Pending'}`;
    cardHeader.appendChild(filmNumberEl);
    
    // Add roll ID and type
    const rollInfoEl = document.createElement('div');
    rollInfoEl.className = 'roll-info';
    rollInfoEl.innerHTML = `<span>Roll ID: ${roll.roll_id}</span> <span>Type: ${filmType}</span>`;
    cardHeader.appendChild(rollInfoEl);
    
    rollCard.appendChild(cardHeader);
    
    // Create usage statistics
    const usageStats = document.createElement('div');
    usageStats.className = 'usage-stats';
    
    // Calculate utilization
    const utilization = Math.round((roll.pages_used / roll.capacity) * 100);
    
    usageStats.innerHTML = `
        <div class="usage-bar">
            <div class="usage-fill" style="width: ${utilization}%"></div>
        </div>
        <div class="usage-text">
            <span>${roll.pages_used} pages used / ${roll.capacity} capacity (${utilization}%)</span>
        </div>
    `;
    
    rollCard.appendChild(usageStats);
    
    // Create document list with collapse functionality
    if (roll.document_segments && roll.document_segments.length > 0) {
        const docsContainer = document.createElement('div');
        docsContainer.className = 'documents-container';
        
        // Create collapsible header
        const docsHeader = document.createElement('div');
        docsHeader.className = 'docs-header';
        docsHeader.innerHTML = `
            <h5>
                <i class="fas fa-file-alt"></i>
                Documents (${roll.document_segments.length})
            </h5>
            <span class="toggle-icon">
                <i class="fas fa-chevron-down"></i>
            </span>
        `;
        docsContainer.appendChild(docsHeader);
        
        // Create content container
        const docsContent = document.createElement('div');
        docsContent.className = 'docs-content';
        
        // Create table for documents
        const docsTable = document.createElement('table');
        docsTable.className = 'docs-table';
        docsTable.innerHTML = `
            <thead>
                <tr>
                    <th>Doc ID</th>
                    <th>Pages</th>
                    <th>Start Blip</th>
                    <th>End Blip</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;
        
        // Add document segments
        roll.document_segments.forEach(segment => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${segment.doc_id || segment.document_id}</td>
                <td>${segment.pages}</td>
                <td>${segment.blip || 'Pending'}</td>
                <td>${segment.blipend || 'Pending'}</td>
            `;
            docsTable.querySelector('tbody').appendChild(row);
        });
        
        docsContent.appendChild(docsTable);
        docsContainer.appendChild(docsContent);
        rollCard.appendChild(docsContainer);
        
        // Add click event for collapsing/expanding
        docsHeader.addEventListener('click', function() {
            // Toggle collapsed class on header
            this.classList.toggle('collapsed');
            
            // Toggle collapsed class on content
            const content = this.nextElementSibling;
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                content.style.maxHeight = content.scrollHeight + 'px';
                // Animate icon
                const icon = this.querySelector('.toggle-icon i');
                icon.className = 'fas fa-chevron-down';
                icon.classList.add('rotate-icon');
                setTimeout(() => icon.classList.remove('rotate-icon'), 300);
            } else {
                content.classList.add('collapsed');
                content.style.maxHeight = '0';
                // Animate icon
                const icon = this.querySelector('.toggle-icon i');
                icon.className = 'fas fa-chevron-right';
                icon.classList.add('rotate-icon');
                setTimeout(() => icon.classList.remove('rotate-icon'), 300);
            }
        });
    }
    
    return rollCard;
}

/**
 * Clear roll containers
 */
export function clearRollContainers() {
    const dom = getDomElements();
    
    // Clear 16mm container
    if (dom.filmRolls16mm) {
        // Keep empty state but hide it
        const emptyState = dom.filmRolls16mm.querySelector('.empty-state');
        if (emptyState) {
            emptyState.style.display = 'block';
        }
        
        // Remove all roll cards
        const cards = dom.filmRolls16mm.querySelectorAll('.roll-card');
        cards.forEach(card => card.remove());
    }
    
    // Clear 35mm container
    if (dom.filmRolls35mm) {
        // Keep empty state but hide it
        const emptyState = dom.filmRolls35mm.querySelector('.empty-state');
        if (emptyState) {
            emptyState.style.display = 'block';
        }
        
        // Remove all roll cards
        const cards = dom.filmRolls35mm.querySelectorAll('.roll-card');
        cards.forEach(card => card.remove());
    }
}

/**
 * Update split documents display
 */
function updateSplitDocuments() {
    const state = getState();
    const dom = getDomElements();
    
    if (!state.filmNumberResults || !dom.splitDocumentsPanel || !dom.splitDocumentsTable) {
        return;
    }
    
    // Find split documents (documents that appear in multiple rolls)
    const documentSegments = [];
    
    // Process 16mm segments
    if (state.filmNumberResults.rolls_16mm) {
        state.filmNumberResults.rolls_16mm.forEach(roll => {
            if (roll.document_segments) {
                roll.document_segments.forEach(segment => {
                    documentSegments.push({
                        doc_id: segment.doc_id || segment.document_id,
                        pages: segment.pages,
                        roll_id: roll.roll_id,
                        film_number: roll.film_number,
                        blip: segment.blip,
                        film_type: '16mm'
                    });
                });
            }
        });
    }
    
    // Process 35mm segments
    if (state.filmNumberResults.rolls_35mm) {
        state.filmNumberResults.rolls_35mm.forEach(roll => {
            if (roll.document_segments) {
                roll.document_segments.forEach(segment => {
                    documentSegments.push({
                        doc_id: segment.doc_id || segment.document_id,
                        pages: segment.pages,
                        roll_id: roll.roll_id,
                        film_number: roll.film_number,
                        blip: segment.blip,
                        film_type: '35mm'
                    });
                });
            }
        });
    }
    
    // Group by document ID
    const docGroups = {};
    documentSegments.forEach(segment => {
        if (!docGroups[segment.doc_id]) {
            docGroups[segment.doc_id] = {
                doc_id: segment.doc_id,
                totalPages: 0,
                segments: []
            };
        }
        
        docGroups[segment.doc_id].segments.push(segment);
        docGroups[segment.doc_id].totalPages += segment.pages;
    });
    
    // Filter to only split documents (more than one segment)
    const splitDocs = Object.values(docGroups).filter(doc => doc.segments.length > 1);
    
    // If we have split documents, show the panel
    if (splitDocs.length > 0) {
        dom.splitDocumentsPanel.classList.remove('hidden');
        
        // Clear the table
        const tbody = dom.splitDocumentsTable.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = '';
            
            // Add each split document
            splitDocs.forEach(doc => {
                const row = document.createElement('tr');
                
                // Format rolls as comma-separated list
                const rollsText = doc.segments.map(seg => 
                    `${seg.film_number} (${seg.film_type})`
                ).join(', ');
                
                // Format blips
                const blipsText = doc.segments.map(seg => 
                    seg.blip || 'Pending'
                ).join(', ');
                
                row.innerHTML = `
                    <td>${doc.doc_id}</td>
                    <td>${doc.totalPages}</td>
                    <td>${doc.segments.length} parts</td>
                    <td>${rollsText}</td>
                    <td>${blipsText}</td>
                `;
                
                tbody.appendChild(row);
            });
            
            // Hide empty state
            const emptyState = dom.splitDocumentsPanel.querySelector('.empty-state');
            if (emptyState) {
                emptyState.style.display = 'none';
            }
        }
    } else {
        // No split documents, hide the panel
        dom.splitDocumentsPanel.classList.add('hidden');
    }
}

/**
 * Clear film number results
 */
export function clearFilmNumberResults() {
    // Clear roll containers
    clearRollContainers();
    
    // Hide split documents panel
    const dom = getDomElements();
    if (dom.splitDocumentsPanel) {
        dom.splitDocumentsPanel.classList.add('hidden');
    }
    
    // Clear JSON details
    if (dom.filmNumberDetailsJson) {
        dom.filmNumberDetailsJson.textContent = '{}';
    }
}

// Placeholder for getDomElements function reference which will be imported in ui.js
function getDomElements() {
    // This will be replaced with the actual function from ui.js
    return {};
} 