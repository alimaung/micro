/**
 * notification_manager.js - Notification system for microfilm control interface
 * Handles displaying user notifications and alerts
 */

// Create namespace for notification functions
const NotificationManager = {
    // State tracking for notification throttling
    lastNotificationTimes: {},
    NOTIFICATION_THROTTLE_MS: 3000, // 2 seconds minimum between similar notifications
    activeNotifications: [], // Array to track active notifications
    maxVisibleNotifications: 5, // Maximum number of visible notifications at once
    notificationContainer: null, // Container for all notifications

    /**
     * Initialize the notification container
     */
    init: function() {
        if (!this.notificationContainer) {
            this.notificationContainer = document.createElement('ul');
            this.notificationContainer.className = 'notification-container';
            document.body.appendChild(this.notificationContainer);
            
            // Fixed container styles with overflow fixes
            this.notificationContainer.style.position = 'fixed';
            this.notificationContainer.style.bottom = '20px';
            this.notificationContainer.style.right = '20px';
            this.notificationContainer.style.listStyle = 'none';
            this.notificationContainer.style.padding = '0';
            this.notificationContainer.style.margin = '0';
            this.notificationContainer.style.zIndex = '9999';
            this.notificationContainer.style.maxHeight = 'calc(100vh - 40px)';
            
            // Fix for the overflow issue
            this.notificationContainer.style.overflow = 'visible'; // Changed from 'hidden'
            
            this.notificationContainer.style.width = 'auto';
            this.notificationContainer.style.minWidth = '300px';
            this.notificationContainer.style.maxWidth = '500px';
            this.notificationContainer.style.pointerEvents = 'none';
            
            // Add display flex for better stacking
            this.notificationContainer.style.display = 'flex';
            this.notificationContainer.style.flexDirection = 'column-reverse';
            this.notificationContainer.style.alignItems = 'flex-end'; // Right align notifications
        }
    },

    /**
     * Display a notification to the user
     * @param {string} message - The message to display
     * @param {string} type - The notification type (info, success, warning, error)
     */
    showNotification: function(message, type = 'info') {
        // Initialize container if needed
        this.init();
        
        // Create new notification element as list item
        const notification = document.createElement('li');
        notification.className = 'notification';
        
        // Improved styles to prevent clipping
        notification.style.padding = '12px 20px';
        notification.style.borderRadius = '8px';
        notification.style.color = '#fff';
        notification.style.fontWeight = '500';
        notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        notification.style.width = 'auto';
        notification.style.maxWidth = '100%';
        notification.style.boxSizing = 'border-box'; // Ensure padding is included in width
        notification.style.position = 'relative';
        notification.style.marginBottom = '10px';
        notification.style.minWidth = '250px';
        notification.style.height = 'auto';
        notification.style.minHeight = '24px';
        notification.style.overflowWrap = 'break-word';
        notification.style.pointerEvents = 'auto';
        notification.style.display = 'block'; // Ensure proper display
        notification.style.wordBreak = 'break-word'; // Better handling of long words
        
        // Set color based on notification type
        switch(type) {
            case 'success':
                notification.style.backgroundColor = '#34a853';
                break;
            case 'error':
                notification.style.backgroundColor = '#ea4335';
                break;
            case 'warning':
                notification.style.backgroundColor = '#fbbc04';
                break;
            default:
                notification.style.backgroundColor = '#1a73e8';
        }
        
        // Set message
        notification.textContent = message;
        
        // Add to container
        this.notificationContainer.appendChild(notification);
        
        // Set initial state for animation
        notification.style.transform = 'translateX(100px)';
        notification.style.opacity = '0';
        notification.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
        
        // Track this notification
        this.activeNotifications.push(notification);
        
        // Make sure container has adequate width for this notification
        setTimeout(() => {
            // Get notification width including padding
            const notificationWidth = notification.offsetWidth;
            // If container is too narrow, expand it
            if (notificationWidth > parseInt(this.notificationContainer.style.minWidth)) {
                this.notificationContainer.style.minWidth = (notificationWidth + 20) + 'px';
            }
        }, 10);
        
        // Manage maximum visible notifications
        if (this.activeNotifications.length > this.maxVisibleNotifications) {
            const oldestNotification = this.activeNotifications.shift();
            if (oldestNotification && oldestNotification.parentNode) {
                oldestNotification.style.opacity = '0';
                oldestNotification.style.transform = 'translateX(100px)';
                
                // Remove from DOM after transition
                setTimeout(() => {
                    if (oldestNotification.parentNode) {
                        oldestNotification.parentNode.removeChild(oldestNotification);
                    }
                }, 300);
            }
        }
        
        // Show notification (on next frame to trigger animation)
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        });
        
        // Hide after 3 seconds
        const removeTimeout = setTimeout(() => {
            notification.style.transform = 'translateX(100px)';
            notification.style.opacity = '0';
            
            // Remove from DOM and tracking array after transition
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                const index = this.activeNotifications.indexOf(notification);
                if (index > -1) {
                    this.activeNotifications.splice(index, 1);
                }
            }, 300);
        }, 3000);
        
        // Allow clicking to dismiss early
        notification.addEventListener('click', () => {
            clearTimeout(removeTimeout);
            notification.style.transform = 'translateX(100px)';
            notification.style.opacity = '0';
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                const index = this.activeNotifications.indexOf(notification);
                if (index > -1) {
                    this.activeNotifications.splice(index, 1);
                }
            }, 300);
        });
    },

    /**
     * Check if a notification should be throttled
     * @param {string} type - The notification type/category
     * @returns {boolean} Whether the notification should be throttled
     */
    shouldThrottleNotification: function(type) {
        const now = Date.now();
        const lastTime = this.lastNotificationTimes[type] || 0;
        
        if (now - lastTime < this.NOTIFICATION_THROTTLE_MS) {
            return true; // Should throttle
        }
        
        // Update last notification time
        this.lastNotificationTimes[type] = now;
        return false; // Should not throttle
    }
}; 