// Microfilm Processing Workflow JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const validateProjectBtn = document.getElementById('validate-project');
    const toStep2Btn = document.getElementById('to-step-2');
    const backToStep1Btn = document.getElementById('back-to-step-1');
    const startAnalysisBtn = document.getElementById('start-analysis');
    const resetAnalysisBtn = document.getElementById('reset-analysis');
    const toStep3Btn = document.getElementById('to-step-3');
    const backToStep2Btn = document.getElementById('back-to-step-2');
    const selectStandardWorkflowBtn = document.getElementById('select-standard-workflow');
    const selectHybridWorkflowBtn = document.getElementById('select-hybrid-workflow');
    const toStep4Btn = document.getElementById('to-step-4');
    const backToStep3Btn = document.getElementById('back-to-step-3');
    const generateReferencesBtn = document.getElementById('generate-references');
    const toStep5Btn = document.getElementById('to-step-5');
    
    // State Variables
    let currentStep = 1;
    let workflowType = null;
    let analysisComplete = false;
    let validationComplete = false;
    
    // Progress Step Updates
    function updateStepIndicators() {
        // Reset all steps
        document.querySelectorAll('.progress-step').forEach(step => {
            step.classList.remove('active', 'completed');
        });
        
        // Set current step as active
        const currentStepElem = document.querySelector(`.progress-step[data-step="${currentStep}"]`);
        if (currentStepElem) {
            currentStepElem.classList.add('active');
        }
        
        // Set previous steps as completed
        for (let i = 1; i < currentStep; i++) {
            const prevStep = document.querySelector(`.progress-step[data-step="${i}"]`);
            if (prevStep) {
                prevStep.classList.add('completed');
            }
        }
        
        // Update progress bar
        const progressPercentage = ((currentStep - 1) / 8) * 100;
        document.querySelector('.progress-bar-fill').style.width = `${progressPercentage}%`;
    }
    
    // Step Navigation
    function showStep(stepNumber) {
        // Hide all steps
        document.querySelectorAll('.workflow-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show requested step
        const stepToShow = document.getElementById(`step-${stepNumber}`);
        if (stepToShow) {
            stepToShow.classList.add('active');
            currentStep = stepNumber;
            updateStepIndicators();
            
            // Scroll to top of the step
            window.scrollTo({
                top: stepToShow.offsetTop - 100,
                behavior: 'smooth'
            });
        }
    }
    
    // Data Panel Updates
    function updateProjectData() {
        const projectName = document.getElementById('project-name').value || '';
        const sourcePath = document.getElementById('project-folder').value || '';
        const outputPath = document.getElementById('output-folder').value || '';
        const filmType = document.getElementById('film-type').value;
        const filmStandard = document.getElementById('film-standard').value;
        const debugMode = document.getElementById('debug-mode').checked;
        const retainSources = document.getElementById('retain-sources').checked;
        const autoDetect = document.getElementById('auto-detect').checked;
        
        const projectData = {
            project: {
                name: projectName,
                sourcePath: sourcePath,
                outputPath: outputPath,
                filmType: filmType,
                filmStandard: filmStandard,
                options: {
                    debugMode: debugMode,
                    retainSources: retainSources,
                    autoDetectOversize: autoDetect
                }
            }
        };
        
        document.querySelector('.data-output').textContent = JSON.stringify(projectData, null, 2);
    }
    
    function updateAnalysisData(documentCount, pageCount, oversizedCount, status) {
        const analysisData = {
            analysis: {
                documentCount: documentCount,
                pageCount: pageCount,
                oversizedCount: oversizedCount,
                status: status,
                documentTypes: {
                    pdf: Math.floor(documentCount * 0.7),
                    tiff: Math.floor(documentCount * 0.2),
                    jpeg: Math.floor(documentCount * 0.1)
                },
                sizeDistribution: {
                    standard: documentCount - oversizedCount,
                    oversized: oversizedCount
                }
            }
        };
        
        document.querySelector('#step-2 .data-output').textContent = JSON.stringify(analysisData, null, 2);
    }
    
    function updateWorkflowData(type, recommendationType) {
        const workflowData = {
            workflow: {
                type: type,
                recommendationType: recommendationType,
                documentDistribution: {
                    standard: parseInt(document.querySelector('.document-counter:nth-child(1) .counter-value').textContent) - 
                             parseInt(document.querySelector('.document-counter:nth-child(3) .counter-value').textContent),
                    oversized: parseInt(document.querySelector('.document-counter:nth-child(3) .counter-value').textContent)
                }
            }
        };
        
        document.querySelector('#step-3 .data-output').textContent = JSON.stringify(workflowData, null, 2);
    }
    
    function updateReferenceSheetData(status, reason, count, documentsRef) {
        const referenceData = {
            referenceSheets: {
                status: status,
                reason: reason,
                sheetCount: count,
                referencedDocuments: documentsRef
            }
        };
        
        document.querySelector('#step-4 .data-output').textContent = JSON.stringify(referenceData, null, 2);
    }
    
    // Form Input Handling
    function checkProjectFormValidity() {
        const projectName = document.getElementById('project-name').value;
        const sourcePath = document.getElementById('project-folder').value;
        const outputPath = document.getElementById('output-folder').value;
        
        if (projectName && sourcePath && outputPath) {
            validateProjectBtn.disabled = false;
        } else {
            validateProjectBtn.disabled = true;
        }
    }
    
    // Add input event listeners to form fields
    document.getElementById('project-name').addEventListener('input', checkProjectFormValidity);
    document.getElementById('project-folder').addEventListener('input', checkProjectFormValidity);
    document.getElementById('output-folder').addEventListener('input', checkProjectFormValidity);
    
    // Mock browsing functionality - in a real app, this would be replaced with actual file system access
    document.querySelectorAll('.browse-button').forEach((button, index) => {
        button.addEventListener('click', function() {
            const mockPaths = [
                'C:/Users/admin/Documents/Microfilm_Project_Docs',
                'C:/Users/admin/Documents/Microfilm_Output'
            ];
            
            const inputElement = this.previousElementSibling;
            inputElement.value = mockPaths[index % 2];
            
            // Check form validity after updating
            checkProjectFormValidity();
            
            // Update project data panel
            updateProjectData();
        });
    });
    
    // Toggle options event listeners
    document.getElementById('debug-mode').addEventListener('change', updateProjectData);
    document.getElementById('retain-sources').addEventListener('change', updateProjectData);
    document.getElementById('auto-detect').addEventListener('change', updateProjectData);
    document.getElementById('film-type').addEventListener('change', updateProjectData);
    document.getElementById('film-standard').addEventListener('change', updateProjectData);
    
    // Step 1: Project Setup Stage
    validateProjectBtn.addEventListener('click', function() {
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validating...';
        
        // Simulate validation process
        setTimeout(() => {
            this.innerHTML = '<i class="fas fa-check-circle"></i> Project Validated';
            toStep2Btn.disabled = false;
            validationComplete = true;
            
            // Update status badge
            document.querySelector('#step-1 .status-badge').className = 'status-badge completed';
            document.querySelector('#step-1 .status-badge').innerHTML = '<i class="fas fa-check-circle"></i> Configuration Valid';
            
            // Show notification
            showNotification('Project configuration validated successfully!', 'success');
        }, 1500);
    });
    
    // Step Navigation
    toStep2Btn.addEventListener('click', function() {
        showStep(2);
    });
    
    backToStep1Btn.addEventListener('click', function() {
        showStep(1);
    });
    
    // Step 2: Document Analysis Stage
    startAnalysisBtn.addEventListener('click', function() {
        this.disabled = true;
        resetAnalysisBtn.disabled = true;
        
        // Update status badge
        const statusBadge = document.querySelector('#step-2 .status-badge');
        statusBadge.className = 'status-badge in-progress';
        statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Analysis in Progress';
        
        // Update status text
        document.getElementById('analysis-status').textContent = 'Starting document analysis...';
        
        // Initialize counters and progress
        const documentCounter = document.querySelector('.document-counter:nth-child(1) .counter-value');
        const pageCounter = document.querySelector('.document-counter:nth-child(2) .counter-value');
        const oversizedCounter = document.querySelector('.document-counter:nth-child(3) .counter-value');
        const progressBar = document.querySelector('#step-2 .progress-bar-fill');
        const progressPercentage = document.querySelector('#step-2 .progress-percentage');
        
        // Reset counters
        documentCounter.textContent = '0';
        pageCounter.textContent = '0';
        oversizedCounter.textContent = '0';
        progressBar.style.width = '0%';
        progressPercentage.textContent = '0%';
        
        // Simulate incremental document analysis
        let progress = 0;
        let documentCount = 0;
        let pageCount = 0;
        let oversizedCount = 0;
        
        const totalDocuments = 125; // Simulate finding 125 documents
        const totalPages = 825; // Simulate 825 total pages
        const totalOversized = 18; // Simulate 18 oversized documents
        
        const analysisInterval = setInterval(() => {
            progress += 2;
            
            // Update progress bar
            progressBar.style.width = `${progress}%`;
            progressPercentage.textContent = `${progress}%`;
            
            // Update document count based on progress
            documentCount = Math.floor((progress / 100) * totalDocuments);
            pageCount = Math.floor((progress / 100) * totalPages);
            oversizedCount = Math.floor((progress / 100) * totalOversized);
            
            documentCounter.textContent = documentCount;
            pageCounter.textContent = pageCount;
            oversizedCounter.textContent = oversizedCount;
            
            // Update status message based on progress
            if (progress < 25) {
                document.getElementById('analysis-status').textContent = 'Scanning document files...';
            } else if (progress < 50) {
                document.getElementById('analysis-status').textContent = 'Analyzing document sizes...';
            } else if (progress < 75) {
                document.getElementById('analysis-status').textContent = 'Calculating page counts...';
            } else {
                document.getElementById('analysis-status').textContent = 'Finalizing analysis...';
            }
            
            // Update data panel
            updateAnalysisData(documentCount, pageCount, oversizedCount, 'in-progress');
            
            if (progress >= 100) {
                clearInterval(analysisInterval);
                
                // Enable navigation to next step
                toStep3Btn.disabled = false;
                resetAnalysisBtn.disabled = false;
                
                // Update status
                document.getElementById('analysis-status').textContent = 'Analysis complete. Found ' + totalDocuments + ' documents with ' + totalPages + ' pages.';
                statusBadge.className = 'status-badge completed';
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Analysis Complete';
                
                // Update data panel with final values
                updateAnalysisData(totalDocuments, totalPages, totalOversized, 'completed');
                
                // Set hybrid workflow as recommended if oversized documents found
                if (totalOversized > 0) {
                    updateWorkflowData('pending', 'hybrid');
                    document.querySelector('.workflow-branch.oversized').classList.remove('inactive');
                    selectHybridWorkflowBtn.disabled = false;
                    
                    document.querySelector('.workflow-branch.standard .recommendation-badge').remove();
                    
                    const recommendationBadge = document.createElement('span');
                    recommendationBadge.className = 'recommendation-badge';
                    recommendationBadge.textContent = 'Recommended';
                    document.querySelector('.workflow-branch.oversized .branch-header').appendChild(recommendationBadge);
                } else {
                    updateWorkflowData('pending', 'standard');
                }
                
                // Populate reference sheet data based on analysis
                if (totalOversized > 0) {
                    updateReferenceSheetData('pending', 'Requires hybrid workflow selection', totalOversized, totalOversized);
                } else {
                    updateReferenceSheetData('inactive', 'Standard workflow selected', 0, 0);
                }
                
                // Show notification
                showNotification('Document analysis completed successfully!', 'success');
                
                analysisComplete = true;
            }
        }, 100);
    });
    
    // Reset Analysis button
    resetAnalysisBtn.addEventListener('click', function() {
        // Reset all analysis data
        const documentCounter = document.querySelector('.document-counter:nth-child(1) .counter-value');
        const pageCounter = document.querySelector('.document-counter:nth-child(2) .counter-value');
        const oversizedCounter = document.querySelector('.document-counter:nth-child(3) .counter-value');
        const progressBar = document.querySelector('#step-2 .progress-bar-fill');
        const progressPercentage = document.querySelector('#step-2 .progress-percentage');
        
        documentCounter.textContent = '0';
        pageCounter.textContent = '0';
        oversizedCounter.textContent = '0';
        progressBar.style.width = '0%';
        progressPercentage.textContent = '0%';
        
        // Reset status
        document.getElementById('analysis-status').textContent = 'Waiting to start...';
        
        // Update status badge
        const statusBadge = document.querySelector('#step-2 .status-badge');
        statusBadge.className = 'status-badge pending';
        statusBadge.innerHTML = '<i class="fas fa-clock"></i> Ready to Analyze';
        
        // Enable start button
        startAnalysisBtn.disabled = false;
        toStep3Btn.disabled = true;
        
        // Update data panel
        updateAnalysisData(0, 0, 0, 'pending');
        
        // Reset analysis complete flag
        analysisComplete = false;
    });
    
    // Navigation to Step 3
    toStep3Btn.addEventListener('click', function() {
        showStep(3);
        
        // Update status badge if analysis was completed
        if (analysisComplete) {
            const statusBadge = document.querySelector('#step-3 .status-badge');
            statusBadge.className = 'status-badge pending';
            statusBadge.innerHTML = '<i class="fas fa-clock"></i> Selection Needed';
        }
    });
    
    backToStep2Btn.addEventListener('click', function() {
        showStep(2);
    });
    
    // Step 3: Workflow Determination Stage
    selectStandardWorkflowBtn.addEventListener('click', function() {
        // Update workflow selection
        workflowType = 'standard';
        
        // Update workflow data
        updateWorkflowData('standard', document.querySelectorAll('.recommendation-badge').length > 0 ? 
                           document.querySelector('.recommendation-badge').parentElement.parentElement.classList.contains('standard') ? 'standard' : 'hybrid' 
                           : 'standard');
        
        // Update reference sheet data for standard workflow
        updateReferenceSheetData('inactive', 'Standard workflow selected', 0, 0);
        
        // Update UI
        document.querySelector('.workflow-branch.standard').classList.add('selected');
        document.querySelector('.workflow-branch.oversized').classList.remove('selected');
        
        // Update status badge
        const statusBadge = document.querySelector('#step-3 .status-badge');
        statusBadge.className = 'status-badge completed';
        statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Standard Workflow Selected';
        
        // Enable navigation to next step
        toStep4Btn.disabled = false;
        
        // Show notification
        showNotification('Standard workflow selected!', 'success');
    });
    
    selectHybridWorkflowBtn.addEventListener('click', function() {
        // Update workflow selection
        workflowType = 'hybrid';
        
        // Update workflow data
        updateWorkflowData('hybrid', document.querySelectorAll('.recommendation-badge').length > 0 ? 
                           document.querySelector('.recommendation-badge').parentElement.parentElement.classList.contains('standard') ? 'standard' : 'hybrid' 
                           : 'hybrid');
        
        // Update reference sheet data for hybrid workflow
        const oversizedCount = parseInt(document.querySelector('.document-counter:nth-child(3) .counter-value').textContent);
        updateReferenceSheetData('pending', 'Requires reference sheet generation', oversizedCount, oversizedCount);
        
        // Update UI
        document.querySelector('.workflow-branch.oversized').classList.add('selected');
        document.querySelector('.workflow-branch.standard').classList.remove('selected');
        
        // Update status badge
        const statusBadge = document.querySelector('#step-3 .status-badge');
        statusBadge.className = 'status-badge completed';
        statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Hybrid Workflow Selected';
        
        // Enable navigation to next step
        toStep4Btn.disabled = false;
        
        // Show notification
        showNotification('Hybrid workflow selected!', 'success');
    });
    
    // Navigation to Step 4
    toStep4Btn.addEventListener('click', function() {
        showStep(4);
        
        // Update Reference Sheet UI based on workflow type
        if (workflowType === 'hybrid') {
            // Update status badge
            const statusBadge = document.querySelector('#step-4 .status-badge');
            statusBadge.className = 'status-badge pending';
            statusBadge.innerHTML = '<i class="fas fa-clock"></i> Generation Required';
            
            // Show reference sheet generation UI
            document.querySelector('.status-message.inactive').classList.add('hidden');
            document.querySelector('.reference-animation.hidden').classList.remove('hidden');
            
            // Enable generate button
            generateReferencesBtn.disabled = false;
        } else {
            // Update status badge
            const statusBadge = document.querySelector('#step-4 .status-badge');
            statusBadge.className = 'status-badge completed';
            statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Not Required';
            
            // Keep "not required" message visible
            document.querySelector('.status-message.inactive').classList.remove('hidden');
            document.querySelector('.reference-animation.hidden').classList.add('hidden');
            
            // Keep generate button disabled
            generateReferencesBtn.disabled = true;
        }
    });
    
    backToStep3Btn.addEventListener('click', function() {
        showStep(3);
    });
    
    // Step 4: Reference Sheet Generation
    generateReferencesBtn.addEventListener('click', function() {
        this.disabled = true;
        
        // Update status badge
        const statusBadge = document.querySelector('#step-4 .status-badge');
        statusBadge.className = 'status-badge in-progress';
        statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Generation In Progress';
        
        // Start progress animation
        const progressBar = document.querySelector('#step-4 .progress-bar-fill');
        const progressPercentage = document.querySelector('#step-4 .progress-percentage');
        const progressStatus = document.getElementById('reference-status');
        
        progressStatus.textContent = 'Starting reference sheet generation...';
        
        let progress = 0;
        const oversizedCount = parseInt(document.querySelector('.document-counter:nth-child(3) .counter-value').textContent);
        
        const generationInterval = setInterval(() => {
            progress += 5;
            
            // Update progress bar
            progressBar.style.width = `${progress}%`;
            progressPercentage.textContent = `${progress}%`;
            
            // Update status message based on progress
            if (progress < 30) {
                progressStatus.textContent = 'Creating reference templates...';
            } else if (progress < 60) {
                progressStatus.textContent = 'Mapping document references...';
            } else if (progress < 90) {
                progressStatus.textContent = 'Generating cross-references...';
            } else {
                progressStatus.textContent = 'Finalizing reference sheets...';
            }
            
            // Update data panel
            updateReferenceSheetData('in-progress', 'Generating reference sheets', 
                                    Math.floor((progress / 100) * oversizedCount), 
                                    Math.floor((progress / 100) * oversizedCount));
            
            if (progress >= 100) {
                clearInterval(generationInterval);
                
                // Update status
                progressStatus.textContent = 'Reference sheet generation complete!';
                statusBadge.className = 'status-badge completed';
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Generation Complete';
                
                // Update data panel with final values
                updateReferenceSheetData('completed', 'Reference sheets generated', oversizedCount, oversizedCount);
                
                // Show notification
                showNotification('Reference sheets generated successfully!', 'success');
                
                // Enable the navigation to the next step
                toStep5Btn.disabled = false;
            }
        }, 200);
    });
    
    // Add the missing event listener for toStep5Btn
    toStep5Btn.addEventListener('click', function() {
        showStep(5);
    });
    
    // Continue the existing JavaScript with new functionality for steps 5-9

    // Step 5: Film Allocation Stage
    const backToStep4Btn = document.getElementById('back-to-step-4');
    const calculateAllocationBtn = document.getElementById('calculate-allocation');
    const resetAllocationBtn = document.getElementById('reset-allocation');
    const toStep6Btn = document.getElementById('to-step-6');
    
    // Film roll toggles
    const show16mmToggle = document.getElementById('show-16mm');
    const show35mmToggle = document.getElementById('show-35mm');
    const rolls16mm = document.getElementById('16mm-rolls');
    const rolls35mm = document.getElementById('35mm-rolls');
    
    // Film allocation data
    function updateAllocationData(status, method, maxCapacity, films16mm, films35mm) {
        const allocData = {
            allocation: {
                status: status,
                method: method,
                maxCapacity: maxCapacity,
                films: {
                    "16mm": films16mm || [],
                    "35mm": films35mm || []
                },
                statistics: {
                    totalFilms: (films16mm ? films16mm.length : 0) + (films35mm ? films35mm.length : 0),
                    averageUtilization: calculateAverageUtilization(films16mm, films35mm),
                    documentDistribution: {
                        "16mm": calculateTotalDocuments(films16mm),
                        "35mm": calculateTotalDocuments(films35mm)
                    }
                }
            }
        };
        
        document.querySelector('#step-5 .data-output').textContent = JSON.stringify(allocData, null, 2);
    }
    
    function calculateAverageUtilization(films16mm, films35mm) {
        let totalUtilization = 0;
        let totalFilms = 0;
        
        if (films16mm && films16mm.length) {
            films16mm.forEach(film => {
                totalUtilization += film.utilizationPercent;
            });
            totalFilms += films16mm.length;
        }
        
        if (films35mm && films35mm.length) {
            films35mm.forEach(film => {
                totalUtilization += film.utilizationPercent;
            });
            totalFilms += films35mm.length;
        }
        
        return totalFilms > 0 ? Math.round(totalUtilization / totalFilms) : 0;
    }
    
    function calculateTotalDocuments(films) {
        if (!films || !films.length) return 0;
        
        return films.reduce((total, film) => total + film.documentCount, 0);
    }
    
    // Initialize film allocation data
    updateAllocationData('pending', 'balanced', 90, [], []);
    
    // Film type toggles
    show16mmToggle.addEventListener('change', function() {
        if (this.checked) {
            rolls16mm.classList.remove('hidden');
        } else {
            rolls16mm.classList.add('hidden');
        }
    });
    
    show35mmToggle.addEventListener('change', function() {
        if (this.checked) {
            rolls35mm.classList.remove('hidden');
        } else {
            rolls35mm.classList.add('hidden');
        }
    });
    
    // Calculate film allocation
    calculateAllocationBtn.addEventListener('click', function() {
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating...';
        
        // Update status badge
        const statusBadge = document.querySelector('#step-5 .status-badge');
        statusBadge.className = 'status-badge in-progress';
        statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Calculating Allocation';
        
        // Get allocation parameters
        const allocationMethod = document.getElementById('allocation-method').value;
        const maxCapacity = parseInt(document.getElementById('max-capacity').value);
        
        // Simulate calculation process
        setTimeout(() => {
            // Get document count and oversized count from previous steps
            const documentCount = parseInt(document.querySelector('.document-counter:nth-child(1) .counter-value').textContent);
            const oversizedCount = parseInt(document.querySelector('.document-counter:nth-child(3) .counter-value').textContent);
            
            // Calculate standard document count
            const standardCount = documentCount - oversizedCount;
            
            // Generate 16mm films
            const films16mm = [];
            let remainingStandard = standardCount;
            let filmNumber = 1;
            
            // Calculate frames needed per standard document (average)
            const framesPerDoc = 7; // Assumed average
            const maxFramesPerFilm = 2500;
            const maxDocsPerFilm = Math.floor(maxCapacity * maxFramesPerFilm / 100 / framesPerDoc);
            
            while (remainingStandard > 0) {
                const docsInThisFilm = Math.min(remainingStandard, maxDocsPerFilm);
                const framesUsed = docsInThisFilm * framesPerDoc;
                const utilization = Math.round((framesUsed / maxFramesPerFilm) * 100);
                
                films16mm.push({
                    id: `Roll 16-${String(filmNumber).padStart(3, '0')}`,
                    capacity: maxFramesPerFilm,
                    framesUsed: framesUsed,
                    documentCount: docsInThisFilm,
                    utilizationPercent: utilization
                });
                
                remainingStandard -= docsInThisFilm;
                filmNumber++;
            }
            
            // Generate 35mm films if oversized documents exist
            const films35mm = [];
            
            if (oversizedCount > 0) {
                let remainingOversized = oversizedCount;
                filmNumber = 1;
                
                // Oversized documents use 35mm film with different capacity
                const framesPerOversizedDoc = 4; // Assumed average
                const maxFramesPerLargeFilm = 1200;
                const maxOversizedDocsPerFilm = Math.floor(maxCapacity * maxFramesPerLargeFilm / 100 / framesPerOversizedDoc);
                
                while (remainingOversized > 0) {
                    const docsInThisFilm = Math.min(remainingOversized, maxOversizedDocsPerFilm);
                    const framesUsed = docsInThisFilm * framesPerOversizedDoc;
                    const utilization = Math.round((framesUsed / maxFramesPerLargeFilm) * 100);
                    
                    films35mm.push({
                        id: `Roll 35-${String(filmNumber).padStart(3, '0')}`,
                        capacity: maxFramesPerLargeFilm,
                        framesUsed: framesUsed,
                        documentCount: docsInThisFilm,
                        utilizationPercent: utilization
                    });
                    
                    remainingOversized -= docsInThisFilm;
                    filmNumber++;
                }
                
                // Show 35mm toggle since we have oversized documents
                show35mmToggle.checked = true;
                rolls35mm.classList.remove('hidden');
            }
            
            // Update film roll UI
            updateFilmRollUI(films16mm, films35mm);
            
            // Update summary statistics
            document.getElementById('total-films').textContent = films16mm.length + films35mm.length;
            
            const totalFrames = 
                films16mm.reduce((sum, film) => sum + film.framesUsed, 0) + 
                films35mm.reduce((sum, film) => sum + film.framesUsed, 0);
                
            const totalDocs = standardCount + oversizedCount;
            
            document.getElementById('pages-per-film').textContent = 
                Math.round(totalFrames / (films16mm.length + films35mm.length));
            
            // Update allocation data
            updateAllocationData('completed', allocationMethod, maxCapacity, films16mm, films35mm);
            
            // Reset button and update UI
            this.innerHTML = '<i class="fas fa-calculator"></i> Calculate Allocation';
            this.disabled = false;
            resetAllocationBtn.disabled = false;
            
            // Update status badge
            statusBadge.className = 'status-badge completed';
            statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Allocation Complete';
            
            // Enable navigation to next step - more forceful approach
            console.log('Enabling to-step-6 button...');
            
            // Try multiple approaches to enable the button
            document.querySelector('#to-step-6').disabled = false;
            document.querySelector('#to-step-6').removeAttribute('disabled');
            
            // Force refresh button state
            setTimeout(() => {
                const btns = document.querySelectorAll('.nav-button');
                btns.forEach(btn => {
                    if (btn.id === 'to-step-6') {
                        btn.disabled = false;
                        btn.classList.remove('disabled');
                        btn.style.pointerEvents = 'auto';
                        btn.style.opacity = '1';
                        console.log('Button refreshed:', btn.id);
                    }
                });
                
                // Show notification to confirm button should be enabled
                showNotification('Navigation to Index Generation is now available', 'info');
            }, 500);
            
            // Show notification
            showNotification('Film allocation calculated successfully!', 'success');
        }, 2000);
    });
    
    // Add debug function to diagnose button issues
    window.debugButtons = function() {
        document.querySelectorAll('.nav-button').forEach(btn => {
            console.log(`Button ${btn.id}: disabled=${btn.disabled}, has disabled attr=${btn.hasAttribute('disabled')}`);
            // Force enable the buttons if needed
            if (btn.id === 'to-step-6' || btn.id === 'to-step-7') {
                btn.disabled = false;
                btn.removeAttribute('disabled');
                btn.style.pointerEvents = 'auto';
                btn.style.opacity = '1';
                console.log(`Forced enable: ${btn.id}`);
                showNotification(`Enabled ${btn.id} button`, 'info');
            }
        });
    };
    
    // Force attach click listeners to all buttons to ensure they work
    setTimeout(() => {
        console.log('Attaching click listeners to all navigation buttons');
        document.querySelectorAll('.nav-button').forEach(btn => {
            if (btn.id && btn.id.startsWith('to-step-')) {
                const stepNumber = parseInt(btn.id.replace('to-step-', ''));
                btn.addEventListener('click', function() {
                    console.log(`Clicked ${btn.id}, navigating to step ${stepNumber}`);
                    showStep(stepNumber);
                });
            }
        });
    }, 1000);
    
    // Reset allocation
    resetAllocationBtn.addEventListener('click', function() {
        // Reset film roll UI
        const filmRollContainers = document.querySelectorAll('.film-roll');
        filmRollContainers.forEach(container => {
            if (container.parentNode) {
                container.remove();
            }
        });
        
        // Add back empty film roll templates
        const roll16mm = document.createElement('div');
        roll16mm.className = 'film-roll';
        roll16mm.innerHTML = `
            <div class="roll-header">
                <span class="roll-id">Roll 16-001</span>
                <span class="roll-capacity">
                    <span class="capacity-used">0</span>/<span class="capacity-total">2500</span> frames
                </span>
            </div>
            <div class="roll-usage-bar">
                <div class="usage-fill" style="width: 0%"></div>
            </div>
            <div class="roll-documents">
                <span class="document-count">0</span> documents
            </div>
        `;
        
        const roll35mm = document.createElement('div');
        roll35mm.className = 'film-roll';
        roll35mm.innerHTML = `
            <div class="roll-header">
                <span class="roll-id">Roll 35-001</span>
                <span class="roll-capacity">
                    <span class="capacity-used">0</span>/<span class="capacity-total">1200</span> frames
                </span>
            </div>
            <div class="roll-usage-bar">
                <div class="usage-fill" style="width: 0%"></div>
            </div>
            <div class="roll-documents">
                <span class="document-count">0</span> documents
            </div>
        `;
        
        // Insert before add button
        const addBtn16mm = document.querySelector('#16mm-rolls .add-roll-button');
        const addBtn35mm = document.querySelector('#35mm-rolls .add-roll-button');
        
        rolls16mm.insertBefore(roll16mm, addBtn16mm);
        rolls35mm.insertBefore(roll35mm, addBtn35mm);
        
        // Reset summary statistics
        document.getElementById('total-films').textContent = '0';
        document.getElementById('pages-per-film').textContent = '0';
        
        // Update allocation data
        updateAllocationData('pending', 'balanced', 90, [], []);
        
        // Update status badge
        const statusBadge = document.querySelector('#step-5 .status-badge');
        statusBadge.className = 'status-badge pending';
        statusBadge.innerHTML = '<i class="fas fa-clock"></i> Awaiting Calculation';
        
        // Disable navigation to next step
        toStep6Btn.disabled = true;
        
        // Show notification
        showNotification('Film allocation reset', 'info');
    });
    
    // Update film roll UI
    function updateFilmRollUI(films16mm, films35mm) {
        try {
            // Ensure rolls16mm and rolls35mm are available
            const rolls16mmContainer = document.getElementById('16mm-rolls');
            const rolls35mmContainer = document.getElementById('35mm-rolls');
            
            if (!rolls16mmContainer || !rolls35mmContainer) {
                console.error("Film roll containers not found in the DOM");
                return;
            }
            
            // Clear existing film rolls
            rolls16mmContainer.querySelectorAll('.film-roll').forEach(container => container.remove());
            rolls35mmContainer.querySelectorAll('.film-roll').forEach(container => container.remove());
            
            // Add 16mm film rolls
            const addBtn16mm = rolls16mmContainer.querySelector('.add-roll-button');
            
            films16mm.forEach(film => {
                const rollElem = document.createElement('div');
                rollElem.className = 'film-roll';
                rollElem.innerHTML = `
                    <div class="roll-header">
                        <span class="roll-id">${film.id}</span>
                        <span class="roll-capacity">
                            <span class="capacity-used">${film.framesUsed}</span>/<span class="capacity-total">${film.capacity}</span> frames
                        </span>
                    </div>
                    <div class="roll-usage-bar">
                        <div class="usage-fill" style="width: ${film.utilizationPercent}%"></div>
                    </div>
                    <div class="roll-documents">
                        <span class="document-count">${film.documentCount}</span> documents
                    </div>
                `;
                
                if (addBtn16mm) {
                    rolls16mmContainer.insertBefore(rollElem, addBtn16mm);
                } else {
                    rolls16mmContainer.appendChild(rollElem);
                }
            });
            
            // Add 35mm film rolls if any
            if (films35mm.length > 0) {
                const addBtn35mm = rolls35mmContainer.querySelector('.add-roll-button');
                
                films35mm.forEach(film => {
                    const rollElem = document.createElement('div');
                    rollElem.className = 'film-roll';
                    rollElem.innerHTML = `
                        <div class="roll-header">
                            <span class="roll-id">${film.id}</span>
                            <span class="roll-capacity">
                                <span class="capacity-used">${film.framesUsed}</span>/<span class="capacity-total">${film.capacity}</span> frames
                            </span>
                        </div>
                        <div class="roll-usage-bar">
                            <div class="usage-fill" style="width: ${film.utilizationPercent}%"></div>
                        </div>
                        <div class="roll-documents">
                            <span class="document-count">${film.documentCount}</span> documents
                        </div>
                    `;
                    
                    if (addBtn35mm) {
                        rolls35mmContainer.insertBefore(rollElem, addBtn35mm);
                    } else {
                        rolls35mmContainer.appendChild(rollElem);
                    }
                });
            }
        } catch (err) {
            console.error("Error updating film roll UI:", err);
            showNotification("Error updating film roll display. See console for details.", "error");
        }
    }
    
    // Navigation to Step 5
    backToStep4Btn.addEventListener('click', function() {
        showStep(4);
    });
    
    // Navigation to Step 6
    toStep6Btn.addEventListener('click', function() {
        showStep(6);
        
        // Update index field checkboxes based on detail level
        document.getElementById('index-detail').addEventListener('change', updateIndexFields);
        
        function updateIndexFields() {
            const detailLevel = document.getElementById('index-detail').value;
            
            // Reset all checkboxes
            document.querySelectorAll('.field-option input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = false;
            });
            
            // Set checkboxes based on detail level
            const standardFields = ['field-document-id', 'field-film-number', 'field-frame-start', 'field-page-count', 'field-document-type'];
            const detailedFields = [...standardFields, 'field-created-date', 'field-modified-date'];
            const comprehensiveFields = [...detailedFields, 'field-file-size'];
            
            let activeFields;
            
            switch(detailLevel) {
                case 'detailed':
                    activeFields = detailedFields;
                    break;
                case 'comprehensive':
                    activeFields = comprehensiveFields;
                    break;
                default:
                    activeFields = standardFields;
            }
            
            activeFields.forEach(fieldId => {
                document.getElementById(fieldId).checked = true;
            });
        }
    });

    // Continue adding event listeners and functions for other steps...
    // For brevity and focus, we'll add just key functionality for remaining steps
    
    // Generate index functionality
    const generateIndexBtn = document.getElementById('generate-index');
    if (generateIndexBtn) {
        generateIndexBtn.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            
            setTimeout(() => {
                // Update table with sample data
                const tableBody = document.querySelector('.index-table tbody');
                tableBody.innerHTML = '';
                
                // Generate sample index data
                const indexFormat = document.getElementById('index-format').value;
                const detailLevel = document.getElementById('index-detail').value;
                
                // Get checked fields
                const checkedFields = [];
                document.querySelectorAll('.field-option input[type="checkbox"]:checked').forEach(checkbox => {
                    checkedFields.push(checkbox.id.replace('field-', ''));
                });
                
                // Generate table rows
                for (let i = 1; i <= 5; i++) {
                    const row = document.createElement('tr');
                    
                    if (checkedFields.includes('document-id')) {
                        row.innerHTML += `<td>DOC-${String(i).padStart(3, '0')}</td>`;
                    }
                    
                    if (checkedFields.includes('film-number')) {
                        row.innerHTML += `<td>MF-2023-000${Math.ceil(i/2)}</td>`;
                    }
                    
                    if (checkedFields.includes('frame-start')) {
                        row.innerHTML += `<td>${(i-1)*10+1}</td>`;
                    }
                    
                    if (checkedFields.includes('page-count')) {
                        row.innerHTML += `<td>${Math.floor(Math.random() * 5) + 3}</td>`;
                    }
                    
                    if (checkedFields.includes('document-type')) {
                        const types = ['PDF', 'TIFF', 'JPEG', 'DOC', 'XLS'];
                        row.innerHTML += `<td>${types[Math.floor(Math.random() * types.length)]}</td>`;
                    }
                    
                    if (checkedFields.includes('created-date')) {
                        row.innerHTML += `<td>2023-05-${String(10 + i).padStart(2, '0')}</td>`;
                    }
                    
                    if (checkedFields.includes('modified-date')) {
                        row.innerHTML += `<td>2023-05-${String(15 + i).padStart(2, '0')}</td>`;
                    }
                    
                    if (checkedFields.includes('file-size')) {
                        row.innerHTML += `<td>${Math.floor(Math.random() * 900) + 100} KB</td>`;
                    }
                    
                    tableBody.appendChild(row);
                }
                
                // Show pagination
                document.querySelector('.table-pagination').classList.remove('hidden');
                
                // Update status badge
                const statusBadge = document.querySelector('#step-6 .status-badge');
                statusBadge.className = 'status-badge completed';
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Index Generated';
                
                // Enable navigation to next step - more forceful approach
                console.log('Enabling to-step-7 button...');
                
                // Try multiple approaches to enable the button
                document.querySelector('#to-step-7').disabled = false;
                document.querySelector('#to-step-7').removeAttribute('disabled');
                
                // Force refresh button state
                setTimeout(() => {
                    const btns = document.querySelectorAll('.nav-button');
                    btns.forEach(btn => {
                        if (btn.id === 'to-step-7') {
                            btn.disabled = false;
                            btn.classList.remove('disabled');
                            btn.style.pointerEvents = 'auto';
                            btn.style.opacity = '1';
                            console.log('Button refreshed:', btn.id);
                        }
                    });
                    
                    // Show notification to confirm button should be enabled
                    showNotification('Navigation to Film Numbering is now available', 'info');
                }, 500);
                
                // Reset button
                this.innerHTML = '<i class="fas fa-file-alt"></i> Generate Index';
                this.disabled = false;
                
                // Show notification
                showNotification('Index generated successfully!', 'success');
            }, 1500);
        });
    }
    
    // Add other step-specific code for Film Numbering, Document Distribution, and Export & Summary
    // For brevity, we'll just enable navigation between steps
    
    // Navigation between steps
    const backToStep5Btn = document.getElementById('back-to-step-5');
    const toStep7Btn = document.getElementById('to-step-7');
    const backToStep6Btn = document.getElementById('back-to-step-6');
    const toStep8Btn = document.getElementById('to-step-8');
    const backToStep7Btn = document.getElementById('back-to-step-7');
    const toStep9Btn = document.getElementById('to-step-9');
    const backToStep8Btn = document.getElementById('back-to-step-8');
    
    if (backToStep5Btn) backToStep5Btn.addEventListener('click', () => showStep(5));
    
    // Expand/Copy Data Panel Actions
    document.querySelectorAll('.panel-action').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.id.includes('expand') ? 'expand' : 'copy';
            const panel = this.closest('.workflow-card');
            const dataOutput = panel.querySelector('.data-output');
            
            if (action === 'expand') {
                // In a real implementation, this would open a modal with expanded view
                showNotification('Expanded view would open in a modal', 'info');
            } else if (action === 'copy') {
                // Copy data to clipboard
                navigator.clipboard.writeText(dataOutput.textContent)
                    .then(() => {
                        showNotification('Data copied to clipboard!', 'success');
                    })
                    .catch(err => {
                        console.error('Failed to copy: ', err);
                        showNotification('Failed to copy data', 'error');
                    });
            }
        });
    });
    
    // Notification system
    function showNotification(message, type = 'info') {
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
            notification.style.display = 'flex';
            notification.style.alignItems = 'center';
            notification.style.gap = '10px';
        }
        
        // Set icon based on type
        let icon = '';
        switch(type) {
            case 'success':
                icon = '<i class="fas fa-check-circle"></i>';
                notification.style.backgroundColor = '#34a853';
                break;
            case 'error':
                icon = '<i class="fas fa-times-circle"></i>';
                notification.style.backgroundColor = '#ea4335';
                break;
            case 'warning':
                icon = '<i class="fas fa-exclamation-triangle"></i>';
                notification.style.backgroundColor = '#fbbc04';
                break;
            default:
                icon = '<i class="fas fa-info-circle"></i>';
                notification.style.backgroundColor = '#1a73e8';
        }
        
        // Set message with icon
        notification.innerHTML = icon + message;
        
        // Show notification
        notification.style.transform = 'translateY(0)';
        notification.style.opacity = '1';
        
        // Hide after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
        }, 3000);
    }
    
    // Initialize project data panel
    updateProjectData();
    
    // Initialize analysis data panel
    updateAnalysisData(0, 0, 0, 'pending');
    
    // Initialize workflow data panel
    updateWorkflowData('pending', 'standard');
    
    // Initialize reference sheet data panel
    updateReferenceSheetData('inactive', 'Workflow not yet determined', 0, 0);

    if (toStep7Btn) toStep7Btn.addEventListener('click', () => showStep(7));
    if (backToStep6Btn) backToStep6Btn.addEventListener('click', () => showStep(6));
    if (toStep8Btn) toStep8Btn.addEventListener('click', () => showStep(8));
    if (backToStep7Btn) backToStep7Btn.addEventListener('click', () => showStep(7));
    if (toStep9Btn) toStep9Btn.addEventListener('click', () => showStep(9));
    if (backToStep8Btn) backToStep8Btn.addEventListener('click', () => showStep(8));
    
    // Film Numbering (Step 7)
    const applyNumberingBtn = document.getElementById('apply-numbering');
    const resetNumberingBtn = document.getElementById('reset-numbering');
    
    // Preview film ID update based on form changes
    function updateFilmIDPreview() {
        const prefix = document.getElementById('numbering-prefix').value;
        const includeYear = document.getElementById('include-year').checked;
        const year = includeYear ? document.getElementById('numbering-year').value : '';
        const digits = parseInt(document.getElementById('sequence-digits').value);
        const separator = document.getElementById('separation-char').value;
        const startingNumber = parseInt(document.getElementById('starting-number').value);
        
        // Format the film IDs
        let filmID16mm = prefix;
        let filmID35mm = prefix;
        
        // Add year if enabled
        if (includeYear) {
            const sepChar = getSeparatorChar(separator);
            filmID16mm += sepChar + year;
            filmID35mm += sepChar + year;
        }
        
        // Add sequence with proper digits
        const sepChar = getSeparatorChar(separator);
        filmID16mm += sepChar + String(startingNumber).padStart(digits, '0');
        filmID35mm += sepChar + String(startingNumber).padStart(digits, '0') + 'L';
        
        // Update preview display
        const filmIDDisplays = document.querySelectorAll('.film-id-display');
        filmIDDisplays[0].textContent = filmID16mm;
        filmIDDisplays[1].textContent = filmID35mm;
        
        // Update diagram film IDs
        document.querySelectorAll('.diagram-film .film-id').forEach((elem, index) => {
            if (index === 0) {
                elem.textContent = filmID16mm;
            } else if (index === 1) {
                elem.textContent = prefix + sepChar + year + sepChar + String(startingNumber + 1).padStart(digits, '0');
            } else if (index === 2) {
                elem.textContent = filmID35mm;
            }
        });
        
        // Update numbering data
        updateNumberingData('pending', {
            prefix,
            includeYear,
            year: year.toString(),
            sequenceDigits: digits,
            separator,
            startingNumber
        });
    }
    
    function getSeparatorChar(separatorType) {
        switch (separatorType) {
            case 'dash': return '-';
            case 'dot': return '.';
            case 'underscore': return '_';
            default: return '';
        }
    }
    
    // Update numbering data
    function updateNumberingData(status, scheme, assignments16mm, assignments35mm) {
        const numberingData = {
            numbering: {
                status: status,
                scheme: scheme,
                assignments: {
                    "16mm": assignments16mm || [],
                    "35mm": assignments35mm || []
                }
            }
        };
        
        document.querySelector('#step-7 .data-output').textContent = JSON.stringify(numberingData, null, 2);
    }
    
    // Initialize with default values
    updateNumberingData('pending', {
        prefix: 'MF',
        includeYear: true,
        year: '2023',
        sequenceDigits: 4,
        separator: 'dash',
        startingNumber: 1
    });
    
    // Add event listeners for form fields
    if (document.getElementById('numbering-prefix')) {
        const numberingFields = [
            'numbering-prefix',
            'include-year',
            'numbering-year',
            'sequence-digits',
            'separation-char',
            'starting-number'
        ];
        
        numberingFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('change', updateFilmIDPreview);
                field.addEventListener('input', updateFilmIDPreview);
            }
        });
        
        // Toggle year field visibility based on checkbox
        document.getElementById('include-year').addEventListener('change', function() {
            document.getElementById('numbering-year').disabled = !this.checked;
        });
    }
    
    // Apply numbering scheme
    if (applyNumberingBtn) {
        applyNumberingBtn.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Applying...';
            
            // Update status badge
            const statusBadge = document.querySelector('#step-7 .status-badge');
            statusBadge.className = 'status-badge in-progress';
            statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Applying Numbering Scheme';
            
            setTimeout(() => {
                // Generate sample assignments
                const prefix = document.getElementById('numbering-prefix').value;
                const includeYear = document.getElementById('include-year').checked;
                const year = includeYear ? document.getElementById('numbering-year').value : '';
                const digits = parseInt(document.getElementById('sequence-digits').value);
                const separator = document.getElementById('separation-char').value;
                const startingNumber = parseInt(document.getElementById('starting-number').value);
                
                const sepChar = getSeparatorChar(separator);
                
                // Generate assignments for 16mm films (from step 5)
                const assignments16mm = [];
                const rolls16mmContainer = document.getElementById('16mm-rolls');
                const filmRolls16mm = rolls16mmContainer ? rolls16mmContainer.querySelectorAll('.film-roll') : [];
                
                filmRolls16mm.forEach((roll, index) => {
                    const sequenceNumber = startingNumber + index;
                    let filmId = prefix;
                    
                    if (includeYear) {
                        filmId += sepChar + year;
                    }
                    
                    filmId += sepChar + String(sequenceNumber).padStart(digits, '0');
                    
                    assignments16mm.push({
                        originalId: roll.querySelector('.roll-id').textContent,
                        assignedId: filmId,
                        documentCount: parseInt(roll.querySelector('.document-count').textContent)
                    });
                });
                
                // Generate assignments for 35mm films
                const assignments35mm = [];
                const rolls35mmContainer = document.getElementById('35mm-rolls');
                const filmRolls35mm = rolls35mmContainer ? rolls35mmContainer.querySelectorAll('.film-roll') : [];
                
                filmRolls35mm.forEach((roll, index) => {
                    const sequenceNumber = startingNumber + index;
                    let filmId = prefix;
                    
                    if (includeYear) {
                        filmId += sepChar + year;
                    }
                    
                    filmId += sepChar + String(sequenceNumber).padStart(digits, '0') + 'L';
                    
                    assignments35mm.push({
                        originalId: roll.querySelector('.roll-id').textContent,
                        assignedId: filmId,
                        documentCount: parseInt(roll.querySelector('.document-count').textContent)
                    });
                });
                
                // Update numbering data
                updateNumberingData('completed', {
                    prefix,
                    includeYear,
                    year: year.toString(),
                    sequenceDigits: digits,
                    separator,
                    startingNumber
                }, assignments16mm, assignments35mm);
                
                // Enable navigation to next step
                toStep8Btn.disabled = false;
                
                // Update status badge
                statusBadge.className = 'status-badge completed';
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Numbering Applied';
                
                // Reset button
                this.innerHTML = '<i class="fas fa-check"></i> Apply Numbering Scheme';
                this.disabled = false;
                
                // Show notification
                showNotification('Film numbering scheme applied successfully!', 'success');
            }, 1500);
        });
    }
    
    // Reset numbering to defaults
    if (resetNumberingBtn) {
        resetNumberingBtn.addEventListener('click', function() {
            // Reset form fields to defaults
            document.getElementById('numbering-prefix').value = 'MF';
            document.getElementById('include-year').checked = true;
            document.getElementById('numbering-year').value = '2023';
            document.getElementById('sequence-digits').value = '4';
            document.getElementById('separation-char').value = 'dash';
            document.getElementById('starting-number').value = '1';
            
            // Enable year selection
            document.getElementById('numbering-year').disabled = false;
            
            // Update preview
            updateFilmIDPreview();
            
            // Show notification
            showNotification('Numbering scheme reset to defaults', 'info');
        });
    }
    
    // Document Distribution (Step 8)
    const startDistributionBtn = document.getElementById('start-distribution');
    
    // Update distribution data
    function updateDistributionData(status, structure, pattern, options, statistics) {
        const distData = {
            distribution: {
                status: status,
                folderStructure: structure,
                namingPattern: pattern,
                options: options,
                statistics: statistics || {
                    totalFolders: 0,
                    totalFiles: 0,
                    totalSize: "0 MB"
                }
            }
        };
        
        document.querySelector('#step-8 .data-output').textContent = JSON.stringify(distData, null, 2);
    }
    
    // Initialize distribution data
    updateDistributionData('pending', 'by-film', 'filmid_docid', {
        includeOriginals: true,
        copyIndexToFolders: true
    });
    
    // Preview folder structure based on selected options
    if (document.getElementById('folder-structure')) {
        document.getElementById('folder-structure').addEventListener('change', updateFolderPreview);
        document.getElementById('naming-pattern').addEventListener('change', updateFolderPreview);
        document.getElementById('include-originals').addEventListener('change', updateDistributionOptions);
        document.getElementById('copy-index-folders').addEventListener('change', updateDistributionOptions);
        
        function updateFolderPreview() {
            const structure = document.getElementById('folder-structure').value;
            const pattern = document.getElementById('naming-pattern').value;
            const folderTree = document.querySelector('.folder-tree');
            
            // Update the folder tree based on the selected structure
            switch (structure) {
                case 'flat':
                    folderTree.innerHTML = `
                        <div class="tree-node root">
                            <i class="fas fa-folder-open"></i>
                            <span class="node-name">Output Folder</span>
                            <div class="tree-children">
                                <div class="tree-node">
                                    <i class="fas fa-file-alt"></i>
                                    <span class="node-name">MF-2023-0001_D001.pdf</span>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-file-alt"></i>
                                    <span class="node-name">MF-2023-0001_D002.pdf</span>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-file-alt"></i>
                                    <span class="node-name">MF-2023-0002_D003.pdf</span>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-file-excel"></i>
                                    <span class="node-name">master_index.csv</span>
                                </div>
                            </div>
                        </div>
                    `;
                    break;
                case 'by-film':
                    folderTree.innerHTML = `
                        <div class="tree-node root">
                            <i class="fas fa-folder-open"></i>
                            <span class="node-name">Output Folder</span>
                            <div class="tree-children">
                                <div class="tree-node">
                                    <i class="fas fa-folder"></i>
                                    <span class="node-name">MF-2023-0001</span>
                                    <div class="tree-children">
                                        <div class="tree-node">
                                            <i class="fas fa-file-alt"></i>
                                            <span class="node-name">MF-2023-0001_D001.pdf</span>
                                        </div>
                                        <div class="tree-node">
                                            <i class="fas fa-file-alt"></i>
                                            <span class="node-name">MF-2023-0001_D002.pdf</span>
                                        </div>
                                        <div class="tree-node">
                                            <i class="fas fa-file-excel"></i>
                                            <span class="node-name">MF-2023-0001_index.csv</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-folder"></i>
                                    <span class="node-name">MF-2023-0002</span>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-folder"></i>
                                    <span class="node-name">MF-2023-0001L</span>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-file-excel"></i>
                                    <span class="node-name">master_index.csv</span>
                                </div>
                            </div>
                        </div>
                    `;
                    break;
                case 'by-type':
                    folderTree.innerHTML = `
                        <div class="tree-node root">
                            <i class="fas fa-folder-open"></i>
                            <span class="node-name">Output Folder</span>
                            <div class="tree-children">
                                <div class="tree-node">
                                    <i class="fas fa-folder"></i>
                                    <span class="node-name">PDF</span>
                                    <div class="tree-children">
                                        <div class="tree-node">
                                            <i class="fas fa-file-alt"></i>
                                            <span class="node-name">MF-2023-0001_D001.pdf</span>
                                        </div>
                                        <div class="tree-node">
                                            <i class="fas fa-file-alt"></i>
                                            <span class="node-name">MF-2023-0001_D002.pdf</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-folder"></i>
                                    <span class="node-name">TIFF</span>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-folder"></i>
                                    <span class="node-name">JPEG</span>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-file-excel"></i>
                                    <span class="node-name">master_index.csv</span>
                                </div>
                            </div>
                        </div>
                    `;
                    break;
                case 'hierarchical':
                    folderTree.innerHTML = `
                        <div class="tree-node root">
                            <i class="fas fa-folder-open"></i>
                            <span class="node-name">Output Folder</span>
                            <div class="tree-children">
                                <div class="tree-node">
                                    <i class="fas fa-folder"></i>
                                    <span class="node-name">PDF</span>
                                    <div class="tree-children">
                                        <div class="tree-node">
                                            <i class="fas fa-folder"></i>
                                            <span class="node-name">MF-2023-0001</span>
                                            <div class="tree-children">
                                                <div class="tree-node">
                                                    <i class="fas fa-file-alt"></i>
                                                    <span class="node-name">MF-2023-0001_D001.pdf</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="tree-node">
                                            <i class="fas fa-folder"></i>
                                            <span class="node-name">MF-2023-0002</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-folder"></i>
                                    <span class="node-name">TIFF</span>
                                </div>
                                <div class="tree-node">
                                    <i class="fas fa-file-excel"></i>
                                    <span class="node-name">master_index.csv</span>
                                </div>
                            </div>
                        </div>
                    `;
                    break;
            }
            
            // Update filename patterns based on selected pattern
            const fileNodes = document.querySelectorAll('.tree-node i.fa-file-alt + .node-name');
            
            fileNodes.forEach((node, index) => {
                let filename;
                const docId = `D${String(index + 1).padStart(3, '0')}`;
                const filmId = `MF-2023-${String(Math.ceil((index + 1) / 2)).padStart(4, '0')}`;
                
                switch (pattern) {
                    case 'filmid_docid':
                        filename = `${filmId}_${docId}.pdf`;
                        break;
                    case 'docid_filmid':
                        filename = `${docId}_${filmId}.pdf`;
                        break;
                    case 'original':
                        filename = `original_file_${index + 1}.pdf`;
                        break;
                }
                
                node.textContent = filename;
            });
            
            // Update distribution data
            updateDistributionData(
                'pending',
                structure,
                pattern,
                {
                    includeOriginals: document.getElementById('include-originals').checked,
                    copyIndexToFolders: document.getElementById('copy-index-folders').checked
                }
            );
        }
        
        function updateDistributionOptions() {
            updateDistributionData(
                'pending',
                document.getElementById('folder-structure').value,
                document.getElementById('naming-pattern').value,
                {
                    includeOriginals: document.getElementById('include-originals').checked,
                    copyIndexToFolders: document.getElementById('copy-index-folders').checked
                }
            );
        }
    }
    
    // Start distribution process
    if (startDistributionBtn) {
        startDistributionBtn.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            
            // Update status badge
            const statusBadge = document.querySelector('#step-8 .status-badge');
            statusBadge.className = 'status-badge in-progress';
            statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Distribution In Progress';
            
            // Show progress section
            const progressSection = document.querySelector('.distribution-progress');
            progressSection.classList.remove('hidden');
            
            // Get distribution options
            const structure = document.getElementById('folder-structure').value;
            const pattern = document.getElementById('naming-pattern').value;
            const includeOriginals = document.getElementById('include-originals').checked;
            const copyIndexToFolders = document.getElementById('copy-index-folders').checked;
            
            // Start distribution simulation
            const progressBar = document.querySelector('#step-8 .progress-bar-fill');
            const progressPercentage = document.querySelector('#step-8 .progress-percentage');
            const operationLog = document.querySelector('.operation-log');
            
            let progress = 0;
            let totalFolders = 0;
            let totalFiles = 0;
            
            // Simulate distribution process
            const distributionInterval = setInterval(() => {
                progress += 5;
                progressBar.style.width = `${progress}%`;
                progressPercentage.textContent = `${progress}%`;
                
                // Add log entries based on progress
                if (progress === 5) {
                    addLogEntry('Created directory structure', 'success');
                    totalFolders = structure === 'flat' ? 1 : (structure === 'by-film' ? 4 : (structure === 'by-type' ? 4 : 7));
                } else if (progress === 20) {
                    addLogEntry('Copying standard documents to destination', 'success');
                } else if (progress === 40) {
                    addLogEntry('Processing film MF-2023-0001 (35/35 documents)', 'success');
                    totalFiles += 35;
                } else if (progress === 55) {
                    addLogEntry('Processing film MF-2023-0002 (40/40 documents)', 'success');
                    totalFiles += 40;
                } else if (progress === 70) {
                    addLogEntry('Processing film MF-2023-0001L (18/18 documents)', 'success');
                    totalFiles += 18;
            } else if (progress === 85) {
                    addLogEntry('Generating master index file', 'success');
                    totalFiles += 1;
                    
                    if (copyIndexToFolders) {
                        addLogEntry('Copying index to film-specific folders', 'success');
                        totalFiles += 3;
                    }
            }
            
            if (progress >= 100) {
                    clearInterval(distributionInterval);
                    
                    // Add final log entries
                    addLogEntry('Distribution completed successfully', 'success');
                    
                    // Calculate total size (for demo)
                    const avgFileSize = 220; // KB
                    const totalSize = Math.round(totalFiles * avgFileSize / 100) / 10; // MB
                    
                    // Update distribution data with final statistics
                    updateDistributionData(
                        'completed',
                        structure,
                        pattern,
                        {
                            includeOriginals,
                            copyIndexToFolders
                        },
                        {
                            totalFolders,
                            totalFiles,
                            totalSize: `${totalSize} MB`
                        }
                    );
                    
                    // Update status badge
                    statusBadge.className = 'status-badge completed';
                    statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Distribution Complete';
                    
                    // Reset button
                    this.innerHTML = '<i class="fas fa-play"></i> Start Distribution';
                    this.disabled = false;
                    
                    // Enable navigation to next step
                    toStep9Btn.disabled = false;
                    
                    // Show notification
                    showNotification('Document distribution completed successfully!', 'success');
                }
            }, 300);
            
            function addLogEntry(message, status) {
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.innerHTML = `
                    <span class="log-status ${status}">
                        <i class="fas fa-${status === 'success' ? 'check' : status === 'error' ? 'times' : 'exclamation'}-circle"></i>
                    </span>
                    <span class="log-message">${message}</span>
                `;
                
                operationLog.appendChild(entry);
                
                // Auto-scroll to bottom
                const fileOps = document.querySelector('.file-operations');
                fileOps.scrollTop = fileOps.scrollHeight;
            }
        });
    }
    
    // Export & Summary (Step 9)
    const newProjectBtn = document.getElementById('new-project');
    const downloadAllBtn = document.getElementById('download-all');
    
    // Populate summary data
    function populateSummary() {
        // Get values from previous steps
        const documentCount = parseInt(document.querySelector('.document-counter:nth-child(1) .counter-value')?.textContent || '0');
        const pageCount = parseInt(document.querySelector('.document-counter:nth-child(2) .counter-value')?.textContent || '0');
        
        // Get film counts safely using getElementById first
        const rolls16mmContainer = document.getElementById('16mm-rolls');
        const rolls35mmContainer = document.getElementById('35mm-rolls');
        const filmCount16mm = rolls16mmContainer ? rolls16mmContainer.querySelectorAll('.film-roll')?.length || 0 : 0;
        const filmCount35mm = rolls35mmContainer ? rolls35mmContainer.querySelectorAll('.film-roll')?.length || 0 : 0;
        
        // Update summary statistics
        if (document.getElementById('summary-documents')) {
            document.getElementById('summary-documents').textContent = documentCount;
        }
        
        if (document.getElementById('summary-films')) {
            document.getElementById('summary-films').textContent = filmCount16mm + filmCount35mm;
        }
        
        // Mock duration and size
        if (document.getElementById('summary-duration')) {
            document.getElementById('summary-duration').textContent = '00:45:23';
        }
        
        if (document.getElementById('summary-size')) {
            const avgFileSize = 220; // KB
            const totalFiles = 93; // Estimated from previous steps
            const totalSize = Math.round(totalFiles * avgFileSize / 100) / 10; // MB
            document.getElementById('summary-size').textContent = `${totalSize} MB`;
        }
        
        // Update summary data in JSON panel
        const summaryData = {
            summary: {
                status: 'completed',
                projectName: document.getElementById('project-name')?.value || 'Microfilm Project',
                startTime: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
                endTime: new Date().toISOString(),
                duration: '00:45:23',
                documentCount: documentCount,
                pageCount: pageCount,
                filmRolls: {
                    "16mm": filmCount16mm,
                    "35mm": filmCount35mm
                },
                exports: [
                    {
                        name: "Master Index (CSV)",
                        path: "/exports/master_index.csv",
                        size: "10 KB"
                    },
                    {
                        name: "Project Report (PDF)",
                        path: "/exports/project_report.pdf",
                        size: "250 KB"
                    },
                    {
                        name: "Project Configuration (JSON)",
                        path: "/exports/project_config.json",
                        size: "5 KB"
                    },
                    {
                        name: "Reference Sheet Images",
                        path: "/exports/reference_sheets/",
                        size: "5 MB"
                    }
                ]
            }
        };
        
        if (document.querySelector('#step-9 .data-output')) {
            document.querySelector('#step-9 .data-output').textContent = JSON.stringify(summaryData, null, 2);
        }
    }
    
    // When navigating to summary page
    if (toStep9Btn) {
        toStep9Btn.addEventListener('click', function() {
            showStep(9);
            
            // Update status badge
            const statusBadge = document.querySelector('#step-9 .status-badge');
            statusBadge.className = 'status-badge completed';
            statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Project Complete';
            
            // Populate summary data
            populateSummary();
        });
    }
    
    // Finish project button
    if (newProjectBtn) {
        newProjectBtn.addEventListener('click', function() {
            // Reset all steps and go back to step 1
            showStep(1);
            
            // Reset all form fields would go here in a real implementation
            
            showNotification('Starting new project', 'info');
        });
    }
    
    // Download all button
    if (downloadAllBtn) {
        downloadAllBtn.addEventListener('click', function() {
            showNotification('In a real implementation, this would download a ZIP file with all exports.', 'info');
        });
    }
    
    // Finish project button
    const finishProjectBtn = document.getElementById('finish-project');
    if (finishProjectBtn) {
        finishProjectBtn.addEventListener('click', function() {
            showNotification('Project has been completed successfully!', 'success');
        });
    }
    
    // File download buttons
    document.querySelectorAll('.file-download').forEach(button => {
        button.addEventListener('click', function() {
            const fileName = this.parentElement.querySelector('.file-name').textContent;
            showNotification(`Downloading ${fileName}...`, 'info');
        });
    });
});