// export.js - Handles the Export & Summary stage functionality

document.addEventListener('DOMContentLoaded', function() {
    // Load project data from localStorage
    loadProjectData();
    
    // Setup event listeners
    setupEventListeners();
});

/**
 * Get CSRF token from cookie - utility function for Django CSRF protection
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Load project data from localStorage and populate the UI
 */
function loadProjectData() {
    // Get data from localStorage
    const projectStateJSON = localStorage.getItem('microfilmProjectState');
    const analysisDataJSON = localStorage.getItem('microfilmAnalysisData');
    const allocationDataJSON = localStorage.getItem('microfilmAllocationData');
    const filmNumbersJSON = localStorage.getItem('microfilmFilmNumberResults');
    const indexDataJSON = localStorage.getItem('microfilmIndexData');
    const referenceSheetsJSON = localStorage.getItem('microfilmReferenceSheets');
    
    let projectState = null;
    let analysisData = null;
    let allocationData = null;
    let filmNumberData = null;
    let indexData = null;
    let referenceSheetsData = null;
    
    // Parse projectState if available
    if (projectStateJSON) {
        try {
            projectState = JSON.parse(projectStateJSON);
            
            // Update project header card
            updateProjectHeaderCard(projectState);
            
            console.log('Project data loaded successfully', projectState);
        } catch (error) {
            console.error('Error parsing project data:', error);
        }
    } else {
        console.warn('No project data found in localStorage');
    }
    
    // Parse analysis data if available
    if (analysisDataJSON) {
        try {
            analysisData = JSON.parse(analysisDataJSON);
            
            // Update summary stats using analysis data
            updateSummaryStats(projectState, analysisData, null);
            
            // Update document analysis summary
            updateDocumentAnalysisSummary(analysisData, projectState);
            
            console.log('Analysis data loaded successfully', analysisData);
        } catch (error) {
            console.error('Error parsing analysis data:', error);
        }
    } else {
        console.warn('No analysis data found in localStorage');
    }
    
    // Parse allocation data if available
    if (allocationDataJSON) {
        try {
            allocationData = JSON.parse(allocationDataJSON);
            
            // Update film allocation summary
            updateFilmAllocationSummary(allocationData);
            
            // Update summary stats with allocation data
            if (projectState) {
                updateSummaryStats(projectState, analysisData, allocationData);
            }
            
            console.log('Allocation data loaded successfully', allocationData);
        } catch (error) {
            console.error('Error parsing allocation data:', error);
        }
    } else {
        console.warn('No allocation data found in localStorage');
        
        // If no allocation data, still update summary stats with project and analysis data
        if (projectState) {
            updateSummaryStats(projectState, analysisData, null);
        }
    }
    
    // Parse film number data if available
    if (filmNumbersJSON) {
        try {
            filmNumberData = JSON.parse(filmNumbersJSON);
            
            // Update film number assignment summary
            updateFilmNumberAssignment(filmNumberData);
            
            console.log('Film number data loaded successfully', filmNumberData);
        } catch (error) {
            console.error('Error parsing film number data:', error);
        }
    } else {
        console.warn('No film number data found in localStorage');
    }
    
    // Parse index data if available
    if (indexDataJSON) {
        try {
            indexData = JSON.parse(indexDataJSON);
            
            // Update document index summary
            updateDocumentIndexSummary(indexData);
            
            console.log('Index data loaded successfully', indexData);
        } catch (error) {
            console.error('Error parsing index data:', error);
        }
    } else {
        console.warn('No index data found in localStorage');
    }
    
    // Parse reference sheets data if available
    if (referenceSheetsJSON) {
        try {
            referenceSheetsData = JSON.parse(referenceSheetsJSON);
            
            // Update reference sheets summary
            updateReferenceSheetsCard(referenceSheetsData);
            
            console.log('Reference sheets data loaded successfully', referenceSheetsData);
        } catch (error) {
            console.error('Error parsing reference sheets data:', error);
        }
    } else {
        console.warn('No reference sheets data found in localStorage');
    }
    
    // Load distribution results data if available
    const distributionDataJSON = localStorage.getItem('microfilmDistributionResults');
    if (distributionDataJSON) {
        try {
            const distributionData = JSON.parse(distributionDataJSON);
            
            // Update distribution results summary
            updateDistributionResults(distributionData);
            
            console.log('Distribution results data loaded successfully', distributionData);
        } catch (error) {
            console.error('Error parsing distribution results data:', error);
        }
    } else {
        console.warn('No distribution results data found in localStorage');
    }
}

/**
 * Update the project header card with data from microfilmProjectState
 */
function updateProjectHeaderCard(projectState) {
    // Update project title and metadata
    if (projectState.projectInfo) {
        document.getElementById('project-archive-id').textContent = projectState.projectInfo.archiveId || 'Unnamed Project';
        document.getElementById('project-location').textContent = `Location: ${projectState.projectInfo.location || 'Not specified'}`;
        document.getElementById('project-doc-type').textContent = `Document Type: ${projectState.projectInfo.documentType || 'Not specified'}`;
    }
    document.getElementById('project-id').textContent = projectState.projectId || 'Unknown';
}

/**
 * Update summary statistics with data from available sources
 */
function updateSummaryStats(projectState, analysisData, allocationData) {
    let documentCount = projectState?.sourceData?.fileCount || 0;
    let totalPages = 0;
    let totalSize = projectState?.sourceData?.totalSizeFormatted || '0 MB';
    let estimatedRolls = 0;
    
    // If we have analysis data, use it for more accurate document and page counts
    if (analysisData && analysisData.analysisResults) {
        documentCount = analysisData.analysisResults.documentCount || documentCount;
        totalPages = analysisData.analysisResults.pageCount || 0;
    }
    
    // If we have allocation data, use it for most accurate film roll count
    if (allocationData && allocationData.allocationResults) {
        const results = allocationData.allocationResults.results;
        if (results) {
            estimatedRolls = (results.total_rolls_16mm || 0) + (results.total_rolls_35mm || 0);
            
            // Update page count if not set by analysis data
            if (totalPages === 0) {
                totalPages = allocationData.allocationResults.totalPagesWithRefs || 0;
            }
        }
    } else {
        // Estimate film rolls based on total pages
        const estimatedRollCapacity = 300; // pages per roll (average)
        estimatedRolls = Math.ceil(totalPages / estimatedRollCapacity);
    }
    
    // Update summary stats
    document.getElementById('summary-documents').textContent = documentCount;
    document.getElementById('summary-pages').textContent = totalPages;
    document.getElementById('summary-size').textContent = totalSize;
    document.getElementById('summary-films').textContent = estimatedRolls;
}

/**
 * Update film allocation summary with data from microfilmAllocationData
 */
function updateFilmAllocationSummary(allocationData) {
    if (!allocationData || !allocationData.allocationResults) {
        console.warn('No valid allocation results found');
        return;
    }
    
    const allocation = allocationData.allocationResults;
    const results = allocation.results;
    
    if (!results) {
        console.warn('No allocation results data found');
        return;
    }
    
    // Update film roll stats
    const totalRolls16mm = results.total_rolls_16mm || 0;
    const totalRolls35mm = results.total_rolls_35mm || 0;
    const totalRolls = totalRolls16mm + totalRolls35mm;
    
    document.getElementById('film-rolls-16mm').textContent = totalRolls16mm;
    document.getElementById('film-rolls-35mm').textContent = totalRolls35mm;
    document.getElementById('total-film-rolls').textContent = totalRolls;
    
    // Calculate documents with split allocation (documents that appear in both 16mm and 35mm)
    const splitDocs = Object.keys(results.split_documents_16mm || {}).length + 
                      Object.keys(results.split_documents_35mm || {}).length;
    document.getElementById('docs-with-split-allocation').textContent = splitDocs;
    
    // Update utilization metrics
    document.getElementById('utilization-16mm').textContent = `${results.avg_utilization_16mm || 0}%`;
    document.getElementById('utilization-35mm').textContent = `${results.avg_utilization_35mm || 0}%`;
    
    // Calculate overall utilization (weighted average)
    const total16mmPages = results.total_pages_16mm || 0;
    const total35mmPages = results.total_pages_35mm || 0;
    const totalPages = total16mmPages + total35mmPages;
    
    let overallUtilization = 0;
    if (totalPages > 0) {
        overallUtilization = Math.round(
            ((total16mmPages * results.avg_utilization_16mm) + 
             (total35mmPages * results.avg_utilization_35mm)) / totalPages
        );
    }
    
    document.getElementById('overall-utilization-percent').textContent = `${overallUtilization}%`;
    document.getElementById('overall-utilization-path').setAttribute('stroke-dasharray', `${overallUtilization}, 100`);
    
    // Update allocation status
    const statusElement = document.getElementById('allocation-status');
    statusElement.textContent = capitalizeFirstLetter(allocation.status || 'not started');
    if (allocation.status === 'completed') {
        statusElement.classList.add('completed');
    } else if (allocation.status === 'in_progress') {
        statusElement.classList.add('in-progress');
    }
    
    // Update film utilization bars
    // 16mm Film
    const total16mmCapacity = (results.rolls_16mm || []).reduce((sum, roll) => sum + roll.capacity, 0);
    const used16mmPages = total16mmPages;
    
    const used16mmPercent = total16mmCapacity > 0 ? (used16mmPages / total16mmCapacity) * 100 : 0;
    
    document.getElementById('film-16mm-used').style.width = `${used16mmPercent}%`;
    document.getElementById('film-16mm-used-pages').textContent = `${used16mmPages} pages used`;
    document.getElementById('film-16mm-total-capacity').textContent = `${total16mmCapacity} total capacity`;
    
    // 35mm Film
    const total35mmCapacity = (results.rolls_35mm || []).reduce((sum, roll) => sum + roll.capacity, 0);
    const used35mmPages = total35mmPages;
    
    const used35mmPercent = total35mmCapacity > 0 ? (used35mmPages / total35mmCapacity) * 100 : 0;
    
    document.getElementById('film-35mm-used').style.width = `${used35mmPercent}%`;
    document.getElementById('film-35mm-used-pages').textContent = `${used35mmPages} pages used`;
    document.getElementById('film-35mm-total-capacity').textContent = `${total35mmCapacity} total capacity`;
    
    // Update total capacity and remaining capacity
    const totalCapacity = total16mmCapacity + total35mmCapacity;
    document.getElementById('total-film-capacity').textContent = `${totalCapacity} pages`;
    
    // Calculate total remaining capacity
    const remaining16mm = (results.partial_rolls_16mm || []).reduce((sum, roll) => sum + roll.remainingCapacity, 0);
    const remaining35mm = (results.partial_rolls_35mm || []).reduce((sum, roll) => sum + roll.remainingCapacity, 0);
    const totalRemaining = remaining16mm + remaining35mm;
    
    document.getElementById('remaining-capacity').textContent = `${totalRemaining} pages`;
    
    // Update document allocation details
    // Count unique documents on 16mm
    let uniqueDocs16mm = 0;
    if (results.rolls_16mm && results.rolls_16mm.length > 0) {
        const docIds = new Set();
        results.rolls_16mm.forEach(roll => {
            if (roll.document_segments) {
                roll.document_segments.forEach(segment => {
                    docIds.add(segment.doc_id);
                });
            }
        });
        uniqueDocs16mm = docIds.size;
    }
    document.getElementById('docs-on-16mm').textContent = uniqueDocs16mm;
    document.getElementById('pages-on-16mm').textContent = total16mmPages;
    
    // Count unique documents on 35mm
    let uniqueDocs35mm = 0;
    if (results.rolls_35mm && results.rolls_35mm.length > 0) {
        const docIds = new Set();
        results.rolls_35mm.forEach(roll => {
            if (roll.document_segments) {
                roll.document_segments.forEach(segment => {
                    docIds.add(segment.doc_id);
                });
            }
        });
        uniqueDocs35mm = docIds.size;
    }
    document.getElementById('docs-on-35mm').textContent = uniqueDocs35mm;
    document.getElementById('pages-on-35mm').textContent = total35mmPages;
    
    // Format and display allocation date
    if (results.creation_date) {
        const allocationDate = new Date(results.creation_date);
        const formattedDate = allocationDate.toLocaleDateString('en-US', {
            year: 'numeric', 
            month: 'short', 
            day: 'numeric'
        });
        document.getElementById('allocation-date').textContent = formattedDate;
    } else {
        document.getElementById('allocation-date').textContent = '--';
    }
}

/**
 * Update document analysis summary with data from microfilmAnalysisData
 */
function updateDocumentAnalysisSummary(analysisData, projectState) {
    // Get analysis results
    const analysis = analysisData.analysisResults;
    
    if (!analysis) {
        console.warn('No analysis results found in analysis data');
        return;
    }
    
    // Update project overview metrics
    document.getElementById('analysis-doc-count').textContent = analysis.documentCount;
    document.getElementById('analysis-page-count').textContent = analysis.pageCount;
    document.getElementById('analysis-workflow-type').textContent = capitalizeFirstLetter(analysis.recommendedWorkflow);
    
    // Format and display analysis date
    const analysisDate = new Date(analysis.timestamp);
    const formattedDate = analysisDate.toLocaleDateString('en-US', {
        year: 'numeric', 
        month: 'short', 
        day: 'numeric'
    });
    document.getElementById('analysis-completion-date').textContent = formattedDate;
    
    // Update document distribution
    const standardDocs = analysis.documentCount - analysis.documentsWithOversized;
    document.getElementById('standard-doc-count').textContent = standardDocs;
    document.getElementById('docs-with-oversized-count').textContent = analysis.documentsWithOversized;
    document.getElementById('oversized-page-count').textContent = analysis.oversizedCount;
    document.getElementById('reference-items-count').textContent = analysis.totalReferences;
    
    // Calculate page distribution for visualization
    const totalPages = analysis.pageCount;
    const oversizedPages = analysis.oversizedCount || 0;
    const referencePages = analysis.totalReferences || 0;
    const standardPages = totalPages - oversizedPages; // References are included in total, not separated
    
    // Calculate percentages
    const standardPercent = ((standardPages / totalPages) * 100).toFixed(1);
    const oversizedPercent = ((oversizedPages / totalPages) * 100).toFixed(1);
    const referencePercent = ((referencePages / totalPages) * 100).toFixed(1);
    
    // Update stacked bar segments
    document.getElementById('standard-pages-segment').style.width = `${standardPercent}%`;
    document.getElementById('oversized-pages-segment').style.width = `${oversizedPercent}%`;
    document.getElementById('reference-pages-segment').style.width = `${referencePercent}%`;
    
    // Update legend percentages
    document.getElementById('standard-pages-percent').textContent = `${standardPercent}%`;
    document.getElementById('oversized-pages-percent').textContent = `${oversizedPercent}%`;
    document.getElementById('reference-pages-percent').textContent = `${referencePercent}%`;
    
    // Update project completion - set to 95% if analysis is completed
    const completionPercent = analysis.status === 'completed' ? 95 : 75;
    document.getElementById('completion-circle-path').setAttribute('stroke-dasharray', `${completionPercent}, 100`);
    document.getElementById('completion-percentage').textContent = `${completionPercent}%`;
    
    // Find document with most oversized pages
    let maxOversizedDoc = { name: 'None', totalOversized: 0 };
    let totalOverSizingPercent = 0;
    let countOversizedPages = 0;
    
    if (analysis.documents && analysis.documents.length > 0) {
        analysis.documents.forEach(doc => {
            if (doc.totalOversized > maxOversizedDoc.totalOversized) {
                maxOversizedDoc = doc;
            }
            
            // Calculate average oversizing percentage
            if (doc.dimensions && doc.dimensions.length > 0) {
                doc.dimensions.forEach(dim => {
                    totalOverSizingPercent += dim.oversize_percent;
                    countOversizedPages++;
                });
            }
        });
    }
    
    // Update oversized document details
    document.getElementById('max-oversized-doc').textContent = maxOversizedDoc.name || 'None';
    
    // Calculate average oversizing percentage
    const avgOversizingPercent = countOversizedPages > 0 
        ? (totalOverSizingPercent / countOversizedPages).toFixed(1) 
        : 0;
    document.getElementById('avg-oversized-percent').textContent = `${avgOversizingPercent}%`;
    
    // Estimate film frames required (simple estimate)
    const estimatedFramesPerPage = 1.2; // Average of 1.2 frames per page
    const estimatedTotalFrames = Math.ceil(totalPages * estimatedFramesPerPage);
    document.getElementById('est-film-frames').textContent = `${estimatedTotalFrames} frames`;
}

/**
 * Helper function to capitalize the first letter of a string
 */
function capitalizeFirstLetter(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Setup event listeners for the export page
 */
function setupEventListeners() {
    // Back button
    const backButton = document.getElementById('back-to-step-7');
    if (backButton) {
        backButton.addEventListener('click', function() {
            window.location.href = '../distribution/';
        });
    }
    
    // Generate exports button
    const generateExportsButton = document.getElementById('generate-exports');
    if (generateExportsButton) {
        generateExportsButton.addEventListener('click', function() {
            generateExports();
        });
    }
    
    // Finish project button
    const finishProjectButton = document.getElementById('finish-project');
    if (finishProjectButton) {
        finishProjectButton.addEventListener('click', function() {
            finishProject();
        });
    }
    
    // View export buttons
    const viewButtons = document.querySelectorAll('.view-export-btn');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const exportType = this.getAttribute('data-type');
            viewExportFile(exportType);
        });
    });
    
    // Open output directory button
    const openOutputDirButton = document.getElementById('open-output-directory');
    if (openOutputDirButton) {
        openOutputDirButton.addEventListener('click', function() {
            openOutputDirectory();
        });
    }
}

/**
 * Generate export files
 */
function generateExports() {
    // Show progress bar
    const progressElement = document.getElementById('export-progress');
    progressElement.style.display = 'block';
    
    // Reset progress
    const progressBar = document.getElementById('export-progress-bar-inner');
    const progressText = document.getElementById('export-progress-text');
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    
    // Get project ID from localStorage
    const projectStateJSON = localStorage.getItem('microfilmProjectState');
    let projectId = null;
    
    if (projectStateJSON) {
        try {
            const projectState = JSON.parse(projectStateJSON);
            projectId = projectState.projectId;
        } catch (error) {
            console.error('Error parsing project state:', error);
        }
    }
    
    if (!projectId) {
        alert('Project ID not found. Cannot generate exports.');
        return;
    }
    
    // Start progress simulation
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 5;
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;
        
        // Stop at 90% - the actual API call will complete it
        if (progress >= 90) {
            clearInterval(progressInterval);
        }
    }, 200);
    
    // Important localStorage keys needed for export
    const keysToExport = [
        'microfilmProjectState',
        'microfilmAnalysisData',
        'microfilmAllocationData',
        'microfilmFilmNumberResults',
        'microfilmDistributionResults',
        'microfilmIndexData',
        'microfilmReferenceSheets'
    ];
    
    // Gather data from localStorage
    const exportData = {};
    keysToExport.forEach(key => {
        const data = localStorage.getItem(key);
        if (data) {
            try {
                exportData[key] = JSON.parse(data);
            } catch (e) {
                console.warn(`Failed to parse ${key} data, storing as string`);
                exportData[key] = data;
            }
        }
    });
    
    // First, export the data to create the directory structure
    fetch(`/api/export/${projectId}/save/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(exportData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(exportResult => {
        if (exportResult.status !== 'success') {
            throw new Error(`Failed to export data: ${exportResult.message}`);
        }
        
        // Get the export directory from the response
        const exportDir = exportResult.export_dir || '';
        console.log('Export directory created:', exportDir);
        
        // Now that data is exported, generate the exports
        return fetch(`/api/export/${projectId}/generate/?export_dir=${encodeURIComponent(exportDir)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                clearInterval(progressInterval);
                
                if (data.status === 'success') {
                    // Complete the progress bar
                    progressBar.style.width = '100%';
                    progressText.textContent = '100%';
                    
                    // Show available exports
                    document.getElementById('available-exports').style.display = 'block';
                    
                    // Store the output directory
                    const finalOutputDir = exportDir || (data.zip_path ? data.zip_path.substring(0, data.zip_path.lastIndexOf('/')) : 'Not available');
                    
                    // Update output directory display
                    document.getElementById('output-directory-path').textContent = finalOutputDir;
                    
                    // Store the path in a data attribute for easier retrieval
                    document.getElementById('output-directory-path').setAttribute('data-path', finalOutputDir);
                    
                    // Show and enable the output location card
                    document.getElementById('output-location').style.display = 'flex';
                    document.getElementById('open-output-directory').disabled = false;
                    
                    console.log('Exports generated successfully:', data);
                } else {
                    alert(`Failed to generate exports: ${data.message}`);
                    console.error('Export generation failed:', data);
                }
            });
    })
    .catch(error => {
        clearInterval(progressInterval);
        alert(`Error generating exports: ${error.message}`);
        console.error('Export generation error:', error);
        
        // Reset progress bar
        progressBar.style.width = '0%';
        progressText.textContent = '0%';
    });
}

/**
 * View an export file by revealing its location
 */
function viewExportFile(exportType) {
    console.log(`Viewing export file: ${exportType}`);
    
    // Get project ID from localStorage
    const projectStateJSON = localStorage.getItem('microfilmProjectState');
    let projectId = null;
    
    if (projectStateJSON) {
        try {
            const projectState = JSON.parse(projectStateJSON);
            projectId = projectState.projectId;
        } catch (error) {
            console.error('Error parsing project state:', error);
        }
    }
    
    if (!projectId) {
        alert('Project ID not found. Cannot locate export file.');
        return;
    }
    
    // Get the base directory
    const basePath = document.getElementById('output-directory-path').getAttribute('data-path');
    if (!basePath) {
        alert('Output directory path is not available.');
        return;
    }
    
    // Map export types to file names
    const exportFiles = {
        'index': 'index.csv',
        'summary': 'summary.json',
        'analysis': 'microfilmProjectState.json',
        'allocation': 'microfilmAllocationData.json',
        'filmnumbers': 'microfilmFilmNumberResults.json',
        'distribution': 'microfilmDistributionResults.json'
    };
    
    // Just open the directory as the reveal function doesn't select specific files
    openOutputDirectory(basePath);
}

/**
 * Handle finishing the project
 */
function finishProject() {
    console.log('Project finished');
    
    
}

/**
 * Open output directory
 */
function openOutputDirectory() {
    // Get the path from the data attribute
    const pathElement = document.getElementById('output-directory-path');
    const path = pathElement.getAttribute('data-path');
    
    console.log(`Opening output directory: ${path}`);
    
    // Validate path
    if (!path) {
        alert('Output directory path is not available.');
        return;
    }
    
    // Call the existing reveal-in-explorer endpoint (which uses POST method)
    fetch('/reveal-in-explorer/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `path=${encodeURIComponent(path)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Directory opened successfully');
        } else {
            alert('Failed to open directory');
        }
    })
    .catch(error => {
        alert(`Error opening directory: ${error.message}`);
        console.error('Error opening directory:', error);
    });
}

/**
 * Update film number assignment summary with data from microfilmFilmNumberResults
 */
function updateFilmNumberAssignment(filmNumberData) {
    if (!filmNumberData || !filmNumberData.results) {
        console.warn('No valid film number results found');
        return;
    }
    
    const results = filmNumberData.results;
    
    // Update assignment status
    const statusElement = document.getElementById('assignment-status');
    if (results.film_allocation_complete) {
        statusElement.textContent = 'Completed';
        statusElement.classList.add('completed');
    } else {
        statusElement.textContent = 'In Progress';
        statusElement.classList.add('in-progress');
    }
    
    // Get film rolls
    const film16mmRolls = results.rolls_16mm || [];
    const film35mmRolls = results.rolls_35mm || [];
    
    // Update total film numbers count
    const totalFilmNumbers = film16mmRolls.length + film35mmRolls.length;
    document.getElementById('total-film-numbers').textContent = totalFilmNumbers;
    
    // Find film number series start and end
    let allFilmNumbers = [];
    film16mmRolls.forEach(roll => {
        if (roll.film_number) {
            allFilmNumbers.push(roll.film_number);
        }
    });
    film35mmRolls.forEach(roll => {
        if (roll.film_number) {
            allFilmNumbers.push(roll.film_number);
        }
    });
    
    // Sort film numbers to find start and end
    if (allFilmNumbers.length > 0) {
        allFilmNumbers.sort();
        document.getElementById('film-number-series-start').textContent = allFilmNumbers[0];
        document.getElementById('film-number-series-end').textContent = allFilmNumbers[allFilmNumbers.length - 1];
    } else {
        document.getElementById('film-number-series-start').textContent = '--';
        document.getElementById('film-number-series-end').textContent = '--';
    }
    
    // Update film rolls overview
    updateFilmRollsList(film16mmRolls, '16mm');
    updateFilmRollsList(film35mmRolls, '35mm');
}

/**
 * Update film rolls list for a specific film type
 */
function updateFilmRollsList(filmRolls, filmType) {
    const containerId = `film-rolls-${filmType}-list`;
    const container = document.getElementById(containerId);
    
    // Clear existing content
    container.innerHTML = '';
    
    if (!filmRolls || filmRolls.length === 0) {
        // Display placeholder for empty list
        const placeholder = document.createElement('div');
        placeholder.className = 'film-roll-placeholder';
        placeholder.innerHTML = `<p>No ${filmType} film rolls available</p>`;
        container.appendChild(placeholder);
        return;
    }
    
    // Create film roll cards
    filmRolls.forEach(roll => {
        // Calculate utilization percentage
        const utilization = roll.capacity > 0 ? Math.round((roll.pages_used / roll.capacity) * 100) : 0;
        
        // Count documents in this roll
        const documentCount = roll.document_segments ? roll.document_segments.length : 0;
        
        // Create the film roll card
        const rollCard = document.createElement('div');
        rollCard.className = 'film-roll-card';
        
        // Create the roll header with film number and roll ID
        const rollHeader = document.createElement('div');
        rollHeader.className = 'film-roll-header';
        
        const filmNumber = document.createElement('div');
        filmNumber.className = 'film-number';
        filmNumber.textContent = roll.film_number || 'No Number Assigned';
        
        const rollId = document.createElement('div');
        rollId.className = 'roll-id';
        rollId.textContent = roll.roll_id ? `Roll ID: ${roll.roll_id}` : '';
        
        rollHeader.appendChild(filmNumber);
        rollHeader.appendChild(rollId);
        rollCard.appendChild(rollHeader);
        
        // Create the metrics grid
        const metricsGrid = document.createElement('div');
        metricsGrid.className = 'film-roll-metrics';
        
        // Capacity metric
        const capacityMetric = document.createElement('div');
        capacityMetric.className = 'metric-item';
        capacityMetric.innerHTML = `
            <div class="metric-label">Total Capacity</div>
            <div class="metric-value">${roll.capacity || 0} frames</div>
        `;
        metricsGrid.appendChild(capacityMetric);
        
        // Pages used metric
        const pagesMetric = document.createElement('div');
        pagesMetric.className = 'metric-item';
        pagesMetric.innerHTML = `
            <div class="metric-label">Pages Used</div>
            <div class="metric-value">${roll.pages_used || 0} pages</div>
        `;
        metricsGrid.appendChild(pagesMetric);
        
        // Utilization metric
        const utilizationMetric = document.createElement('div');
        utilizationMetric.className = 'metric-item';
        utilizationMetric.innerHTML = `
            <div class="metric-label">Utilization</div>
            <div class="metric-value">${utilization}%</div>
        `;
        metricsGrid.appendChild(utilizationMetric);
        
        // Remaining capacity metric
        const remainingMetric = document.createElement('div');
        remainingMetric.className = 'metric-item';
        remainingMetric.innerHTML = `
            <div class="metric-label">Remaining</div>
            <div class="metric-value">${roll.pages_remaining || 0} frames</div>
        `;
        metricsGrid.appendChild(remainingMetric);
        
        rollCard.appendChild(metricsGrid);
        
        // Create usage bar
        const usageBar = document.createElement('div');
        usageBar.className = 'film-usage-bar';
        
        const usageFill = document.createElement('div');
        usageFill.className = 'film-usage-fill';
        usageFill.style.width = `${utilization}%`;
        
        usageBar.appendChild(usageFill);
        rollCard.appendChild(usageBar);
        
        // Create documents info
        const documentsInfo = document.createElement('div');
        documentsInfo.className = 'film-roll-documents';
        documentsInfo.innerHTML = `
            <span>${documentCount} document${documentCount !== 1 ? 's' : ''}</span>
            <span>Frame range: 1-${roll.pages_used || 0}</span>
        `;
        rollCard.appendChild(documentsInfo);
        
        // Add card to container
        container.appendChild(rollCard);
    });
}

/**
 * Update document index summary with data from microfilmIndexData
 */
function updateDocumentIndexSummary(indexData) {
    if (!indexData || !indexData.indexData) {
        console.warn('No valid index data found');
        return;
    }
    
    const index = indexData.indexData.index;
    
    // Update document count for the preview note
    const documentCount = index ? index.length : 0;
    document.getElementById('index-total-count').textContent = documentCount;
    
    // Update index preview table
    updateIndexPreviewTable(index);
}

/**
 * Update the index preview table with data from the index
 */
function updateIndexPreviewTable(index) {
    const previewBody = document.getElementById('index-preview-body');
    
    // Clear existing content
    previewBody.innerHTML = '';
    
    if (!index || index.length === 0) {
        // If no documents, show placeholder
        const placeholderRow = document.createElement('tr');
        placeholderRow.className = 'index-preview-placeholder';
        placeholderRow.innerHTML = '<td colspan="4">No index data available</td>';
        previewBody.appendChild(placeholderRow);
        return;
    }
    
    // Display all documents (not limited to 5)
    index.forEach(item => {
        // Extract data from the index item
        // Format: [filename, document_id, [film_number, start_frame, end_frame], additional_info, sequence]
        const fileName = item[0];
        const documentId = item[1];
        const filmInfo = item[2]; // [film_number, start_frame, end_frame]
        const sequence = item[4];
        
        // Create simplified frame range text
        let frameRange = '--';
        if (filmInfo && filmInfo.length >= 3) {
            frameRange = `${filmInfo[1]}-${filmInfo[2]}`;
        }
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${fileName}</td>
            <td>${documentId}</td>
            <td>${frameRange}</td>
            <td>${sequence}</td>
        `;
        previewBody.appendChild(row);
    });
}

/**
 * Update reference sheets card with data from microfilmReferenceSheets
 */
function updateReferenceSheetsCard(referenceSheetsData) {
    if (!referenceSheetsData || !referenceSheetsData.reference_sheets) {
        console.warn('No valid reference sheets data found');
        return;
    }
    
    // Get total sheets count and documents with references count
    const sheetsCreated = referenceSheetsData.sheets_created || 0;
    const documentsWithReferences = Object.keys(referenceSheetsData.reference_sheets).length || 0;
    
    // Update reference overview
    document.getElementById('reference-total-sheets').textContent = sheetsCreated;
    document.getElementById('reference-doc-count').textContent = documentsWithReferences;
    document.getElementById('reference-sheets-count').textContent = sheetsCreated;
    
    // Update reference sheets table
    updateReferenceSheetsTable(referenceSheetsData);
}

/**
 * Update the reference sheets table with data
 */
function updateReferenceSheetsTable(referenceSheetsData) {
    const sheetsBody = document.getElementById('reference-sheets-body');
    
    // Clear existing content
    sheetsBody.innerHTML = '';
    
    if (!referenceSheetsData.reference_sheets || Object.keys(referenceSheetsData.reference_sheets).length === 0) {
        // If no reference sheets, show placeholder
        const placeholderRow = document.createElement('tr');
        placeholderRow.className = 'reference-sheets-placeholder';
        placeholderRow.innerHTML = '<td colspan="4">No reference sheets available</td>';
        sheetsBody.appendChild(placeholderRow);
        return;
    }
    
    // Collect all reference sheets
    let allSheets = [];
    
    // For each document with references
    for (const [docName, sheets] of Object.entries(referenceSheetsData.reference_sheets)) {
        // Add each sheet with document name
        sheets.forEach(sheet => {
            allSheets.push({
                document: docName,
                pageRange: sheet.range.join('-'),
                sheetId: sheet.id,
                filmNumber: ''
            });
        });
    }
    
    // Add film numbers if available in documents_details
    if (referenceSheetsData.documents_details) {
        for (const [docName, details] of Object.entries(referenceSheetsData.documents_details)) {
            // If this document has film_numbers
            if (details.film_numbers && details.sheet_ids) {
                // Match sheet IDs with film numbers
                for (let i = 0; i < details.sheet_ids.length; i++) {
                    const sheetId = details.sheet_ids[i];
                    const filmNumber = details.film_numbers[i];
                    
                    // Find the sheet in allSheets and add the film number
                    const sheet = allSheets.find(s => s.document === docName && s.sheetId === sheetId);
                    if (sheet) {
                        sheet.filmNumber = filmNumber;
                    }
                }
            }
        }
    }
    
    // Sort sheets by document name and then sheet ID
    allSheets.sort((a, b) => {
        if (a.document !== b.document) {
            return a.document.localeCompare(b.document);
        }
        return a.sheetId - b.sheetId;
    });
    
    // Create table rows
    allSheets.forEach(sheet => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${sheet.document}</td>
            <td>${sheet.pageRange}</td>
            <td>${sheet.sheetId}</td>
            <td>${sheet.filmNumber || '--'}</td>
        `;
        sheetsBody.appendChild(row);
    });
}

/**
 * Update distribution results with data from microfilmDistributionResults
 */
function updateDistributionResults(distributionData) {
    if (!distributionData || !distributionData.results) {
        console.warn('No valid distribution results found');
        return;
    }
    
    const results = distributionData.results;
    
    // Update document distribution metrics
    const standardDocs = results.processed_files.filter(file => !file.is_oversized).length;
    const oversizedDocs = results.oversized_documents_extracted || 0;
    const docsWithRefs = results.documents_with_references || 0;
    const referenceSheets = results.reference_sheets || 0;
    
    document.getElementById('distribution-standard-docs').textContent = standardDocs;
    document.getElementById('distribution-oversized-docs').textContent = oversizedDocs;
    document.getElementById('distribution-docs-with-refs').textContent = docsWithRefs;
    document.getElementById('distribution-reference-sheets').textContent = referenceSheets;
    
    // Update film distribution metrics
    const docs16mm = results.processed_16mm_documents || 0;
    const docs35mm = results.processed_35mm_documents || 0;
    const totalDocs = docs16mm + docs35mm;
    
    document.getElementById('distribution-16mm-docs').textContent = docs16mm;
    document.getElementById('distribution-35mm-docs').textContent = docs35mm;
    
    // Update distribution status
    const statusElement = document.getElementById('distribution-status');
    statusElement.textContent = capitalizeFirstLetter(distributionData.status || 'not started');
    if (distributionData.status === 'completed') {
        statusElement.classList.add('completed');
    } else if (distributionData.status === 'in_progress') {
        statusElement.classList.add('in-progress');
    }
    
    // Format and display completion date
    if (results.completed_at) {
        const completionDate = new Date(results.completed_at);
        const formattedDate = completionDate.toLocaleDateString('en-US', {
            year: 'numeric', 
            month: 'short', 
            day: 'numeric'
        });
        document.getElementById('distribution-completion-date').textContent = formattedDate;
    } else {
        document.getElementById('distribution-completion-date').textContent = '--';
    }
    
    // Update output directory
    document.getElementById('distribution-output-dir').textContent = results.output_dir || 'Not available';
    
    // Update processing metrics
    const totalProcessed = results.processed_16mm_documents + results.processed_35mm_documents;
    const totalCopied = results.copied_16mm_documents + results.copied_35mm_documents;
    document.getElementById('distribution-processed-docs').textContent = totalProcessed;
    document.getElementById('distribution-copied-docs').textContent = totalCopied;
    
    // Calculate and update film type distribution percentages
    if (totalDocs > 0) {
        const percent16mm = Math.round((docs16mm / totalDocs) * 100);
        const percent35mm = Math.round((docs35mm / totalDocs) * 100);
        
        document.getElementById('distribution-16mm-segment').style.width = `${percent16mm}%`;
        document.getElementById('distribution-35mm-segment').style.width = `${percent35mm}%`;
        document.getElementById('distribution-16mm-percent').textContent = `${percent16mm}%`;
        document.getElementById('distribution-35mm-percent').textContent = `${percent35mm}%`;
    }
}
