// Main JavaScript functionality for Microfilm Processing System

// DOM ready function
document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle functionality
    const toggleButton = document.getElementById('dark-mode-toggle');
    const body = document.body;
    const logo = document.getElementById('logo');
    const darkModeIcon = document.getElementById('dark-mode-icon');
    
    // Handle prefers-color-scheme media query
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Get the base static URL for the logo images
    const logoLightPath = logo.getAttribute('src');
    const logoDarkPath = logoLightPath.replace('logo_light.png', 'logo_dark.png');

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

    // Add click event for dark mode toggle with animation
    toggleButton.addEventListener('click', () => {
        const isDarkMode = body.classList.contains('dark-mode');
        
        // First animate the icon
        darkModeIcon.style.transform = 'rotate(360deg)';
        
        // After a small delay, toggle the theme
        setTimeout(() => {
            setDarkMode(!isDarkMode);
            darkModeIcon.style.transform = '';
        }, 200);
    });
    
    // Listen for changes in system color scheme preference
    prefersDarkMode.addEventListener('change', (event) => {
        // Only apply if the user hasn't set a preference
        if (!localStorage.getItem('dark-mode')) {
            setDarkMode(event.matches);
        }
    });
    
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