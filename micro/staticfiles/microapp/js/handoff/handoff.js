/**
 * Handoff Interface JavaScript
 * Microfilm Processing System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let selectedProject = null;
    let validationData = [];
    let validationResults = null;
    
    // State management keys
    const STATE_KEYS = {
        SELECTED_PROJECT: 'handoff_selected_project',
        VALIDATION_DATA: 'handoff_validation_data',
        VALIDATION_RESULTS: 'handoff_validation_results',
        CURRENT_SECTION: 'handoff_current_section',
        EMAIL_FORM_DATA: 'handoff_email_form_data'
    };
    
    // DOM elements
    const projectSelectionSection = document.getElementById('project-selection-section');
    const validationSection = document.getElementById('validation-section');
    const emailSection = document.getElementById('email-section');
    const progressModal = document.getElementById('progress-modal');
    const successModal = document.getElementById('success-modal');
    
    // Project selection elements
    const projectCardsContainer = document.getElementById('project-cards-container');
    const projectSearchInput = document.getElementById('project-search');
    const statusFilter = document.getElementById('status-filter');
    
    // Validation elements
    const selectedProjectName = document.getElementById('selected-project-name');
    const selectedProjectId = document.getElementById('selected-project-id');
    const validateBtn = document.getElementById('validate-btn');
    const validationTableBody = document.getElementById('validation-table-body');
    const validationSummary = document.getElementById('validation-summary');
    
    // Email elements
    const emailTo = document.getElementById('email-to');
    const emailCc = document.getElementById('email-cc');
    const emailBcc = document.getElementById('email-bcc');
    const emailSubject = document.getElementById('email-subject');
    const emailArchiveId = document.getElementById('email-archive-id');
    const emailFilmNumbers = document.getElementById('email-film-numbers');
    const emailCustomMessage = document.getElementById('email-custom-message');
    const emailPreview = document.getElementById('email-preview');
    const sendEmailBtn = document.getElementById('send-email-btn');
    const attachmentList = document.getElementById('attachment-list');
    
    // Rich text editor
    let tinyMceEditor = null;
    let emailHtmlContent = '';
    
    // Progress elements
    const progressTitle = document.getElementById('progress-title');
    const progressMessage = document.getElementById('progress-message');
    const progressFill = document.getElementById('progress-fill');
    
    // Initialize event handlers
    initializeEventHandlers();
    
    // Clear any stuck modals on page load
    hideAllModals();
    
    // Restore state from localStorage or load initial data
    restoreStateOrInitialize();
    
    // State Management Functions
    function saveState() {
        try {
            if (selectedProject) {
                localStorage.setItem(STATE_KEYS.SELECTED_PROJECT, JSON.stringify(selectedProject));
            }
            if (validationData.length > 0) {
                localStorage.setItem(STATE_KEYS.VALIDATION_DATA, JSON.stringify(validationData));
            }
            if (validationResults) {
                localStorage.setItem(STATE_KEYS.VALIDATION_RESULTS, JSON.stringify(validationResults));
            }
            
            // Save current section
            const currentSection = getCurrentSection();
            if (currentSection) {
                localStorage.setItem(STATE_KEYS.CURRENT_SECTION, currentSection);
            }
            
            // Save email form data if in email section
            if (currentSection === 'email') {
                saveEmailFormData();
            }
        } catch (error) {
            console.warn('Error saving state to localStorage:', error);
        }
    }
    
    function restoreState() {
        try {
            // Restore selected project
            const savedProject = localStorage.getItem(STATE_KEYS.SELECTED_PROJECT);
            if (savedProject) {
                selectedProject = JSON.parse(savedProject);
                updateProjectInfo();
            }
            
            // Restore validation data
            const savedValidationData = localStorage.getItem(STATE_KEYS.VALIDATION_DATA);
            if (savedValidationData) {
                validationData = JSON.parse(savedValidationData);
                renderValidationTable();
            }
            
            // Restore validation results
            const savedValidationResults = localStorage.getItem(STATE_KEYS.VALIDATION_RESULTS);
            if (savedValidationResults) {
                validationResults = JSON.parse(savedValidationResults);
                showValidationSummary(validationResults);
            }
            
            // Restore current section
            const savedSection = localStorage.getItem(STATE_KEYS.CURRENT_SECTION);
            if (savedSection && selectedProject) {
                switch (savedSection) {
                    case 'validation':
                        showValidationSection();
                        break;
                    case 'email':
                        showEmailSection();
                        restoreEmailFormData();
                        break;
                    default:
                        showProjectSelection();
                }
            } else {
                showProjectSelection();
            }
            
            return true;
        } catch (error) {
            console.warn('Error restoring state from localStorage:', error);
            clearAllState();
            return false;
        }
    }
    
    function clearAllState() {
        try {
            Object.values(STATE_KEYS).forEach(key => {
                localStorage.removeItem(key);
            });
            
            // Reset variables
            selectedProject = null;
            validationData = [];
            validationResults = null;
            
            console.log('All handoff state cleared');
        } catch (error) {
            console.warn('Error clearing state:', error);
        }
    }
    
    function getCurrentSection() {
        if (emailSection.style.display !== 'none') return 'email';
        if (validationSection.style.display !== 'none') return 'validation';
        return 'projects';
    }
    
    function saveEmailFormData() {
        try {
            const emailFormData = {
                to: emailTo ? emailTo.value : '',
                cc: emailCc ? emailCc.value : '',
                bcc: emailBcc ? emailBcc.value : '',
                subject: emailSubject ? emailSubject.value : '',
                archive_id: emailArchiveId ? emailArchiveId.value : '',
                film_numbers: emailFilmNumbers ? emailFilmNumbers.value : '',
                custom_message: emailCustomMessage ? emailCustomMessage.value : ''
            };
            localStorage.setItem(STATE_KEYS.EMAIL_FORM_DATA, JSON.stringify(emailFormData));
        } catch (error) {
            console.warn('Error saving email form data:', error);
        }
    }
    
    function restoreEmailFormData() {
        try {
            const savedEmailData = localStorage.getItem(STATE_KEYS.EMAIL_FORM_DATA);
            if (savedEmailData) {
                const emailFormData = JSON.parse(savedEmailData);
                
                if (emailTo) {
                    emailTo.value = emailFormData.to || 'dilek.kursun@rolls-royce.com';
                }
                if (emailCc) {
                    emailCc.value = emailFormData.cc || 'jan.becker@rolls-royce.com; thomas.lux@rolls-royce.com';
                }
                if (emailBcc) {
                    emailBcc.value = emailFormData.bcc || 'michael.wuske@rolls-royce.com; tetiana.isakii@rolls-royce.com; shmaila.aslam@rolls-royce.com';
                }
                if (emailSubject) {
                    emailSubject.value = emailFormData.subject || `Microfilm Project Handoff - ${selectedProject?.archive_id || '[Archive ID]'}`;
                }
                if (emailArchiveId) {
                    emailArchiveId.value = emailFormData.archive_id || '';
                }
                if (emailFilmNumbers) {
                    emailFilmNumbers.value = emailFormData.film_numbers || '';
                }
                if (emailCustomMessage) {
                    emailCustomMessage.value = emailFormData.custom_message || '';
                }
                
                // Update preview after restoring data
                updateEmailPreview();
            }
        } catch (error) {
            console.warn('Error restoring email form data:', error);
        }
    }
    
    function updateProjectInfo() {
        if (selectedProject) {
            selectedProjectName.textContent = selectedProject.name;
            selectedProjectId.textContent = selectedProject.archive_id;
        }
    }
    
    function restoreStateOrInitialize() {
        const restored = restoreState();
        if (!restored) {
            // Load initial data if no state to restore
            console.log('No state to restore, loading initial projects');
            loadProjects();
        } else {
            // Still load projects to refresh the list, but don't change current section
            console.log('State restored, refreshing project list');
            loadProjects();
        }
    }
    
    function hideAllModals() {
        progressModal.style.display = 'none';
        successModal.style.display = 'none';
    }
    
    function initializeEventHandlers() {
        // Project selection
        document.getElementById('back-to-selection').addEventListener('click', showProjectSelection);
        document.getElementById('back-to-validation').addEventListener('click', showValidationSection);
        
        // Project search and filter
        if (projectSearchInput) {
            projectSearchInput.addEventListener('input', filterProjects);
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                // Reload projects from server when status filter changes
                console.log('Status filter changed to:', statusFilter.value);
                loadProjects();
                // Apply current search filter to new results after loading
                setTimeout(() => {
                    if (projectSearchInput && projectSearchInput.value) {
                        filterProjects();
                    }
                }, 100);
            });
        }
        
        // Project sorting
        const sortSelect = document.getElementById('sort-projects');
        if (sortSelect) {
            sortSelect.addEventListener('change', filterProjects);
        }
        
        // Validation
        document.getElementById('validate-btn').addEventListener('click', validateProject);
        document.getElementById('proceed-to-email').addEventListener('click', function() {
            // Double-check validation before proceeding
            const actualSummary = calculateActualValidationSummary();
            if (actualSummary.errors > 0) {
                showNotification(`Cannot proceed: ${actualSummary.errors} document(s) have missing COM IDs or other critical errors.`, 'error');
                return;
            }
            showEmailSection();
        });
        
        // Email - only add listeners for elements that exist
        const addRecipientBtn = document.getElementById('add-recipient');
        if (addRecipientBtn) {
            addRecipientBtn.addEventListener('click', addRecipient);
        }
        
        const clearCcBtn = document.getElementById('clear-cc-btn');
        if (clearCcBtn) {
            clearCcBtn.addEventListener('click', clearCcRecipients);
        }
        
        const clearBccBtn = document.getElementById('clear-bcc-btn');
        if (clearBccBtn) {
            clearBccBtn.addEventListener('click', clearBccRecipients);
        }
        
        // Use the correct send button ID
        const sendEmailBtn = document.getElementById('send-email-btn');
        if (sendEmailBtn) {
            sendEmailBtn.addEventListener('click', sendEmail);
        }
        
        // Add event listener for Save as MSG button
        const saveMsgBtn = document.getElementById('save-msg-btn');
        if (saveMsgBtn) {
            saveMsgBtn.addEventListener('click', saveMsgFile);
        }
        
        // Success modal
        const successCloseBtn = document.getElementById('success-close-btn');
        if (successCloseBtn) {
            successCloseBtn.addEventListener('click', closeSuccessModal);
        }
        
        // New Project button in success modal
        const newProjectBtn = document.getElementById('choose-new-project-btn');
        if (newProjectBtn) {
            newProjectBtn.addEventListener('click', chooseNewProject);
        }
        
        // Abort button - use existing button from HTML
        const abortBtn = document.getElementById('abort-handoff-btn');
        if (abortBtn) {
            abortBtn.addEventListener('click', abortHandoff);
        }
        
        // Auto-save email form data when typing - only for elements that exist
        if (emailTo) {
            emailTo.addEventListener('input', saveEmailFormData);
        }
        
        if (emailCc) {
            emailCc.addEventListener('input', () => {
                // Mark CC field as user-modified so we don't override their choice
                emailCc.setAttribute('data-user-modified', 'true');
                saveEmailFormData();
            });
        }
        
        if (emailBcc) {
            emailBcc.addEventListener('input', () => {
                // Mark BCC field as user-modified so we don't override their choice
                emailBcc.setAttribute('data-user-modified', 'true');
                saveEmailFormData();
            });
        }
        
        if (emailSubject) {
            emailSubject.addEventListener('input', saveEmailFormData);
        }
    }
    

    
    function abortHandoff() {
        const confirmed = confirm(
            'Are you sure you want to abort the handoff process?\n\n' +
            'This will:\n' +
            '• Clear all progress and saved data\n' +
            '• Return to the project selection screen\n' +
            '• Cancel any unsaved email drafts\n\n' +
            'This action cannot be undone.'
        );
        
        if (confirmed) {
            clearAllState();
            showProjectSelection();
            
            // Show confirmation message
            setTimeout(() => {
                alert('Handoff process aborted. All progress has been cleared.');
            }, 100);
        }
    }
    
    function showSection(sectionToShow) {
        // Save current state before switching
        saveState();
        
        // Hide all sections
        projectSelectionSection.style.display = 'none';
        validationSection.style.display = 'none';
        emailSection.style.display = 'none';
        
        // Show the requested section
        sectionToShow.style.display = 'block';
        
        // Scroll to top
        window.scrollTo(0, 0);
    }
    
    function showProjectSelection() {
        showSection(projectSelectionSection);
        // Don't clear state when going back to project selection
        // selectedProject = null;
        // clearValidationData();
    }
    
    function showValidationSection() {
        showSection(validationSection);
        saveState();
    }
    
    function showEmailSection() {
        showSection(emailSection);
        populateEmailTemplate();
        generateAttachments();
        saveState();
    }
    
    function loadProjects() {
        // Get current status filter
        const statusFilter = document.getElementById('status-filter')?.value || 'ready';
        
        // Load projects from API with status filter
        const url = new URL('/api/handoff/projects/', window.location.origin);
        url.searchParams.append('status', statusFilter);
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Handle different project categories based on API response structure
                    let allProjects = [];
                    
                    // Check if data.projects is an object with categories
                    if (data.projects && typeof data.projects === 'object') {
                        // Handle categorized response (ready, filmed, completed, etc.)
                        if (statusFilter === 'all') {
                            // Combine all categories
                            allProjects = [
                                ...(data.projects.ready || []),
                                ...(data.projects.filmed || []),
                                ...(data.projects.completed || [])
                            ];
                        } else {
                            // Use specific category
                            if (data.projects[statusFilter] && Array.isArray(data.projects[statusFilter])) {
                                allProjects = data.projects[statusFilter];
                            } else {
                                // Fallback: combine ready and filmed for backward compatibility
                                allProjects = [
                                    ...(data.projects.ready || []),
                                    ...(data.projects.filmed || [])
                                ];
                            }
                        }
                    } else if (Array.isArray(data.projects)) {
                        // Handle direct array response
                        allProjects = data.projects;
                    } else {
                        console.warn('Unexpected API response structure:', data);
                        allProjects = [];
                    }
                    
                    console.log(`Loaded ${allProjects.length} projects for filter: ${statusFilter}`);
                    
                    // Store projects for filtering
                    currentProjects = allProjects;
                    
                    // Sort projects by default (film number descending)
                    const sortedProjects = sortProjects(allProjects);
                    
                    renderProjects(sortedProjects);
                } else {
                    console.error('Error loading projects:', data.error);
                    showError('Failed to load projects: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error loading projects:', error);
                showError('Failed to load projects. Please try again.');
            });
    }
    
    function renderProjects(projects) {
        projectCardsContainer.innerHTML = '';
        
        if (projects.length === 0) {
            const searchTerm = projectSearchInput ? projectSearchInput.value : '';
            const statusFilter = document.getElementById('status-filter')?.value || 'ready';
            
            let message = '';
            let subtitle = '';
            
            if (searchTerm) {
                message = 'No Matching Projects';
                subtitle = 'Try adjusting your search criteria or clear the search field.';
            } else {
                switch (statusFilter) {
                    case 'ready':
                        message = 'No Projects Ready for Handoff';
                        subtitle = 'Complete filming, development, and labeling to see projects here.';
                        break;
                    case 'completed':
                        message = 'No Completed Projects';
                        subtitle = 'Completed handoff projects will appear here.';
                        break;
                    case 'all':
                        message = 'No Projects Available';
                        subtitle = 'No projects found in the system.';
                        break;
                    default:
                        message = `No ${statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1)} Projects`;
                        subtitle = `No projects with status "${statusFilter}" found.`;
                }
            }
            
            projectCardsContainer.innerHTML = `
                <div class="no-projects-message">
                    <i class="fas fa-search"></i>
                    <h3>${message}</h3>
                    <p>${subtitle}</p>
                </div>
            `;
            return;
        }
        
        projects.forEach(project => {
            const projectCard = createProjectCard(project);
            projectCardsContainer.appendChild(projectCard);
        });
    }
    
    function createProjectCard(project) {
        const template = document.getElementById('project-card-template');
        const card = template.content.cloneNode(true);
        
        // Set project data
        card.querySelector('.project-card').dataset.projectId = project.id;
        card.querySelector('.project-name').textContent = project.name;
        card.querySelector('.project-status').textContent = project.status_text;
        card.querySelector('.project-status').className = `project-status ${project.status}`;
        card.querySelector('.archive-id').textContent = project.archive_id;
        card.querySelector('.doc-type').textContent = project.doc_type;
        card.querySelector('.roll-count').textContent = `${project.total_rolls} (${project.filmed_rolls}F/${project.developed_rolls}D/${project.labeled_rolls}L)`;
        
        // Add roll range if available
        if (project.roll_range) {
            const rollRangeElem = card.querySelector('.roll-range');
            if (rollRangeElem) {
                rollRangeElem.textContent = project.roll_range;
            } else {
                // If element doesn't exist in template, create it
                const rollInfoDiv = card.querySelector('.project-info');
                if (rollInfoDiv) {
                    const rollRangeDiv = document.createElement('div');
                    rollRangeDiv.className = 'info-item roll-range';
                    rollRangeDiv.innerHTML = `<span class="info-label">Roll Range:</span> <span class="roll-range">${project.roll_range}</span>`;
                    rollInfoDiv.appendChild(rollRangeDiv);
                }
            }
        }
        
        card.querySelector('.completion-date').textContent = project.completion_date ? formatDate(project.completion_date) : 'In Progress';
        
        // Add handoff status badge if available
        if (project.handoff_status) {
            addHandoffStatusBadge(card, project.handoff_status);
        }
        
        // Add handoff history button if project has handoff records
        if (project.has_handoff_records) {
            addHandoffHistoryButton(card, project.id);
        }
        
        // Add click handler
        const selectBtn = card.querySelector('.select-project-btn');
        selectBtn.addEventListener('click', () => selectProject(project));
        
        return card;
    }
    
    function selectProject(project) {
        selectedProject = project;
        
        // Update UI
        selectedProjectName.textContent = project.name;
        selectedProjectId.textContent = project.archive_id;
        
        // Add roll range info to selectedProject if available
        if (project.roll_range) {
            selectedProject.roll_range = project.roll_range;
        }
        
        // Save state immediately
        saveState();
        
        // Load validation data
        loadValidationData(project.id);
        
        // Show validation section
        showValidationSection();
    }
    
    function loadValidationData(projectId) {
        // Load validation data from API
        fetch(`/api/handoff/projects/${projectId}/validation-data/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    validationData = data.validation_data;
                    renderValidationTable();
                } else {
                    console.error('Error loading validation data:', data.error);
                    showError('Failed to load validation data: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error loading validation data:', error);
                showError('Failed to load validation data. Please try again.');
            });
    }
    
    function renderValidationTable() {
        validationTableBody.innerHTML = '';
        
        validationData.forEach(item => {
            const row = createValidationRow(item);
            validationTableBody.appendChild(row);
        });
        
        // Hide summary initially
        validationSummary.style.display = 'none';
    }
    
    function createValidationRow(item) {
        const template = document.getElementById('validation-row-template');
        const row = template.content.cloneNode(true);
        
        // Validate the item data and determine actual status
        const actualStatus = validateItemData(item);
        
        // Set data
        row.querySelector('.validation-row').dataset.documentId = item.document_id;
        row.querySelector('.roll-cell').textContent = item.roll || '-';
        
        // Show full document ID (with suffix like _001 if present)
        const documentIdCell = row.querySelector('.document-id-cell');
        documentIdCell.textContent = item.document_id || '-';
        
        // Show normalized barcode (base barcode without suffix)
        // Strip .pdf and suffix to show clean 16-digit barcode
        let displayBarcode = item.barcode || '-';
        if (displayBarcode !== '-') {
            // Remove .pdf extension (case-insensitive)
            displayBarcode = displayBarcode.replace(/\.pdf$/i, '');
            // Remove suffix like _001, _002, etc.
            displayBarcode = displayBarcode.replace(/_\d{3,}$/, '');
        }
        row.querySelector('.barcode-cell').textContent = displayBarcode;
        
        // Handle COM ID display with validation
        const comIdCell = row.querySelector('.com-id-cell');
        if (!item.com_id || item.com_id === '' || item.com_id === null || item.com_id === undefined) {
            comIdCell.textContent = 'MISSING';
            comIdCell.style.color = '#dc3545';
            comIdCell.style.fontWeight = 'bold';
        } else {
            comIdCell.textContent = item.com_id;
            comIdCell.style.color = '';
            comIdCell.style.fontWeight = '';
        }
        
        row.querySelector('.temp-blip-cell').textContent = item.temp_blip || '-';
        row.querySelector('.film-blip-cell').textContent = item.film_blip || '-';
        
        // Set status based on actual validation
        const statusBadge = row.querySelector('.status-badge');
        const validationIcon = row.querySelector('.validation-icon');
        
        statusBadge.className = `status-badge ${actualStatus}`;
        statusBadge.textContent = actualStatus.charAt(0).toUpperCase() + actualStatus.slice(1);
        
        // Set icon based on actual status
        validationIcon.className = `fas validation-icon ${actualStatus}`;
        if (actualStatus === 'pending') {
            validationIcon.classList.add('fa-clock');
        } else if (actualStatus === 'validated') {
            validationIcon.classList.add('fa-check-circle');
        } else if (actualStatus === 'warning') {
            validationIcon.classList.add('fa-exclamation-triangle');
        } else if (actualStatus === 'error') {
            validationIcon.classList.add('fa-times-circle');
        }
        
        // Add tooltip with validation message if there are issues
        if (actualStatus !== 'validated' && actualStatus !== 'pending') {
            const validationMessage = getValidationMessage(item);
            if (validationMessage) {
                row.querySelector('.validation-row').title = validationMessage;
            }
        }
        
        return row;
    }
    
    function validateItemData(item) {
        const issues = [];
        
        // Check for missing required fields
        if (!item.barcode || item.barcode === '' || item.barcode === null) {
            issues.push('Missing barcode');
        }
        
        if (!item.com_id || item.com_id === '' || item.com_id === null || item.com_id === undefined) {
            issues.push('Missing COM ID');
        }
        
        if (!item.roll || item.roll === '' || item.roll === null) {
            issues.push('Missing roll number');
        }
        
        if (!item.temp_blip || item.temp_blip === '' || item.temp_blip === null) {
            issues.push('Missing temporary blip');
        }
        
        // If there are critical missing fields, mark as error
        if (issues.length > 0) {
            // COM ID missing is always an error
            if (issues.includes('Missing COM ID')) {
                return 'error';
            }
            // Other missing fields are warnings
            return 'warning';
        }
        
        // If all required fields are present, use the original status from validation
        // but ensure it's not 'validated' if film_blip is missing (should be pending)
        if (!item.film_blip || item.film_blip === '' || item.film_blip === null) {
            return item.status === 'validated' ? 'pending' : item.status;
        }
        
        return item.status || 'pending';
    }
    
    function getValidationMessage(item) {
        const issues = [];
        
        if (!item.barcode || item.barcode === '' || item.barcode === null) {
            issues.push('Missing barcode');
        }
        
        if (!item.com_id || item.com_id === '' || item.com_id === null || item.com_id === undefined) {
            issues.push('Missing COM ID - document may not be in COM list');
        }
        
        if (!item.roll || item.roll === '' || item.roll === null) {
            issues.push('Missing roll number');
        }
        
        if (!item.temp_blip || item.temp_blip === '' || item.temp_blip === null) {
            issues.push('Missing temporary blip');
        }
        
        if (!item.film_blip || item.film_blip === '' || item.film_blip === null) {
            issues.push('Film blip not found in log files');
        }
        
        return issues.length > 0 ? issues.join('; ') : '';
    }
    
    function validateProject() {
        if (!selectedProject) return;
        
        showProgress('Validating Project', 'Reading film log files...');
        
        const csrfToken = getCsrfToken();
        console.log('CSRF Token:', csrfToken ? 'Found' : 'Not found');
        
        // Call validation API
        fetch(`/api/handoff/projects/${selectedProject.id}/validate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({})
        })
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            hideProgress();
            console.log('Validation response:', data);
            
            if (data.success) {
                // Update validation data with results
                validationData = data.validated_data;
                validationResults = data.validation_results;
                
                // Re-render table with results (this will apply client-side validation)
                renderValidationTable();
                
                // Show summary with corrected counts
                showValidationSummary(validationResults);
                
                // Save state after successful validation
                saveState();
                
                // Log validation summary for debugging
                const actualSummary = calculateActualValidationSummary();
                console.log('Validation completed:', {
                    serverResults: validationResults,
                    clientValidation: actualSummary
                });
            } else {
                showError('Validation failed: ' + data.error);
            }
        })
        .catch(error => {
            hideProgress();
            console.error('Error during validation:', error);
            showError('Validation failed: ' + error.message);
        });
    }
    
    function getValidationMessage(progress) {
        if (progress <= 20) return 'Reading film log files...';
        if (progress <= 40) return 'Parsing log data...';
        if (progress <= 60) return 'Cross-checking with temporary index...';
        if (progress <= 80) return 'Validating blip sequences...';
        return 'Finalizing validation results...';
    }
    
    function processValidationResults() {
        // Mock validation results
        const results = {
            total: validationData.length,
            validated: 3,
            warnings: 1,
            errors: 0
        };
        
        // Update validation data with results
        validationData[0].status = 'validated';
        validationData[0].film_blip = '10000001-0001.00001';
        
        validationData[1].status = 'validated';
        validationData[1].film_blip = '10000001-0002.00015';
        
        validationData[2].status = 'warning';
        validationData[2].film_blip = '10000002-0001.00002'; // Slight difference
        
        validationData[3].status = 'validated';
        validationData[3].film_blip = '10000002-0002.00012';
        
        validationResults = results;
        
        // Re-render table with results
        renderValidationTable();
        
        // Show summary
        showValidationSummary(results);
    }
    
    function showValidationSummary(results) {
        // Recalculate summary based on actual validation status
        const actualSummary = calculateActualValidationSummary();
        
        document.getElementById('total-documents').textContent = actualSummary.total;
        document.getElementById('validated-documents').textContent = actualSummary.validated;
        document.getElementById('warning-documents').textContent = actualSummary.warnings;
        document.getElementById('error-documents').textContent = actualSummary.errors;
        
        // Enable proceed button if no errors
        const proceedBtn = document.getElementById('proceed-to-email');
        proceedBtn.disabled = actualSummary.errors > 0;
        
        // Show warning message if there are errors
        if (actualSummary.errors > 0) {
            const errorMessage = document.createElement('div');
            errorMessage.className = 'validation-error-message';
            errorMessage.style.cssText = 'margin-top: 10px; padding: 10px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; color: #721c24;';
            errorMessage.innerHTML = `<strong>⚠️ Cannot proceed:</strong> ${actualSummary.errors} document(s) have missing COM IDs or other critical errors. Please resolve these issues before sending the handoff email.`;
            
            // Remove any existing error message
            const existingError = validationSummary.querySelector('.validation-error-message');
            if (existingError) {
                existingError.remove();
            }
            
            validationSummary.appendChild(errorMessage);
        } else {
            // Remove error message if no errors
            const existingError = validationSummary.querySelector('.validation-error-message');
            if (existingError) {
                existingError.remove();
            }
        }
        
        validationSummary.style.display = 'block';
    }
    
    function calculateActualValidationSummary() {
        const summary = {
            total: validationData.length,
            validated: 0,
            warnings: 0,
            errors: 0,
            pending: 0
        };
        
        validationData.forEach(item => {
            const actualStatus = validateItemData(item);
            switch (actualStatus) {
                case 'validated':
                    summary.validated++;
                    break;
                case 'warning':
                    summary.warnings++;
                    break;
                case 'error':
                    summary.errors++;
                    break;
                case 'pending':
                    summary.pending++;
                    break;
            }
        });
        
        return summary;
    }
    
    function populateEmailTemplate() {
        if (!selectedProject || !validationResults) return;
        
        // Only set default recipients if fields are completely empty (first time setup)
        if (!emailTo.value) {
            emailTo.value = 'dilek.kursun@rolls-royce.com';
        }
        
        if (!emailCc.value && !emailCc.hasAttribute('data-user-modified')) {
            emailCc.value = 'jan.becker@rolls-royce.com; thomas.lux@rolls-royce.com';
        }
        
        if (!emailBcc.value && !emailBcc.hasAttribute('data-user-modified')) {
            emailBcc.value = 'michael.wuske@rolls-royce.com; tetiana.isakii@rolls-royce.com; shmaila.aslam@rolls-royce.com';
        }
        
        // Update subject with archive ID and date
        const today = new Date();
        const day = String(today.getDate()).padStart(2, '0');
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const year = today.getFullYear();
        const dateStr = `${day}.${month}.${year}`;
        emailSubject.value = `MIKROVERFILMUNG: BLIPS für ${selectedProject.archive_id} am ${dateStr}`;
        
        // Populate form fields with project data
        if (emailArchiveId) {
            emailArchiveId.value = selectedProject.archive_id || '';
        }
        
        // Get film numbers from validation results
        const filmNumbers = getFilmNumbersFromValidation();
        console.log('Debug - validationData:', validationData);
        console.log('Debug - extracted filmNumbers:', filmNumbers);
        if (emailFilmNumbers) {
            emailFilmNumbers.value = filmNumbers;
        }
        
        // Update preview immediately to show the populated data
        updateEmailPreview();
        
        console.log('Email template populated with form fields');
    }

    function getFilmNumbersFromValidation() {
        // Use validationData instead of validationResults.validated_data
        if (!validationData || validationData.length === 0) return '';
        
        // Extract unique roll/film numbers from validation data
        const filmNumbers = new Set();
        
        validationData.forEach(item => {
            if (item.roll && (item.status === 'validated' || item.status === 'warning')) {
                filmNumbers.add(item.roll);
            }
        });
        
        // Convert Set to sorted array and join
        const sortedFilmNumbers = Array.from(filmNumbers).sort();
        return sortedFilmNumbers.join(', ');
    }

    function updateEmailPreview() {
        if (!emailPreview) return;
        
        const archiveId = emailArchiveId ? emailArchiveId.value : selectedProject?.archive_id || 'XXX';
        let filmNumbers = emailFilmNumbers ? emailFilmNumbers.value : '';
        
        // If film numbers field is empty, try to get them from validation results
        if (!filmNumbers && validationData) {
            filmNumbers = getFilmNumbersFromValidation();
        }
        
        // If still empty, show placeholder
        if (!filmNumbers) {
            filmNumbers = 'YYY';
        }
        
        const customMessage = emailCustomMessage ? emailCustomMessage.value : '';
        
        // Generate timestamp for preview
        const now = new Date();
        const timestamp = now.toLocaleDateString('de-DE').replace(/\./g, '') + 
                         now.toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit'}).replace(':', '');
        
        // Create preview content
        const previewContent = `
            <div class="email-preview-content">
                <h4>Email Preview:</h4>
                <div class="preview-section">
                    <strong>To:</strong> ${emailTo ? emailTo.value : ''}<br>
                    <strong>CC:</strong> ${emailCc ? emailCc.value : ''}<br>
                    <strong>BCC:</strong> ${emailBcc ? emailBcc.value : ''}<br>
                    <strong>Subject:</strong> ${emailSubject ? emailSubject.value : ''}
                </div>
                
                ${customMessage ? `
                <div class="preview-section">
                    <strong>Custom Message:</strong><br>
                    <div class="custom-message-preview">${customMessage.replace(/\n/g, '<br>')}</div>
                </div>
                ` : ''}
                
                <div class="preview-section signature-preview">
                    <strong>Signature will include:</strong><br>
                    • Auftragsnummer: <span class="highlight">${archiveId}</span><br>
                    • Filmnummern: <span class="highlight">${filmNumbers}</span><br>
                    • Excel file: <span class="highlight">${archiveId}_blips_${timestamp}.xlsx</span><br>
                    <!-- DAT file generation disabled -->
                </div>
                
                <div class="preview-section">
                    <strong>Attachments:</strong><br>
                    📎 <span class="highlight">${archiveId}_blips_${timestamp}.xlsx</span> (Excel format)<br>
                    <!-- DAT file attachment disabled -->
                </div>
            </div>
        `;
        
        emailPreview.innerHTML = previewContent;
    }
    
    function loadEmailTemplate() {
        // This function is now simplified since we use Outlook's signature
        editorStatus.textContent = 'Email ready - Outlook will add signature automatically when sending';
        
        // Show info about the new approach
        const noteDiv = document.createElement('div');
        noteDiv.style.cssText = 'margin-top: 10px; padding: 10px; background-color: #e7f3ff; border-left: 4px solid #2196F3; font-size: 12px; color: #1976D2;';
        noteDiv.innerHTML = '<strong>Note:</strong> Your Outlook signature will be automatically added when the email is sent. The signature will include project-specific information (Archive ID, Film Numbers, etc.).';
        noteDiv.className = 'template-note';
        
        // Remove any existing note
        const existingNote = document.querySelector('.template-note');
        if (existingNote) {
            existingNote.remove();
        }
        
        // Add the note after the email editor container
        const emailField = document.querySelector('.email-field');
        emailField.appendChild(noteDiv);
    }
    
    function loadOriginalTemplate() {
        // Remove this functionality since we're using Outlook signatures
        editorStatus.textContent = 'Using Outlook signature system - no template loading needed';
        
        // Show info message
        alert('Template loading is no longer needed. Your Outlook signature will be automatically used with project-specific information when sending emails.');
    }
    
    function generateAttachments() {
        if (!selectedProject) return;
        
        // Generate timestamp for filenames
        const now = new Date();
        const timestamp = now.toLocaleDateString('de-DE').replace(/\./g, '') + 
                         now.toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit'}).replace(':', '');
        
        const archiveId = selectedProject.archive_id || 'PROJECT';
        
        const attachments = [
            { 
                name: `${archiveId}_blips_${timestamp}.xlsx`, 
                size: '~25 KB', 
                type: 'excel',
                description: 'Excel format index file'
            }
            // DAT file attachment disabled
            // { 
            //     name: `${archiveId}_scan_${timestamp}.dat`, 
            //     size: '~18 KB', 
            //     type: 'text',
            //     description: 'Legacy format index file'
            // }
        ];
        
        attachmentList.innerHTML = '';
        
        attachments.forEach(attachment => {
            const item = createAttachmentItem(attachment);
            attachmentList.appendChild(item);
        });
    }
    
    function createAttachmentItem(attachment) {
        const template = document.getElementById('attachment-template');
        const item = template.content.cloneNode(true);
        
        item.querySelector('.attachment-name').textContent = attachment.name;
        item.querySelector('.attachment-size').textContent = attachment.size;
        
        // Set icon based on type
        const icon = item.querySelector('i');
        icon.className = attachment.type === 'excel' ? 'fas fa-file-excel' : 'fas fa-file-alt';
        
        // Add remove handler
        item.querySelector('.remove-attachment-btn').addEventListener('click', (e) => {
            e.target.closest('.attachment-item').remove();
        });
        
        return item;
    }
    
    function addRecipient() {
        const newRecipient = prompt('Enter email address:');
        if (newRecipient && isValidEmail(newRecipient)) {
            const currentValue = emailTo.value;
            emailTo.value = currentValue ? `${currentValue}, ${newRecipient}` : newRecipient;
        }
    }
    
    function clearCcRecipients() {
        const confirmed = confirm('Are you sure you want to clear all CC recipients?\n\nThe email will be sent without any CC recipients.');
        if (confirmed) {
            emailCc.value = '';
            emailCc.setAttribute('data-user-modified', 'true');
            saveEmailFormData();
            
            // Show confirmation
            setTimeout(() => {
                alert('CC recipients cleared. Email will be sent without CC recipients.');
            }, 100);
        }
    }
    
    function clearBccRecipients() {
        const confirmed = confirm('Are you sure you want to clear all BCC recipients?\n\nThe email will be sent without any BCC recipients.');
        if (confirmed) {
            emailBcc.value = '';
            emailBcc.setAttribute('data-user-modified', 'true');
            saveEmailFormData();
            
            // Show confirmation
            setTimeout(() => {
                alert('BCC recipients cleared. Email will be sent without BCC recipients.');
            }, 100);
        }
    }
    
    function previewEmail() {
        const emailData = {
            to: emailTo.value,
            cc: emailCc.value,
            subject: emailSubject.value,
            body: emailBody.value,
            attachments: Array.from(attachmentList.children).map(item => 
                item.querySelector('.attachment-name').textContent
            )
        };
        
        // Show preview modal (simplified for now)
        alert(`Email Preview:\n\nTo: ${emailData.to}\nSubject: ${emailData.subject}\n\nAttachments: ${emailData.attachments.join(', ')}`);
    }
    
    function sendEmail() {
        processEmailAction('send');
    }
    
    function saveMsgFile() {
        processEmailAction('save');
    }
    
    function processEmailAction(action) {
        if (!selectedProject || !validationResults) {
            showNotification('Please select a project and validate files first', 'error');
            return;
        }

        // Check for validation errors (missing COM IDs, etc.)
        const actualSummary = calculateActualValidationSummary();
        if (actualSummary.errors > 0) {
            showNotification(`Cannot ${action} email: ${actualSummary.errors} document(s) have missing COM IDs or other critical errors. Please resolve these issues first.`, 'error');
            return;
        }

        // Validate required fields
        if (!emailTo.value.trim()) {
            showNotification('Please enter recipient email address', 'error');
            return;
        }

        if (!emailSubject.value.trim()) {
            showNotification('Please enter email subject', 'error');
            return;
        }

        // Prepare email data with form fields AND validation data
        const emailData = {
            to: emailTo.value.trim(),
            cc: emailCc.value.trim(),
            bcc: emailBcc.value.trim(),
            subject: emailSubject.value.trim(),
            archive_id: emailArchiveId ? emailArchiveId.value.trim() : selectedProject.archive_id,
            film_numbers: emailFilmNumbers ? emailFilmNumbers.value.trim() : '',
            custom_message: emailCustomMessage ? emailCustomMessage.value.trim() : '',
            use_form_data: true,  // Flag to indicate we're using form data instead of HTML body
            action: action,  // 'send' or 'save'
            validated_data: validationData  // Include validation data with film_blip info
        };

        // Show loading state for the appropriate button
        const currentBtn = action === 'send' ? sendEmailBtn : document.getElementById('save-msg-btn');
        const originalText = action === 'send' ? 'Send Email' : 'Save as MSG';
        const loadingText = action === 'send' ? 'Sending...' : 'Saving...';
        
        if (currentBtn) {
            currentBtn.disabled = true;
            currentBtn.textContent = loadingText;
        }

        // Send request
        fetch(`/api/handoff/projects/${selectedProject.id}/send-email/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(emailData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success notification based on method
                const method = data.method || 'displayed';
                if (method === 'sent') {
                    showNotification('Email sent successfully!', 'success');
                } else if (method === 'saved_msg') {
                    showNotification(`Email saved as MSG file: ${data.msg_filename}`, 'success');
                    
                    // Trigger browser download for MSG files
                    if (data.msg_filename) {
                        triggerFileDownload(data.msg_filename);
                    }
                } else {
                    showNotification('Email opened in Outlook. Please review and send manually.', 'success');
                }
                console.log('Email processed:', data);
                
                // Show email success dialog with data
                showEmailSuccess(data);
            } else {
                showNotification(`Failed to ${action} email: ${data.error}`, 'error');
                console.error('Email process error:', data);
            }
        })
        .catch(error => {
            showNotification(`Error ${action === 'send' ? 'sending' : 'saving'} email`, 'error');
            console.error('Email process error:', error);
        })
        .finally(() => {
            // Reset button state
            if (currentBtn) {
                currentBtn.disabled = false;
                currentBtn.textContent = originalText;
            }
        });
    }
    
    function getEmailMessage(progress) {
        if (progress <= 25) return 'Generating index files...';
        if (progress <= 50) return 'Preparing email attachments...';
        if (progress <= 75) return 'Connecting to Outlook...';
        return 'Sending email...';
    }
    
    function showHandoffHistory(projectId) {
        // Load handoff history for the project
        fetch(`/api/handoff/projects/${projectId}/history/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayHandoffHistoryModal(data.handoff_records);
                } else {
                    showNotification('Failed to load handoff history: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error loading handoff history:', error);
                showNotification('Failed to load handoff history', 'error');
            });
    }
    
    function displayHandoffHistoryModal(handoffRecords) {
        // Create modal content for handoff history
        let historyContent = '<div class="handoff-history-list">';
        
        if (handoffRecords.length === 0) {
            historyContent += '<p class="no-history">No handoff records found for this project.</p>';
        } else {
            handoffRecords.forEach(record => {
                const statusClass = record.status.toLowerCase();
                const statusIcon = getHandoffStatusIcon(record.status);
                
                historyContent += `
                    <div class="handoff-record ${statusClass}">
                        <div class="record-header">
                            <span class="handoff-id">${record.handoff_id}</span>
                            <span class="handoff-status">
                                <i class="${statusIcon}"></i>
                                ${record.status.charAt(0).toUpperCase() + record.status.slice(1)}
                            </span>
                        </div>
                        <div class="record-details">
                            <div class="detail-row">
                                <strong>Recipient:</strong> ${record.recipient_email}
                                ${record.recipient_name ? ` (${record.recipient_name})` : ''}
                            </div>
                            <div class="detail-row">
                                <strong>Subject:</strong> ${record.subject}
                            </div>
                            <div class="detail-row">
                                <strong>Created:</strong> ${formatDateTime(record.created_at)}
                            </div>
                            ${record.sent_at ? `
                                <div class="detail-row">
                                    <strong>Sent:</strong> ${formatDateTime(record.sent_at)}
                                </div>
                            ` : ''}
                            ${record.validation_summary ? `
                                <div class="detail-row">
                                    <strong>Validation:</strong> ${record.validation_summary}
                                </div>
                            ` : ''}
                            ${record.film_numbers ? `
                                <div class="detail-row">
                                    <strong>Film Numbers:</strong> ${record.film_numbers}
                                </div>
                            ` : ''}
                            ${record.total_file_size_mb ? `
                                <div class="detail-row">
                                    <strong>Attachments:</strong> ${record.total_file_size_mb} MB
                                </div>
                            ` : ''}
                            ${record.error_message ? `
                                <div class="detail-row error-message">
                                    <strong>Error:</strong> ${record.error_message}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
        }
        
        historyContent += '</div>';
        
        // Show modal with history content
        showModal('Handoff History', historyContent);
    }
    
    function getHandoffStatusIcon(status) {
        switch (status) {
            case 'sent': return 'fas fa-check-circle';
            case 'pending': return 'fas fa-clock';
            case 'failed': return 'fas fa-exclamation-triangle';
            case 'acknowledged': return 'fas fa-thumbs-up';
            case 'completed': return 'fas fa-flag-checkered';
            default: return 'fas fa-info-circle';
        }
    }
    
    function formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    function showModal(title, content) {
        // Create a simple modal for displaying content
        const modal = document.createElement('div');
        modal.className = 'custom-modal';
        modal.innerHTML = `
            <div class="modal-backdrop">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${title}</h3>
                        <button class="close-modal" onclick="this.closest('.custom-modal').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close modal when clicking backdrop
        modal.querySelector('.modal-backdrop').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                modal.remove();
            }
        });
    }
    
    function showEmailSuccess(data) {
        // Populate modal with success data
        if (data && data.recipients) {
            document.getElementById('success-to-recipients').textContent = data.recipients.to || 'N/A';
            
            const ccSection = document.getElementById('success-cc-section');
            if (data.recipients.cc) {
                document.getElementById('success-cc-recipients').textContent = data.recipients.cc;
                ccSection.style.display = 'block';
            } else {
                ccSection.style.display = 'none';
            }
        }
        
        // Populate attachments
        const attachmentList = document.getElementById('success-attachment-list');
        attachmentList.innerHTML = '';
        
        if (data && data.attachments && data.attachments.length > 0) {
            data.attachments.forEach(attachment => {
                const tag = document.createElement('div');
                tag.className = 'attachment-tag';
                
                // Determine icon based on file extension
                const extension = attachment.split('.').pop().toLowerCase();
                let icon = 'fas fa-file';
                if (extension === 'xlsx' || extension === 'xls' || extension === 'xlsm') {
                    icon = 'fas fa-file-excel';
                } else if (extension === 'dat' || extension === 'txt') {
                    icon = 'fas fa-file-alt';  // Keep for legacy support but DAT files are disabled
                }
                
                tag.innerHTML = `<i class="${icon}"></i> ${attachment}`;
                attachmentList.appendChild(tag);
            });
            document.getElementById('success-attachments-section').style.display = 'block';
        } else {
            document.getElementById('success-attachments-section').style.display = 'none';
        }
        
        // Populate project details
        if (selectedProject) {
            document.getElementById('success-project-name').textContent = selectedProject.name || 'N/A';
            document.getElementById('success-archive-id').textContent = selectedProject.archive_id || 'N/A';
        }
        
        // Format and display sent time
        const sentTime = data && data.sent_at ? new Date(data.sent_at).toLocaleString() : new Date().toLocaleString();
        document.getElementById('success-sent-time').textContent = sentTime;
        
        // Display handoff ID if available
        if (data && data.handoff_id) {
            const handoffIdElement = document.getElementById('success-handoff-id');
            if (handoffIdElement) {
                handoffIdElement.textContent = data.handoff_id;
                handoffIdElement.parentElement.style.display = 'block';
            } else {
                // Create handoff ID display if element doesn't exist
                const projectDetails = document.querySelector('.success-project-details');
                if (projectDetails) {
                    const handoffIdDiv = document.createElement('div');
                    handoffIdDiv.className = 'detail-row';
                    handoffIdDiv.innerHTML = `<strong>Handoff ID:</strong> <span id="success-handoff-id">${data.handoff_id}</span>`;
                    projectDetails.appendChild(handoffIdDiv);
                }
            }
        }
        
        // Update success message based on email method
        const successMessage = document.getElementById('success-message');
        if (successMessage) {
            const method = data && data.method || 'displayed';
            if (method === 'sent') {
                successMessage.textContent = 'Email sent successfully!';
            } else if (method === 'saved_msg') {
                successMessage.textContent = `Email saved as MSG file: ${data.msg_filename || 'handoff.msg'}`;
            } else {
                successMessage.textContent = 'Email opened in Outlook for manual sending.';
            }
        }
        
        // Ensure the New Project button exists
        const modalFooter = document.querySelector('.modal-footer');
        if (modalFooter) {
            // Check if button already exists
            let newProjectBtn = document.getElementById('choose-new-project-btn');
            if (!newProjectBtn) {
                // Create new button if it doesn't exist
                newProjectBtn = document.createElement('button');
                newProjectBtn.id = 'choose-new-project-btn';
                newProjectBtn.className = 'btn btn-primary';
                newProjectBtn.innerHTML = '<i class="fas fa-folder-plus"></i> Choose New Project';
                newProjectBtn.addEventListener('click', chooseNewProject);
                
                // Insert before the close button
                const closeBtn = document.getElementById('success-close-btn');
                if (closeBtn) {
                    modalFooter.insertBefore(newProjectBtn, closeBtn);
                } else {
                    modalFooter.appendChild(newProjectBtn);
                }
            }
        }
        
        // Show the modal
        successModal.style.display = 'flex';
        
        // Add a subtle celebration effect
        setTimeout(() => {
            const icon = document.querySelector('.success-icon');
            if (icon) {
                icon.style.animation = 'none';
                setTimeout(() => {
                    icon.style.animation = 'successIconBounce 0.6s ease-out';
                }, 10);
            }
        }, 100);
    }
    
    function closeSuccessModal() {
        successModal.style.display = 'none';
        
        // Clear all state since handoff is complete
        clearAllState();
        
        // Reset form and variables
        selectedProject = null;
        validationData = [];
        validationResults = null;
        
        // Clear validation table and summary
        clearValidationData();
        
        // Reset email form
        resetEmailForm();
        
        // Return to project selection
        showProjectSelection();
        loadProjects();  // Add this line to reload projects, similar to chooseNewProject function
        
        console.log('Handoff completed successfully - state cleared');
    }
    
    function chooseNewProject() {
        // Close the modal
        successModal.style.display = 'none';
        
        // Clear all state since handoff is complete
        clearAllState();
        
        // Reset form and variables
        selectedProject = null;
        validationData = [];
        validationResults = null;
        
        // Clear validation table and summary
        clearValidationData();
        
        // Reset email form
        resetEmailForm();
        
        // Return to project selection and refresh the list
        showProjectSelection();
        loadProjects();  // Reload projects to get fresh data
        
        console.log('Handoff completed - starting new project selection');
    }
    
    function resetEmailForm() {
        // Reset form fields using the correct IDs from the HTML template
        if (emailTo) {
            emailTo.value = 'dilek.kursun@rolls-royce.com';
        }
        
        if (emailCc) {
            emailCc.value = 'jan.becker@rolls-royce.com; thomas.lux@rolls-royce.com';
        }
        
        if (emailBcc) {
            emailBcc.value = 'michael.wuske@rolls-royce.com; tetiana.isakii@rolls-royce.com; shmaila.aslam@rolls-royce.com';
        }
        
        if (emailSubject) {
            emailSubject.value = 'Microfilm Project Handoff - [Archive ID]';
        }
        
        // Reset signature form fields
        if (emailArchiveId) {
            emailArchiveId.value = '';
        }
        
        if (emailFilmNumbers) {
            emailFilmNumbers.value = '';
        }
        
        if (emailCustomMessage) {
            emailCustomMessage.value = '';
        }
        
        // Clear user-modified flags
        if (emailCc) {
            emailCc.removeAttribute('data-user-modified');
        }
        
        if (emailBcc) {
            emailBcc.removeAttribute('data-user-modified');
        }
        
        // Clear TinyMCE content if available
        if (tinyMceEditor) {
            try {
                tinyMceEditor.setContent('');
            } catch (error) {
                console.warn('Error clearing TinyMCE content:', error);
            }
        }
        
        // Clear email preview
        if (emailPreview) {
            emailPreview.innerHTML = '<p class="preview-placeholder">Fill in the form fields above to see a preview of your email</p>';
        }
        
        // Clear editor status if it exists
        const editorStatus = document.getElementById('editor-status');
        if (editorStatus) {
            editorStatus.textContent = 'Editor ready';
        }
    }
    
    function validateEmailForm() {
        if (!emailTo.value.trim()) {
            alert('Please enter at least one recipient email address.');
            return false;
        }
        
        if (!emailSubject.value.trim()) {
            alert('Please enter an email subject.');
            return false;
        }
        
        // Check for email content from editor
        let hasContent = false;
        if (tinyMceEditor) {
            try {
                const editorText = tinyMceEditor.getContent();
                hasContent = editorText.length > 0 && editorText !== 'Loading email template...';
            } catch (error) {
                console.warn('Error getting TinyMCE content:', error);
                hasContent = emailBody.value && emailBody.value.trim();
            }
        } else {
            // Check fallback editor
            const fallbackEditor = document.getElementById('email-editor');
            if (fallbackEditor) {
                hasContent = fallbackEditor.value && fallbackEditor.value.trim() && fallbackEditor.value !== 'Loading email template...';
            } else {
                hasContent = emailBody.value && emailBody.value.trim();
            }
        }
        
        if (!hasContent) {
            alert('Please wait for the email template to load, or enter email content.');
            return false;
        }
        
        return true;
    }
    
    function sortProjects(projects) {
        const sortOption = document.getElementById('sort-projects').value;
        
        return [...projects].sort((a, b) => {
            switch (sortOption) {
                case 'film_number_desc':
                    // Extract first film number from roll_range
                    const getFirstFilm = project => {
                        if (!project.roll_range) return '';
                        return project.roll_range.split(' - ')[0] || '';
                    };
                    return getFirstFilm(b).localeCompare(getFirstFilm(a));
                
                case 'film_number_asc':
                    const getFirstFilmAsc = project => {
                        if (!project.roll_range) return '';
                        return project.roll_range.split(' - ')[0] || '';
                    };
                    return getFirstFilmAsc(a).localeCompare(getFirstFilmAsc(b));
                
                case 'archive_id_asc':
                    return a.archive_id.localeCompare(b.archive_id);
                    
                case 'archive_id_desc':
                    return b.archive_id.localeCompare(a.archive_id);
                    
                case 'doc_type_asc':
                    return a.doc_type.localeCompare(b.doc_type);
                    
                case 'doc_type_desc':
                    return b.doc_type.localeCompare(a.doc_type);
                    
                case 'date_desc':
                    const dateB = b.completion_date || b.created_at || '';
                    const dateA = a.completion_date || a.created_at || '';
                    return dateB.localeCompare(dateA);
                    
                case 'date_asc':
                    const dateAsc1 = a.completion_date || a.created_at || '';
                    const dateAsc2 = b.completion_date || b.created_at || '';
                    return dateAsc1.localeCompare(dateAsc2);
                    
                default:
                    return 0;
            }
        });
    }
    
    // Store the current loaded projects for filtering
    let currentProjects = [];
    
    function filterProjects() {
        const searchTerm = projectSearchInput.value.toLowerCase();
        
        // Filter projects based on search term only (status filter is handled by loadProjects)
        const filteredProjects = currentProjects.filter(project => {
            const matchesSearch = 
                project.name.toLowerCase().includes(searchTerm) || 
                project.archive_id.toLowerCase().includes(searchTerm) ||
                project.doc_type.toLowerCase().includes(searchTerm);
            
            return matchesSearch;
        });
        
        console.log(`Filtered ${filteredProjects.length} projects from ${currentProjects.length} total`);
        
        // Sort the filtered projects
        const sortedProjects = sortProjects(filteredProjects);
        
        // Re-render only the filtered and sorted projects
        renderProjects(sortedProjects);
    }
    

    
    function clearValidationData() {
        validationData = [];
        validationResults = null;
        validationTableBody.innerHTML = '';
        validationSummary.style.display = 'none';
    }
    
    function showProgress(title, message) {
        progressTitle.textContent = title;
        progressMessage.textContent = message;
        progressFill.style.width = '0%';
        progressModal.style.display = 'flex';
    }
    
    function updateProgress(percent, message) {
        progressFill.style.width = `${percent}%`;
        progressMessage.textContent = message;
    }
    
    function hideProgress() {
        progressModal.style.display = 'none';
    }
    
    function addHandoffStatusBadge(card, handoffStatus) {
        // Create handoff status badge
        const statusBadge = document.createElement('div');
        statusBadge.className = `handoff-status-badge ${handoffStatus.status}`;
        
        // Set badge content based on status
        let badgeContent = '';
        let badgeIcon = '';
        
        switch (handoffStatus.status) {
            case 'sent':
                badgeIcon = 'fas fa-check-circle';
                badgeContent = `Sent ${formatDate(handoffStatus.sent_at)}`;
                break;
            case 'pending':
                badgeIcon = 'fas fa-clock';
                badgeContent = 'Handoff Pending';
                break;
            case 'failed':
                badgeIcon = 'fas fa-exclamation-triangle';
                badgeContent = 'Send Failed';
                break;
            case 'acknowledged':
                badgeIcon = 'fas fa-thumbs-up';
                badgeContent = `Acknowledged ${formatDate(handoffStatus.acknowledged_at)}`;
                break;
            case 'completed':
                badgeIcon = 'fas fa-flag-checkered';
                badgeContent = `Completed ${formatDate(handoffStatus.completed_at)}`;
                break;
            default:
                badgeIcon = 'fas fa-info-circle';
                badgeContent = handoffStatus.status;
        }
        
        statusBadge.innerHTML = `
            <i class="${badgeIcon}"></i>
            <span>${badgeContent}</span>
        `;
        
        // Add tooltip with more details
        if (handoffStatus.recipient_email) {
            statusBadge.title = `Sent to: ${handoffStatus.recipient_email}`;
            if (handoffStatus.handoff_id) {
                statusBadge.title += `\nHandoff ID: ${handoffStatus.handoff_id}`;
            }
            if (handoffStatus.validation_summary) {
                statusBadge.title += `\nValidation: ${handoffStatus.validation_summary}`;
            }
        }
        
        // Find the project info section and add the badge
        const projectInfo = card.querySelector('.project-info');
        if (projectInfo) {
            const badgeContainer = document.createElement('div');
            badgeContainer.className = 'handoff-status-container';
            badgeContainer.appendChild(statusBadge);
            projectInfo.appendChild(badgeContainer);
        }
    }
    
    function addHandoffHistoryButton(card, projectId) {
        // Create handoff history button
        const historyBtn = document.createElement('button');
        historyBtn.className = 'handoff-history-btn';
        historyBtn.innerHTML = '<i class="fas fa-history"></i> View Handoff History';
        historyBtn.title = 'View all handoff records for this project';
        
        // Add click handler
        historyBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent card selection
            showHandoffHistory(projectId);
        });
        
        // Find the project actions section or create one
        let actionsSection = card.querySelector('.project-actions');
        if (!actionsSection) {
            actionsSection = document.createElement('div');
            actionsSection.className = 'project-actions';
            
            // Insert before the select button
            const selectBtn = card.querySelector('.select-project-btn');
            if (selectBtn && selectBtn.parentNode) {
                selectBtn.parentNode.insertBefore(actionsSection, selectBtn);
            } else {
                card.appendChild(actionsSection);
            }
        }
        
        actionsSection.appendChild(historyBtn);
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
    
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    function showError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button class="close-notification" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
        
        console.error('Error:', message);
    }

    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        // Set icon based on type
        let icon = 'fas fa-info-circle';
        if (type === 'success') icon = 'fas fa-check-circle';
        else if (type === 'error') icon = 'fas fa-exclamation-triangle';
        else if (type === 'warning') icon = 'fas fa-exclamation-circle';
        
        notification.innerHTML = `
            <div class="notification-content">
                <i class="${icon}"></i>
                <span>${message}</span>
                <button class="close-notification" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 4 seconds (success) or 6 seconds (error)
        const timeout = type === 'success' ? 4000 : 6000;
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, timeout);
        
        console.log(`${type.toUpperCase()}: ${message}`);
    }
    
    function getCsrfToken() {
        // Get CSRF token from cookie or meta tag
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) {
            return token.value;
        }
        
        // Try to get from meta tag
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }
        
        // Fallback: get from cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        console.warn('CSRF token not found');
        return '';
    }
    
    function triggerFileDownload(filename) {
        /**
         * Trigger browser download for a handoff file.
         * Creates a temporary link and clicks it to start the download.
         */
        if (!selectedProject || !filename) {
            console.error('Cannot trigger download: missing project or filename');
            return;
        }
        
        try {
            // Construct download URL
            const downloadUrl = `/api/handoff/projects/${selectedProject.id}/download/${encodeURIComponent(filename)}/`;
            
            // Create temporary link element
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = filename; // Suggest filename for download
            link.style.display = 'none';
            
            // Add to DOM, click, and remove
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            console.log(`Triggered download for: ${filename}`);
            
            // Show additional notification about download
            setTimeout(() => {
                showNotification(`Download started: ${filename}`, 'info');
            }, 500);
            
        } catch (error) {
            console.error('Error triggering file download:', error);
            showNotification('Failed to start download. File saved to project directory.', 'warning');
        }
    }
    
    // Expose functions for debugging
    window.handoffDebug = {
        selectProject: (id) => {
            const project = { id, name: 'Debug Project', archive_id: 'DEBUG-001' };
            selectProject(project);
        },
        showValidation: () => showValidationSection(),
        showEmail: () => showEmailSection(),
        validateProject: validateProject,
        testEndpoint: () => {
            fetch('/api/handoff/test/')
                .then(response => response.json())
                .then(data => console.log('Test endpoint response:', data))
                .catch(error => console.error('Test endpoint error:', error));
        },
        testValidateEndpoint: (projectId = 1) => {
            const csrfToken = getCsrfToken();
            fetch(`/api/handoff/projects/${projectId}/validate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({})
            })
            .then(response => {
                console.log('Validate test - Status:', response.status);
                return response.text();
            })
            .then(text => {
                console.log('Validate test - Response:', text);
                try {
                    const data = JSON.parse(text);
                    console.log('Validate test - Parsed:', data);
                } catch (e) {
                    console.log('Validate test - Not JSON:', e);
                }
            })
            .catch(error => console.error('Validate test error:', error));
        }
    };
    
    function initializeEmailEditor() {
        try {
            // Wait for TinyMCE to be loaded
            if (typeof tinymce === 'undefined') {
                console.error('TinyMCE not loaded');
                editorStatus.textContent = 'Editor failed to load';
                return;
            }
            
            // Initialize TinyMCE editor with Outlook-like toolbar and Roboto font
            tinymce.init({
                selector: '#email-editor',
                height: 400,
                menubar: false,
                plugins: [
                    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                    'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                    'insertdatetime', 'media', 'table', 'help', 'wordcount'
                ],
                toolbar: 'undo redo | formatselect fontselect fontsizeselect | bold italic underline strikethrough | ' +
                        'forecolor backcolor | alignleft aligncenter alignright alignjustify | ' +
                        'bullist numlist outdent indent | removeformat | link | help',
                font_formats: 'Roboto=Roboto,sans-serif;Arial=arial,helvetica,sans-serif;Calibri=calibri,sans-serif;Times New Roman=times new roman,times,serif;Verdana=verdana,geneva,sans-serif',
                fontsize_formats: '8pt 9pt 10pt 11pt 12pt 14pt 16pt 18pt 20pt 24pt 36pt',
                content_style: `
                    body { 
                        font-family: 'Roboto', sans-serif !important; 
                        font-size: 10pt !important; 
                        line-height: 1.4 !important; 
                        color: #000 !important; 
                        padding: 20px !important; 
                        margin: 0 !important;
                        background-color: white !important;
                    }
                    * {
                        font-family: 'Roboto', sans-serif !important;
                    }
                    .greeting { 
                        font-weight: bold !important; 
                        color: #1B75BB !important; 
                        margin-bottom: 10px !important; 
                        font-family: 'Roboto', sans-serif !important;
                        font-size: 10pt !important;
                    }
                    .section { 
                        margin: 15px 0 !important; 
                        padding-left: 30px !important; 
                        font-family: 'Roboto', sans-serif !important;
                        font-size: 10pt !important;
                    }
                    .section-header { 
                        font-weight: bold !important; 
                        color: red !important; 
                        margin-bottom: 5px !important; 
                        font-family: 'Roboto', sans-serif !important;
                        font-size: 10pt !important;
                    }
                    .info-header { 
                        font-weight: bold !important; 
                        color: #0070C0 !important; 
                        font-family: 'Roboto', sans-serif !important;
                        font-size: 10pt !important;
                    }
                    .project-info { 
                        margin: 5px 0 !important; 
                        font-family: 'Roboto', sans-serif !important;
                        font-size: 10pt !important;
                    }
                    .signature { 
                        margin-top: 30px !important; 
                        border-top: 1px solid #ccc !important; 
                        padding-top: 15px !important; 
                        font-family: 'Roboto', sans-serif !important;
                        font-size: 10pt !important;
                    }
                    .signature-name { 
                        font-weight: bold !important; 
                        color: #1B75BB !important; 
                        font-family: 'Roboto', sans-serif !important;
                        font-size: 10pt !important;
                    }
                    .company-info { 
                        font-size: 8pt !important; 
                        color: #7F7F7F !important; 
                        margin-top: 10px !important; 
                        line-height: 1.3 !important; 
                        font-family: 'Roboto', sans-serif !important;
                    }
                    .legal-text { 
                        font-size: 8pt !important; 
                        color: #767171 !important; 
                        margin-top: 15px !important; 
                        font-family: 'Arial', sans-serif !important; 
                        line-height: 1.2 !important; 
                    }
                    p, div, span, td, th, h1, h2, h3, h4, h5, h6 {
                        font-family: 'Roboto', sans-serif !important;
                        font-size: 10pt !important;
                    }
                    b, strong {
                        font-family: 'Roboto', sans-serif !important;
                        font-weight: bold !important;
                    }
                    i, em {
                        font-family: 'Roboto', sans-serif !important;
                        font-style: italic !important;
                    }
                `,
                automatic_uploads: false,
                file_picker_types: 'image',
                setup: function (editor) {
                    // Store reference to editor
                    tinyMceEditor = editor;
                    
                    // Update hidden textarea when content changes
                    editor.on('change keyup', function () {
                        try {
                            const content = editor.getContent();
                            emailBody.value = content;
                            emailHtmlContent = content;
                            
                            // Auto-save email form data
                            saveEmailFormData();
                        } catch (error) {
                            console.warn('Error updating email content:', error);
                        }
                    });
                    
                    // Handle editor ready state
                    editor.on('init', function () {
                        editorStatus.textContent = 'Editor ready';
                        console.log('TinyMCE editor initialized successfully');
                        
                        // Set default font to Roboto
                        editor.execCommand('FontName', false, 'Roboto');
                        editor.execCommand('FontSize', false, '10pt');
                    });
                    
                    // Handle editor focus
                    editor.on('focus', function () {
                        editorStatus.textContent = 'Editing...';
                    });
                    
                    // Handle editor blur
                    editor.on('blur', function () {
                        editorStatus.textContent = 'Ready to edit';
                        // Save when user stops editing
                        saveEmailFormData();
                    });
                }
            }).then(function (editors) {
                console.log('TinyMCE editors initialized:', editors.length);
                editorStatus.textContent = 'Editor ready';
            }).catch(function (error) {
                console.error('TinyMCE initialization error:', error);
                editorStatus.textContent = 'Editor initialization failed';
                
                // Fallback to textarea
                const editorContainer = document.getElementById('email-editor');
                if (editorContainer) {
                    editorContainer.style.display = 'block';
                    editorContainer.addEventListener('input', function() {
                        emailBody.value = editorContainer.value;
                        emailHtmlContent = editorContainer.value;
                    });
                }
            });
            
        } catch (error) {
            console.error('Failed to initialize TinyMCE editor:', error);
            editorStatus.textContent = 'Editor initialization failed';
            
            // Fallback to textarea
            const editorContainer = document.getElementById('email-editor');
            if (editorContainer) {
                editorContainer.style.display = 'block';
                editorContainer.addEventListener('input', function() {
                    emailBody.value = editorContainer.value;
                    emailHtmlContent = editorContainer.value;
                });
            }
        }
    }

    // Add event listeners for real-time preview updates
    function setupEmailFormListeners() {
        const formFields = [emailTo, emailCc, emailBcc, emailSubject, emailArchiveId, emailFilmNumbers, emailCustomMessage];
        
        formFields.forEach(field => {
            if (field) {
                field.addEventListener('input', updateEmailPreview);
                field.addEventListener('change', updateEmailPreview);
                
                // Also save form data when fields change
                field.addEventListener('input', saveEmailFormData);
            }
        });

        // Mark CC field as user-modified when changed
        if (emailCc) {
            emailCc.addEventListener('input', () => {
                emailCc.setAttribute('data-user-modified', 'true');
            });
        }

        // Mark BCC field as user-modified when changed
        if (emailBcc) {
            emailBcc.addEventListener('input', () => {
                emailBcc.setAttribute('data-user-modified', 'true');
            });
        }

        // Note: Send button listener is already added in initializeEventHandlers
        // so we don't duplicate it here
    }

    // Initialize the page
    function initializePage() {
        initializeEventHandlers();  // Changed from setupEventListeners
        setupEmailFormListeners();  // Setup form listeners for real-time preview
        loadProjects();
        
        // Remove TinyMCE initialization since we're using form fields now
        console.log('Handoff page initialized with form-based email interface');
    }

    // Call initialization
    initializePage();
});
