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
    const emailSubject = document.getElementById('email-subject');
    const emailBody = document.getElementById('email-body');
    const loadTemplateBtn = document.getElementById('load-template-btn');
    const editorStatus = document.getElementById('editor-status');
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
                to: emailTo.value,
                cc: emailCc.value,
                subject: emailSubject.value,
                body: emailBody.value
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
                emailTo.value = emailFormData.to || 'dilek.kursun@rolls-royce.com';
                emailCc.value = emailFormData.cc || 'thomas.lux@rolls-royce.com, jan.becker@rolls-royce.com';
                emailSubject.value = emailFormData.subject || `Microfilm Project Handoff - ${selectedProject?.archive_id || '[Archive ID]'}`;
                emailBody.value = emailFormData.body || '';
                
                // Restore content in TinyMCE if available
                if (tinyMceEditor && emailFormData.body) {
                    try {
                        tinyMceEditor.setContent(emailFormData.body);
                    } catch (error) {
                        console.warn('Error restoring TinyMCE content:', error);
                    }
                }
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
            loadProjects();
        } else {
            // Still load projects to refresh the list, but don't change current section
            loadProjects();
        }
    }
    
    function hideAllModals() {
        progressModal.style.display = 'none';
        successModal.style.display = 'none';
    }
    
    function initializeEventHandlers() {
        // Navigation buttons
        document.getElementById('back-to-selection').addEventListener('click', () => {
            if (confirm('Are you sure you want to go back? Your validation progress will be saved.')) {
                showProjectSelection();
            }
        });
        document.getElementById('back-to-validation').addEventListener('click', () => {
            if (confirm('Are you sure you want to go back? Your email draft will be saved.')) {
                showValidationSection();
            }
        });
        
        // Project selection
        projectSearchInput.addEventListener('input', filterProjects);
        statusFilter.addEventListener('change', filterProjects);
        
        // Validation
        validateBtn.addEventListener('click', validateProject);
        document.getElementById('proceed-to-email').addEventListener('click', showEmailSection);
        
        // Email
        document.getElementById('add-recipient').addEventListener('click', addRecipient);
        document.getElementById('clear-cc-btn').addEventListener('click', clearCcRecipients);
        document.getElementById('preview-email').addEventListener('click', previewEmail);
        document.getElementById('send-email').addEventListener('click', sendEmail);
        
        // Email editor
        loadTemplateBtn.addEventListener('click', loadEmailTemplate);
        
        // Test original template button
        const testOriginalTemplateBtn = document.getElementById('test-original-template-btn');
        if (testOriginalTemplateBtn) {
            testOriginalTemplateBtn.addEventListener('click', loadOriginalTemplate);
        }
        
        // Success modal
        document.getElementById('success-close-btn').addEventListener('click', closeSuccessModal);
        
        // Add abort button functionality
        addAbortButton();
        
        // Auto-save email form data when typing
        emailTo.addEventListener('input', saveEmailFormData);
        emailCc.addEventListener('input', () => {
            // Mark CC field as user-modified so we don't override their choice
            emailCc.setAttribute('data-user-modified', 'true');
            saveEmailFormData();
        });
        emailSubject.addEventListener('input', saveEmailFormData);
        
        // Initialize rich text editor with a small delay to ensure TinyMCE is loaded
        setTimeout(initializeEmailEditor, 100);
    }
    
    function addAbortButton() {
        // Add abort button to email section
        const emailActions = document.querySelector('.email-actions');
        if (emailActions && !document.getElementById('abort-handoff-btn')) {
            const abortBtn = document.createElement('button');
            abortBtn.id = 'abort-handoff-btn';
            abortBtn.className = 'abort-btn';
            abortBtn.innerHTML = '<i class="fas fa-times"></i> Abort Handoff';
            abortBtn.addEventListener('click', abortHandoff);
            
            // Insert before the send button
            const sendBtn = document.getElementById('send-email');
            emailActions.insertBefore(abortBtn, sendBtn);
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
        // Load projects from API
        fetch('/api/handoff/projects/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Combine ready and filmed projects, prioritizing ready ones
                    const allProjects = [
                        ...data.projects.ready,
                        ...data.projects.filmed
                    ];
                    renderProjects(allProjects);
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
            projectCardsContainer.innerHTML = `
                <div class="no-projects-message">
                    <i class="fas fa-inbox"></i>
                    <h3>No Projects Ready for Handoff</h3>
                    <p>Complete filming, development, and labeling to see projects here.</p>
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
        card.querySelector('.completion-date').textContent = project.completion_date ? formatDate(project.completion_date) : 'In Progress';
        
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
        
        // Set data
        row.querySelector('.validation-row').dataset.documentId = item.document_id;
        row.querySelector('.roll-cell').textContent = item.roll;
        row.querySelector('.barcode-cell').textContent = item.barcode;
        row.querySelector('.com-id-cell').textContent = item.com_id;
        row.querySelector('.temp-blip-cell').textContent = item.temp_blip;
        row.querySelector('.film-blip-cell').textContent = item.film_blip || '-';
        
        // Set status
        const statusBadge = row.querySelector('.status-badge');
        const validationIcon = row.querySelector('.validation-icon');
        
        statusBadge.className = `status-badge ${item.status}`;
        statusBadge.textContent = item.status.charAt(0).toUpperCase() + item.status.slice(1);
        
        // Set icon based on status
        validationIcon.className = `fas validation-icon ${item.status}`;
        if (item.status === 'pending') {
            validationIcon.classList.add('fa-clock');
        } else if (item.status === 'validated') {
            validationIcon.classList.add('fa-check-circle');
        } else if (item.status === 'warning') {
            validationIcon.classList.add('fa-exclamation-triangle');
        } else if (item.status === 'error') {
            validationIcon.classList.add('fa-times-circle');
        }
        
        return row;
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
                
                // Re-render table with results
                renderValidationTable();
                
                // Show summary
                showValidationSummary(validationResults);
                
                // Save state after successful validation
                saveState();
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
        document.getElementById('total-documents').textContent = results.total;
        document.getElementById('validated-documents').textContent = results.validated;
        document.getElementById('warning-documents').textContent = results.warnings;
        document.getElementById('error-documents').textContent = results.errors;
        
        // Enable proceed button if no errors
        const proceedBtn = document.getElementById('proceed-to-email');
        proceedBtn.disabled = results.errors > 0;
        
        validationSummary.style.display = 'block';
    }
    
    function populateEmailTemplate() {
        if (!selectedProject || !validationResults) return;
        
        // Only set default recipients if fields are completely empty (first time setup)
        // Don't override if user has intentionally cleared them
        if (!emailTo.value) {
            emailTo.value = 'dilek.kursun@rolls-royce.com';
        }
        
        // For CC: only set default if it's the first time (empty and no user interaction)
        // If user has cleared it, respect their choice
        if (!emailCc.value && !emailCc.hasAttribute('data-user-modified')) {
            emailCc.value = 'thomas.lux@rolls-royce.com, jan.becker@rolls-royce.com';
        }
        
        // Update subject
        emailSubject.value = emailSubject.value.replace('[Archive ID]', selectedProject.archive_id);
        
        // Load the actual template content
        loadEmailTemplate();
    }
    
    function loadEmailTemplate() {
        // Update status
        editorStatus.textContent = 'Loading template...';
        loadTemplateBtn.disabled = true;
        
        // Show loading in editor
        if (tinyMceEditor) {
            try {
                tinyMceEditor.setContent('Loading email template...');
            } catch (error) {
                console.warn('Error setting TinyMCE content:', error);
            }
        } else {
            // Fallback editor
            const fallbackEditor = document.getElementById('email-editor');
            if (fallbackEditor) {
                fallbackEditor.value = 'Loading email template...';
            }
        }
        
        // Fetch the rendered template
        fetch(`/api/handoff/projects/${selectedProject.id}/preview-email/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Store the HTML content
                emailHtmlContent = data.template_content;
                emailBody.value = emailHtmlContent;
                
                // Set content in editor
                if (tinyMceEditor) {
                    try {
                        tinyMceEditor.setContent(emailHtmlContent);
                    } catch (error) {
                        console.warn('Error setting TinyMCE content:', error);
                        // Try alternative method
                        try {
                            tinyMceEditor.setContent(emailHtmlContent);
                        } catch (error2) {
                            console.warn('Error with alternative TinyMCE method:', error2);
                        }
                    }
                } else {
                    // Fallback editor
                    const fallbackEditor = document.getElementById('email-editor');
                    if (fallbackEditor) {
                        fallbackEditor.value = emailHtmlContent;
                    }
                }
                
                // Update status
                editorStatus.textContent = 'Template loaded - Ready to edit';
                loadTemplateBtn.disabled = false;
                
                // Remove any existing note
                const existingNote = document.querySelector('.template-note');
                if (existingNote) {
                    existingNote.remove();
                }
                
                // Add note about editability
                const noteDiv = document.createElement('div');
                noteDiv.style.cssText = 'margin-top: 10px; padding: 10px; background-color: #e7f3ff; border-left: 4px solid #2196F3; font-size: 12px; color: #1976D2;';
                noteDiv.innerHTML = '<strong>Note:</strong> Edit the email content directly like in Outlook. All formatting and styling is preserved.';
                noteDiv.className = 'template-note';
                
                // Add the note after the email editor container
                const emailField = document.querySelector('.email-field');
                emailField.appendChild(noteDiv);
                
            } else {
                editorStatus.textContent = 'Error loading template';
                loadTemplateBtn.disabled = false;
                
                if (tinyMceEditor) {
                    try {
                        tinyMceEditor.setContent(`Error loading template: ${data.error}`);
                    } catch (error) {
                        console.warn('Error setting TinyMCE error text:', error);
                    }
                } else {
                    const fallbackEditor = document.getElementById('email-editor');
                    if (fallbackEditor) {
                        fallbackEditor.value = `Error loading template: ${data.error}`;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error loading email template:', error);
            editorStatus.textContent = 'Error loading template';
            loadTemplateBtn.disabled = false;
            
            if (tinyMceEditor) {
                try {
                    tinyMceEditor.setContent(`Error loading template: ${error.message}`);
                } catch (tinyMceError) {
                    console.warn('Error setting TinyMCE error text:', tinyMceError);
                }
            } else {
                const fallbackEditor = document.getElementById('email-editor');
                if (fallbackEditor) {
                    fallbackEditor.value = `Error loading template: ${error.message}`;
                }
            }
        });
    }
    
    function loadOriginalTemplate() {
        // Update status
        editorStatus.textContent = 'Loading original template...';
        const testBtn = document.getElementById('test-original-template-btn');
        testBtn.disabled = true;
        
        // Show loading in editor
        if (tinyMceEditor) {
            try {
                tinyMceEditor.setContent('Loading original email template...');
            } catch (error) {
                console.warn('Error setting TinyMCE content:', error);
            }
        } else {
            // Fallback editor
            const fallbackEditor = document.getElementById('email-editor');
            if (fallbackEditor) {
                fallbackEditor.value = 'Loading original email template...';
            }
        }
        
        // Fetch the original template (no project ID needed)
        fetch('/api/handoff/preview-original-template/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Store the HTML content
                emailHtmlContent = data.template_content;
                emailBody.value = emailHtmlContent;
                
                // Set content in editor
                if (tinyMceEditor) {
                    try {
                        tinyMceEditor.setContent(emailHtmlContent);
                    } catch (error) {
                        console.warn('Error setting TinyMCE content:', error);
                        // Try alternative method
                        try {
                            tinyMceEditor.setContent(emailHtmlContent);
                        } catch (error2) {
                            console.warn('Error with alternative TinyMCE method:', error2);
                        }
                    }
                } else {
                    // Fallback editor
                    const fallbackEditor = document.getElementById('email-editor');
                    if (fallbackEditor) {
                        fallbackEditor.value = emailHtmlContent;
                    }
                }
                
                // Update status
                editorStatus.textContent = 'Original template loaded - Testing styling and icons';
                testBtn.disabled = false;
                
                // Remove any existing note
                const existingNote = document.querySelector('.template-note');
                if (existingNote) {
                    existingNote.remove();
                }
                
                // Add note about test template
                const noteDiv = document.createElement('div');
                noteDiv.style.cssText = 'margin-top: 10px; padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107; font-size: 12px; color: #856404;';
                noteDiv.innerHTML = '<strong>Test Mode:</strong> This is the original template without variables. Use this to test styling and icon display. Static data: RRD-TEST-001, Films: 430180, 430181, 430182';
                noteDiv.className = 'template-note';
                
                // Add the note after the email editor container
                const emailField = document.querySelector('.email-field');
                emailField.appendChild(noteDiv);
                
            } else {
                editorStatus.textContent = 'Error loading original template';
                testBtn.disabled = false;
                
                if (tinyMceEditor) {
                    try {
                        tinyMceEditor.setContent(`Error loading original template: ${data.error}`);
                    } catch (error) {
                        console.warn('Error setting TinyMCE error text:', error);
                    }
                } else {
                    const fallbackEditor = document.getElementById('email-editor');
                    if (fallbackEditor) {
                        fallbackEditor.value = `Error loading original template: ${data.error}`;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error loading original template:', error);
            editorStatus.textContent = 'Error loading original template';
            testBtn.disabled = false;
            
            if (tinyMceEditor) {
                try {
                    tinyMceEditor.setContent(`Error loading original template: ${error.message}`);
                } catch (tinyMceError) {
                    console.warn('Error setting TinyMCE error text:', tinyMceError);
                }
            } else {
                const fallbackEditor = document.getElementById('email-editor');
                if (fallbackEditor) {
                    fallbackEditor.value = `Error loading original template: ${error.message}`;
                }
            }
        });
    }
    
    function generateAttachments() {
        const attachments = [
            { name: 'scan.xlsx', size: '24.5 KB', type: 'excel' },
            { name: 'scan.dat', size: '18.2 KB', type: 'text' }
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
        if (!validateEmailForm()) return;
        
        // Get the current email content from editor
        let emailContent = '';
        if (tinyMceEditor) {
            try {
                emailContent = tinyMceEditor.getContent();
                emailHtmlContent = emailContent;
                emailBody.value = emailContent;
            } catch (error) {
                console.warn('Error getting TinyMCE content:', error);
                emailContent = emailBody.value;
            }
        } else {
            // Fallback editor
            const fallbackEditor = document.getElementById('email-editor');
            if (fallbackEditor) {
                emailContent = fallbackEditor.value;
                emailBody.value = emailContent;
            } else {
                emailContent = emailBody.value;
            }
        }
        
        showProgress('Sending Email', 'Preparing email with attachments...');
        
        // First generate the handoff files
        fetch(`/api/handoff/projects/${selectedProject.id}/generate-files/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                validated_data: validationData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateProgress(50, 'Files generated, sending email...');
                
                // Now send the email with the current content
                return fetch(`/api/handoff/projects/${selectedProject.id}/send-email/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        to: emailTo.value,
                        cc: emailCc.value,
                        subject: emailSubject.value,
                        body: emailContent, // Send the current content from editor
                        use_custom_body: true, // Always use custom body since we have content
                        attachments: data.files
                    })
                });
            } else {
                throw new Error('Failed to generate files: ' + data.error);
            }
        })
        .then(response => response.json())
        .then(data => {
            hideProgress();
            if (data.success) {
                showEmailSuccess(data);
            } else {
                // Show the actual error message from the backend
                showError('Email sending failed: ' + (data.error || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            hideProgress();
            console.error('Error sending email:', error);
            showError('Failed to send email: ' + error.message);
        });
    }
    
    function getEmailMessage(progress) {
        if (progress <= 25) return 'Generating index files...';
        if (progress <= 50) return 'Preparing email attachments...';
        if (progress <= 75) return 'Connecting to Outlook...';
        return 'Sending email...';
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
                if (extension === 'xlsx' || extension === 'xls') {
                    icon = 'fas fa-file-excel';
                } else if (extension === 'dat' || extension === 'txt') {
                    icon = 'fas fa-file-alt';
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
        
        console.log('Handoff completed successfully - state cleared');
    }
    
    function resetEmailForm() {
        emailTo.value = 'dilek.kursun@rolls-royce.com';
        emailCc.value = 'thomas.lux@rolls-royce.com, jan.becker@rolls-royce.com';
        emailSubject.value = 'Microfilm Project Handoff - [Archive ID]';
        emailBody.value = '';
        
        // Clear user-modified flags
        emailCc.removeAttribute('data-user-modified');
        
        // Clear TinyMCE content if available
        if (tinyMceEditor) {
            try {
                tinyMceEditor.setContent('');
            } catch (error) {
                console.warn('Error clearing TinyMCE content:', error);
            }
        }
        
        // Clear editor status
        editorStatus.textContent = 'Editor ready';
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
    
    function filterProjects() {
        const searchTerm = projectSearchInput.value.toLowerCase();
        const statusFilter = document.getElementById('status-filter').value;
        
        const projectCards = projectCardsContainer.querySelectorAll('.project-card');
        
        projectCards.forEach(card => {
            const projectName = card.querySelector('.project-name').textContent.toLowerCase();
            const archiveId = card.querySelector('.archive-id').textContent.toLowerCase();
            const projectStatus = card.querySelector('.project-status').textContent.toLowerCase();
            
            const matchesSearch = projectName.includes(searchTerm) || archiveId.includes(searchTerm);
            const matchesStatus = statusFilter === 'all' || projectStatus === statusFilter;
            
            card.style.display = matchesSearch && matchesStatus ? 'block' : 'none';
        });
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
        // Enhanced error display with options
        const errorMessage = `Error: ${message}\n\nWhat would you like to do?\n\n` +
                           `• Click OK to continue (your progress is saved)\n` +
                           `• Click Cancel to abort and clear all progress`;
        
        const continueWithError = confirm(errorMessage);
        
        if (!continueWithError) {
            // User chose to abort - clear state and return to start
            clearAllState();
            resetEmailForm();
            selectedProject = null;
            validationData = [];
            validationResults = null;
            clearValidationData();
            showProjectSelection();
            
            setTimeout(() => {
                alert('Progress cleared. You can start over with a new project.');
            }, 100);
        }
        // If user clicks OK, they continue with saved progress
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
});
