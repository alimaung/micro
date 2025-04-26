/**
 * notification_manager.js - Notification system for microfilm control interface
 * Handles displaying user notifications and alerts
 */

// Create namespace for notification functions
const NotificationManager = {
    // State tracking for notification throttling
    lastNotificationTimes: {},
    NOTIFICATION_THROTTLE_MS: 30000, // 30 seconds minimum between similar notifications

    /**
     * Display a notification to the user
     * @param {string} message - The message to display
     * @param {string} type - The notification type (info, success, warning, error)
     */
    showNotification: function(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.querySelector('.notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'notification';
            document.body.appendChild(notification);
            
            // Add styles if not in stylesheet
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.right = '20px';
            notification.style.padding = '12px 20px';
            notification.style.borderRadius = '8px';
            notification.style.color = '#fff';
            notification.style.fontWeight = '500';
            notification.style.zIndex = '9999';
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
            notification.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
            notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        }
        
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
        
        // Show notification
        notification.style.transform = 'translateY(0)';
        notification.style.opacity = '1';
        
        // Hide after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
        }, 3000);
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