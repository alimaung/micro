/**
 * analysis.js - PDF Analysis Tool functionality
 * Handles PDF document analysis for size, DPI, and other properties
 */

// Create a namespace for the Analysis component to avoid global variable conflicts
window.MicroAnalysis = (function() {
    // Chart for paper size distribution
    let paperSizeChart = null;

    // DOM Elements - scoped to this module
    const directoryPathInput = document.getElementById('directoryPath');
    const browseDirBtn = document.getElementById('browseDirBtn');
    const loadingContainer = document.getElementById('loadingContainer');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Status elements
    const resultStatusCard = document.getElementById('resultStatusCard');
    const statusIcon = document.getElementById('statusIcon');
    const statusMessage = document.getElementById('statusMessage');

    // Stats elements
    const totalFilesElement = document.getElementById('totalFiles');
    const oversizedFilesElement = document.getElementById('oversizedFiles');
    const totalPagesElement = document.getElementById('totalPages');
    const oversizedPagesElement = document.getElementById('oversizedPages');
    const oversizedSummary = document.getElementById('oversizedSummary');
    
    // Chart and table containers
    const chartContainer = document.getElementById('chartContainer');
    const tableContainer = document.getElementById('tableContainer');

    // Table elements
    const oversizedTableBody = document.getElementById('oversizedTableBody');

    // Initialize the PDF Analysis component
    function init() {
        // Only initialize if we're on the analysis page
        if (!document.querySelector('.analysis-card')) {
            return;
        }
        
        initAnalysisUI();
    }

    // Initialize the UI and event listeners
    function initAnalysisUI() {
        // Initialize directory input and combined browse & analyze button
        if (directoryPathInput && browseDirBtn) {
            // Style the button properly
            browseDirBtn.classList.add('browse-btn');
            browseDirBtn.style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color') || '#4285f4';
            browseDirBtn.style.color = 'white';
            
            // Enable the browse button when directory path is entered manually
            directoryPathInput.addEventListener('input', function() {
                if (this.value.trim()) {
                    // If path is entered manually, add click handler to analyze on Enter key
                    this.onkeydown = function(e) {
                        if (e.key === 'Enter') {
                            analyzePDFs();
                        }
                    };
                }
            });
            
            // Set up combined browse & analyze button
            browseDirBtn.addEventListener('click', browseAndAnalyze);
        }
        
        // Hide results container initially
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        // Hide chart and table containers initially
        if (chartContainer) chartContainer.style.display = 'none';
        if (tableContainer) tableContainer.style.display = 'none';
        
        // Make sure the status card is styled correctly
        if (resultStatusCard) {
            resultStatusCard.style.display = 'none'; // Initially hidden
        }
        
        // Log that initialization is complete
        console.log('PDF Analysis UI initialized');
    }

    // Combined function to browse directory and then analyze
    function browseAndAnalyze() {
        fetch('/browse_folder', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                window.MicroCore.showNotification(`Error opening folder browser: ${data.error}`, 'error');
                console.error('Folder browser error:', data.error);
                return;
            }
            
            if (data.path && directoryPathInput) {
                directoryPathInput.value = data.path;
                // Immediately analyze the selected directory
                analyzePDFs();
            } else if (data.message) {
                window.MicroCore.showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            window.MicroCore.showNotification('Error opening folder browser', 'error');
            console.error('Fetch error:', error);
        });
    }

    // Analyze PDFs in the selected directory
    function analyzePDFs() {
        const directoryPath = directoryPathInput.value.trim();
        
        if (!directoryPath) {
            window.MicroCore.showNotification('Please select a directory first', 'warning');
            return;
        }
        
        // Show loading indicator
        if (loadingContainer) {
            loadingContainer.style.display = 'flex';
        }
        
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        // Prepare form data
        const formData = new FormData();
        formData.append('directory', directoryPath);
        
        // Send request to server
        fetch('/pdf_pages', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (loadingContainer) {
                loadingContainer.style.display = 'none';
            }
            
            if (data.error) {
                window.MicroCore.showNotification(data.error, 'error');
                return;
            }
            
            // Display results
            displayResults(data);
        })
        .catch(error => {
            if (loadingContainer) {
                loadingContainer.style.display = 'none';
            }
            window.MicroCore.showNotification('Error analyzing PDFs', 'error');
            console.error('Analysis error:', error);
        });
    }

    // Display analysis results
    function displayResults(data) {
        if (!resultsContainer) return;
        
        console.log('Received data:', data);
        
        // Show results container
        resultsContainer.style.display = 'block';
        
        // Extract oversized files data
        const oversizedFiles = data.oversized_files || [];
        
        // Get all unique filenames from oversized files list
        let uniqueOversizedFiles = new Set();
        if (oversizedFiles.length > 0) {
            oversizedFiles.forEach(file => {
                if (file.filename) {
                    uniqueOversizedFiles.add(file.filename);
                }
            });
        }
        const countOfPDFsWithOversizedPages = uniqueOversizedFiles.size;
        
        // Use the total_pdf_files from API response if available
        let totalPDFFiles = data.total_pdf_files || 0;
        
        // Update the UI with total PDFs count
        if (totalFilesElement) {
            totalFilesElement.textContent = totalPDFFiles;
        }
        
        // Update the UI with count of PDFs containing oversized pages
        if (oversizedFilesElement) {
            oversizedFilesElement.textContent = countOfPDFsWithOversizedPages;
        }
        
        // Update total pages
        if (totalPagesElement) {
            totalPagesElement.textContent = data.total_pages || 0;
        }
        
        // Update oversized pages
        if (oversizedPagesElement) {
            oversizedPagesElement.textContent = data.oversized_pages || 0;
        }
        
        // Update Result Status Card
        const hasOversizedPages = (data.oversized_pages || 0) > 0;
        // Check if there are any PDFs found
        const hasPDFs = totalPDFFiles > 0;
        updateStatusCard(hasOversizedPages, hasPDFs);
        
        // Conditional display of chart and table containers
        if (hasOversizedPages) {
            // Show chart and table
            if (chartContainer) chartContainer.style.display = 'block';
            if (tableContainer) tableContainer.style.display = 'block';
            
            // Populate oversized files table
            updateOversizedTable(oversizedFiles);
            
            // Generate paper size distribution data directly from oversized files and total pages
            const paperSizes = {};
            
            // Count occurrences of each paper size from oversized files
            if (oversizedFiles.length > 0) {
                oversizedFiles.forEach(file => {
                    if (file.paper_size) {
                        if (paperSizes[file.paper_size]) {
                            paperSizes[file.paper_size]++;
                        } else {
                            paperSizes[file.paper_size] = 1;
                        }
                    }
                });
            }
            
            // Add information about non-oversized pages
            const standardPages = (data.total_pages || 0) - (data.oversized_pages || 0);
            if (standardPages > 0) {
                paperSizes['A4/Standard'] = standardPages;
            }
            
            console.log('Generated paper sizes data:', paperSizes);
            
            // Create the chart using our generated data
            if (Object.keys(paperSizes).length > 0) {
                createPaperSizeChart(paperSizes);
            } else {
                // No data available for chart, hide it
                if (chartContainer) chartContainer.style.display = 'none';
            }

            // Update oversized summary
            if (oversizedSummary) {
                // Only show the summary if we have valid numbers
                if (countOfPDFsWithOversizedPages > 0 && totalPDFFiles && typeof totalPDFFiles === 'number' && totalPDFFiles > 0) {
                    const ratio = countOfPDFsWithOversizedPages / totalPDFFiles;
                    const percentage = (ratio * 100).toFixed(0);
                    oversizedSummary.textContent = `(${countOfPDFsWithOversizedPages} of ${totalPDFFiles} PDFs - ${percentage}%)`;
                    oversizedSummary.style.display = 'inline';
                } else {
                    oversizedSummary.style.display = 'none';
                }
            }
        } else {
            // Hide chart and table when no oversized pages
            if (chartContainer) chartContainer.style.display = 'none';
            if (tableContainer) tableContainer.style.display = 'none';
        }
    }
    
    // Update the status card based on analysis results
    function updateStatusCard(hasOversizedPages, hasPDFs) {
        if (!resultStatusCard || !statusIcon || !statusMessage) return;
        
        // Clear existing icon classes
        statusIcon.innerHTML = '';
        
        // Create the icon element
        const iconElement = document.createElement('i');
        
        if (!hasPDFs) {
            // No PDFs found - info status
            iconElement.className = 'fas fa-info-circle info-icon';
            statusMessage.textContent = 'No PDF documents found in the selected directory.';
            statusMessage.className = 'status-message info';
            console.log('Setting no PDFs status'); // Debug log
        } else if (hasOversizedPages) {
            // Warning status
            iconElement.className = 'fas fa-exclamation-triangle warning-icon';
            statusMessage.textContent = 'Oversized pages detected! These may need special handling.';
            statusMessage.className = 'status-message warn';
            console.log('Setting warning status'); // Debug log
        } else {
            // Success status
            iconElement.className = 'fas fa-check-circle success-icon';
            statusMessage.textContent = 'All documents are within standard size limits. No action required.';
            statusMessage.className = 'status-message success';
            console.log('Setting success status'); // Debug log
        }
        
        // Add the icon to the container
        statusIcon.appendChild(iconElement);
        
        // Ensure the card is visible
        resultStatusCard.style.display = 'flex';
    }

    // Update the oversized files table
    function updateOversizedTable(oversizedFiles) {
        if (!oversizedTableBody) return;
        
        // Clear existing table rows
        oversizedTableBody.innerHTML = '';
        
        // Add rows for each oversized file
        oversizedFiles.forEach(file => {
            const row = document.createElement('tr');
            
            // Create cells
            const filenameCell = document.createElement('td');
            filenameCell.textContent = file.filename;
            
            const pageCell = document.createElement('td');
            pageCell.textContent = file.page_number;
            
            const dimensionsCell = document.createElement('td');
            dimensionsCell.textContent = file.dimensions;
            
            const paperSizeCell = document.createElement('td');
            paperSizeCell.textContent = file.paper_size;
            
            // Add cells to row
            row.appendChild(filenameCell);
            row.appendChild(pageCell);
            row.appendChild(dimensionsCell);
            row.appendChild(paperSizeCell);
            
            // Add row to table
            oversizedTableBody.appendChild(row);
        });
    }

    // Create the paper size distribution chart
    function createPaperSizeChart(paperSizes) {
        // Get canvas element
        const chartCanvas = document.getElementById('paperSizeChart');
        if (!chartCanvas) {
            console.error('Paper size chart canvas not found!');
            return;
        }
        
        console.log('Creating chart with data:', paperSizes);
        
        // Get chart container for messaging
        const chartContainer = chartCanvas.parentElement;
        if (!chartContainer) {
            console.error('Chart container not found!');
            return;
        }
        
        // Clean up any previous no-data messages
        const existingMessages = chartContainer.querySelectorAll('.no-data');
        existingMessages.forEach(message => message.remove());
        
        // Convert data format for Chart.js
        const labels = Object.keys(paperSizes);
        const data = Object.values(paperSizes);
        
        if (labels.length === 0) {
            console.warn('No paper size data available for chart');
            chartCanvas.style.display = 'none';
            return;
        }
        
        // Calculate percentages for labels
        const total = data.reduce((sum, value) => sum + value, 0);
        const labelsWithPercentages = labels.map((label, index) => {
            const percentage = ((data[index] / total) * 100).toFixed(1);
            return `${label} (${percentage}%)`;
        });
        
        // Define chart colors - use more colors if needed
        const backgroundColors = [
            'rgba(75, 192, 192, 0.7)',   // teal
            'rgba(54, 162, 235, 0.7)',   // blue
            'rgba(153, 102, 255, 0.7)',  // purple
            'rgba(255, 159, 64, 0.7)',   // orange
            'rgba(255, 99, 132, 0.7)',   // red
            'rgba(255, 206, 86, 0.7)',   // yellow
            'rgba(201, 203, 207, 0.7)',  // grey
            'rgba(75, 192, 100, 0.7)',   // green
            'rgba(150, 100, 150, 0.7)'   // lavender
        ];
        
        // Ensure we have enough colors
        while (backgroundColors.length < labels.length) {
            // Generate additional random colors if needed
            const r = Math.floor(Math.random() * 255);
            const g = Math.floor(Math.random() * 255);
            const b = Math.floor(Math.random() * 255);
            backgroundColors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
        }
        
        // Destroy previous chart if it exists
        if (paperSizeChart) {
            paperSizeChart.destroy();
        }
        
        // Ensure canvas is visible
        chartCanvas.style.display = 'block';
        
        try {
            // Create new chart
            paperSizeChart = new Chart(chartCanvas, {
                type: 'pie',
                data: {
                    labels: labelsWithPercentages,
                    datasets: [{
                        label: 'Paper Size Distribution',
                        data: data,
                        backgroundColor: backgroundColors.slice(0, labels.length),
                        borderColor: backgroundColors.slice(0, labels.length).map(color => color.replace('0.7', '1')),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                padding: 20,
                                boxWidth: 12,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${value} pages (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
            console.log('Chart created successfully');
        } catch (error) {
            console.error('Error creating chart:', error);
            // Hide the chart container if there's an error
            if (chartContainer.parentElement && chartContainer.parentElement.parentElement) {
                chartContainer.parentElement.parentElement.style.display = 'none';
            }
        }
    }

    // Register the initialization function to run when the DOM is loaded
    document.addEventListener('DOMContentLoaded', init);

    // Return public methods and properties
    return {
        init: init
    };
})(); 