/**
 * Analyze Page JavaScript
 * Handles all functionality for the analyze page and project detail view
 */

// Global state for sorting and view
let currentView = 'card'; // 'card' or 'table'
let currentSort = {
    field: 'name',
    direction: 'asc'
};

// Initialize from URL parameters if available
function initializeSortFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const sortField = urlParams.get('sort');
    const sortDirection = urlParams.get('dir');
    
    if (sortField) {
        currentSort.field = sortField;
    }
    if (sortDirection) {
        currentSort.direction = sortDirection;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Analyze page loaded');
    
    // Initialize the analyze page
    initializeAnalyzePage();
});

/**
 * Initialize the analyze page
 */
function initializeAnalyzePage() {
    console.log('Initializing analyze page...');
    
    // DEBUG: Log what sections are loaded
    logSectionDebugInfo();
    
    // Initialize from URL parameters
    initializeSortFromURL();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize tooltips and interactive elements
    initializeInteractiveElements();
    
    // Initialize section toggles for detail view
    initializeSectionToggles();
    
    // Initialize raw data tabs
    initializeRawDataTabs();
    
    // Initialize sorting and view controls
    initializeSortingAndViewControls();
}

/**
 * Initialize sorting and view controls
 */
function initializeSortingAndViewControls() {
    // Initialize view toggle
    initializeViewToggle();
    
    // Initialize sorting controls
    initializeSortingControls();
    
    // Set initial sort control values
    updateSortControlsFromState();
    
    // Apply initial view state
    updateViewDisplay();
}

/**
 * Initialize view toggle (card/table)
 */
function initializeViewToggle() {
    // Create view toggle if it doesn't exist
    if (!document.querySelector('.view-toggle')) {
        createViewToggle();
    }
    
    // Add event listeners for view toggle
    const cardViewBtn = document.querySelector('.view-toggle .card-view');
    const tableViewBtn = document.querySelector('.view-toggle .table-view');
    
    if (cardViewBtn) {
        cardViewBtn.addEventListener('click', () => switchView('card'));
    }
    
    if (tableViewBtn) {
        tableViewBtn.addEventListener('click', () => switchView('table'));
    }
}

/**
 * Initialize sorting controls
 */
function initializeSortingControls() {
    // Create sort controls if they don't exist
    if (!document.querySelector('.sort-controls')) {
        createSortControls();
    }
    
    // Add event listeners for sort controls
    const sortSelect = document.querySelector('.sort-select');
    const sortDirectionBtn = document.querySelector('.sort-direction');
    
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            currentSort.field = e.target.value;
            applySorting();
        });
    }
    
    if (sortDirectionBtn) {
        sortDirectionBtn.addEventListener('click', () => {
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            updateSortDirectionIcon();
            applySorting();
        });
    }
}

/**
 * Create view toggle controls
 */
function createViewToggle() {
    const controlsContainer = document.querySelector('.controls-container');
    if (!controlsContainer) return;
    
    // Check if view toggle already exists
    if (controlsContainer.querySelector('.view-toggle')) return;
    
    const viewToggle = document.createElement('div');
    viewToggle.className = 'view-toggle';
    viewToggle.innerHTML = `
        <div class="toggle-group">
            <button class="toggle-btn card-view active" title="Card View">
                <i class="fas fa-th-large"></i>
            </button>
            <button class="toggle-btn table-view" title="Table View">
                <i class="fas fa-table"></i>
            </button>
        </div>
    `;
    
    controlsContainer.appendChild(viewToggle);
}

/**
 * Create sort controls
 */
function createSortControls() {
    const controlsContainer = document.querySelector('.controls-container');
    if (!controlsContainer) return;
    
    // Check if sort controls already exist
    if (controlsContainer.querySelector('.sort-controls')) return;
    
    const sortControls = document.createElement('div');
    sortControls.className = 'sort-controls';
    sortControls.innerHTML = `
        <div class="sort-group">
            <select class="sort-select">
                <option value="name">Name</option>
                <option value="size">Size</option>
                <option value="files">Files</option>
                <option value="pdfs">PDFs</option>
                <option value="documents">Documents</option>
                <option value="pages">Pages</option>
                <option value="rolls">Rolls</option>
                <option value="utilization">Utilization</option>
                <option value="oversized">Oversized</option>
                <option value="location">Location</option>
                <option value="status">Status</option>
                <option value="date">Date</option>
            </select>
            <button class="sort-direction" title="Sort Direction">
                <i class="fas fa-sort-alpha-down"></i>
            </button>
        </div>
    `;
    
    controlsContainer.appendChild(sortControls);
}

/**
 * Switch between card and table view
 */
function switchView(viewType) {
    currentView = viewType;
    
    // Update toggle buttons
    const cardBtn = document.querySelector('.view-toggle .card-view');
    const tableBtn = document.querySelector('.view-toggle .table-view');
    
    if (cardBtn && tableBtn) {
        cardBtn.classList.toggle('active', viewType === 'card');
        tableBtn.classList.toggle('active', viewType === 'table');
    }
    
    // Update view display
    updateViewDisplay();
}

/**
 * Update the display based on current view
 */
function updateViewDisplay() {
    const sections = document.querySelectorAll('.section-container');
    
    sections.forEach(section => {
        const cardsGrid = section.querySelector('.cards-grid');
        if (!cardsGrid) return;
        
        if (currentView === 'table') {
            createTableView(section, cardsGrid);
        } else {
            restoreCardView(section);
        }
    });
}

/**
 * Create table view for a section
 */
function createTableView(section, cardsGrid) {
    // Check if table already exists
    let tableContainer = section.querySelector('.table-container');
    
    if (!tableContainer) {
        tableContainer = document.createElement('div');
        tableContainer.className = 'table-container';
        cardsGrid.insertAdjacentElement('afterend', tableContainer);
    }
    
    // Get section type
    const sectionType = getSectionType(section);
    
    // Generate table HTML
    const tableHTML = generateTableHTML(cardsGrid, sectionType);
    tableContainer.innerHTML = tableHTML;
    
    // Hide cards grid and show table
    cardsGrid.style.display = 'none';
    tableContainer.style.display = 'block';
}

/**
 * Restore card view for a section
 */
function restoreCardView(section) {
    const cardsGrid = section.querySelector('.cards-grid');
    const tableContainer = section.querySelector('.table-container');
    
    if (cardsGrid) {
        cardsGrid.style.display = 'grid';
    }
    
    if (tableContainer) {
        tableContainer.style.display = 'none';
    }
}

/**
 * Get section type from section element
 */
function getSectionType(section) {
    if (section.classList.contains('unanalyzed-section')) return 'unanalyzed';
    if (section.classList.contains('analyzed-section')) return 'analyzed';
    if (section.classList.contains('registered-section')) return 'registered';
    return 'unknown';
}

/**
 * Generate table HTML for a section
 */
function generateTableHTML(cardsGrid, sectionType) {
    const cards = cardsGrid.querySelectorAll('.folder-card, .project-card');
    
    let headerHTML = '';
    let rowsHTML = '';
    
    if (sectionType === 'unanalyzed') {
        headerHTML = `
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Path</th>
                    <th>Total Files</th>
                    <th>PDFs</th>
                    <th>Excel</th>
                    <th>Others</th>
                    <th>Size</th>
                    <th>Actions</th>
                </tr>
            </thead>
        `;
        
        cards.forEach(card => {
            const name = card.querySelector('h3')?.textContent || 'N/A';
            const path = card.querySelector('.folder-path span')?.getAttribute('title') || 'N/A';
            const totalFiles = card.querySelector('.metric:nth-child(1) .metric-value')?.textContent || '0';
            const pdfs = card.querySelector('.metric:nth-child(2) .metric-value')?.textContent || '0';
            const excel = card.querySelector('.metric:nth-child(3) .metric-value')?.textContent || '0';
            const others = card.querySelector('.metric:nth-child(4) .metric-value')?.textContent || '0';
            const size = card.querySelector('.metric:nth-child(5) .metric-value')?.textContent || 'N/A';
            const actions = card.querySelector('.card-actions')?.innerHTML || '';
            
            rowsHTML += `
                <tr>
                    <td class="name-cell">${name}</td>
                    <td class="path-cell" title="${path}">${truncateText(path, 50)}</td>
                    <td class="number-cell">${totalFiles}</td>
                    <td class="number-cell">${pdfs}</td>
                    <td class="number-cell">${excel}</td>
                    <td class="number-cell">${others}</td>
                    <td class="size-cell">${size}</td>
                    <td class="actions-cell">${actions}</td>
                </tr>
            `;
        });
    } else if (sectionType === 'analyzed') {
        headerHTML = `
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Path</th>
                    <th>Documents</th>
                    <th>Pages</th>
                    <th>16mm Rolls</th>
                    <th>35mm Rolls</th>
                    <th>Oversized</th>
                    <th>Utilization</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
        `;
        
        cards.forEach(card => {
            const name = card.querySelector('h3')?.textContent || 'N/A';
            const path = card.querySelector('.folder-path span')?.getAttribute('title') || 'N/A';
            const documents = card.querySelector('.metric:nth-child(1) .metric-value')?.textContent || '0';
            const pages = card.querySelector('.metric:nth-child(2) .metric-value')?.textContent || '0';
            
            // Extract roll counts (need to handle dynamic metrics)
            const filmMetrics = card.querySelectorAll('.metric-film .metric-value');
            let rolls16mm = '0';
            let rolls35mm = '0';
            
            filmMetrics.forEach(metric => {
                const label = metric.parentElement.querySelector('.metric-label')?.textContent || '';
                if (label.includes('16mm')) {
                    rolls16mm = metric.textContent || '0';
                } else if (label.includes('35mm')) {
                    rolls35mm = metric.textContent || '0';
                }
            });
            
            // If no specific roll metrics, try to get from general metric
            if (rolls16mm === '0' && rolls35mm === '0') {
                const generalRoll = card.querySelector('.metric:not(.metric-film):not(.metric-oversized) .metric-label');
                if (generalRoll && generalRoll.textContent.includes('Rolls')) {
                    const rollValue = generalRoll.parentElement.querySelector('.metric-value')?.textContent || '0';
                    rolls16mm = rollValue; // Default to 16mm if not specified
                }
            }
            
            const oversized = card.querySelector('.metric-oversized .metric-value')?.textContent || '0';
            const utilization = card.querySelector('.utilization-percentage')?.textContent || 'N/A';
            const status = card.querySelector('.status-badge')?.textContent || 'N/A';
            const actions = card.querySelector('.card-actions')?.innerHTML || '';
            
            rowsHTML += `
                <tr>
                    <td class="name-cell">${name}</td>
                    <td class="path-cell" title="${path}">${truncateText(path, 50)}</td>
                    <td class="number-cell">${documents}</td>
                    <td class="number-cell">${pages}</td>
                    <td class="number-cell film-16mm-cell">${rolls16mm}</td>
                    <td class="number-cell film-35mm-cell">${rolls35mm}</td>
                    <td class="number-cell oversized-cell">${oversized}</td>
                    <td class="utilization-cell">${utilization}</td>
                    <td class="status-cell">${status}</td>
                    <td class="actions-cell">${actions}</td>
                </tr>
            `;
        });
    } else if (sectionType === 'registered') {
        headerHTML = `
            <thead>
                <tr>
                    <th>Archive ID</th>
                    <th>Location</th>
                    <th>Documents</th>
                    <th>Pages</th>
                    <th>Rolls</th>
                    <th>Size</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
        `;
        
        cards.forEach(card => {
            const archiveId = card.querySelector('h3')?.textContent || 'N/A';
            const location = card.querySelector('.location-badge')?.textContent || 'N/A';
            const documents = card.querySelector('.metric:nth-child(1) .metric-value')?.textContent || '0';
            const pages = card.querySelector('.metric:nth-child(2) .metric-value')?.textContent || '0';
            const rolls = card.querySelector('.metric:nth-child(3) .metric-value')?.textContent || '0';
            const size = card.querySelector('.metric:nth-child(4) .metric-value')?.textContent || 'N/A';
            const status = card.querySelector('.status-badge')?.textContent || 'N/A';
            const actions = card.querySelector('.card-actions')?.innerHTML || '';
            const projectId = card.getAttribute('onclick')?.match(/\d+/)?.[0] || '';
            
            const rowClass = projectId ? `onclick="viewProjectDetail(${projectId})" style="cursor: pointer;"` : '';
            
            rowsHTML += `
                <tr ${rowClass}>
                    <td class="name-cell">${archiveId}</td>
                    <td class="location-cell">${location}</td>
                    <td class="number-cell">${documents}</td>
                    <td class="number-cell">${pages}</td>
                    <td class="number-cell">${rolls}</td>
                    <td class="size-cell">${size}</td>
                    <td class="status-cell">${status}</td>
                    <td class="actions-cell" onclick="event.stopPropagation();">${actions}</td>
                </tr>
            `;
        });
    }
    
    return `
        <div class="table-wrapper">
            <table class="data-table">
                ${headerHTML}
                <tbody>
                    ${rowsHTML}
                </tbody>
            </table>
        </div>
    `;
}

/**
 * Apply sorting to current data (for client-side only, backend sorting preferred)
 */
function applySorting() {
    // Update URL and reload to get server-side sorted data
    updateURLWithSortParams();
}

/**
 * Update URL with current sort parameters and reload
 */
function updateURLWithSortParams() {
    const url = new URL(window.location);
    url.searchParams.set('sort', currentSort.field);
    url.searchParams.set('dir', currentSort.direction);
    
    // Reload with new parameters
    window.location.href = url.toString();
}

/**
 * Update sort controls from current state
 */
function updateSortControlsFromState() {
    const sortSelect = document.querySelector('.sort-select');
    const sortDirectionBtn = document.querySelector('.sort-direction');
    
    if (sortSelect) {
        sortSelect.value = currentSort.field;
    }
    
    updateSortDirectionIcon();
}

/**
 * Apply client-side sorting (fallback for when backend sorting isn't desired)
 */
function applyClientSideSorting() {
    const sections = document.querySelectorAll('.section-container');
    
    sections.forEach(section => {
        const cardsGrid = section.querySelector('.cards-grid');
        if (!cardsGrid) return;
        
        const cards = Array.from(cardsGrid.querySelectorAll('.folder-card, .project-card'));
        
        // Sort cards
        const sortedCards = sortCards(cards, currentSort.field, currentSort.direction);
        
        // Re-append sorted cards
        sortedCards.forEach(card => cardsGrid.appendChild(card));
        
        // Update table view if active
        if (currentView === 'table') {
            createTableView(section, cardsGrid);
        }
    });
}

/**
 * Sort cards array
 */
function sortCards(cards, field, direction) {
    return cards.sort((a, b) => {
        let valueA, valueB;
        
        switch (field) {
            case 'name':
                valueA = a.querySelector('h3')?.textContent?.toLowerCase() || '';
                valueB = b.querySelector('h3')?.textContent?.toLowerCase() || '';
                break;
                
            case 'size':
                valueA = getSizeValue(a.querySelector('.metric:last-child .metric-value')?.textContent || '0');
                valueB = getSizeValue(b.querySelector('.metric:last-child .metric-value')?.textContent || '0');
                break;
                
            case 'files':
                valueA = getNumericValue(a.querySelector('.metric:nth-child(1) .metric-value')?.textContent || '0');
                valueB = getNumericValue(b.querySelector('.metric:nth-child(1) .metric-value')?.textContent || '0');
                break;
                
            case 'pdfs':
                valueA = getNumericValue(a.querySelector('.metric:nth-child(2) .metric-value')?.textContent || '0');
                valueB = getNumericValue(b.querySelector('.metric:nth-child(2) .metric-value')?.textContent || '0');
                break;
                
            case 'pages':
                // Try multiple selectors for pages (different sections have different layouts)
                valueA = getNumericValue(a.querySelector('.metric:nth-child(2) .metric-value, .metric .metric-label:contains("Pages") + .metric-value')?.textContent || '0');
                valueB = getNumericValue(b.querySelector('.metric:nth-child(2) .metric-value, .metric .metric-label:contains("Pages") + .metric-value')?.textContent || '0');
                break;
                
            case 'documents':
                valueA = getNumericValue(a.querySelector('.metric .metric-label:contains("Documents") + .metric-value, .metric:nth-child(1) .metric-value')?.textContent || '0');
                valueB = getNumericValue(b.querySelector('.metric .metric-label:contains("Documents") + .metric-value, .metric:nth-child(1) .metric-value')?.textContent || '0');
                break;
                
            case 'rolls':
                // Look for roll-related metrics
                valueA = getNumericValue(a.querySelector('.metric .metric-label:contains("Rolls") + .metric-value, .metric:nth-child(3) .metric-value')?.textContent || '0');
                valueB = getNumericValue(b.querySelector('.metric .metric-label:contains("Rolls") + .metric-value, .metric:nth-child(3) .metric-value')?.textContent || '0');
                break;
                
            case 'utilization':
                valueA = getNumericValue(a.querySelector('.utilization-percentage')?.textContent?.replace('%', '') || '0');
                valueB = getNumericValue(b.querySelector('.utilization-percentage')?.textContent?.replace('%', '') || '0');
                break;
                
            case 'oversized':
                valueA = getNumericValue(a.querySelector('.metric-oversized .metric-value')?.textContent || '0');
                valueB = getNumericValue(b.querySelector('.metric-oversized .metric-value')?.textContent || '0');
                break;
                
            case 'location':
                valueA = a.querySelector('.location-badge')?.textContent?.toLowerCase() || '';
                valueB = b.querySelector('.location-badge')?.textContent?.toLowerCase() || '';
                break;
                
            case 'status':
                valueA = a.querySelector('.status-badge')?.textContent?.toLowerCase() || '';
                valueB = b.querySelector('.status-badge')?.textContent?.toLowerCase() || '';
                break;
                
            case 'date':
                valueA = getDateValue(a);
                valueB = getDateValue(b);
                break;
                
            default:
                return 0;
        }
        
        if (typeof valueA === 'string') {
            return direction === 'asc' ? valueA.localeCompare(valueB) : valueB.localeCompare(valueA);
        } else {
            return direction === 'asc' ? valueA - valueB : valueB - valueA;
        }
    });
}

/**
 * Get numeric value from text (handles formatted numbers like "1.2K")
 */
function getNumericValue(text) {
    if (!text || text === 'N/A') return 0;
    
    // Remove commas and handle K/M suffixes
    const cleanText = text.replace(/,/g, '');
    const match = cleanText.match(/^([\d.]+)([KM]?)$/);
    
    if (!match) return 0;
    
    const num = parseFloat(match[1]);
    const suffix = match[2];
    
    if (suffix === 'K') return num * 1000;
    if (suffix === 'M') return num * 1000000;
    
    return num;
}

/**
 * Get size value in bytes
 */
function getSizeValue(text) {
    if (!text || text === 'N/A') return 0;
    
    const match = text.match(/^([\d.]+)\s*([KMGT]?B?)$/i);
    if (!match) return 0;
    
    const num = parseFloat(match[1]);
    const unit = match[2].toUpperCase();
    
    switch (unit) {
        case 'TB': return num * 1024 * 1024 * 1024 * 1024;
        case 'GB': return num * 1024 * 1024 * 1024;
        case 'MB': return num * 1024 * 1024;
        case 'KB': return num * 1024;
        default: return num;
    }
}

/**
 * Get date value for sorting
 */
function getDateValue(card) {
    // Try to find date in various locations
    const dateElements = card.querySelectorAll('small');
    for (const elem of dateElements) {
        const text = elem.textContent;
        if (text.includes('Created:') || text.includes('Analyzed:') || text.includes('Updated:')) {
            const dateStr = text.split(':')[1]?.trim();
            if (dateStr) {
                return new Date(dateStr).getTime() || 0;
            }
        }
    }
    return 0;
}

/**
 * Update sort direction icon
 */
function updateSortDirectionIcon() {
    const icon = document.querySelector('.sort-direction i');
    if (!icon) return;
    
    // Determine if this is a numeric or alphabetic sort
    const numericFields = ['size', 'files', 'pdfs', 'pages', 'documents', 'rolls', 'utilization', 'oversized'];
    const isNumeric = numericFields.includes(currentSort.field);
    
    if (isNumeric) {
        icon.className = currentSort.direction === 'asc' ? 'fas fa-sort-numeric-down' : 'fas fa-sort-numeric-up';
    } else {
        icon.className = currentSort.direction === 'asc' ? 'fas fa-sort-alpha-down' : 'fas fa-sort-alpha-up';
    }
}

/**
 * Truncate text to specified length
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Debug function to log section information
 */
function logSectionDebugInfo() {
    console.log('=== FRONTEND DEBUG: Section Analysis ===');
    
    // Check unanalyzed section
    const unanalyzedSection = document.querySelector('.unanalyzed-section');
    if (unanalyzedSection) {
        const unanalyzedCards = unanalyzedSection.querySelectorAll('.folder-card');
        console.log(`Unanalyzed section found with ${unanalyzedCards.length} cards:`);
        unanalyzedCards.forEach((card, index) => {
            const name = card.querySelector('h3')?.textContent || 'Unknown';
            const path = card.querySelector('.folder-path span')?.getAttribute('title') || 'Unknown';
            const status = card.querySelector('.status-badge')?.textContent || 'Unknown';
            console.log(`  ${index + 1}. ${name} - Status: ${status} - Path: ${path}`);
        });
    } else {
        console.log('No unanalyzed section found');
    }
    
    // Check analyzed section
    const analyzedSection = document.querySelector('.analyzed-section');
    if (analyzedSection) {
        const analyzedCards = analyzedSection.querySelectorAll('.folder-card');
        console.log(`Analyzed section found with ${analyzedCards.length} cards:`);
        analyzedCards.forEach((card, index) => {
            const name = card.querySelector('h3')?.textContent || 'Unknown';
            const path = card.querySelector('.folder-path span')?.getAttribute('title') || 'Unknown';
            const status = card.querySelector('.status-badge')?.textContent || 'Unknown';
            console.log(`  ${index + 1}. ${name} - Status: ${status} - Path: ${path}`);
        });
    } else {
        console.log('No analyzed section found');
    }
    
    // Check registered section
    const registeredSection = document.querySelector('.registered-section');
    if (registeredSection) {
        const registeredCards = registeredSection.querySelectorAll('.project-card');
        console.log(`Registered section found with ${registeredCards.length} cards:`);
        registeredCards.forEach((card, index) => {
            const name = card.querySelector('h3')?.textContent || 'Unknown';
            const status = card.querySelector('.status-badge')?.textContent || 'Unknown';
            console.log(`  ${index + 1}. ${name} - Status: ${status}`);
        });
    } else {
        console.log('No registered section found');
    }
    
    console.log('=== END FRONTEND DEBUG ===');
}

/**
 * Setup event listeners for the analyze page
 */
function setupEventListeners() {
    console.log('Setting up analyze page event listeners...');
    
    // Search form auto-submit
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.form.submit();
            }, 500); // Debounce search for 500ms
        });
    }
    
    // Project card hover effects
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Action button ripple effects
    const actionBtns = document.querySelectorAll('.action-btn, .btn');
    actionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Escape key to close modals
        if (e.key === 'Escape') {
            hideLoadingModal();
        }
        
        // Enter key to search
        if (e.key === 'Enter' && e.target.classList.contains('search-input')) {
            e.target.form.submit();
        }
    });
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchForm = document.getElementById('search-form');
    if (!searchForm) return;
    
    // Add search suggestions (if needed in the future)
    const searchInput = searchForm.querySelector('.search-input');
    if (searchInput) {
        searchInput.setAttribute('autocomplete', 'off');
        
        // Focus search input with Ctrl+F or Cmd+F
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        });
    }
}

/**
 * Initialize interactive elements
 */
function initializeInteractiveElements() {
    // Add smooth animations to stat cards
    const statCards = document.querySelectorAll('.stat-card, .stat-item');
    statCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Initialize lazy loading for project cards (if there are many)
    initializeLazyLoading();
    
    // Initialize progressive enhancement
    progressiveEnhancement();
}

/**
 * Initialize section toggles for detail view
 */
function initializeSectionToggles() {
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const sectionId = this.onclick ? this.onclick.toString().match(/'([^']+)'/)[1] : null;
            if (sectionId) {
                toggleSection(sectionId);
            }
        });
    });
}

/**
 * Initialize raw data tabs
 */
function initializeRawDataTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const dataType = this.onclick ? this.onclick.toString().match(/'([^']+)'/)[1] : null;
            if (dataType) {
                showRawData(dataType);
            }
        });
    });
}

/**
 * View project detail
 */
function viewProjectDetail(projectId) {
    showLoadingModal();
    
    // Add a small delay to show the loading animation
    setTimeout(() => {
        window.location.href = `/analyze/${projectId}/`;
    }, 300);
}

/**
 * Export project data
 */
function exportProjectData(projectId) {
    console.log('Exporting project data for project:', projectId);
    
    showLoadingModal();
    
    // Create a download link
    const downloadUrl = `/api/analyze/${projectId}/export/`;
    
    fetch(downloadUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Export failed');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `project_${projectId}_analysis_data.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            hideLoadingModal();
            showNotification('Project data exported successfully', 'success');
        })
        .catch(error => {
            console.error('Export error:', error);
            hideLoadingModal();
            showNotification('Failed to export project data', 'error');
        });
}

/**
 * Refresh project data
 */
function refreshProjectData(projectId) {
    console.log('Refreshing project data for project:', projectId);
    
    showLoadingModal();
    
    fetch(`/api/analyze/${projectId}/refresh/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingModal();
        if (data.status === 'success') {
            showNotification('Project data refreshed successfully', 'success');
            // Reload the page to show updated data
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Failed to refresh project data', 'error');
        }
    })
    .catch(error => {
        console.error('Refresh error:', error);
        hideLoadingModal();
        showNotification('Failed to refresh project data', 'error');
    });
}

/**
 * Refresh all data
 */
function refreshAllData() {
    console.log('Refreshing all project data...');
    
    showLoadingModal();
    
    // Clear browser cache and reload
    if ('caches' in window) {
        caches.keys().then(names => {
            names.forEach(name => {
                caches.delete(name);
            });
        });
    }
    
    setTimeout(() => {
        window.location.reload(true);
    }, 1000);
}

/**
 * Toggle section visibility
 */
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const toggleBtn = document.querySelector(`[onclick*="${sectionId}"]`);
    
    if (!section || !toggleBtn) return;
    
    const isCollapsed = section.classList.contains('collapsed');
    const icon = toggleBtn.querySelector('i');
    
    if (isCollapsed) {
        section.classList.remove('collapsed');
        if (icon) {
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-chevron-down');
        }
    } else {
        section.classList.add('collapsed');
        if (icon) {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-right');
        }
    }
}

/**
 * Show raw data tab
 */
function showRawData(dataType) {
    // Hide all raw data content
    const contents = document.querySelectorAll('.raw-data-content');
    contents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected content
    const targetContent = document.getElementById(`raw-${dataType}`);
    if (targetContent) {
        targetContent.classList.add('active');
    }
    
    // Activate corresponding tab button
    const targetBtn = document.querySelector(`[onclick*="${dataType}"]`);
    if (targetBtn) {
        targetBtn.classList.add('active');
    }
}

/**
 * Show loading modal
 */
function showLoadingModal() {
    const modal = document.getElementById('loading-modal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Hide loading modal
 */
function hideLoadingModal() {
    const modal = document.getElementById('loading-modal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1001;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

/**
 * Get notification icon based on type
 */
function getNotificationIcon(type) {
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return icons[type] || icons['info'];
}

/**
 * Get notification color based on type
 */
function getNotificationColor(type) {
    const colors = {
        'success': '#4caf50',
        'error': '#f44336',
        'warning': '#ff9800',
        'info': '#2196f3'
    };
    return colors[type] || colors['info'];
}

/**
 * Get CSRF token for POST requests
 */
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) {
        return token.value;
    }
    
    // Try to get from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    return '';
}

/**
 * Initialize lazy loading for better performance
 */
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    }
}

/**
 * Progressive enhancement
 */
function progressiveEnhancement() {
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add support for reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.documentElement.style.scrollBehavior = 'auto';
        
        // Disable animations for users who prefer reduced motion
        const style = document.createElement('style');
        style.textContent = `
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Add focus management
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });
}

/**
 * Utility function for formatting numbers
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Utility function for formatting file sizes
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Analyze folder without registering it
 */
function analyzeFolder(folderPath) {
    console.log('Analyzing folder:', folderPath);
    
    showLoadingModal();
    
    fetch('/api/analyze/folder/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            folder_path: folderPath,
            force_reanalyze: false
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingModal();
        if (data.status === 'success') {
            showNotification('Folder analyzed successfully', 'success');
            // Reload the page to show the analyzed folder in the analyzed section
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.message || 'Failed to analyze folder', 'error');
        }
    })
    .catch(error => {
        console.error('Analyze error:', error);
        hideLoadingModal();
        showNotification('Failed to analyze folder', 'error');
    });
}

/**
 * Register an analyzed folder as a project
 */
function registerAnalyzedFolder(analyzedFolderId, projectData) {
    console.log('Registering analyzed folder:', analyzedFolderId, 'with data:', projectData);
    
    showLoadingModal();
    
    fetch('/api/analyze/register-folder/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            analyzed_folder_id: analyzedFolderId,
            project_data: projectData
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingModal();
        if (data.status === 'success') {
            showNotification('Folder registered as project successfully', 'success');
            // Reload the page to show the project in the registered section
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.message || 'Failed to register folder', 'error');
        }
    })
    .catch(error => {
        console.error('Register error:', error);
        hideLoadingModal();
        showNotification('Failed to register folder', 'error');
    });
}

/**
 * Get basic folder information
 */
function getFolderInfo(folderPath) {
    return fetch(`/api/analyze/folder-info/?folder_path=${encodeURIComponent(folderPath)}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                return data.data;
            } else {
                throw new Error(data.message || 'Failed to get folder info');
            }
        });
}

/**
 * Switch between sections
 */
function switchSection(sectionName) {
    const url = new URL(window.location);
    url.searchParams.set('section', sectionName);
    if (url.searchParams.get('page')) {
        url.searchParams.delete('page'); // Reset to first page when switching sections
    }
    // Maintain current sort parameters
    if (currentSort.field !== 'name') {
        url.searchParams.set('sort', currentSort.field);
    }
    if (currentSort.direction !== 'asc') {
        url.searchParams.set('dir', currentSort.direction);
    }
    window.location.href = url.toString();
}

/**
 * Navigate to project registration with pre-selected folder
 */
function showRegistrationModal(analyzedFolderId, folderName) {
    console.log('Navigating to project registration for folder:', folderName, 'ID:', analyzedFolderId);
    
    // Get the folder path from the card by finding the button that was clicked
    // and traversing up to find the folder-path element in the same card
    let folderPath = '';
    
    // Try to find the clicked button's parent card
    const clickedButton = event && event.target ? event.target.closest('button') : null;
    if (clickedButton) {
        const parentCard = clickedButton.closest('.folder-card');
        if (parentCard) {
            const pathElement = parentCard.querySelector('.folder-path span[title]');
            if (pathElement) {
                folderPath = pathElement.getAttribute('title');
                console.log('Found folder path from clicked button context:', folderPath);
            }
        }
    }
    
    // Fallback: search through all cards to find the one with matching register button
    if (!folderPath) {
        console.log('Fallback: searching through all cards...');
        const folderCards = document.querySelectorAll('.folder-card.analyzed');
        
        for (const card of folderCards) {
            // Look for a register button with the matching analyzed folder ID
            const registerBtn = card.querySelector(`button[onclick*="showRegistrationModal(${analyzedFolderId}"]`);
            if (registerBtn) {
                const pathElement = card.querySelector('.folder-path span[title]');
                if (pathElement) {
                    folderPath = pathElement.getAttribute('title');
                    console.log('Found folder path in card via fallback:', folderPath);
                    break;
                }
            }
        }
    }
    
    // Last resort: try to find by folder name
    if (!folderPath && folderName) {
        console.log('Last resort: searching by folder name...');
        const folderCards = document.querySelectorAll('.folder-card.analyzed');
        
        for (const card of folderCards) {
            const nameElement = card.querySelector('h3');
            if (nameElement && nameElement.textContent.trim() === folderName) {
                const pathElement = card.querySelector('.folder-path span[title]');
                if (pathElement) {
                    folderPath = pathElement.getAttribute('title');
                    console.log('Found folder path by matching folder name:', folderPath);
                    break;
                }
            }
        }
    }
    
    // Debug logging
    if (!folderPath) {
        console.warn('Could not find folder path in any way');
        console.log('Available analyzed cards:', document.querySelectorAll('.folder-card.analyzed').length);
        console.log('Looking for analyzedFolderId:', analyzedFolderId);
        console.log('Looking for folderName:', folderName);
        
        // Log all available folder paths for debugging
        const allCards = document.querySelectorAll('.folder-card.analyzed');
        console.log('All analyzed folder paths:');
        allCards.forEach((card, index) => {
            const pathElement = card.querySelector('.folder-path span[title]');
            const nameElement = card.querySelector('h3');
            console.log(`  Card ${index}:`, {
                name: nameElement ? nameElement.textContent.trim() : 'no name',
                path: pathElement ? pathElement.getAttribute('title') : 'no path'
            });
        });
    }
    
    // Create URL with parameters
    const baseUrl = '/register/project/';
    const url = new URL(baseUrl, window.location.origin);
    
    // Add parameters
    url.searchParams.set('mode', 'manual');
    
    if (folderPath) {
        url.searchParams.set('source_folder', folderPath);
        console.log('Adding source_folder parameter:', folderPath);
    } else {
        console.warn('No source_folder parameter will be added - path not found');
    }
    
    // Add analyzed folder ID for backend lookup if needed
    url.searchParams.set('analyzed_folder_id', analyzedFolderId);
    
    // Add folder name for display purposes
    if (folderName) {
        url.searchParams.set('folder_name', folderName);
    }
    
    console.log('Final URL:', url.toString());
    
    // Open the registration page in a new window
    window.open(url.toString(), '_blank');
}

/**
 * Submit registration form (deprecated - now handled by navigation)
 */
function submitRegistration(analyzedFolderId) {
    console.warn('submitRegistration called but registration now handled via navigation');
    showNotification('Registration method has changed - please use the Register button', 'info');
}

/**
 * Show analyze confirmation modal
 */
function showAnalyzeModal(folderPath, folderName) {
    const modal = document.createElement('div');
    modal.className = 'analyze-modal';
    modal.innerHTML = `
        <div class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Analyze Folder</h3>
                    <button class="modal-close" onclick="this.parentElement.parentElement.parentElement.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to analyze the folder:</p>
                    <p><strong>${folderName}</strong></p>
                    <p><small>${folderPath}</small></p>
                    <p>This will scan the folder and estimate document counts, page counts, and roll requirements.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.parentElement.parentElement.parentElement.parentElement.remove()">
                        Cancel
                    </button>
                    <button type="button" class="btn btn-primary" onclick="confirmAnalyze('${folderPath}')">
                        Analyze Folder
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add styles
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
}

/**
 * Confirm analyze action
 */
function confirmAnalyze(folderPath) {
    // Close modal
    document.querySelector('.analyze-modal').remove();
    document.body.style.overflow = '';
    
    // Start analysis
    analyzeFolder(folderPath);
}

/**
 * Debug utility functions
 */
window.analyzeDebug = {
    showLoadingModal,
    hideLoadingModal,
    showNotification,
    toggleSection,
    showRawData,
    refreshProjectData,
    exportProjectData,
    formatNumber,
    formatFileSize,
    analyzeFolder,
    registerAnalyzedFolder,
    getFolderInfo,
    switchSection,
    showRegistrationModal,
    showAnalyzeModal,
    switchView,
    applySorting,
    applyClientSideSorting,
    currentSort,
    currentView
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease forwards;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 5px;
        margin-left: auto;
    }
    
    .keyboard-navigation *:focus {
        outline: 2px solid #1a73e8;
        outline-offset: 2px;
    }
`;
document.head.appendChild(style); 