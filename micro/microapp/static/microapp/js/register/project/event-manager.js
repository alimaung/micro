/**
 * event-manager.js - Custom event management for the Transfer module
 * Manages event subscriptions and dispatching for component communication
 */

// Make the class available globally
window.EventManager = class EventManager {
    constructor() {
        // Event storage: { eventName: [callbacks] }
        this.events = {};
    }
    
    /**
     * Subscribe to an event
     * @param {string} eventName - Name of the event to subscribe to
     * @param {Function} callback - Function to call when event is triggered
     * @returns {Object} - Subscription object with unsubscribe method
     */
    subscribe(eventName, callback) {
        if (!this.events[eventName]) {
            this.events[eventName] = [];
        }
        
        this.events[eventName].push(callback);
        
        return {
            unsubscribe: () => {
                this.events[eventName] = this.events[eventName].filter(cb => cb !== callback);
                if (this.events[eventName].length === 0) {
                    delete this.events[eventName];
                }
            }
        };
    }
    
    /**
     * Publish an event
     * @param {string} eventName - Name of the event to trigger
     * @param {any} data - Data to pass to event callbacks
     */
    publish(eventName, data) {
        if (this.events[eventName]) {
            this.events[eventName].forEach(callback => {
                callback(data);
            });
        }
    }
    
    /**
     * Clear all event subscriptions
     */
    clear() {
        this.events = {};
    }
};
