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
    
    // Clean up old cache entries on page load
    clearOldCache();
    
    // Add cache status indicator
    addCacheStatusIndicator();
    
    // Check if we're in skeleton mode and need to load real data
    if (window.SKELETON_MODE) {
        console.log('Skeleton mode detected - loading real data...');
        loadRealData();
    } else {
        // Initialize the analyze page normally
        initializeAnalyzePage();
        
        // Update cache status for non-skeleton mode
        updateCacheStatus();
    }
});

// Cache configuration
const CACHE_CONFIG = {
    key: 'analyze_dashboard_data',
    version: '1.0',
    ttl: 5 * 60 * 1000, // 5 minutes in milliseconds
    maxSize: 2 * 1024 * 1024 // 2MB max cache size
};

/**
 * Generate cache key based on current filters
 */
function generateCacheKey() {
    const params = new URLSearchParams({
        section: window.SECTION_FILTER || 'all',
        search: window.SEARCH_QUERY || '',
        sort: window.SORT_FIELD || 'folder_name',
        direction: window.SORT_DIRECTION || 'asc'
    });
    return `${CACHE_CONFIG.key}_${params.toString()}`;
}

/**
 * Check if cached data is valid and not expired
 */
function isCacheValid(cacheData) {
    if (!cacheData || !cacheData.timestamp || !cacheData.version) {
        return false;
    }
    
    // Check version compatibility
    if (cacheData.version !== CACHE_CONFIG.version) {
        return false;
    }
    
    // Check if data has expired
    const now = Date.now();
    const age = now - cacheData.timestamp;
    return age < CACHE_CONFIG.ttl;
}

/**
 * Get cached data from localStorage
 */
function getCachedData() {
    try {
        const cacheKey = generateCacheKey();
        const cached = localStorage.getItem(cacheKey);
        
        if (!cached) {
            return null;
        }
        
        const cacheData = JSON.parse(cached);
        
        if (!isCacheValid(cacheData)) {
            // Remove expired cache
            localStorage.removeItem(cacheKey);
            return null;
        }
        
        console.log('📦 Using cached dashboard data');
        return cacheData.data;
    } catch (error) {
        console.warn('Failed to read cache:', error);
        return null;
    }
}

/**
 * Save data to localStorage cache
 */
function setCachedData(data) {
    try {
        const cacheKey = generateCacheKey();
        const cacheData = {
            data: data,
            timestamp: Date.now(),
            version: CACHE_CONFIG.version
        };
        
        const serialized = JSON.stringify(cacheData);
        
        // Check cache size
        if (serialized.length > CACHE_CONFIG.maxSize) {
            console.warn('Data too large to cache:', serialized.length, 'bytes');
            return false;
        }
        
        localStorage.setItem(cacheKey, serialized);
        console.log('💾 Dashboard data cached successfully');
        return true;
    } catch (error) {
        console.warn('Failed to cache data:', error);
        // Handle quota exceeded error
        if (error.name === 'QuotaExceededError') {
            clearOldCache();
            // Try again after cleanup
            try {
                localStorage.setItem(cacheKey, JSON.stringify(cacheData));
                return true;
            } catch (retryError) {
                console.warn('Failed to cache after cleanup:', retryError);
            }
        }
        return false;
    }
}

/**
 * Clear old or invalid cache entries
 */
function clearOldCache() {
    try {
        const keysToRemove = [];
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(CACHE_CONFIG.key)) {
                try {
                    const cached = localStorage.getItem(key);
                    const cacheData = JSON.parse(cached);
                    
                    if (!isCacheValid(cacheData)) {
                        keysToRemove.push(key);
                    }
                } catch (error) {
                    // Remove invalid cache entries
                    keysToRemove.push(key);
                }
            }
        }
        
        keysToRemove.forEach(key => {
            localStorage.removeItem(key);
            console.log('🗑️ Removed expired cache:', key);
        });
        
        console.log(`🧹 Cleaned up ${keysToRemove.length} cache entries`);
    } catch (error) {
        console.warn('Failed to clear old cache:', error);
    }
}

/**
 * Invalidate cache for current filters
 */
function invalidateCache() {
    try {
        const cacheKey = generateCacheKey();
        localStorage.removeItem(cacheKey);
        console.log('🗑️ Cache invalidated');
    } catch (error) {
        console.warn('Failed to invalidate cache:', error);
    }
}

/**
 * Clear all analyze dashboard cache
 */
function clearAllCache() {
    try {
        const keysToRemove = [];
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(CACHE_CONFIG.key)) {
                keysToRemove.push(key);
            }
        }
        
        keysToRemove.forEach(key => localStorage.removeItem(key));
        console.log(`🗑️ Cleared all cache (${keysToRemove.length} entries)`);
    } catch (error) {
        console.warn('Failed to clear all cache:', error);
    }
}

/**
 * Load real data from cache or API
 */
async function loadRealData() {
    try {
        // First try to get cached data
        const cachedData = getCachedData();
        if (cachedData) {
            showSkeletonLoadingIndicator();
            setTimeout(() => {
                replaceSkeletonWithRealData(cachedData);
                hideSkeletonLoadingIndicator();
            }, 100); // Small delay to show loading briefly
            return;
        }
        
        // If no cache, show loading and fetch from API
        showSkeletonLoadingIndicator();
        
        const params = new URLSearchParams();
        if (window.SECTION_FILTER && window.SECTION_FILTER !== 'all') {
            params.append('section', window.SECTION_FILTER);
        }
        if (window.SEARCH_QUERY) {
            params.append('search', window.SEARCH_QUERY);
        }
        if (window.SORT_FIELD) {
            params.append('sort', window.SORT_FIELD);
        }
        if (window.SORT_DIRECTION) {
            params.append('direction', window.SORT_DIRECTION);
        }
        
        const url = `/api/analyze/dashboard-data/${params.toString() ? '?' + params.toString() : ''}`;
        console.log('🌐 Fetching fresh data from API:', url);
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Cache the fresh data
        setCachedData(data);
        
        // Update the UI
        replaceSkeletonWithRealData(data);
        hideSkeletonLoadingIndicator();
        
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        hideSkeletonLoadingIndicator();
        
        // Show error message
        const realContent = document.getElementById('real-content');
        if (realContent) {
            realContent.innerHTML = `
                <div class="error-message">
                    <div class="error-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h3>Failed to Load Data</h3>
                    <p>Unable to load dashboard data. Please try refreshing the page.</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        <i class="fas fa-sync-alt"></i>
                        Refresh Page
                    </button>
                </div>
            `;
            realContent.style.display = 'block';
            
            // Hide skeleton
            const skeletonContent = document.getElementById('skeleton-content');
            if (skeletonContent) {
                skeletonContent.style.display = 'none';
            }
        }
    }
}

/**
 * Show skeleton loading indicator
 */
function showSkeletonLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'skeleton-loading-indicator';
    indicator.className = 'skeleton-loading-indicator';
    indicator.innerHTML = `
        <div class="spinner"></div>
        <span>Loading dashboard data...</span>
    `;
    document.body.appendChild(indicator);
}

/**
 * Hide skeleton loading indicator
 */
function hideSkeletonLoadingIndicator() {
    const indicator = document.getElementById('skeleton-loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Replace skeleton content with real data
 */
function replaceSkeletonWithRealData(data) {
    console.log('Replacing skeleton with real data...', data);
    
    // Update stats in header
    updateHeaderStats(data.summary_stats);
    
    // Update section tab counts
    updateSectionTabCounts(data.summary_stats);
    
    // Replace skeleton content sections
    const skeletonContent = document.getElementById('skeleton-content');
    const realContent = document.getElementById('real-content');
    
    if (skeletonContent && realContent) {
        // Generate real content HTML
        generateRealContentHTML(data, realContent);
        
        // Fade out skeleton and fade in real content
        skeletonContent.classList.add('skeleton-fade-out');
        
        setTimeout(() => {
            skeletonContent.style.display = 'none';
            realContent.style.display = 'block';
            realContent.classList.add('real-content-fade-in');
            
            // Initialize controls after content loads
            console.log('Initializing controls after skeleton replacement...');
            initializeAnalyzePage();
            
            // Update cache status after content loads
            updateCacheStatus();
        }, 300);
    }
    
    // Update window state
    window.SKELETON_MODE = false;
}

/**
 * Update header statistics
 */
function updateHeaderStats(stats) {
    const statCards = document.querySelectorAll('.header-stats .stat-card');
    
    if (statCards.length >= 4) {
        // Update unanalyzed stats
        updateStatCard(statCards[0], stats.total_unanalyzed, 
            `${stats.unanalyzed_total_pdfs} PDFs • ${stats.unanalyzed_total_excel} Excel • ${stats.unanalyzed_total_size_formatted}`);
        
        // Update analyzed stats
        updateStatCard(statCards[1], stats.total_analyzed, 
            `${stats.analyzed_total_16mm} × 16mm • ${stats.analyzed_total_35mm} × 35mm • ${stats.analyzed_avg_utilization}% util • ${stats.analyzed_temp_rolls_created + stats.analyzed_temp_rolls_used} temp`);
        
        // Update registered stats
        updateStatCard(statCards[2], stats.total_registered, 
            `${stats.registered_total_rolls} rolls • ${stats.registered_total_size_formatted || 'Size N/A'}`);
        
        // Update total documents stats
        const totalDocs = stats.analyzed_total_documents + stats.registered_total_documents;
        const totalPages = stats.analyzed_total_pages + stats.registered_total_pages;
        updateStatCard(statCards[3], totalDocs, 
            `${totalPages} pages • ${stats.analyzed_total_oversized} oversized`);
    }
}

/**
 * Update individual stat card
 */
function updateStatCard(card, number, details) {
    const numberEl = card.querySelector('.stat-number');
    const detailsEl = card.querySelector('.stat-details small');
    
    if (numberEl) {
        numberEl.classList.remove('skeleton-text');
        numberEl.textContent = number;
    }
    
    if (detailsEl) {
        detailsEl.classList.remove('skeleton-text');
        detailsEl.textContent = details;
    }
    
    card.classList.remove('skeleton-loading');
}

/**
 * Update section tab counts
 */
function updateSectionTabCounts(stats) {
    const tabs = document.querySelectorAll('.section-tab');
    
    tabs.forEach(tab => {
        const text = tab.textContent.trim();
        if (text.includes('Unanalyzed')) {
            tab.innerHTML = `<i class="fas fa-folder-open"></i> Unanalyzed (${stats.total_unanalyzed})`;
        } else if (text.includes('Analyzed')) {
            tab.innerHTML = `<i class="fas fa-chart-line"></i> Analyzed (${stats.total_analyzed})`;
        } else if (text.includes('Registered')) {
            tab.innerHTML = `<i class="fas fa-check-circle"></i> Registered (${stats.total_registered})`;
        }
    });
}

/**
 * Generate real content HTML from data
 */
function generateRealContentHTML(data, realContent) {
    let htmlContent = '';
    
    // Generate unanalyzed section
    if (data.sections_data.unanalyzed && data.sections_data.unanalyzed.length > 0) {
        htmlContent += generateUnanalyzedSectionHTML(data.sections_data.unanalyzed);
    }
    
    // Generate analyzed section
    if (data.sections_data.analyzed && data.sections_data.analyzed.length > 0) {
        htmlContent += generateAnalyzedSectionHTML(data.sections_data.analyzed);
    }
    
    // Generate registered section
    if (data.sections_data.registered && data.sections_data.registered.length > 0) {
        htmlContent += generateRegisteredSectionHTML(data.sections_data.registered);
    }
    
    // Handle empty state
    if (!data.sections_data.unanalyzed.length && !data.sections_data.analyzed.length && !data.sections_data.registered.length) {
        htmlContent = generateEmptyStateHTML();
    }
    
    // Add pagination if needed
    if (data.page_obj && data.page_obj.num_pages > 1) {
        htmlContent += generatePaginationHTML(data.page_obj);
    }
    
    realContent.innerHTML = htmlContent;
}

/**
 * Generate unanalyzed section HTML
 */
function generateUnanalyzedSectionHTML(folders) {
    return `
        <div class="section-container unanalyzed-section">
            <div class="section-header">
                <h2><i class="fas fa-folder-open"></i> Unanalyzed Folders</h2>
                <p class="section-description">Folders that haven't been analyzed yet - unknown content</p>
            </div>
            <div class="cards-grid">
                ${folders.map(folder => generateUnanalyzedCardHTML(folder)).join('')}
            </div>
        </div>
    `;
}

/**
 * Generate analyzed section HTML
 */
function generateAnalyzedSectionHTML(folders) {
    return `
        <div class="section-container analyzed-section">
            <div class="section-header">
                <h2><i class="fas fa-chart-line"></i> Analyzed Folders</h2>
                <p class="section-description">Folders that have been analyzed but not yet registered</p>
            </div>
            <div class="cards-grid">
                ${folders.map(folder => generateAnalyzedCardHTML(folder)).join('')}
            </div>
        </div>
    `;
}

/**
 * Generate registered section HTML
 */
function generateRegisteredSectionHTML(projects) {
    return `
        <div class="section-container registered-section">
            <div class="section-header">
                <h2><i class="fas fa-check-circle"></i> Registered Projects</h2>
                <p class="section-description">Projects that have been registered and are in the workflow</p>
            </div>
            <div class="cards-grid">
                ${projects.map(project => generateRegisteredCardHTML(project)).join('')}
            </div>
        </div>
    `;
}

/**
 * Generate individual card HTML for unanalyzed folders
 */
function generateUnanalyzedCardHTML(folder) {
    return `
        <div class="folder-card unanalyzed">
            <div class="card-header">
                <div class="card-title">
                    <h3>${escapeHtml(folder.folder_name)}</h3>
                    <div class="card-meta">
                        <span class="status-badge status-unanalyzed">Unanalyzed</span>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <div class="folder-path">
                    <i class="fas fa-folder-open"></i>
                    <span title="${escapeHtml(folder.folder_path)}">${escapeHtml(truncateText(folder.folder_path, 50))}</span>
                </div>
                <div class="key-metrics">
                    <div class="metric">
                        <i class="fas fa-file metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${folder.file_count || 0}</div>
                            <div class="metric-label">Total Files</div>
                        </div>
                    </div>
                    <div class="metric">
                        <i class="fas fa-file-pdf metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${folder.pdf_count || 0}</div>
                            <div class="metric-label">PDFs</div>
                        </div>
                    </div>
                    <div class="metric">
                        <i class="fas fa-file-excel metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${folder.excel_count || 0}</div>
                            <div class="metric-label">Excel</div>
                        </div>
                    </div>
                    <div class="metric">
                        <i class="fas fa-file-alt metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${folder.other_count || 0}</div>
                            <div class="metric-label">Others</div>
                        </div>
                    </div>
                    <div class="metric">
                        <i class="fas fa-hdd metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${folder.total_size_formatted || 'N/A'}</div>
                            <div class="metric-label">Size</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <div class="card-actions">
                    <button class="btn btn-primary" onclick="showAnalyzeModal('${escapeJs(folder.folder_path)}', '${escapeJs(folder.folder_name)}')">
                        <i class="fas fa-chart-line"></i>
                        Analyze
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Generate individual card HTML for analyzed folders
 */
function generateAnalyzedCardHTML(folder) {
    // Format analyzed date and user info
    const analyzedDate = folder.analyzed_at ? formatDate(folder.analyzed_at) : 'Unknown';
    const analyzedBy = folder.analyzed_by ? folder.analyzed_by.username : 'Unknown';
    
    // Generate workflow badge
    let workflowBadge = '';
    if (folder.recommended_workflow && folder.recommended_workflow !== 'unknown') {
        workflowBadge = `<span class="workflow-badge">${escapeHtml(folder.recommended_workflow.charAt(0).toUpperCase() + folder.recommended_workflow.slice(1))}</span>`;
    }
    
    // Generate film type badges
    let filmTypeBadges = '';
    if (folder.estimated_rolls_16mm > 0 && folder.estimated_rolls_35mm > 0) {
        filmTypeBadges = `
            <span class="film-type-badge film-16mm">16mm</span>
            <span class="film-type-badge film-35mm">35mm</span>
        `;
    } else if (folder.estimated_rolls_35mm > 0) {
        filmTypeBadges = `<span class="film-type-badge film-35mm">35mm</span>`;
    } else if (folder.estimated_rolls_16mm > 0) {
        filmTypeBadges = `<span class="film-type-badge film-16mm">16mm</span>`;
    }
    
    // Generate film roll metrics
    let filmRollMetrics = '';
    if (folder.estimated_rolls_16mm > 0 && folder.estimated_rolls_35mm > 0) {
        // Show both 16mm and 35mm
        filmRollMetrics = `
            <div class="metric metric-film">
                <i class="fas fa-film metric-icon film-16mm-icon"></i>
                <div class="metric-content">
                    <div class="metric-value">${folder.estimated_rolls_16mm}</div>
                    <div class="metric-label">16mm Rolls</div>
                </div>
            </div>
            <div class="metric metric-film">
                <i class="fas fa-film metric-icon film-35mm-icon"></i>
                <div class="metric-content">
                    <div class="metric-value">${folder.estimated_rolls_35mm}</div>
                    <div class="metric-label">35mm Rolls</div>
                </div>
            </div>
        `;
    } else if (folder.estimated_rolls_35mm > 0) {
        // Show only 35mm
        filmRollMetrics = `
            <div class="metric metric-film">
                <i class="fas fa-film metric-icon film-35mm-icon"></i>
                <div class="metric-content">
                    <div class="metric-value">${folder.estimated_rolls_35mm}</div>
                    <div class="metric-label">35mm Rolls</div>
                </div>
            </div>
        `;
    } else if (folder.estimated_rolls_16mm > 0) {
        // Show only 16mm
        filmRollMetrics = `
            <div class="metric metric-film">
                <i class="fas fa-film metric-icon film-16mm-icon"></i>
                <div class="metric-content">
                    <div class="metric-value">${folder.estimated_rolls_16mm}</div>
                    <div class="metric-label">16mm Rolls</div>
                </div>
            </div>
        `;
    } else {
        // Fallback to total rolls
        filmRollMetrics = `
            <div class="metric">
                <i class="fas fa-film metric-icon"></i>
                <div class="metric-content">
                    <div class="metric-value">${folder.estimated_rolls || 0}</div>
                    <div class="metric-label">Est. Rolls</div>
                </div>
            </div>
        `;
    }
    
    // Generate temp roll metrics
    let tempRollMetrics = '';
    if (folder.estimated_temp_rolls_created > 0 || folder.estimated_temp_rolls_used > 0) {
        let tempRollValue = '';
        if (folder.estimated_temp_rolls_created > 0 && folder.estimated_temp_rolls_used > 0) {
            tempRollValue = `${folder.estimated_temp_rolls_created}+${folder.estimated_temp_rolls_used}`;
        } else if (folder.estimated_temp_rolls_created > 0) {
            tempRollValue = `+${folder.estimated_temp_rolls_created}`;
        } else {
            tempRollValue = `${folder.estimated_temp_rolls_used}`;
        }
        
        tempRollMetrics = `
            <div class="metric metric-temp-rolls">
                <i class="fas fa-recycle metric-icon"></i>
                <div class="metric-content">
                    <div class="metric-value">${tempRollValue}</div>
                    <div class="metric-label">Temp Rolls</div>
                </div>
            </div>
        `;
    }
    
    // Generate oversized alert
    let oversizedAlert = '';
    if (folder.has_oversized) {
        oversizedAlert = `
            <div class="oversized-alert">
                <i class="fas fa-exclamation-triangle"></i>
                Contains oversized documents (${folder.oversized_count})
            </div>
        `;
    }
    
    // Generate PDF folder info
    let pdfFolderInfo = '';
    if (folder.pdf_folder_found) {
        pdfFolderInfo = `
            <div class="pdf-folder-info">
                <i class="fas fa-check-circle"></i>
                PDF folder found
            </div>
        `;
    }
    
    // Generate utilization bar
    let utilizationBar = '';
    if (folder.overall_utilization > 0) {
        let utilizationClass = '';
        let utilizationText = '';
        
        if (folder.overall_utilization >= 85) {
            utilizationClass = 'utilization-excellent';
            utilizationText = 'Excellent efficiency';
        } else if (folder.overall_utilization >= 70) {
            utilizationClass = 'utilization-good';
            utilizationText = 'Good efficiency';
        } else if (folder.overall_utilization >= 50) {
            utilizationClass = 'utilization-fair';
            utilizationText = 'Fair efficiency';
        } else {
            utilizationClass = 'utilization-poor';
            utilizationText = 'Low efficiency';
        }
        
        utilizationBar = `
            <div class="utilization-container">
                <div class="utilization-header">
                    <span class="utilization-label">Roll Utilization</span>
                    <span class="utilization-percentage">${folder.overall_utilization}%</span>
                </div>
                <div class="utilization-bar">
                    <div class="utilization-fill" style="width: ${folder.overall_utilization}%"></div>
                </div>
                <div class="utilization-description">
                    <small class="${utilizationClass}">${utilizationText}</small>
                </div>
            </div>
        `;
    }
    
    return `
        <div class="folder-card analyzed">
            <div class="card-header">
                <div class="card-title">
                    <h3>${escapeHtml(folder.folder_name)}</h3>
                    <div class="card-meta">
                        <span class="status-badge status-analyzed">Analyzed</span>
                        ${workflowBadge}
                        ${filmTypeBadges}
                    </div>
                </div>
            </div>
            <div class="card-body">
                <div class="folder-path">
                    <i class="fas fa-folder-open"></i>
                    <span title="${escapeHtml(folder.folder_path)}">${escapeHtml(truncateText(folder.folder_path, 50))}</span>
                </div>
                
                <div class="key-metrics">
                    <div class="metric">
                        <i class="fas fa-file-alt metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${folder.total_documents || 0}</div>
                            <div class="metric-label">Documents</div>
                        </div>
                    </div>
                    <div class="metric">
                        <i class="fas fa-copy metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${folder.total_pages || 0}</div>
                            <div class="metric-label">Pages</div>
                        </div>
                    </div>
                    
                    ${filmRollMetrics}
                    
                    <!-- Always show oversized count -->
                    <div class="metric metric-oversized">
                        <i class="fas fa-exclamation-triangle metric-icon ${folder.has_oversized ? 'oversized-icon' : ''}"></i>
                        <div class="metric-content">
                            <div class="metric-value ${folder.has_oversized ? 'oversized-value' : ''}">${folder.oversized_count || 0}</div>
                            <div class="metric-label">Oversized</div>
                        </div>
                    </div>
                    
                    ${tempRollMetrics}
                    
                    <div class="metric">
                        <i class="fas fa-hdd metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${folder.total_size_formatted || 'N/A'}</div>
                            <div class="metric-label">Size</div>
                        </div>
                    </div>
                </div>

                ${oversizedAlert}
                ${pdfFolderInfo}
                ${utilizationBar}
            </div>
            <div class="card-footer">
                <div class="analysis-info">
                    <small>Analyzed: ${analyzedDate}</small>
                    <small>By: ${analyzedBy}</small>
                </div>
                <div class="card-actions">
                    <button class="btn btn-secondary" onclick="showAnalyzeModal('${escapeJs(folder.folder_path)}', '${escapeJs(folder.folder_name)}')">
                        <i class="fas fa-sync-alt"></i>
                        Re-analyze
                    </button>
                    <button class="btn btn-primary" onclick="showRegistrationModal(${folder.id}, '${escapeJs(folder.folder_name)}')">
                        <i class="fas fa-plus-circle"></i>
                        Register
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Generate individual card HTML for registered projects
 */
function generateRegisteredCardHTML(item) {
    const project = item.project;
    const data = item.data;
    
    // Generate doc type badge
    let docTypeBadge = '';
    if (project.doc_type) {
        docTypeBadge = `<span class="doc-type-badge">${escapeHtml(project.doc_type)}</span>`;
    }
    
    // Generate status badge based on project state
    let statusBadge = '';
    if (project.processing_complete) {
        statusBadge = '<span class="status-badge status-completed">Completed</span>';
    } else if (project.film_allocation_complete) {
        statusBadge = '<span class="status-badge status-allocated">Allocated</span>';
    } else if (data.total_documents) {
        statusBadge = '<span class="status-badge status-analyzed">Analyzed</span>';
    } else {
        statusBadge = '<span class="status-badge status-registered">Registered</span>';
    }
    
    // Generate temp roll metrics for registered projects
    let tempRollMetrics = '';
    if (data.temp_rolls_created > 0 || data.temp_rolls_used > 0) {
        let tempRollValue = '';
        if (data.temp_rolls_created > 0 && data.temp_rolls_used > 0) {
            tempRollValue = `${data.temp_rolls_created}+${data.temp_rolls_used}`;
        } else if (data.temp_rolls_created > 0) {
            tempRollValue = `+${data.temp_rolls_created}`;
        } else {
            tempRollValue = `${data.temp_rolls_used}`;
        }
        
        tempRollMetrics = `
            <div class="metric metric-temp-rolls">
                <i class="fas fa-recycle metric-icon"></i>
                <div class="metric-content">
                    <div class="metric-value">${tempRollValue}</div>
                    <div class="metric-label">Temp Rolls</div>
                </div>
            </div>
        `;
    }
    
    // Generate oversized alert for registered projects
    let oversizedAlert = '';
    if (data.has_oversized) {
        oversizedAlert = `
            <div class="oversized-alert">
                <i class="fas fa-exclamation-triangle"></i>
                Contains oversized documents (${data.oversized_count})
            </div>
        `;
    }
    
    // Format size value
    const sizeValue = (data.total_size_formatted && data.total_size_formatted !== "0 B") 
        ? data.total_size_formatted 
        : 'N/A';
    
    return `
        <div class="project-card registered" onclick="viewProjectDetail(${project.id})">
            <div class="card-header">
                <div class="card-title">
                    <h3>${escapeHtml(project.archive_id)}</h3>
                    <div class="card-meta">
                        <span class="location-badge location-${project.location.toLowerCase()}">${escapeHtml(project.location)}</span>
                        ${docTypeBadge}
                    </div>
                </div>
                <div class="card-status">
                    ${statusBadge}
                </div>
            </div>
            <div class="card-body">
                <div class="key-metrics">
                    <div class="metric">
                        <i class="fas fa-file-alt metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${Math.floor(data.total_documents || 0)}</div>
                            <div class="metric-label">Documents</div>
                        </div>
                    </div>
                    <div class="metric">
                        <i class="fas fa-copy metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${Math.floor(data.total_pages || 0)}</div>
                            <div class="metric-label">Pages</div>
                        </div>
                    </div>
                    <div class="metric">
                        <i class="fas fa-film metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${data.total_rolls || 0}</div>
                            <div class="metric-label">Rolls</div>
                        </div>
                    </div>
                    <div class="metric">
                        <i class="fas fa-hdd metric-icon"></i>
                        <div class="metric-content">
                            <div class="metric-value">${sizeValue}</div>
                            <div class="metric-label">Size</div>
                        </div>
                    </div>
                    
                    ${tempRollMetrics}
                </div>

                ${oversizedAlert}
            </div>
            <div class="card-footer">
                <div class="project-dates">
                    <small>Created: ${formatDate(project.created_at)}</small>
                    <small>Updated: ${formatDate(project.updated_at)}</small>
                </div>
                <div class="card-actions">
                    <button class="action-btn" onclick="event.stopPropagation(); exportProjectData(${project.id})">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="action-btn" onclick="event.stopPropagation(); refreshProjectData(${project.id})">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Generate empty state HTML
 */
function generateEmptyStateHTML() {
    return `
        <div class="empty-state">
            <div class="empty-state-content">
                <i class="fas fa-search empty-state-icon"></i>
                <h3>No Items Found</h3>
                <p>No folders or projects found matching your criteria.</p>
                <div class="empty-state-actions">
                    <button class="btn btn-primary" onclick="switchSection('all')">
                        <i class="fas fa-eye"></i>
                        View All
                    </button>
                    <a href="/register/" class="btn btn-secondary">
                        <i class="fas fa-plus"></i>
                        Register New Project
                    </a>
                </div>
            </div>
        </div>
    `;
}

/**
 * Generate pagination HTML
 */
function generatePaginationHTML(pageObj) {
    let paginationHTML = '<div class="pagination-container"><div class="pagination">';
    
    if (pageObj.has_previous) {
        paginationHTML += `<a href="?page=${pageObj.previous_page_number}" class="page-link"><i class="fas fa-chevron-left"></i></a>`;
    }
    
    // Simplified pagination - just show current page
    paginationHTML += `<span class="page-link current">${pageObj.number}</span>`;
    
    if (pageObj.has_next) {
        paginationHTML += `<a href="?page=${pageObj.next_page_number}" class="page-link"><i class="fas fa-chevron-right"></i></a>`;
    }
    
    paginationHTML += '</div>';
    paginationHTML += `<div class="pagination-info">Showing ${pageObj.start_index} - ${pageObj.end_index} of ${pageObj.count} items</div>`;
    paginationHTML += '</div>';
    
    return paginationHTML;
}

/**
 * Utility functions for HTML generation
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeJs(text) {
    return text.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    let date;
    if (typeof dateString === 'string') {
        // Handle ISO date strings from API
        date = new Date(dateString);
    } else {
        // Handle Date objects
        date = dateString;
    }
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
        return 'Invalid Date';
    }
    
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

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
    console.log('About to initialize sorting and view controls...');
    initializeSortingAndViewControls();
    
    // Ensure controls are properly initialized
    setTimeout(() => {
        const controlsContainer = document.querySelector('.controls-container');
        if (controlsContainer && !controlsContainer.querySelector('.sort-controls')) {
            console.log('Controls missing, re-initializing...');
            initializeSortingAndViewControls();
        }
    }, 100);
}

/**
 * Initialize sorting and view controls
 */
function initializeSortingAndViewControls() {
    console.log('Initializing sorting and view controls...');
    
    // Check if controls container exists
    const controlsContainer = document.querySelector('.controls-container');
    if (!controlsContainer) {
        console.warn('Controls container not found');
        return;
    }
    
    // Clear any existing controls to prevent duplicates
    const existingControls = controlsContainer.querySelectorAll('.view-toggle, .sort-controls, .section-filters');
    existingControls.forEach(control => control.remove());
    
    // Initialize controls
    initializeViewToggle();
    initializeSectionFilters();
    initializeSortingControls();
    
    // Set initial values and state
    updateSortControlsFromState();
    updateViewDisplay();
}

/**
 * Initialize section-specific filters
 */
function initializeSectionFilters() {
    console.log('Initializing section filters...');
    
    // Create new filters for current section
    createSectionFilters();
}

/**
 * Initialize view toggle (card/table)
 */
function initializeViewToggle() {
    console.log('Initializing view toggle...');
    
    // Create view toggle
    createViewToggle();
    
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
    console.log('Initializing sorting controls...');
    
    // Create new sort controls
    createSortControls();
    
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
    if (!controlsContainer) {
        console.warn('Controls container not found for view toggle');
        return;
    }
    
    const viewToggle = document.createElement('div');
    viewToggle.className = 'view-toggle';
    viewToggle.innerHTML = `
        <label style="font-size: 14px; color: var(--color-text); margin-right: 10px; font-weight: 500;">View:</label>
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
    console.log('View toggle created');
}

/**
 * Create section-specific filters
 */
function createSectionFilters() {
    const controlsContainer = document.querySelector('.controls-container');
    
    if (!controlsContainer) {
        console.warn('Controls container not found, cannot create filters');
        return;
    }
    
    const currentSection = window.SECTION_FILTER || 'all';
    const filters = getSectionFilterOptions(currentSection);
    
    console.log('Creating filters for section:', currentSection, 'filters:', filters.length);
    
    if (filters.length === 0) {
        console.log('No filters available for section:', currentSection);
        return; // No filters for this section
    }
    
    const filtersContainer = document.createElement('div');
    filtersContainer.className = 'section-filters';
    filtersContainer.innerHTML = `
        <label style="font-size: 14px; color: var(--color-text); margin-right: 15px; font-weight: 500;">Filters:</label>
        <div class="filters-group">
            ${filters.map(filter => `
                <div class="filter-item">
                    <label for="filter-${filter.id}">${filter.label}:</label>
                    <select id="filter-${filter.id}" class="filter-select" data-filter="${filter.id}">
                        <option value="">All ${filter.label}</option>
                        ${filter.options.map(option => `
                            <option value="${option.value}">${option.label}</option>
                        `).join('')}
                    </select>
                </div>
            `).join('')}
        </div>
    `;
    
    controlsContainer.appendChild(filtersContainer);
    console.log('Filters appended to controls container');
    
    // Add event listeners
    filtersContainer.querySelectorAll('.filter-select').forEach(select => {
        select.addEventListener('change', () => {
            applyClientSideFilters();
        });
    });
    
    console.log('Filter event listeners added');
}

/**
 * Get filter options for a specific section
 */
function getSectionFilterOptions(section) {
    const commonFilters = [
        {
            id: 'location',
            label: 'Location',
            options: [
                { value: 'OU', label: 'OU' },
                { value: 'DW', label: 'DW' },
                { value: 'main-archive', label: 'Main Archive' },
                { value: 'satellite-office', label: 'Satellite Office' },
                { value: 'remote-storage', label: 'Remote Storage' }
            ]
        }
    ];
    
    switch (section) {
        case 'unanalyzed':
            return [
                ...commonFilters,
                {
                    id: 'file-type',
                    label: 'Primary File Type',
                    options: [
                        { value: 'pdf', label: 'PDF Heavy' },
                        { value: 'excel', label: 'Excel Heavy' },
                        { value: 'mixed', label: 'Mixed Files' },
                        { value: 'other', label: 'Other Types' }
                    ]
                },
                {
                    id: 'size-range',
                    label: 'Folder Size',
                    options: [
                        { value: 'small', label: 'Small (< 100MB)' },
                        { value: 'medium', label: 'Medium (100MB - 1GB)' },
                        { value: 'large', label: 'Large (1GB - 5GB)' },
                        { value: 'xlarge', label: 'Very Large (> 5GB)' }
                    ]
                }
            ];
            
        case 'analyzed':
            return [
                ...commonFilters,
                {
                    id: 'document-type',
                    label: 'Document Type',
                    options: [
                        { value: 'archive', label: 'Archive' },
                        { value: 'document', label: 'Document' },
                        { value: 'book', label: 'Book' },
                        { value: 'newspaper', label: 'Newspaper' },
                        { value: 'correspondence', label: 'Correspondence' },
                        { value: 'records', label: 'Records' }
                    ]
                },
                {
                    id: 'roll-count',
                    label: 'Roll Count',
                    options: [
                        { value: 'low', label: 'Low (1-5 rolls)' },
                        { value: 'medium', label: 'Medium (6-20 rolls)' },
                        { value: 'high', label: 'High (21+ rolls)' }
                    ]
                },
                {
                    id: 'has-oversized',
                    label: 'Has Oversized',
                    options: [
                        { value: 'true', label: 'Yes' },
                        { value: 'false', label: 'No' }
                    ]
                }
            ];
            
        case 'registered':
            return [
                ...commonFilters,
                {
                    id: 'project-status',
                    label: 'Status',
                    options: [
                        { value: 'draft', label: 'Draft' },
                        { value: 'processing', label: 'Processing' },
                        { value: 'allocated', label: 'Film Allocated' },
                        { value: 'complete', label: 'Complete' }
                    ]
                },
                {
                    id: 'completion-rate',
                    label: 'Completion',
                    options: [
                        { value: 'not-started', label: 'Not Started (0%)' },
                        { value: 'in-progress', label: 'In Progress (1-99%)' },
                        { value: 'complete', label: 'Complete (100%)' }
                    ]
                }
            ];
            
        default:
            return commonFilters;
    }
}

/**
 * Create sort controls
 */
function createSortControls() {
    const controlsContainer = document.querySelector('.controls-container');
    
    if (!controlsContainer) {
        console.warn('Controls container not found, cannot create sort controls');
        return;
    }
    
    const currentSection = window.SECTION_FILTER || 'all';
    const sortOptions = getSectionSortOptions(currentSection);
    
    console.log('Creating sort controls for section:', currentSection, 'options:', sortOptions.length);
    
    const sortControls = document.createElement('div');
    sortControls.className = 'sort-controls';
    sortControls.innerHTML = `
        <label style="font-size: 14px; color: var(--color-text); margin-right: 10px; font-weight: 500;">Sort by:</label>
        <div class="sort-group">
            <select class="sort-select">
                ${sortOptions.map(option => `
                    <option value="${option.value}">${option.label}</option>
                `).join('')}
            </select>
            <button class="sort-direction" title="Sort Direction">
                <i class="fas fa-sort-alpha-down"></i>
            </button>
        </div>
    `;
    
    controlsContainer.appendChild(sortControls);
    console.log('Sort controls appended to controls container');
}

/**
 * Get sort options for a specific section
 */
function getSectionSortOptions(section) {
    const commonOptions = [
        { value: 'name', label: 'Name' },
        { value: 'location', label: 'Location' }
    ];
    
    switch (section) {
        case 'unanalyzed':
            return [
                ...commonOptions,
                { value: 'size', label: 'Size' },
                { value: 'files', label: 'Files' },
                { value: 'pdfs', label: 'PDFs' },
                { value: 'documents', label: 'Documents' }
            ];
            
        case 'analyzed':
            return [
                ...commonOptions,
                { value: 'pages', label: 'Pages' },
                { value: 'rolls', label: 'Rolls' },
                { value: 'utilization', label: 'Utilization' },
                { value: 'oversized', label: 'Oversized' },
                { value: 'temp_created', label: 'Temp Rolls Created' },
                { value: 'temp_used', label: 'Temp Rolls Used' },
                { value: 'temp_strategy', label: 'Temp Roll Strategy' }
            ];
            
        case 'registered':
            return [
                ...commonOptions,
                { value: 'status', label: 'Status' },
                { value: 'date', label: 'Date' },
                { value: 'completion', label: 'Completion' }
            ];
            
        default:
            return [
                ...commonOptions,
                { value: 'size', label: 'Size' },
                { value: 'files', label: 'Files' },
                { value: 'status', label: 'Status' }
            ];
    }
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
                    <th>Temp Rolls</th>
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
            
            // Extract temp roll information
            const tempRollElement = card.querySelector('.metric-temp-rolls .metric-value');
            const tempRollDisplay = tempRollElement ? tempRollElement.textContent.trim() : '0';
            
            rowsHTML += `
                <tr>
                    <td class="name-cell">${name}</td>
                    <td class="path-cell" title="${path}">${truncateText(path, 50)}</td>
                    <td class="number-cell">${documents}</td>
                    <td class="number-cell">${pages}</td>
                    <td class="number-cell film-16mm-cell">${rolls16mm}</td>
                    <td class="number-cell film-35mm-cell">${rolls35mm}</td>
                    <td class="number-cell oversized-cell">${oversized}</td>
                    <td class="number-cell temp-rolls-cell">${tempRollDisplay}</td>
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
                    <th>Temp Rolls</th>
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
            
            // Extract temp roll information for registered projects
            const tempRollElement = card.querySelector('.metric-temp-rolls .metric-value');
            const tempRollDisplay = tempRollElement ? tempRollElement.textContent.trim() : '0';
            
            const rowClass = projectId ? `onclick="viewProjectDetail(${projectId})" style="cursor: pointer;"` : '';
            
            rowsHTML += `
                <tr ${rowClass}>
                    <td class="name-cell">${archiveId}</td>
                    <td class="location-cell">${location}</td>
                    <td class="number-cell">${documents}</td>
                    <td class="number-cell">${pages}</td>
                    <td class="number-cell">${rolls}</td>
                    <td class="number-cell temp-rolls-cell">${tempRollDisplay}</td>
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
                
            case 'temp_created':
                // For temp rolls, we need to parse the combined display or look for individual values
                valueA = getTempRollValue(a, 'created');
                valueB = getTempRollValue(b, 'created');
                break;
                
            case 'temp_used':
                valueA = getTempRollValue(a, 'used');
                valueB = getTempRollValue(b, 'used');
                break;
                
            case 'temp_strategy':
                // Strategy would be stored as data attribute or derived from display
                valueA = getTempRollStrategy(a);
                valueB = getTempRollStrategy(b);
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
    const numericFields = ['size', 'files', 'pdfs', 'pages', 'documents', 'rolls', 'utilization', 'oversized', 'temp_created', 'temp_used'];
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
            
            // Clear cache to ensure fresh data
            clearAllCache();
            
            // Reload the page with cache busting to show the analyzed folder in the analyzed section
            setTimeout(() => {
                const url = new URL(window.location);
                url.searchParams.set('_t', Date.now());
                window.location.href = url.toString();
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
            
            // Clear cache to ensure fresh data
            clearAllCache();
            
            // Reload the page with cache busting to show the project in the registered section
            setTimeout(() => {
                const url = new URL(window.location);
                url.searchParams.set('_t', Date.now());
                window.location.href = url.toString();
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
    console.log('Switching to section:', sectionName);
    
    // Clear cache when switching sections to ensure fresh data
    clearAllCache();
    
    // Update global section filter
    window.SECTION_FILTER = sectionName;
    
    if (window.SKELETON_MODE) {
        // In skeleton mode, reload data immediately
        loadRealData().then(() => {
            // Re-initialize controls for the new section
            console.log('Re-initializing controls after section switch...');
            initializeSortingAndViewControls();
        });
    } else {
        // In regular mode, redirect with cache busting
        const url = new URL(window.location);
        url.searchParams.set('section', sectionName);
        url.searchParams.set('_t', Date.now()); // Cache busting parameter
        
        if (url.searchParams.get('page')) {
            url.searchParams.delete('page'); // Reset to first page when switching sections
        }
        
        // Maintain current sort parameters
        if (currentSort && currentSort.field !== 'name') {
            url.searchParams.set('sort', currentSort.field);
        }
        if (currentSort && currentSort.direction !== 'asc') {
            url.searchParams.set('dir', currentSort.direction);
        }
        
        window.location.href = url.toString();
    }
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
 * Get temp roll value from card (created or used)
 */
function getTempRollValue(card, type) {
    const tempRollMetric = card.querySelector('.metric-temp-rolls .metric-value');
    if (!tempRollMetric) return 0;
    
    const text = tempRollMetric.textContent.trim();
    
    // Parse different formats:
    // "+3" = 3 created, 0 used
    // "2" = 2 used, 0 created  
    // "2+3" = 2 created, 3 used
    
    if (text.includes('+')) {
        const parts = text.split('+');
        if (type === 'created') {
            return getNumericValue(parts[0] || '0');
        } else if (type === 'used') {
            return getNumericValue(parts[1] || '0');
        }
    } else if (text.startsWith('+')) {
        // Only created rolls (e.g., "+3")
        if (type === 'created') {
            return getNumericValue(text.substring(1));
        } else {
            return 0;
        }
    } else {
        // Only used rolls (e.g., "2")
        if (type === 'used') {
            return getNumericValue(text);
        } else {
            return 0;
        }
    }
    
    return 0;
}

/**
 * Get temp roll strategy from card
 */
function getTempRollStrategy(card) {
    // Try to determine strategy from temp roll display
    const tempRollMetric = card.querySelector('.metric-temp-rolls .metric-value');
    if (!tempRollMetric) return 'none';
    
    const text = tempRollMetric.textContent.trim();
    
    if (text.includes('+')) {
        return 'both';  // Has both created and used
    } else if (text.startsWith('+')) {
        return 'create';  // Only creates temp rolls
    } else if (text && text !== '0') {
        return 'use';  // Only uses temp rolls
    } else {
        return 'none';  // No temp rolls
    }
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

/**
 * Perform search with cache invalidation
 */
function performSearch() {
    const searchInput = document.getElementById('search-input');
    const newQuery = searchInput ? searchInput.value.trim() : '';
    
    // Check if search query has changed
    if (window.SEARCH_QUERY !== newQuery) {
        window.SEARCH_QUERY = newQuery;
        invalidateCache(); // Invalidate cache when search changes
        
        if (window.SKELETON_MODE) {
            loadRealData(); // Reload with new search
        } else {
            // Redirect with new search parameter
            updateUrlAndReload();
        }
    }
}

/**
 * Apply section filter with cache invalidation
 */
function applyFilter(section) {
    // Check if filter has changed
    if (window.SECTION_FILTER !== section) {
        window.SECTION_FILTER = section;
        invalidateCache(); // Invalidate cache when filter changes
        
        if (window.SKELETON_MODE) {
            loadRealData(); // Reload with new filter
        } else {
            // Redirect with new filter parameter
            updateUrlAndReload();
        }
    }
    
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

/**
 * Apply client-side filters to visible cards
 */
function applyClientSideFilters() {
    const filterSelects = document.querySelectorAll('.filter-select');
    const activeFilters = {};
    
    // Collect active filters
    filterSelects.forEach(select => {
        const filterId = select.dataset.filter;
        const value = select.value;
        if (value) {
            activeFilters[filterId] = value;
        }
    });
    
    console.log('Applying client-side filters:', activeFilters);
    
    // If no filters are active, show all cards
    if (Object.keys(activeFilters).length === 0) {
        document.querySelectorAll('.folder-card, .project-card').forEach(card => {
            card.style.display = '';
        });
        // Clear any empty state messages
        document.querySelectorAll('.empty-state-message').forEach(msg => {
            msg.style.display = 'none';
        });
        return;
    }
    
    // Get current section and apply filters to cards
    const currentSection = window.SECTION_FILTER || 'all';
    const sectionContainers = document.querySelectorAll('.section-container');
    
    sectionContainers.forEach(container => {
        if (currentSection !== 'all') {
            // Only filter the current section
            if (!container.classList.contains(`${currentSection}-section`)) {
                return;
            }
        }
        
        const cards = container.querySelectorAll('.folder-card, .project-card');
        let visibleCount = 0;
        
        cards.forEach(card => {
            const shouldShow = cardMatchesFilters(card, activeFilters, currentSection);
            card.style.display = shouldShow ? '' : 'none';
            if (shouldShow) visibleCount++;
        });
        
        // Update empty state if no cards are visible
        updateEmptyState(container, visibleCount === 0);
    });
}

/**
 * Check if a card matches the applied filters
 */
function cardMatchesFilters(card, filters, section) {
    for (const [filterId, filterValue] of Object.entries(filters)) {
        if (!cardMatchesFilter(card, filterId, filterValue, section)) {
            return false;
        }
    }
    return true;
}

/**
 * Check if a card matches a specific filter
 */
function cardMatchesFilter(card, filterId, filterValue, section) {
    switch (filterId) {
        case 'location':
            // Check for location badge in registered projects
            const locationBadge = card.querySelector('.location-badge');
            if (locationBadge) {
                const location = locationBadge.textContent.trim().toLowerCase();
                return location === filterValue.toLowerCase();
            }
            
            // Fallback to folder path for unanalyzed/analyzed
            const locationElement = card.querySelector('.folder-path span[title]');
            if (locationElement) {
                const path = locationElement.getAttribute('title') || '';
                return path.toLowerCase().includes(filterValue.toLowerCase());
            }
            return false;
            
        case 'file-type':
            // For unanalyzed section - check file type composition
            // Find metrics by their labels since data attributes may not be set
            const metrics = card.querySelectorAll('.metric');
            let pdfCount = 0, excelCount = 0, totalFiles = 0;
            
            metrics.forEach(metric => {
                const label = metric.querySelector('.metric-label')?.textContent.toLowerCase();
                const value = parseInt(metric.querySelector('.metric-value')?.textContent || '0');
                
                if (label === 'pdfs') pdfCount = value;
                else if (label === 'excel') excelCount = value;
                else if (label === 'total files') totalFiles = value;
            });
            
            if (totalFiles === 0) return filterValue === 'other';
            
            const pdfRatio = pdfCount / totalFiles;
            const excelRatio = excelCount / totalFiles;
            
            switch (filterValue) {
                case 'pdf': return pdfRatio > 0.6;
                case 'excel': return excelRatio > 0.6;
                case 'mixed': return pdfRatio > 0.1 && excelRatio > 0.1;
                case 'other': return pdfRatio < 0.1 && excelRatio < 0.1;
                default: return true;
            }
            
        case 'size-range':
            // Find size metric by label
            let sizeText = '';
            const sizeMetrics = card.querySelectorAll('.metric');
            sizeMetrics.forEach(metric => {
                const label = metric.querySelector('.metric-label')?.textContent.toLowerCase();
                if (label === 'size') {
                    sizeText = metric.querySelector('.metric-value')?.textContent || '';
                }
            });
            
            if (sizeText) {
                const sizeBytes = parseSizeToBytes(sizeText);
                
                switch (filterValue) {
                    case 'small': return sizeBytes < 100 * 1024 * 1024; // < 100MB
                    case 'medium': return sizeBytes >= 100 * 1024 * 1024 && sizeBytes < 1024 * 1024 * 1024; // 100MB - 1GB
                    case 'large': return sizeBytes >= 1024 * 1024 * 1024 && sizeBytes < 5 * 1024 * 1024 * 1024; // 1GB - 5GB
                    case 'xlarge': return sizeBytes >= 5 * 1024 * 1024 * 1024; // > 5GB
                    default: return true;
                }
            }
            return false;
            
        case 'document-type':
            const docTypeElement = card.querySelector('.document-type, [data-doc-type]');
            if (docTypeElement) {
                const docType = docTypeElement.textContent || docTypeElement.dataset.docType || '';
                return docType.toLowerCase() === filterValue.toLowerCase();
            }
            return false;
            
        case 'roll-count':
            const rollsElement = card.querySelector('[data-metric="rolls"] .metric-value');
            if (rollsElement) {
                const rollCount = parseInt(rollsElement.textContent || '0');
                switch (filterValue) {
                    case 'low': return rollCount >= 1 && rollCount <= 5;
                    case 'medium': return rollCount >= 6 && rollCount <= 20;
                    case 'high': return rollCount >= 21;
                    default: return true;
                }
            }
            return false;
            
        case 'has-oversized':
            // Find oversized metric by label or class
            let hasOversized = false;
            const oversizedMetrics = card.querySelectorAll('.metric');
            oversizedMetrics.forEach(metric => {
                const label = metric.querySelector('.metric-label')?.textContent.toLowerCase();
                if (label === 'oversized') {
                    const value = parseInt(metric.querySelector('.metric-value')?.textContent || '0');
                    hasOversized = value > 0;
                }
            });
            
            // Also check for oversized alert
            if (!hasOversized) {
                hasOversized = !!card.querySelector('.oversized-alert');
            }
            
            return filterValue === 'true' ? hasOversized : !hasOversized;
            
        case 'project-status':
            const statusElement = card.querySelector('.status-badge, .project-status');
            if (statusElement) {
                const status = statusElement.textContent.toLowerCase().trim();
                return status.includes(filterValue.toLowerCase());
            }
            return false;
            
        case 'completion-rate':
            const completionElement = card.querySelector('.completion-percentage, [data-completion]');
            if (completionElement) {
                const completion = parseInt(completionElement.textContent || completionElement.dataset.completion || '0');
                switch (filterValue) {
                    case 'not-started': return completion === 0;
                    case 'in-progress': return completion > 0 && completion < 100;
                    case 'complete': return completion === 100;
                    default: return true;
                }
            }
            return false;
            
        default:
            return true;
    }
}

/**
 * Parse size string to bytes for comparison
 */
function parseSizeToBytes(sizeText) {
    if (!sizeText) return 0;
    
    const units = {
        'b': 1,
        'kb': 1024,
        'mb': 1024 * 1024,
        'gb': 1024 * 1024 * 1024,
        'tb': 1024 * 1024 * 1024 * 1024
    };
    
    const match = sizeText.toLowerCase().match(/^([\d.]+)\s*([a-z]+)$/);
    if (match) {
        const value = parseFloat(match[1]);
        const unit = match[2];
        return value * (units[unit] || 1);
    }
    
    return 0;
}

/**
 * Update empty state for a section container
 */
function updateEmptyState(container, isEmpty = null) {
    const cards = container.querySelectorAll('.folder-card, .project-card');
    const visibleCards = isEmpty === null 
        ? Array.from(cards).filter(card => card.style.display !== 'none')
        : (isEmpty ? [] : cards);
    
    let emptyState = container.querySelector('.empty-state-message');
    
    if (visibleCards.length === 0) {
        if (!emptyState) {
            emptyState = document.createElement('div');
            emptyState.className = 'empty-state-message';
            emptyState.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-filter"></i>
                    <h3>No items match your filters</h3>
                    <p>Try adjusting your filter criteria to see more results.</p>
                </div>
            `;
            const cardsGrid = container.querySelector('.cards-grid');
            if (cardsGrid) {
                cardsGrid.appendChild(emptyState);
            }
        }
        emptyState.style.display = 'block';
    } else {
        if (emptyState) {
            emptyState.style.display = 'none';
        }
    }
}

/**
 * Apply sorting with cache invalidation
 */
function applySort(field, direction = null) {
    let hasChanged = false;
    
    // Determine sort direction
    if (direction === null) {
        if (window.SORT_FIELD === field) {
            direction = window.SORT_DIRECTION === 'asc' ? 'desc' : 'asc';
        } else {
            direction = 'asc';
        }
    }
    
    // Check if sort has changed
    if (window.SORT_FIELD !== field || window.SORT_DIRECTION !== direction) {
        window.SORT_FIELD = field;
        window.SORT_DIRECTION = direction;
        hasChanged = true;
    }
    
    if (hasChanged) {
        invalidateCache(); // Invalidate cache when sort changes
        
        if (window.SKELETON_MODE) {
            loadRealData(); // Reload with new sort
        } else {
            // Redirect with new sort parameter
            updateUrlAndReload();
        }
    }
    
    // Update sort indicators
    updateSortIndicators();
}

/**
 * Update sort direction icons and indicators
 */
function updateSortIndicators() {
    const sortDirectionBtn = document.querySelector('.sort-direction');
    if (sortDirectionBtn) {
        updateSortDirectionIcon();
    }
}

/**
 * Update URL and reload page (for non-skeleton mode)
 */
function updateUrlAndReload() {
    const url = new URL(window.location);
    
    // Update URL parameters
    if (window.SECTION_FILTER && window.SECTION_FILTER !== 'all') {
        url.searchParams.set('section', window.SECTION_FILTER);
    } else {
        url.searchParams.delete('section');
    }
    
    if (window.SEARCH_QUERY) {
        url.searchParams.set('search', window.SEARCH_QUERY);
    } else {
        url.searchParams.delete('search');
    }
    
    if (window.SORT_FIELD && window.SORT_FIELD !== 'folder_name') {
        url.searchParams.set('sort', window.SORT_FIELD);
    } else {
        url.searchParams.delete('sort');
    }
    
    if (window.SORT_DIRECTION && window.SORT_DIRECTION !== 'asc') {
        url.searchParams.set('direction', window.SORT_DIRECTION);
    } else {
        url.searchParams.delete('direction');
    }
    
    // Reload page with new parameters
    window.location.href = url.toString();
}

/**
 * Refresh data and clear cache
 */
function refreshDashboardData() {
    console.log('🔄 Refreshing dashboard data...');
    
    // Clear all cache
    clearAllCache();
    
    if (window.SKELETON_MODE) {
        // Reload data in skeleton mode
        loadRealData().then(() => {
            // Re-initialize controls after refresh
            console.log('Re-initializing controls after data refresh...');
            initializeSortingAndViewControls();
        });
    } else {
        // Reload page for non-skeleton mode with cache busting
        const url = new URL(window.location);
        url.searchParams.set('_t', Date.now()); // Cache busting parameter
        window.location.href = url.toString();
    }
}

/**
 * Add cache status indicator to the page
 */
function addCacheStatusIndicator() {
    const header = document.querySelector('.dashboard-header');
    if (!header) return;
    
    const cacheIndicator = document.createElement('div');
    cacheIndicator.id = 'cache-status';
    cacheIndicator.className = 'cache-status';
    cacheIndicator.innerHTML = `
        <div class="cache-info">
            <span class="cache-icon" title="Data cached locally">
                <i class="fas fa-database"></i>
            </span>
            <span class="cache-time" id="cache-time"></span>
        </div>
        <div class="cache-actions">
            <button class="btn-link" onclick="refreshDashboardData()" title="Refresh data">
                <i class="fas fa-sync-alt"></i>
            </button>
            <button class="btn-link" onclick="clearAllCache()" title="Clear cache">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    header.appendChild(cacheIndicator);
    updateCacheStatus();
}

/**
 * Update cache status display
 */
function updateCacheStatus() {
    const cacheTime = document.getElementById('cache-time');
    const cacheStatus = document.getElementById('cache-status');
    
    if (!cacheTime || !cacheStatus) return;
    
    const cachedData = getCachedData();
    if (cachedData) {
        const cacheKey = generateCacheKey();
        const cached = localStorage.getItem(cacheKey);
        
        if (cached) {
            const cacheData = JSON.parse(cached);
            const age = Date.now() - cacheData.timestamp;
            const ageMinutes = Math.floor(age / (1000 * 60));
            
            cacheTime.textContent = ageMinutes === 0 ? 'Just now' : `${ageMinutes}m ago`;
            cacheStatus.style.display = 'flex';
            return;
        }
    }
    
    // No cache or invalid cache
    cacheStatus.style.display = 'none';
}