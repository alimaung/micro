/**
 * Analyze Page JavaScript
 * Handles all functionality for the analyze page and project detail view
 */

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
    formatFileSize
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