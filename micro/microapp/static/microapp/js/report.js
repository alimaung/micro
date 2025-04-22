/**
 * Report Generation Module
 * Microfilm Processing System
 * 
 * This script handles the dynamic functionality for the report generation module,
 * including project selection, filtering, preview generation, and export functionality.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI components
    initializeSections();
    initializeProjects();
    initializeFilters();
    initializeReportOptions();
    initializeEventListeners();
    
    // Show initial mock data
    generateMockPreview();
});

/**
 * Toggles section visibility when headers are clicked
 */
function initializeSections() {
    const sectionHeaders = document.querySelectorAll('.section-header');
    
    sectionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const icon = this.querySelector('.toggle-icon');
            
            this.classList.toggle('collapsed');
            
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    });
}

/**
 * Initializes mock project data
 */
function initializeProjects() {
    const projectList = document.querySelector('.project-list');
    const mockProjects = [
        {
            id: "PRJ001",
            name: "County Records Digitization",
            date: "May 15, 2023",
            progress: 100,
            films: 12,
            documents: 1458
        },
        {
            id: "PRJ002",
            name: "Historical Archives Phase 2",
            date: "Jun 22, 2023",
            progress: 100,
            films: 8,
            documents: 952
        },
        {
            id: "PRJ003",
            name: "University Records 2023",
            date: "Jul 10, 2023",
            progress: 85,
            films: 15,
            documents: 2105,
            inProgress: true
        },
        {
            id: "PRJ004",
            name: "Legal Documentation Project",
            date: "Aug 05, 2023",
            progress: 100,
            films: 6,
            documents: 734
        },
        {
            id: "PRJ005",
            name: "Medical Records Conversion",
            date: "Sep 18, 2023",
            progress: 72,
            films: 20,
            documents: 3250,
            inProgress: true
        }
    ];
    
    // Populate project list
    projectList.innerHTML = '';
    mockProjects.forEach(project => {
        const projectItem = document.createElement('div');
        projectItem.className = 'project-item';
        projectItem.dataset.id = project.id;
        
        projectItem.innerHTML = `
            <div class="project-details">
                <div class="project-name">${project.name}</div>
                <div class="project-info">
                    <span>ID: ${project.id}</span>
                    <span>Started: ${project.date}</span>
                    <span>Films: ${project.films}</span>
                </div>
            </div>
            <div class="project-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${project.progress}%"></div>
                </div>
                <div class="progress-text">${project.progress}% Complete</div>
            </div>
        `;
        
        projectItem.addEventListener('click', function() {
            // Remove selected class from all projects
            document.querySelectorAll('.project-item').forEach(item => {
                item.classList.remove('selected');
            });
            
            // Add selected class to clicked project
            this.classList.add('selected');
            
            // Update preview with selected project data
            updateProjectSelection(project);
        });
        
        projectList.appendChild(projectItem);
    });
    
    // Select first project by default
    if (mockProjects.length > 0) {
        const firstProject = document.querySelector('.project-item');
        if (firstProject) {
            firstProject.classList.add('selected');
            updateProjectSelection(mockProjects[0]);
        }
    }
}

/**
 * Updates the UI with the selected project data
 */
function updateProjectSelection(project) {
    const projectNameElement = document.getElementById('selected-project-name');
    const projectIdElement = document.getElementById('selected-project-id');
    
    if (projectNameElement) {
        projectNameElement.textContent = project.name;
    }
    
    if (projectIdElement) {
        projectIdElement.textContent = project.id;
    }
    
    // Update PDF preview with project data
    updatePdfPreview(project);
    
    // Enable generate button if disabled
    document.getElementById('generate-report-btn').disabled = false;
}

/**
 * Initializes filter controls
 */
function initializeFilters() {
    // Range filter
    const filmRangeInput = document.getElementById('film-count-range');
    const filmRangeValue = document.getElementById('film-count-value');
    
    if (filmRangeInput && filmRangeValue) {
        filmRangeInput.addEventListener('input', function() {
            filmRangeValue.textContent = this.value;
        });
    }
    
    // Date filters
    const dateInputs = document.querySelectorAll('.date-range input');
    dateInputs.forEach(input => {
        if (!input.value) {
            // Set default date values (current date and one month ago)
            const now = new Date();
            if (input.id === 'date-start') {
                const oneMonthAgo = new Date();
                oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
                input.value = formatDateForInput(oneMonthAgo);
            } else {
                input.value = formatDateForInput(now);
            }
        }
    });
    
    // Filter checkboxes
    const filterCheckboxes = document.querySelectorAll('.filter-checkbox');
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Toggle related filters visibility
            const targetId = this.dataset.target;
            if (targetId) {
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    if (this.checked) {
                        targetElement.style.display = 'block';
                    } else {
                        targetElement.style.display = 'none';
                    }
                }
            }
            
            // Update preview when filters change
            generateMockPreview();
        });
    });
}

/**
 * Format date for input fields (YYYY-MM-DD)
 */
function formatDateForInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * Initializes report options
 */
function initializeReportOptions() {
    // Fix: Use actual IDs from HTML for checkboxes
    const sectionCheckboxes = document.querySelectorAll('#include-overview, #include-stats, #include-films, #include-handoffs, #include-charts');
    
    sectionCheckboxes.forEach(checkbox => {
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                // Update preview when sections options change
                generateMockPreview();
            });
        }
    });
    
    // Additional option listeners
    const formatOptions = document.querySelectorAll('input[name="format"]');
    formatOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Update based on selected format
            const format = this.value;
            console.log(`Format changed to: ${format}`);
            // Could update preview format or other options
        });
    });
    
    const additionalOptions = document.querySelectorAll('#include-logo, #include-pagination, #include-toc');
    additionalOptions.forEach(option => {
        option.addEventListener('change', function() {
            // These could update the preview styling
            console.log(`Option ${this.id} changed to: ${this.checked}`);
        });
    });
}

/**
 * Initializes all button event listeners
 */
function initializeEventListeners() {
    // Project search
    const searchInput = document.getElementById('project-search');
    const searchButton = document.getElementById('search-btn');
    
    if (searchInput && searchButton) {
        searchButton.addEventListener('click', function() {
            filterProjects(searchInput.value);
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                filterProjects(this.value);
            }
        });
    }
    
    // Generate report button
    const generateBtn = document.getElementById('generate-report-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            generateReport();
        });
    }
    
    // Download button - Fix: Use correct button IDs from HTML
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            downloadReport();
        });
    }
    
    // Export button
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            exportReport();
        });
    }
    
    // Share button
    const shareBtn = document.getElementById('share-btn');
    const shareModal = document.getElementById('share-modal');
    const closeModal = document.querySelector('.close-btn');
    
    if (shareBtn && shareModal && closeModal) {
        shareBtn.addEventListener('click', function() {
            shareModal.style.display = 'flex';
        });
        
        closeModal.addEventListener('click', function() {
            shareModal.style.display = 'none';
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', function(e) {
            if (e.target === shareModal) {
                shareModal.style.display = 'none';
            }
        });
    }
    
    // Toggle fullscreen
    const fullscreenBtn = document.getElementById('toggle-fullscreen-btn');
    const previewPanel = document.querySelector('.preview-panel');
    
    if (fullscreenBtn && previewPanel) {
        fullscreenBtn.addEventListener('click', function() {
            previewPanel.classList.toggle('fullscreen');
            this.querySelector('i').classList.toggle('fa-expand');
            this.querySelector('i').classList.toggle('fa-compress');
        });
    }
    
    // Copy link button
    const copyLinkBtn = document.getElementById('copy-link-btn');
    const linkInput = document.getElementById('share-link');
    
    if (copyLinkBtn && linkInput) {
        copyLinkBtn.addEventListener('click', function() {
            linkInput.select();
            document.execCommand('copy');
            
            // Show copied notification
            showNotification('Link copied to clipboard!', 'success');
        });
    }
    
    // Social share buttons
    const socialBtns = document.querySelectorAll('.social-btn');
    socialBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const platform = this.classList[1]; // Get the platform class (teams, slack, drive)
            shareViaService(platform);
        });
    });
    
    // Send email button - Fix: Use the correct ID from HTML
    const sendEmailBtn = document.getElementById('send-email-btn');
    if (sendEmailBtn) {
        sendEmailBtn.addEventListener('click', function() {
            const email = document.getElementById('share-email').value;
            const message = document.getElementById('share-message').value;
            
            if (email) {
                sendReportEmail(email, message);
            } else {
                showNotification('Please enter an email address', 'error');
            }
        });
    }
    
    // Other filter controls
    const qualityScore = document.getElementById('quality-score');
    const qualityScoreValue = document.getElementById('quality-score-value');
    
    if (qualityScore && qualityScoreValue) {
        qualityScore.addEventListener('input', function() {
            qualityScoreValue.textContent = `${this.value}%+`;
        });
    }
    
    // Make filters update the preview
    const allFilters = document.querySelectorAll('select, input[type="date"]');
    allFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            generateMockPreview();
        });
    });
}

/**
 * Filters project list based on search query
 */
function filterProjects(query) {
    if (!query) return;
    
    query = query.toLowerCase();
    const projectItems = document.querySelectorAll('.project-item');
    
    projectItems.forEach(item => {
        const projectName = item.querySelector('.project-name').textContent.toLowerCase();
        const projectId = item.dataset.id.toLowerCase();
        
        if (projectName.includes(query) || projectId.includes(query)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
    
    // Show notification with results count
    const visibleCount = Array.from(projectItems).filter(item => item.style.display !== 'none').length;
    showNotification(`Found ${visibleCount} matching projects`, 'info');
}

/**
 * Generates a mock preview of the report
 */
function generateMockPreview() {
    // This function would typically call an API to generate a real preview
    // For now, we'll just update the mock PDF with current options
    
    const pdfSectionOverview = document.querySelector('.pdf-section:nth-child(3)'); // Project Overview section
    const pdfSectionProcessing = document.querySelector('.pdf-section:nth-child(4)'); // Processing Statistics section
    const pdfSectionFilms = document.querySelector('.pdf-section:nth-child(5)'); // Film Details section
    const pdfHandoffSection = document.getElementById('pdf-handoff-section');
    
    // Update PDF date
    const dateElement = document.querySelector('.pdf-header .date');
    if (dateElement) {
        const now = new Date();
        dateElement.textContent = `Generated on ${now.toLocaleDateString()} at ${now.toLocaleTimeString()}`;
    }
    
    // Get selected filtering options based on the actual IDs in the HTML
    const includeOverview = document.getElementById('include-overview');
    const includeStats = document.getElementById('include-stats');
    const includeFilms = document.getElementById('include-films');
    const includeHandoffs = document.getElementById('include-handoffs');
    
    // Update visibility based on options
    if (includeOverview && pdfSectionOverview) {
        pdfSectionOverview.style.display = includeOverview.checked ? 'block' : 'none';
    }
    
    if (includeStats && pdfSectionProcessing) {
        pdfSectionProcessing.style.display = includeStats.checked ? 'block' : 'none';
    }
    
    if (includeFilms && pdfSectionFilms) {
        pdfSectionFilms.style.display = includeFilms.checked ? 'block' : 'none';
    }
    
    if (includeHandoffs && pdfHandoffSection) {
        pdfHandoffSection.style.display = includeHandoffs.checked ? 'block' : 'none';
    }
}

/**
 * Updates the PDF preview with project data
 */
function updatePdfPreview(project) {
    // Project title
    const title = document.querySelector('.pdf-header .title');
    if (title) {
        title.textContent = `${project.name} Report`;
    }
    
    // Project details
    const projectDetails = {
        'Project ID': project.id,
        'Project Name': project.name,
        'Start Date': project.date,
        'Completion Status': `${project.progress}% Complete`,
        'Total Films': project.films,
        'Total Documents': project.documents
    };
    
    // Update overview table
    const overviewTable = document.querySelector('#pdf-section-overview .pdf-table table tbody');
    if (overviewTable) {
        overviewTable.innerHTML = '';
        
        for (const [key, value] of Object.entries(projectDetails)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <th>${key}</th>
                <td>${value}</td>
            `;
            overviewTable.appendChild(row);
        }
    }
    
    // Update processing statistics with random data
    updateProcessingStatistics(project);
    
    // Update film details table
    updateFilmDetails(project);
    
    // Update handoff history
    updateHandoffHistory(project);
}

/**
 * Populates processing statistics with mock data
 */
function updateProcessingStatistics(project) {
    const stats = {
        'Scanning Time': `${Math.floor(20 + Math.random() * 80)} hours`,
        'Processing Time': `${Math.floor(10 + Math.random() * 40)} hours`,
        'Quality Checks': Math.floor(20 + Math.random() * 50),
        'Errors Detected': Math.floor(Math.random() * 10),
        'Errors Resolved': Math.floor(Math.random() * 8),
        'Operator Notes': Math.floor(Math.random() * 15)
    };
    
    const statsTable = document.querySelector('#pdf-section-processing .pdf-table table tbody');
    if (statsTable) {
        statsTable.innerHTML = '';
        
        for (const [key, value] of Object.entries(stats)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <th>${key}</th>
                <td>${value}</td>
            `;
            statsTable.appendChild(row);
        }
    }
}

/**
 * Updates film details table with mock data
 */
function updateFilmDetails(project) {
    const filmsTable = document.querySelector('#pdf-section-films .pdf-table-full table tbody');
    if (!filmsTable) return;
    
    filmsTable.innerHTML = '';
    
    // Generate mock film data
    const filmCount = project.films;
    for (let i = 1; i <= filmCount; i++) {
        const status = i <= filmCount * (project.progress / 100) ? 'completed' : (i === Math.ceil(filmCount * (project.progress / 100)) + 1 ? 'processing' : 'queued');
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>F${project.id.substring(3)}-${String(i).padStart(3, '0')}</td>
            <td>${Math.floor(50 + Math.random() * 200)}</td>
            <td>${formatMockDate(project.date, i)}</td>
            <td>${getRandomOperator()}</td>
            <td><span class="status ${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</span></td>
        `;
        filmsTable.appendChild(row);
    }
}

/**
 * Updates handoff history with mock data
 */
function updateHandoffHistory(project) {
    const handoffTable = document.querySelector('#pdf-section-handoff .pdf-table-full table tbody');
    if (!handoffTable) return;
    
    handoffTable.innerHTML = '';
    
    // Generate mock handoff events
    const handoffs = [
        {
            date: formatMockDate(project.date, 10),
            method: 'USB Drive',
            recipient: 'Sarah Johnson',
            department: 'Archives',
            files: Math.floor(project.documents * 0.3)
        },
        {
            date: formatMockDate(project.date, 20),
            method: 'Network Transfer',
            recipient: 'Michael Chen',
            department: 'IT Operations',
            files: Math.floor(project.documents * 0.5)
        }
    ];
    
    // Add third handoff only if project is complete
    if (project.progress === 100) {
        handoffs.push({
            date: formatMockDate(project.date, 30),
            method: 'Cloud Storage',
            recipient: 'Robert Davis',
            department: 'Records Management',
            files: project.documents
        });
    }
    
    // Populate table
    handoffs.forEach(handoff => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${handoff.date}</td>
            <td>${handoff.method}</td>
            <td>${handoff.recipient}</td>
            <td>${handoff.department}</td>
            <td>${handoff.files}</td>
        `;
        handoffTable.appendChild(row);
    });
}

/**
 * Format a mock date based on a start date and an offset in days
 */
function formatMockDate(startDateStr, daysToAdd) {
    const dateParts = startDateStr.split(' ');
    const month = dateParts[0];
    const day = parseInt(dateParts[1].replace(',', ''));
    const year = parseInt(dateParts[2]);
    
    // Map month names to numbers
    const months = {
        'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5, 
        'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
    };
    
    const date = new Date(year, months[month], day);
    date.setDate(date.getDate() + daysToAdd);
    
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

/**
 * Returns a random operator name
 */
function getRandomOperator() {
    const operators = [
        'John Smith', 'Maria Garcia', 'David Kim', 
        'Lisa Wong', 'James Johnson', 'Emma Davis'
    ];
    return operators[Math.floor(Math.random() * operators.length)];
}

/**
 * Simulates the report generation process with progress updates
 */
function generateReport() {
    // Get the generate button and progress elements
    const generateBtn = document.getElementById('generate-report-btn');
    const progressDiv = document.querySelector('.generation-progress');
    const progressFill = document.querySelector('.generation-progress .progress-fill');
    const percentage = document.querySelector('.generation-progress .percentage');
    const statusText = document.querySelector('.generation-progress .status-text');
    const actionButtons = document.querySelector('.action-buttons');
    
    // Disable generate button and show progress
    generateBtn.disabled = true;
    progressDiv.style.display = 'flex';
    actionButtons.style.display = 'none';
    
    // Reset progress
    let progress = 0;
    progressFill.style.width = '0%';
    percentage.textContent = '0%';
    statusText.textContent = 'Starting generation...';
    
    // Simulate progress
    const interval = setInterval(() => {
        progress += Math.floor(Math.random() * 10) + 1;
        
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            
            // Update status and enable download/export/share
            statusText.textContent = 'Report generated successfully!';
            actionButtons.style.display = 'flex';
            
            // Show success notification
            showNotification('Report generated successfully!', 'success');
            
            // Enable action buttons - Fix: Use the correct button IDs from HTML
            document.getElementById('download-btn').disabled = false;
            document.getElementById('export-btn').disabled = false;
            document.getElementById('share-btn').disabled = false;
        } else {
            // Update status text based on progress
            if (progress < 30) {
                statusText.textContent = 'Collecting project data...';
            } else if (progress < 60) {
                statusText.textContent = 'Processing statistics...';
            } else if (progress < 90) {
                statusText.textContent = 'Generating visualizations...';
            } else {
                statusText.textContent = 'Finalizing report...';
            }
        }
        
        // Update progress bar and text
        progressFill.style.width = `${progress}%`;
        percentage.textContent = `${progress}%`;
    }, 200);
}

/**
 * Simulates downloading the report
 */
function downloadReport() {
    showNotification('Downloading PDF report...', 'info');
    
    // Simulate download delay
    setTimeout(() => {
        showNotification('Report downloaded successfully!', 'success');
    }, 1500);
}

/**
 * Simulates exporting the report to different formats
 */
function exportReport() {
    const formats = ['Excel (.xlsx)', 'CSV (.csv)', 'XML (.xml)'];
    const formatList = formats.map(f => `<li>${f}</li>`).join('');
    
    // Show a more complex notification with format options
    const notification = document.createElement('div');
    notification.className = 'notification info';
    notification.innerHTML = `
        <div>Export as:</div>
        <ul>${formatList}</ul>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.add('notification-exit');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

/**
 * Simulates sharing the report via a service
 */
function shareViaService(service) {
    // Close modal
    document.getElementById('share-modal').style.display = 'none';
    
    // Show notification
    showNotification(`Sharing report via ${service}...`, 'info');
    
    // Simulate sharing
    setTimeout(() => {
        showNotification(`Report shared via ${service} successfully!`, 'success');
    }, 1500);
}

/**
 * Simulates sending an email with the report
 */
function sendReportEmail(email, message) {
    // Close modal
    document.getElementById('share-modal').style.display = 'none';
    
    // Show notification
    showNotification(`Sending report to ${email}...`, 'info');
    
    // Simulate email sending
    setTimeout(() => {
        showNotification(`Report sent to ${email} successfully!`, 'success');
    }, 2000);
    
    // Reset form
    document.getElementById('email-form').reset();
}

/**
 * Displays a notification message
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.add('notification-exit');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

/**
 * Toggle dark mode
 */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    
    // Store preference in local storage
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

// Check for saved dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
