/**
 * Document Analysis Simulation Module
 * 
 * Handles simulation functionality for development and testing:
 * - Simulating document analysis process
 * - Generating mock document data
 */

/**
 * Simulate document analysis for development
 */
function simulateDocumentAnalysis() {
    // Simulation values
    const totalDocuments = 125; // Simulate finding 125 documents
    const totalPages = 825; // Simulate 825 total pages
    const totalOversized = 18; // Simulate 18 oversized documents
    const documentsWithOversized = 5; // Simulate 5 documents with oversized pages
    
    // Generate random document list for simulation
    const simulatedDocuments = generateSimulatedDocuments(totalDocuments, totalPages, totalOversized);
    
    // Start simulation
    let progress = 0;
    let documentCount = 0;
    let pageCount = 0;
    let oversizedCount = 0;
    let processedDocCount = 0;
    
    // Show the current document element
    const currentDocElement = document.querySelector('.current-document');
    const currentDocValue = document.getElementById('current-document');
    
    if (currentDocElement) {
        currentDocElement.style.display = 'block';
    }
    
    const simulationInterval = setInterval(() => {
        // Increment progress
        progress += 2;
        analysisState.progress = progress;
        
        // Update progress bar
        analysisState.progressBar.style.width = `${progress}%`;
        analysisState.progressPercentage.textContent = `${progress}%`;
        
        // Update document count based on progress
        documentCount = Math.floor((progress / 100) * totalDocuments);
        pageCount = Math.floor((progress / 100) * totalPages);
        oversizedCount = Math.floor((progress / 100) * totalOversized);
        
        // Update counters
        analysisState.documentCounter.textContent = documentCount;
        analysisState.pageCounter.textContent = pageCount;
        analysisState.oversizedCounter.textContent = oversizedCount;
        
        // Add document to list based on progress
        const docsToAdd = Math.floor((progress / 100) * totalDocuments) - processedDocCount;
        if (docsToAdd > 0) {
            for (let i = 0; i < docsToAdd; i++) {
                const docIndex = processedDocCount + i;
                if (docIndex < simulatedDocuments.length) {
                    // Add document to UI
                    addDocumentToList(simulatedDocuments[docIndex]);
                    
                    // Update current document display
                    if (currentDocValue) {
                        currentDocValue.textContent = simulatedDocuments[docIndex].fileName;
                    }
                }
            }
            processedDocCount += docsToAdd;
        }
        
        // Update status message based on progress
        if (progress < 25) {
            analysisState.analysisStatusText.textContent = 'Scanning document files...';
        } else if (progress < 50) {
            analysisState.analysisStatusText.textContent = 'Analyzing document sizes...';
        } else if (progress < 75) {
            analysisState.analysisStatusText.textContent = 'Calculating page counts...';
        } else {
            analysisState.analysisStatusText.textContent = 'Finalizing analysis...';
        }
        
        if (progress >= 100) {
            clearInterval(simulationInterval);
            
            // Hide the current document element when complete
            if (currentDocElement) {
                currentDocElement.style.display = 'none';
            }
            
            // Enable buttons
            analysisState.toStep3Btn.disabled = false;
            analysisState.resetAnalysisBtn.disabled = false;
            
            // Remove disabled styling from navigation buttons
            if (analysisState.toStep3Btn) {
                analysisState.toStep3Btn.classList.remove('disabled');
            }
            
            // Update status
            updateStatusBadge('completed', 'Analysis Complete');
            analysisState.analysisStatusText.textContent = 
                `Analysis complete. Found ${totalDocuments} documents with ${totalPages} pages.`;
            
            // Update workflow recommendation
            if (totalOversized > 0) {
                setWorkflowRecommendation('hybrid');
            } else {
                setWorkflowRecommendation('standard');
            }
            
            // Save analysis data
            saveAnalysisData(
                totalDocuments, 
                totalPages, 
                totalOversized, 
                documentsWithOversized, 
                'completed', 
                simulatedDocuments
            );
            
            // Show notification
            showNotification('Document analysis completed successfully!', 'success');
            
            // Set analysis status to completed
            analysisState.analysisStatus = 'completed';
        }
    }, 100);
}

/**
 * Generate simulated documents for demo
 * @param {number} totalDocs - Total number of documents to generate
 * @param {number} totalPages - Total number of pages across all documents
 * @param {number} totalOversized - Total number of oversized pages
 * @returns {Array} Array of simulated document objects
 */
function generateSimulatedDocuments(totalDocs, totalPages, totalOversized) {
    const documents = [];
    let oversizedLeft = totalOversized;
    let pagesLeft = totalPages;
    
    // Create documents with random properties
    for (let i = 0; i < totalDocs; i++) {
        const hasOversized = oversizedLeft > 0 && (Math.random() > 0.8 || i >= totalDocs - oversizedLeft);
        const docPages = Math.max(1, Math.floor(Math.random() * 20) + (hasOversized ? 5 : 1));
        const oversizedPages = hasOversized ? Math.min(oversizedLeft, Math.ceil(docPages * 0.3)) : 0;
        
        // Ensure we don't exceed totals
        pagesLeft -= docPages;
        if (pagesLeft < 0) break;
        
        if (hasOversized) {
            oversizedLeft -= oversizedPages;
        }
        
        // Generate oversized page details
        const oversizedDetails = [];
        if (oversizedPages > 0) {
            // Randomly select pages to be oversized
            const pageIndices = Array.from({ length: docPages }, (_, i) => i + 1);
            for (let j = 0; j < oversizedPages; j++) {
                const randomPageIndex = Math.floor(Math.random() * pageIndices.length);
                const pageNumber = pageIndices.splice(randomPageIndex, 1)[0];
                
                // Random dimensions that exceed the threshold
                const width = 842 + Math.floor(Math.random() * 600); // A3 width + random extra
                const height = 1191 + Math.floor(Math.random() * 600); // A3 height + random extra
                
                oversizedDetails.push({
                    pageNumber,
                    width,
                    height,
                    percentOverThreshold: Math.floor((width / 842 - 1) * 100)
                });
            }
            
            // Sort by page number
            oversizedDetails.sort((a, b) => a.pageNumber - b.pageNumber);
        }
        
        // Create document object
        documents.push({
            id: `DOC-${String(i + 1).padStart(3, '0')}`,
            fileName: `Document_${i + 1}.pdf`,
            pages: docPages,
            hasOversized: hasOversized,
            oversizedPages: oversizedPages,
            oversizedDetails: oversizedDetails,
            status: 'analyzed'
        });
    }
    
    return documents;
}

// Export functions for use in other modules
window.simulateDocumentAnalysis = simulateDocumentAnalysis;
window.generateSimulatedDocuments = generateSimulatedDocuments; 