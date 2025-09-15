/**
 * Film Number Allocation UI Module
 * 
 * This module handles all UI operations for the film number allocation step.
 * Uses IIFE pattern to encapsulate functionality while exposing a public API.
 */

const FilmNumberUI = (function() {
    // Private variables
    let domElements = {};
    let isInitialized = false;

    // Private functions
    /**
     * Get DOM elements for UI manipulation
     */
    function getDomElements() {
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

    /**
     * Initialize event listeners
     */
    function initializeEventListeners() {
        if (!isInitialized) {
            const dom = getDomElements();
            
            // Add click handler for start button
            if (dom.startFilmNumberBtn) {
                dom.startFilmNumberBtn.addEventListener('click', function() {
                    const core = window.FilmNumberCore;
                    if (core && typeof core.startFilmNumberAllocation === 'function') {
                        core.startFilmNumberAllocation();
                    } else {
                        console.error('FilmNumberCore.startFilmNumberAllocation is not available');
                    }
                });
            }
            
            isInitialized = true;
        }
    }

    // Calculate utilization percentage
    function calculateUtilization(pagesUsed, rollCount, capacity) {
        if (!rollCount || rollCount === 0 || !capacity) return 0;
        
        const totalCapacity = rollCount * capacity;
        return Math.round((pagesUsed / totalCapacity) * 100);
    }

    /**
     * Clear roll containers
     */
    function clearRollContainers() {
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

    // From ui_part2.js
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
        
        // Add temp roll status badge if temp roll info is available
        if (roll.temp_roll_info || roll.film_number_source) {
            const tempRollBadge = document.createElement('div');
            tempRollBadge.className = 'temp-roll-badge';
            
            let badgeContent = '';
            let badgeClass = '';
            
            // Check if roll has unusable leftover space (UNWIND)
            if (roll.temp_roll_info && roll.temp_roll_info.has_unwind) {
                const unwindCapacity = roll.temp_roll_info.unwind_capacity;
                badgeContent = `UNWIND ${unwindCapacity}p`;
                badgeClass = 'temp-roll-unwind';
            }
            // Check if roll used a temp roll
            else if (roll.temp_roll_info && roll.temp_roll_info.source_temp_roll) {
                const tempRollId = roll.temp_roll_info.source_temp_roll.id;
                badgeContent = `USE T${tempRollId}`;
                badgeClass = 'temp-roll-used';
            }
            // Check if roll created a temp roll
            else if (roll.temp_roll_info && roll.temp_roll_info.created_temp_roll) {
                const tempRollId = roll.temp_roll_info.created_temp_roll.id;
                badgeContent = `CREATE T${tempRollId}`;
                badgeClass = 'temp-roll-created';
            }
            // Check if it's a new roll (only show if no temp roll operations)
            else if ((roll.film_number_source === 'new' || !roll.film_number_source) && 
                     (!roll.temp_roll_info || 
                      (!roll.temp_roll_info.source_temp_roll && 
                       !roll.temp_roll_info.created_temp_roll && 
                       !roll.temp_roll_info.has_unwind))) {
                badgeContent = 'NEW';
                badgeClass = 'temp-roll-new';
            }
            
            if (badgeContent) {
                tempRollBadge.className = `temp-roll-badge ${badgeClass}`;
                tempRollBadge.textContent = badgeContent;
                tempRollBadge.title = getTempRollTooltip(roll);
                cardHeader.appendChild(tempRollBadge);
            }
        }
        
        // Add roll ID and type
        const rollInfoEl = document.createElement('div');
        rollInfoEl.className = 'roll-info';
        rollInfoEl.innerHTML = `<span>Roll ID: ${roll.roll_id}</span> <span>Type: ${filmType}</span>`;
        cardHeader.appendChild(rollInfoEl);
        
        rollCard.appendChild(cardHeader);
        
        // Create usage statistics with multi-colored bar
        const usageStats = document.createElement('div');
        usageStats.className = 'usage-stats';
        
        // Create multi-colored usage bar based on capacity breakdown
        const usageBarHtml = createMultiColoredUsageBar(roll);
        
        usageStats.innerHTML = `
            ${usageBarHtml}
            <div class="usage-text">
                <span>${roll.pages_used} pages used / ${roll.capacity} capacity (${Math.round((roll.pages_used / roll.capacity) * 100)}%)</span>
            </div>
        `;
        
        rollCard.appendChild(usageStats);
        
        // Create document list with collapse functionality
        if (roll.document_segments && roll.document_segments.length > 0) {
            const docsContainer = document.createElement('div');
            docsContainer.className = 'documents-container';
            
            // Create collapsible header
            const docsHeader = document.createElement('div');
            docsHeader.className = 'docs-header collapsed';
            docsHeader.innerHTML = `
                <h5>
                    <i class="fas fa-file-alt"></i>
                    Documents (${roll.document_segments.length})
                </h5>
                <span class="toggle-icon">
                    <i class="fas fa-chevron-right"></i>
                </span>
            `;
            docsContainer.appendChild(docsHeader);
            
            // Create content container
            const docsContent = document.createElement('div');
            docsContent.className = 'docs-content collapsed';
            docsContent.style.maxHeight = '0';
            
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
     * Create multi-colored usage bar based on temp roll status
     */
    function createMultiColoredUsageBar(roll) {
        if (!roll.capacity_breakdown) {
            // Fallback to simple green bar
            const utilization = Math.round((roll.pages_used / roll.capacity) * 100);
            return `
                <div class="usage-bar">
                    <div class="usage-fill" style="width: ${utilization}%"></div>
                </div>
            `;
        }
        
        const breakdown = roll.capacity_breakdown;
        const usedPercent = (breakdown.used / breakdown.total) * 100;
        
        let barHtml = '<div class="usage-bar multi-colored">';
        
        // Always add the used portion (green)
        barHtml += `<div class="usage-fill used" style="width: ${usedPercent}%"></div>`;
        
        // Add temp portion based on type
        if (breakdown.temp_type) {
            let tempPercent = 0;
            let tempClass = '';
            
            switch (breakdown.temp_type) {
                case 'used':
                    // USE case: remaining usable space (blue)
                    tempPercent = (breakdown.temp_remaining / breakdown.total) * 100;
                    tempClass = 'temp-used';
                    break;
                    
                case 'created':
                    // CREATE case: temp roll capacity (yellow)
                    tempPercent = (breakdown.temp_capacity / breakdown.total) * 100;
                    tempClass = 'temp-created';
                    break;
                    
                case 'unwind':
                    // UNWIND case: unusable remainder (red)
                    tempPercent = (breakdown.unwind_capacity / breakdown.total) * 100;
                    tempClass = 'temp-unwind';
                    break;
            }
            
            if (tempPercent > 0) {
                barHtml += `<div class="usage-fill ${tempClass}" style="width: ${tempPercent}%"></div>`;
            }
        }
        
        barHtml += '</div>';
        return barHtml;
    }

    /**
     * Get tooltip text for temp roll badge
     */
    function getTempRollTooltip(roll) {
        if (!roll.temp_roll_info && !roll.film_number_source) {
            return 'New roll with new film number';
        }
        
        if (roll.temp_roll_info && roll.temp_roll_info.has_unwind) {
            const unwindCapacity = roll.temp_roll_info.unwind_capacity;
            return `Unusable leftover space: ${unwindCapacity} pages (requires complete unwind)`;
        }
        
        if (roll.temp_roll_info && roll.temp_roll_info.source_temp_roll) {
            const tempRoll = roll.temp_roll_info.source_temp_roll;
            return `Uses temp roll T${tempRoll.id} (${tempRoll.usable_capacity} usable capacity)`;
        }
        
        if (roll.temp_roll_info && roll.temp_roll_info.created_temp_roll) {
            const tempRoll = roll.temp_roll_info.created_temp_roll;
            return `Created temp roll T${tempRoll.id} (${tempRoll.usable_capacity} usable capacity)`;
        }
        
        if (roll.film_number_source === 'new') {
            return 'New roll with new film number';
        }
        
        return 'Film number allocation information';
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
     * Update split documents display
     */
    function updateSplitDocuments() {
        const core = window.FilmNumberCore;
        const state = core.getState();
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
        
        // Group by document ID AND film type
        const docGroups = {};
        documentSegments.forEach(segment => {
            // Create a composite key that includes both doc_id and film_type
            const groupKey = `${segment.doc_id}_${segment.film_type}`;
            
            if (!docGroups[groupKey]) {
                docGroups[groupKey] = {
                    doc_id: segment.doc_id,
                    film_type: segment.film_type,
                    totalPages: 0,
                    segments: []
                };
            }
            
            docGroups[groupKey].segments.push(segment);
            docGroups[groupKey].totalPages += segment.pages;
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

    // From ui_part3.js
    /**
     * Render rolls before film number allocation with collapsible document sections
     */
    function renderPreAllocatedRolls(rolls, filmType) {
        const dom = getDomElements();
        const container = filmType === '16mm' ? dom.filmRolls16mm : dom.filmRolls35mm;
        
        if (!container) return;
        
        // Clear any existing empty state
        const emptyState = container.querySelector('.empty-state');
        if (emptyState) {
            emptyState.style.display = 'none';
        }
        
        // For each roll, create a roll card without film numbers
        rolls.forEach(roll => {
            const rollCard = document.createElement('div');
            rollCard.className = 'roll-card pre-allocated';
            
            // Create header with placeholder for film number
            const cardHeader = document.createElement('div');
            cardHeader.className = 'roll-card-header';
            
            // Add film number placeholder with "pending" state
            const filmNumberEl = document.createElement('div');
            filmNumberEl.className = 'film-number pending';
            filmNumberEl.innerHTML = `<strong>Film #:</strong> <span class="pending-badge">Pending Allocation</span>`;
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
            const core = window.FilmNumberCore;
            const capacity = filmType === '16mm' ? core.CAPACITY_16MM : core.CAPACITY_35MM;
            const utilization = Math.round((roll.pages_used / capacity) * 100);
            
            usageStats.innerHTML = `
                <div class="usage-bar">
                    <div class="usage-fill" style="width: ${utilization}%"></div>
                </div>
                <div class="usage-text">
                    <span>${roll.pages_used} pages used / ${capacity} capacity (${utilization}%)</span>
                </div>
            `;
            
            rollCard.appendChild(usageStats);
            
            // Create document list with collapsible functionality
            if (roll.document_segments && roll.document_segments.length > 0) {
                const docsContainer = document.createElement('div');
                docsContainer.className = 'documents-container';
                
                // Create collapsible header
                const docsHeader = document.createElement('div');
                docsHeader.className = 'docs-header collapsed';
                docsHeader.innerHTML = `
                    <h5>
                        <i class="fas fa-file-alt"></i>
                        Documents (${roll.document_segments.length})
                    </h5>
                    <span class="toggle-icon">
                        <i class="fas fa-chevron-right"></i>
                    </span>
                `;
                docsContainer.appendChild(docsHeader);
                
                // Create content container
                const docsContent = document.createElement('div');
                docsContent.className = 'docs-content collapsed';
                docsContent.style.maxHeight = '0';
                
                // Create table for documents - use simpler headers without blip info
                const docsTable = document.createElement('table');
                docsTable.className = 'docs-table';
                docsTable.innerHTML = `
                    <thead>
                        <tr>
                            <th>Doc ID</th>
                            <th>Pages</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                `;
                
                // Add document segments
                roll.document_segments.forEach(segment => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${segment.doc_id}</td>
                        <td>${segment.pages}</td>
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
            
            container.appendChild(rollCard);
        });
    }

    // From ui_part4.js
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

    // Helper function to get core module
    function getCore() {
        return window.FilmNumberCore;
    }

    /**
     * Save updated index data to localStorage
     */
    function saveUpdatedIndexToLocalStorage(updatedIndexData) {
        try {
            const core = getCore();
            const state = core.getState();
            
            localStorage.setItem('microfilmUpdatedIndexData', JSON.stringify({
                projectId: state.projectId,
                indexData: updatedIndexData,
                timestamp: new Date().toISOString()
            }));
            console.log('Updated index data saved to localStorage');
        } catch (error) {
            console.error('Error saving updated index data to localStorage:', error);
        }
    }

    // Public API

    // Basic UI Functions from ui.js
    function updateWorkflowTypeUI() {
        const core = window.FilmNumberCore;
        const state = core.getState();
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

    function updateProjectInfo() {
        const core = window.FilmNumberCore;
        const state = core.getState();
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

    function updateAllocationSummary() {
        const core = window.FilmNumberCore;
        const state = core.getState();
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
                core.CAPACITY_16MM
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
                    core.CAPACITY_35MM
                );
                dom.utilization35mm.textContent = `${utilization}%`;
            }
        }
    }

    // From ui_part2.js
    function updateFilmNumberResults() {
        const core = window.FilmNumberCore;
        const state = core.getState();
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

    function clearFilmNumberResults() {
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

    // From ui_part3.js
    function updateStatusBadge(status, text) {
        const dom = getDomElements();
        if (!dom.statusBadge) return;
        
        // Remove existing status classes
        dom.statusBadge.classList.remove('pending', 'in-progress', 'completed', 'error', 'warning');
        
        // Add new status class
        dom.statusBadge.classList.add(status);
        
        // Update icon
        let icon = 'fa-clock';
        switch (status) {
            case 'in-progress':
                icon = 'fa-spinner fa-spin';
                break;
            case 'completed':
                icon = 'fa-check-circle';
                break;
            case 'error':
                icon = 'fa-exclamation-circle';
                break;
            case 'warning':
                icon = 'fa-exclamation-triangle';
                break;
        }
        
        // Update HTML
        dom.statusBadge.innerHTML = `<i class="fas ${icon}"></i> <span>${text}</span>`;
    }

    function showProgressModal() {
        const dom = getDomElements();
        if (dom.progressModal) {
            dom.progressModal.classList.add('show');
        }
    }

    function hideProgressModal() {
        const dom = getDomElements();
        if (dom.progressModal) {
            dom.progressModal.classList.remove('show');
        }
    }

    function updateProgress(progress) {
        const dom = getDomElements();
        if (dom.progressBar) {
            dom.progressBar.style.width = `${progress}%`;
            dom.progressBar.setAttribute('aria-valuenow', progress);
        }
    }

    function updateProgressText(text) {
        const dom = getDomElements();
        if (dom.progressText) {
            dom.progressText.textContent = text;
        }
    }

    function showError(message) {
        console.error('Film number allocation error:', message);
        
        // Create or update error container
        let errorContainer = document.getElementById('filmnumber-error-container');
        
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.id = 'filmnumber-error-container';
            errorContainer.className = 'error-container';
            
            // Insert after status badge
            const dom = getDomElements();
            if (dom.statusBadge && dom.statusBadge.parentNode) {
                dom.statusBadge.parentNode.insertBefore(errorContainer, dom.statusBadge.nextSibling);
            } else {
                // Fallback - insert at the beginning of the component
                const component = document.querySelector('.allocation-component');
                if (component) {
                    component.insertBefore(errorContainer, component.firstChild);
                }
            }
        }
        
        errorContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                ${message}
            </div>
        `;
        
        errorContainer.style.display = 'block';
    }

    function prePopulateFromAllocation() {
        const core = window.FilmNumberCore;
        const state = core.getState();
        const dom = getDomElements();
        
        if (!state.allocationResults) {
            return;
        }
        
        // Update allocation summary
        updateAllocationSummary();
        
        // Clear existing roll displays
        clearRollContainers();
        
        // Get allocation results in the correct structure
        let allocationData;
        if (state.allocationResults.allocationResults && state.allocationResults.allocationResults.results) {
            allocationData = state.allocationResults.allocationResults.results;
        } else if (state.allocationResults.results) {
            allocationData = state.allocationResults.results;
        } else {
            allocationData = state.allocationResults;
        }
        
        console.log('Pre-populating UI with allocation data:', allocationData);
        
        // Display 16mm rolls
        if (allocationData.rolls_16mm && allocationData.rolls_16mm.length > 0) {
            renderPreAllocatedRolls(allocationData.rolls_16mm, '16mm');
        }
        
        // Display 35mm rolls if in hybrid mode
        if (state.workflowType === 'hybrid' && allocationData.rolls_35mm && allocationData.rolls_35mm.length > 0) {
            renderPreAllocatedRolls(allocationData.rolls_35mm, '35mm');
        }
        
        // Update JSON details
        if (dom.filmNumberDetailsJson) {
            dom.filmNumberDetailsJson.textContent = JSON.stringify(allocationData, null, 2);
        }
    }

    // Show a toast message
    function showToast(message, type = 'info') {
        // Check if toast container exists, create if not
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Auto-remove after delay
        setTimeout(() => {
            toast.classList.add('toast-hide');
            setTimeout(() => {
                toastContainer.removeChild(toast);
            }, 300);
        }, 3000);
    }

    // From ui_part4.js
    function initIndexTable() {
        console.log('Initializing index table...');
        const core = window.FilmNumberCore;
        const state = core.getState();
        console.log('Current state during table init:', state);
        
        // Try to load index data from localStorage
        const indexData = core.getLocalStorageData('microfilmIndexData');
        console.log('Index data loaded during table init:', indexData);
        
        if (indexData) {
            console.log('Found index data in localStorage:', indexData);
            // Transform and update state
            const entries = core.transformToUnifiedFormat(indexData);
            console.log('Transformed entries:', entries);
            
            state.indexData = {
                entries: entries,
                status: core.calculateIndexStatus(entries)
            };
            console.log('Updated state.indexData:', state.indexData);
            
            // Update the index table
            updateIndexTable();
        } else {
            console.log('No index data found in localStorage');
            // Show message in the index panel
            const tableBody = document.getElementById('index-table-body');
            if (tableBody) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td colspan="7" style="text-align: center; padding: 1rem;">
                        <i class="fas fa-info-circle"></i> No index data available. Please complete the index generation step first.
                    </td>
                `;
                tableBody.appendChild(row);
            }
        }
        
        // Bind events for export buttons
        bindIndexExportEvents();
    }

    function updateIndexTable() {
        console.log('Updating index table...');
        const core = window.FilmNumberCore;
        const state = core.getState();
        console.log('Current state during table update:', state);
        
        // First check if we have the new filmIndexData structure, and if not fall back to indexData
        const indexDataToUse = state.filmIndexData || state.indexData;
        
        if (!indexDataToUse || !indexDataToUse.entries) {
            console.warn('No index data available for table update');
            return;
        }
        
        const tableBody = document.getElementById('index-table-body');
        if (!tableBody) {
            console.error('Table body element not found');
            return;
        }
        
        // Clear the table
        tableBody.innerHTML = '';
        
        // Get entries from the selected data source
        const entries = indexDataToUse.entries;
        console.log('Number of entries to display:', entries.length);
        console.log('Using data source:', state.filmIndexData ? 'filmIndexData' : 'indexData');
        
        // Sort entries naturally by document ID
        const sortedEntries = [...entries].sort((a, b) => {
            const aId = String(a.docId);
            const bId = String(b.docId);
            
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
        console.log('Number of entries being displayed:', displayEntries.length);
        
        // Add rows for each index entry
        displayEntries.forEach(entry => {
            const row = document.createElement('tr');
            
            // Add status-based class
            if (entry.status === 'Updated') {
                row.className = 'updated-entry';
            }
            
            row.innerHTML = `
                <td>${entry.docId}</td>
                <td>${entry.comId}</td>
                <td>${entry.rollId || '-'}</td>
                <td>${entry.frameStart ? `${entry.frameStart}-${entry.frameEnd}` : '-'}</td>
                <td>${entry.filmNumber || 'N/A'}</td>
                <td>${entry.finalIndex || 'Pending'}</td>
                <td><span class="status-badge ${entry.status.toLowerCase()}">${entry.status}</span></td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Update statistics
        updateIndexStatistics();
        
        // Update table info
        const tableInfo = document.getElementById('table-info');
        if (tableInfo) {
            tableInfo.textContent = `Showing ${displayEntries.length} of ${entries.length} entries`;
        }
        
        console.log('Table update complete');
    }

    function updateIndexStatistics() {
        const core = window.FilmNumberCore;
        const state = core.getState();
        
        // First check if we have the new filmIndexData structure, and if not fall back to indexData
        const indexDataToUse = state.filmIndexData || state.indexData;
        
        if (!indexDataToUse || !indexDataToUse.status) return;
        
        const stats = indexDataToUse.status;
        
        // Update statistics display
        const totalEntriesEl = document.getElementById('total-entries');
        const updatedEntriesEl = document.getElementById('updated-entries');
        const pendingEntriesEl = document.getElementById('pending-entries');
        
        if (totalEntriesEl) totalEntriesEl.textContent = stats.totalEntries;
        if (updatedEntriesEl) updatedEntriesEl.textContent = stats.updatedEntries;
        if (pendingEntriesEl) pendingEntriesEl.textContent = stats.pendingEntries;
    }

    function exportIndexToCsv() {
        const core = window.FilmNumberCore;
        const state = core.getState();
        
        // First check if we have the new filmIndexData structure, and if not fall back to indexData
        const indexDataToUse = state.filmIndexData || state.indexData;
        
        if (!indexDataToUse || !indexDataToUse.entries) {
            showToast('No index data to export', 'error');
            return;
        }
        
        // Generate CSV content
        const csvContent = generateCsvFromIndexData(indexDataToUse.entries);
        
        // Generate filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `index-${state.projectId}-${timestamp}.csv`;
        
        // Download the file
        downloadFile(csvContent, filename, 'text/csv');
        
        // Show success message
        showToast('CSV exported successfully', 'success');
    }

    function generateCsvFromIndexData(entries) {
        // Generate CSV header
        let csv = 'Document ID,COM ID,Roll ID,Frame Start,Frame End,Film Number,Final Index,Status\n';
        
        // Generate CSV rows
        entries.forEach(entry => {
            csv += `${entry.docId},${entry.comId},${entry.rollId || ''},` +
                   `${entry.frameStart || ''},${entry.frameEnd || ''},` +
                   `${entry.filmNumber || 'N/A'},${entry.finalIndex || 'Pending'},${entry.status}\n`;
        });
        
        return csv;
    }

    function exportIndexToJson() {
        const core = window.FilmNumberCore;
        const state = core.getState();
        
        if (!state.indexData || !state.indexData.entries) {
            showToast('No index data to export', 'error');
            return;
        }
        
        // Generate filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `index-${state.projectId}-${timestamp}.json`;
        
        // Download the file
        const jsonString = JSON.stringify(state.indexData, null, 2);
        downloadFile(jsonString, filename, 'application/json');
        
        // Show success message
        showToast('JSON exported successfully', 'success');
    }

    function downloadFile(content, filename, contentType) {
        const a = document.createElement('a');
        const file = new Blob([content], {type: contentType});
        
        a.href = URL.createObjectURL(file);
        a.download = filename;
        a.click();
        
        URL.revokeObjectURL(a.href);
    }

    // Return public API
    return {
        // UI Part 1: Basic UI functions
        updateWorkflowTypeUI,
        updateProjectInfo,
        updateAllocationSummary,
        
        // UI Part 2: Film number results functions
        updateFilmNumberResults,
        clearFilmNumberResults,
        
        // UI Part 3: Status and progress functions
        updateStatusBadge,
        showProgressModal,
        hideProgressModal,
        updateProgress,
        updateProgressText,
        showError,
        prePopulateFromAllocation,
        showToast,
        
        // UI Part 4: Index table functions
        initIndexTable,
        updateIndexTable,
        exportIndexToCsv,
        generateCsvFromIndexData,
        exportIndexToJson,
        downloadFile,

        getDomElements,

        // Add initialization method
        initialize: function() {
            getDomElements();
            initializeEventListeners();
        }
    };
})();

// Make FilmNumberUI available globally
window.FilmNumberUI = FilmNumberUI;