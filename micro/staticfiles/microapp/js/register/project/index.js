/**
 * index.js - Entry point for Project Configuration module
 */



// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing project configuration module...');
    
    // Verify that required modules are loaded
    if (!FolderPicker) {
        console.error('ERROR: FolderPicker module not loaded');
        document.querySelector('.transfer-container').innerHTML = `
            <div style="padding: 20px; color: #ff453a; text-align: center;">
                <h2>Error Loading Project Configuration Interface</h2>
                <p>Required module FolderPicker failed to load. Please check the browser console for details.</p>
                <p>Try refreshing the page or contact support if the issue persists.</p>
            </div>
        `;
        return;
    }
    
    // Initialize TransferCore - this will set up all the necessary components
    const transferApp = new TransferCore();
    
    // Expose the app to window for debugging purposes
    window.transferApp = transferApp;
});
