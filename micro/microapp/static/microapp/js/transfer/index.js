/**
 * index.js - Entry point for Transfer module
 */

// Add CSS styles for warning messages
const setupStyles = () => {
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .warning-message {
            font-size: 0.85rem;
            margin-top: 0.25rem;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            display: block;
        }
        
        .warning-message.error {
            color: #fff;
            background-color: #ff453a;
        }
        
        .warning-message.warning {
            color: #fff;
            background-color: #ff9500;
        }
        
        .warning-message.success {
            color: #fff;
            background-color: #34c759;
        }
    `;
    document.head.appendChild(styleElement);
};

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing transfer functionality...');
    
    // Verify that required modules are loaded
    if (!FolderPicker) {
        console.error('ERROR: FolderPicker module not loaded');
        document.querySelector('.transfer-container').innerHTML = `
            <div style="padding: 20px; color: #ff453a; text-align: center;">
                <h2>Error Loading Transfer Interface</h2>
                <p>Required module FolderPicker failed to load. Please check the browser console for details.</p>
                <p>Try refreshing the page or contact support if the issue persists.</p>
            </div>
        `;
        return;
    }

    // Setup styles
    setupStyles();
    
    // Initialize TransferCore - this will set up all the necessary components
    const transferApp = new TransferCore();
    
    // Expose the app to window for debugging purposes
    window.transferApp = transferApp;
});
