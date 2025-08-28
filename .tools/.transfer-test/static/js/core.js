/**
 * core.js - Core shared functionality for all Micro Tools applications
 * Contains utilities for: 
 * - Dark mode
 * - Notifications
 * - Internationalization 
 * - Common UI components
 */

// DOM elements for core features
const darkModeToggle = document.getElementById('dark-mode-toggle');
const darkModeIcon = document.getElementById('dark-mode-icon');
const logo = document.getElementById('logo');
const langToggle = document.getElementById('lang-toggle');
const notification = document.getElementById('notification');

// Initialize core features when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize i18n first
    if (window.i18n) {
        window.i18n.init();
    }
    
    // Initialize dark mode
    initDarkMode();

    // Set up language toggle
    if (langToggle) {
        langToggle.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.i18n) {
                window.i18n.cycleLanguage();
            }
        });
    }
});

/**
 * Dark Mode Functions
 */

// Initialize dark mode from user preference
function initDarkMode() {
    // Check if user has a saved preference
    const darkModePreference = localStorage.getItem('darkMode');
    
    // If there's a preference and it's 'enabled', turn on dark mode
    if (darkModePreference === 'enabled') {
        enableDarkMode();
    } else {
        disableDarkMode();
    }

    // Set up dark mode toggle click handler
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            // Check if the body already has the dark-mode class
            if (document.body.classList.contains('dark-mode')) {
                disableDarkMode();
            } else {
                enableDarkMode();
            }
        });
    }
}

// Function to enable dark mode
function enableDarkMode() {
    // Add the dark-mode class to the body
    document.body.classList.add('dark-mode');
    
    // Update the icon to sun
    if (darkModeIcon) {
        darkModeIcon.classList.remove('fa-moon');
        darkModeIcon.classList.add('fa-sun');
    }
    
    // Switch to dark mode logo if available
    if (logo) {
        logo.src = logo.src.replace('logo-light.png', 'logo-dark.png');
    }
    
    // Save the preference to localStorage
    localStorage.setItem('darkMode', 'enabled');
}

// Function to disable dark mode
function disableDarkMode() {
    // Remove the dark-mode class from the body
    document.body.classList.remove('dark-mode');
    
    // Update the icon to moon
    if (darkModeIcon) {
        darkModeIcon.classList.remove('fa-sun');
        darkModeIcon.classList.add('fa-moon');
    }
    
    // Switch to light mode logo if available
    if (logo) {
        logo.src = logo.src.replace('logo-dark.png', 'logo-light.png');
    }
    
    // Save the preference to localStorage
    localStorage.setItem('darkMode', 'disabled');
}

/**
 * Notification System
 */

function showNotification(message, type) {
    // Create notification content with icon
    if (typeof message === 'string' && notification) {
        // Create the notification content structure
        notification.innerHTML = '';
        
        // Add appropriate icon based on notification type
        let iconClass = 'fa-info-circle';
        if (type === 'success') {
            iconClass = 'fa-check-circle';
        } else if (type === 'error') {
            iconClass = 'fa-exclamation-circle';
        } else if (type === 'warning') {
            iconClass = 'fa-exclamation-triangle';
        }
        
        // Create icon element
        const iconElement = document.createElement('i');
        iconElement.className = `fas ${iconClass} notification-icon`;
        
        // Create content container
        const contentDiv = document.createElement('div');
        contentDiv.className = 'notification-content';
        const paragraph = document.createElement('p');
        paragraph.textContent = message;
        contentDiv.appendChild(paragraph);
        
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'notification-close';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.onclick = () => notification.classList.remove('show');
        
        // Append all elements to notification
        notification.appendChild(iconElement);
        notification.appendChild(contentDiv);
        notification.appendChild(closeBtn);
        
        // Set notification class
        notification.className = `notification ${type || 'info'}`;
    }
    
    // Show notification
    if (notification) {
        notification.classList.add('show');
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, 5000);
    }
}

// Utility to open a folder in the file explorer
function openFolder(folderPath) {
    if (!folderPath) return;
    
    const formData = new FormData();
    formData.append('path', folderPath);
    
    fetch('/open_folder', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (!result.success) {
            console.error('Failed to open folder:', result.message);
            const errorMsg = window.i18n ? window.i18n.__('failed_to_open_folder') : 'Failed to open folder';
            showNotification(`${errorMsg}: ${result.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error opening folder:', error);
    });
}

// Export the core functionality
window.MicroCore = {
    showNotification,
    enableDarkMode,
    disableDarkMode,
    openFolder
}; 