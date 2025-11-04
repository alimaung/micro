// Main JavaScript functionality for Microfilm Processing System

// DOM ready function
document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle functionality
    const toggleButton = document.getElementById('dark-mode-toggle');
    const body = document.body;
    const logo = document.getElementById('logo');
    const darkModeIcon = document.getElementById('dark-mode-icon');
    const restartServerButton = document.getElementById('restart-server');
    
    // Handle prefers-color-scheme media query
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Get the base static URL for the logo images
    const logoLightPath = logo.getAttribute('src');
    const logoDarkPath = logoLightPath.replace('logo-light.png', 'logo-dark.png');

    // Function to set dark mode state
    function setDarkMode(isDark) {
        // Apply or remove dark mode class
        body.classList.toggle('dark-mode', isDark);
        
        // Update logo source
        logo.src = isDark ? logoDarkPath : logoLightPath;
        
        // Update icon class with transition
        if (isDark) {
            darkModeIcon.classList.add('fa-sun');
            darkModeIcon.classList.remove('fa-moon');
        } else {
            darkModeIcon.classList.add('fa-moon');
            darkModeIcon.classList.remove('fa-sun');
        }
        
        // Store preference
        localStorage.setItem('dark-mode', isDark ? 'enabled' : 'disabled');
    }

    // Initialize dark mode based on user preference or system preference
    function initializeTheme() {
        const savedTheme = localStorage.getItem('dark-mode');
        
        if (savedTheme === 'enabled') {
            setDarkMode(true);
        } else if (savedTheme === 'disabled') {
            setDarkMode(false);
        } else if (prefersDarkMode.matches) {
            // If no saved preference, respect system preference
            setDarkMode(true);
        }
    }

    // Initialize theme on load
    initializeTheme();

    // Function to toggle Django admin dark mode in iframe
    function toggleAdminDarkMode() {
        console.log('toggleAdminDarkMode called');
        const adminIframe = document.querySelector('.admin-iframe');
        console.log('Admin iframe found:', !!adminIframe);
        
        if (adminIframe && adminIframe.contentWindow) {
            console.log('Iframe has contentWindow');
            try {
                const adminDoc = adminIframe.contentDocument || adminIframe.contentWindow.document;
                console.log('Admin document accessible:', !!adminDoc);
                
                const adminToggleBtn = adminDoc.querySelector('button.theme-toggle');
                console.log('Admin toggle button found:', !!adminToggleBtn);
                
                if (adminToggleBtn) {
                    const adminHtml = adminDoc.documentElement;
                    const currentTheme = adminHtml.getAttribute('data-theme');
                    const ourDarkMode = body.classList.contains('dark-mode');
                    const targetTheme = ourDarkMode ? 'dark' : 'light';
                    
                    console.log('Current admin theme:', currentTheme, 'Target theme:', targetTheme);
                    
                    // Click until we reach the target theme (max 3 clicks to avoid infinite loop)
                    let clickCount = 0;
                    const maxClicks = 3;
                    
                    function clickUntilTarget() {
                        const currentTheme = adminHtml.getAttribute('data-theme');
                        if (currentTheme !== targetTheme && clickCount < maxClicks) {
                            console.log(`Click ${clickCount + 1}: ${currentTheme} → targeting ${targetTheme}`);
                            adminToggleBtn.click();
                            clickCount++;
                            
                            setTimeout(() => {
                                clickUntilTarget();
                            }, 100);
                        } else {
                            console.log('Final admin theme:', adminHtml.getAttribute('data-theme'));
                        }
                    }
                    
                    clickUntilTarget();
                } else {
                    // Try alternative selectors
                    const altBtn1 = adminDoc.querySelector('#user-tools button');
                    const altBtn2 = adminDoc.querySelector('.theme-toggle');
                    const altBtn3 = adminDoc.querySelector('[class*="theme"]');
                    console.log('Alternative buttons found:', {
                        userTools: !!altBtn1,
                        themeToggle: !!altBtn2,
                        anyTheme: !!altBtn3
                    });
                }
            } catch (e) {
                // Iframe might not be loaded or cross-origin restrictions
                console.log('Could not access admin iframe:', e);
            }
        } else {
            console.log('No iframe or contentWindow found');
        }
    }

    // Function to sync admin dark mode with our current state
    function syncAdminDarkMode() {
        const adminIframe = document.querySelector('.admin-iframe');
        if (adminIframe && adminIframe.contentWindow) {
            try {
                const adminDoc = adminIframe.contentDocument || adminIframe.contentWindow.document;
                const adminToggleBtn = adminDoc.querySelector('button.theme-toggle');
                const adminHtml = adminDoc.documentElement;
                
                if (adminToggleBtn && adminHtml) {
                    const ourDarkMode = body.classList.contains('dark-mode');
                    const adminTheme = adminHtml.getAttribute('data-theme');
                    
                    console.log('Syncing - Our dark mode:', ourDarkMode, 'Admin theme:', adminTheme);
                    
                    // Django cycles through: dark → auto → light → dark
                    // We want: ourDarkMode=true → adminTheme='dark', ourDarkMode=false → adminTheme='light'
                    let needsClick = false;
                    
                    if (ourDarkMode && adminTheme !== 'dark') {
                        // We want dark, admin is not dark - keep clicking until it's dark
                        needsClick = true;
                    } else if (!ourDarkMode && adminTheme !== 'light') {
                        // We want light, admin is not light - keep clicking until it's light
                        needsClick = true;
                    }
                    
                    if (needsClick) {
                        console.log('Syncing admin theme...');
                        adminToggleBtn.click();
                        
                        // Check again after a delay to see if we need another click
                        setTimeout(() => {
                            const newTheme = adminHtml.getAttribute('data-theme');
                            console.log('After sync click, admin theme is now:', newTheme);
                            
                            // If still not the right theme, click again
                            if ((ourDarkMode && newTheme !== 'dark') || (!ourDarkMode && newTheme !== 'light')) {
                                console.log('Need another click...');
                                adminToggleBtn.click();
                            }
                        }, 150);
                    }
                }
            } catch (e) {
                console.log('Could not sync admin dark mode:', e);
            }
        }
    }

    // Listen for iframe load to sync dark mode
    document.addEventListener('DOMContentLoaded', function() {
        const adminIframe = document.querySelector('.admin-iframe');
        if (adminIframe) {
            adminIframe.addEventListener('load', function() {
                // Wait a bit for admin to fully load, then sync
                setTimeout(syncAdminDarkMode, 500);
            });
        }
    });

    // Add click event for dark mode toggle with animation
    toggleButton.addEventListener('click', () => {
        const isDarkMode = body.classList.contains('dark-mode');
        
        // First animate the icon
        darkModeIcon.style.transform = 'rotate(360deg)';
        
        // After a small delay, toggle the theme
        setTimeout(() => {
            setDarkMode(!isDarkMode);
            darkModeIcon.style.transform = '';
            
            // Also toggle Django admin dark mode if on admin page
            toggleAdminDarkMode();
        }, 200);
    });
    
    // Listen for changes in system color scheme preference
    prefersDarkMode.addEventListener('change', (event) => {
        // Only apply if the user hasn't set a preference
        if (!localStorage.getItem('dark-mode')) {
            setDarkMode(event.matches);
        }
    });
    
    // Function to show notification
    function showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.querySelector('.notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.classList.add('notification');
            document.body.appendChild(notification);
        }
        
        // Set background color based on type
        if (type === 'success') {
            notification.style.backgroundColor = '#4caf50';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#f44336';
        } else if (type === 'warning') {
            notification.style.backgroundColor = '#ff9800';
        } else {
            notification.style.backgroundColor = '#2196f3';
        }
        
        // Set message
        notification.textContent = message;
        
        // Show notification
        notification.style.transform = 'translateY(0)';
        notification.style.opacity = '1';
        
        // Hide notification after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
        }, 3000);
    }
    
    // Add restart server button functionality
    if (restartServerButton) {
        restartServerButton.addEventListener('click', () => {
            // Animate the icon
            const restartIcon = restartServerButton.querySelector('i');
            restartIcon.style.transform = 'rotate(360deg)';
            
            // Confirm before restarting
            if (confirm('Are you sure you want to restart the server? This may cause temporary service disruption.')) {
                // Show loading state
                restartIcon.classList.add('loading-state');
                
                // Send request to restart server
                fetch('/api/restart-server/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Remove loading state
                    restartIcon.classList.remove('loading-state');
                    
                    // Reset icon animation
                    setTimeout(() => {
                        restartIcon.style.transform = '';
                    }, 200);
                    
                    // Show notification based on result
                    if (data.success) {
                        showNotification('Server restarting...', 'success');
                        // Optional: redirect to a maintenance page or home after a delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 5000);
                    } else {
                        showNotification('Failed to restart server: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    // Remove loading state
                    restartIcon.classList.remove('loading-state');
                    
                    // Reset icon animation
                    setTimeout(() => {
                        restartIcon.style.transform = '';
                    }, 200);
                    
                    // Show error notification
                    showNotification('Error: ' + error.message, 'error');
                });
            } else {
                // Reset icon animation if cancelled
                setTimeout(() => {
                    restartIcon.style.transform = '';
                }, 200);
            }
        });
    }
    
    // Helper function to get CSRF token
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
    
    // Add smooth page transitions
    document.querySelectorAll('.navbar-links a').forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't interfere with ctrl/cmd clicks or right clicks
            if (e.ctrlKey || e.metaKey || e.button !== 0) return;
            
            const href = this.getAttribute('href');
            if (href && href !== '#' && !href.startsWith('javascript:')) {
                e.preventDefault();
                
                // Fade out current content
                document.querySelector('.content').style.opacity = '0';
                
                // Navigate after fade animation
                setTimeout(() => {
                    window.location.href = href;
                }, 300);
            }
        });
    });
}); 