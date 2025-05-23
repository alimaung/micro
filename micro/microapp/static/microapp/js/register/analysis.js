// analysis.js - Handles film analysis functionality

document.addEventListener('DOMContentLoaded', function() {
    const startAnalysisBtn = document.getElementById('start-analysis');
    const resetAnalysisBtn = document.getElementById('reset-analysis');
    const toStep3Btn = document.getElementById('to-step-3');
    const selectHybridWorkflowBtn = document.getElementById('select-hybrid-workflow');
    let analysisComplete = false;

    // --- Data Panel Update ---
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

    // --- Step 2: Document Analysis Stage ---
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

    // --- Initialize analysis data panel on load ---
    updateAnalysisData(0, 0, 0, 'pending');
});

