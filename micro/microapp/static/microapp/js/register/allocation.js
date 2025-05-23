// allocation.js - Handles resource allocation functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize allocation component
    initAllocationComponent();
});

function initAllocationComponent() {
    console.log('Allocation component initialized');
    
    // Get URL parameters to determine flow type and project ID
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get('id');
    const processingMode = urlParams.get('mode') || 'auto';
    const flowType = urlParams.get('flow') || 'standard';
    
    console.log('[Allocation] Parameters:', { projectId, processingMode, flowType });
    
    // Get allocation elements
    const allocationForm = document.querySelector('#allocation-form');
    const resourceInputs = document.querySelectorAll('.resource-input');
    const totalAllocation = document.querySelector('#total-allocation');
    const statusBadge = document.querySelector('#step-5 .status-badge');
    const toStep6Btn = document.getElementById('to-step-6');

    // Auto-show 35mm film rolls if we're in hybrid flow
    const show35mmToggle = document.getElementById('show-35mm');
    const rolls35mm = document.getElementById('35mm-rolls');
    
    if (flowType === 'hybrid' && show35mmToggle && rolls35mm) {
        console.log('[Allocation] Hybrid flow detected, showing 35mm film rolls');
        show35mmToggle.checked = true;
        rolls35mm.classList.remove('hidden');
    }
    
    // Restore saved allocation if available
    const savedAllocation = loadStepData('allocation');
    if (savedAllocation) {
        resourceInputs.forEach(input => {
            const resourceId = input.getAttribute('data-resource-id');
            if (savedAllocation[resourceId] !== undefined) {
                input.value = savedAllocation[resourceId];
            }
        });
    }

    // Add event listeners
    if (allocationForm) {
        allocationForm.addEventListener('submit', handleAllocationSubmit);
    }
    
    // Add input change listeners to update totals
    resourceInputs.forEach(input => {
        input.addEventListener('input', updateTotals);
    });
    
    // --- Add film roll toggles and containers ---
    const show16mmToggle = document.getElementById('show-16mm');
    const rolls16mm = document.getElementById('16mm-rolls');
    const calculateAllocationBtn = document.getElementById('calculate-allocation');
    const resetAllocationBtn = document.getElementById('reset-allocation');
    const totalFilmsElem = document.getElementById('total-films');
    const pagesPerFilmElem = document.getElementById('pages-per-film');
    const allocationMethodSelect = document.getElementById('allocation-method');
    const maxCapacitySelect = document.getElementById('max-capacity');

    // --- Film type toggles ---
    if (show16mmToggle && rolls16mm) {
        show16mmToggle.addEventListener('change', function() {
            if (this.checked) {
                rolls16mm.classList.remove('hidden');
            } else {
                rolls16mm.classList.add('hidden');
            }
        });
    }
    if (show35mmToggle && rolls35mm) {
        show35mmToggle.addEventListener('change', function() {
            if (this.checked) {
                rolls35mm.classList.remove('hidden');
            } else {
                rolls35mm.classList.add('hidden');
            }
        });
    }

    // --- Calculate Allocation Button ---
    if (calculateAllocationBtn) {
        calculateAllocationBtn.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating...';

            if (statusBadge) {
                statusBadge.className = 'status-badge in-progress';
                statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Calculating Allocation';
            }

            // Get allocation parameters
            const allocationMethod = allocationMethodSelect ? allocationMethodSelect.value : 'balanced';
            const maxCapacity = maxCapacitySelect ? parseInt(maxCapacitySelect.value) : 90;

            setTimeout(() => {
                // Get document counts from previous steps
                let documentCount = parseInt(document.querySelector('.document-counter:nth-child(1) .counter-value')?.textContent || '0');
                let oversizedCount = parseInt(document.querySelector('.document-counter:nth-child(3) .counter-value')?.textContent || '0');

                // --- MOCK VALUES FOR TESTING ---
                if (documentCount === 0 && oversizedCount === 0) {
                    documentCount = 125;      // mock: 125 total documents
                    oversizedCount = 18;      // mock: 18 oversized
                }
                const standardCount = documentCount - oversizedCount;
                console.log('documentCount:', documentCount, 'oversizedCount:', oversizedCount, 'standardCount:', standardCount);

                // --- Generate 16mm films ---
                const films16mm = [];
                let remainingStandard = standardCount;
                let filmNumber = 1;
                const framesPerDoc = 7;
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

                // --- Generate 35mm films if oversized documents exist ---
                const films35mm = [];
                if (oversizedCount > 0) {
                    let remainingOversized = oversizedCount;
                    filmNumber = 1;
                    const framesPerOversizedDoc = 4;
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
                    if (show35mmToggle) show35mmToggle.checked = true;
                    if (rolls35mm) rolls35mm.classList.remove('hidden');
                }

                // --- Update film roll UI ---
                updateFilmRollUI(films16mm, films35mm);

                // --- Update summary statistics ---
                if (totalFilmsElem) totalFilmsElem.textContent = films16mm.length + films35mm.length;
                const totalFrames =
                    films16mm.reduce((sum, film) => sum + film.framesUsed, 0) +
                    films35mm.reduce((sum, film) => sum + film.framesUsed, 0);
                if (pagesPerFilmElem) {
                    const totalRolls = films16mm.length + films35mm.length;
                    pagesPerFilmElem.textContent = totalRolls > 0 ? Math.round(totalFrames / totalRolls) : 0;
                }

                // --- Update allocation data panel ---
                updateAllocationData('completed', allocationMethod, maxCapacity, films16mm, films35mm);

                // --- Reset button and update UI ---
                this.innerHTML = '<i class="fas fa-calculator"></i> Calculate Allocation';
                this.disabled = false;
                if (resetAllocationBtn) resetAllocationBtn.disabled = false;

                if (statusBadge) {
                    statusBadge.className = 'status-badge completed';
                    statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Allocation Complete';
                }

                if (toStep6Btn) {
                    toStep6Btn.disabled = false;
                }

                if (typeof showNotification === 'function') {
                    showNotification('Film allocation calculated successfully!', 'success');
                }

                console.log('films16mm:', films16mm, 'films35mm:', films35mm);
            }, 2000);
        });
    }

    // --- Reset Allocation Button ---
    if (resetAllocationBtn) {
        resetAllocationBtn.addEventListener('click', function() {
            // Remove all film rolls
            if (rolls16mm) {
                rolls16mm.querySelectorAll('.film-roll').forEach(container => container.remove());
            }
            if (rolls35mm) {
                rolls35mm.querySelectorAll('.film-roll').forEach(container => container.remove());
            }

            // Add back empty film roll templates
            if (rolls16mm) {
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
                const addBtn16mm = rolls16mm.querySelector('.add-roll-button');
                rolls16mm.insertBefore(roll16mm, addBtn16mm);
            }
            if (rolls35mm) {
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
                const addBtn35mm = rolls35mm.querySelector('.add-roll-button');
                rolls35mm.insertBefore(roll35mm, addBtn35mm);
            }

            if (totalFilmsElem) totalFilmsElem.textContent = '0';
            if (pagesPerFilmElem) pagesPerFilmElem.textContent = '0';

            updateAllocationData('pending', 'balanced', 90, [], []);

            if (statusBadge) {
                statusBadge.className = 'status-badge pending';
                statusBadge.innerHTML = '<i class="fas fa-clock"></i> Awaiting Calculation';
            }
            if (toStep6Btn) toStep6Btn.disabled = true;
            if (typeof showNotification === 'function') {
                showNotification('Film allocation reset', 'info');
            }
        });
    }

    // --- Helper functions for allocation data and visualization ---
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
        const dataOutput = document.querySelector('#step-5 .data-output');
        if (dataOutput) {
            dataOutput.textContent = JSON.stringify(allocData, null, 2);
        }
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

    function updateFilmRollUI(films16mm, films35mm) {
        try {
            // Ensure rolls16mm and rolls35mm are available
            if (!rolls16mm || !rolls35mm) return;
            // Only remove film rolls, not the add button
            rolls16mm.querySelectorAll('.film-roll:not(.add-roll-button)').forEach(container => container.remove());
            rolls35mm.querySelectorAll('.film-roll:not(.add-roll-button)').forEach(container => container.remove());
            // Add 16mm film rolls
            const addBtn16mm = rolls16mm.querySelector('.add-roll-button');
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
                    rolls16mm.insertBefore(rollElem, addBtn16mm);
                } else {
                    rolls16mm.appendChild(rollElem);
                }
            });
            // Add 35mm film rolls if any
            if (films35mm.length > 0) {
                const addBtn35mm = rolls35mm.querySelector('.add-roll-button');
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
                        rolls35mm.insertBefore(rollElem, addBtn35mm);
                    } else {
                        rolls35mm.appendChild(rollElem);
                    }
                });
            }
        } catch (err) {
            console.error("Error updating film roll UI:", err);
            if (typeof showNotification === 'function') {
                showNotification("Error updating film roll display. See console for details.", "error");
            }
        }
    }

    // Event handlers
    function handleAllocationSubmit(event) {
        event.preventDefault();
        if (validateAllocation()) {
            saveAllocationToStorage();
            if (statusBadge) {
                statusBadge.className = 'status-badge completed';
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Allocation Complete';
            }
            if (typeof showNotification === 'function') {
                showNotification('Resource allocation saved!', 'success');
            }
            if (toStep6Btn) toStep6Btn.disabled = false;
            // Optionally, auto-navigate to next step
            // window.registerComponent.showStep('step-6');
        } else {
            if (statusBadge) {
                statusBadge.className = 'status-badge error';
                statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Allocation Invalid';
            }
            if (typeof showNotification === 'function') {
                showNotification('Please check your allocation. The total must equal 100%.', 'error');
            }
            if (toStep6Btn) toStep6Btn.disabled = true;
        }
    }
    
    function updateTotals() {
        let total = 0;
        
        resourceInputs.forEach(input => {
            const value = parseFloat(input.value) || 0;
            total += value;
        });
        
        // Update total display
        if (totalAllocation) {
            totalAllocation.textContent = total.toFixed(2) + '%';
            
            // Add visual feedback
            if (Math.abs(total - 100) < 0.01) {
                totalAllocation.classList.add('valid');
                totalAllocation.classList.remove('invalid');
                if (statusBadge) {
                    statusBadge.className = 'status-badge completed';
                    statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Allocation Valid';
                }
                if (toStep6Btn) toStep6Btn.disabled = false;
            } else {
                totalAllocation.classList.add('invalid');
                totalAllocation.classList.remove('valid');
                if (statusBadge) {
                    statusBadge.className = 'status-badge error';
                    statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Allocation Invalid';
                }
                if (toStep6Btn) toStep6Btn.disabled = true;
            }
        }
        saveAllocationToStorage();
    }
    
    function validateAllocation() {
        let total = 0;
        
        resourceInputs.forEach(input => {
            const value = parseFloat(input.value) || 0;
            total += value;
        });
        
        // Check if total is approximately 100%
        return Math.abs(total - 100) < 0.01;
    }
    
    function saveAllocationToStorage() {
        const data = {};
        
        resourceInputs.forEach(input => {
            const resourceId = input.getAttribute('data-resource-id');
            data[resourceId] = parseFloat(input.value) || 0;
        });
        
        saveStepData('allocation', data);
    }
    
    // Initialize totals and status
    updateTotals();
    
    // Expose public methods
    window.allocationComponent = {
        validateAllocation,
        getAllocationData: () => {
            const data = {};
            
            resourceInputs.forEach(input => {
                const resourceId = input.getAttribute('data-resource-id');
                data[resourceId] = parseFloat(input.value) || 0;
            });
            
            return data;
        }
    };

    // Initialize back to analysis button
    const backToAnalysisBtn = document.getElementById('back-to-analysis');
    if (backToAnalysisBtn) {
        backToAnalysisBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Save current state before navigating
            const allocationData = window.allocationComponent.getAllocationData();
            saveStepData('allocation', allocationData);
            
            // Get URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const projectId = urlParams.get('id');
            const processingMode = urlParams.get('mode') || 'auto'; 
            const flowType = urlParams.get('flow') || 'standard';
            
            // Construct URL for document analysis page with both mode and flow parameters
            let url = '/register/document/?step=2';
            if (projectId) {
                url += '&id=' + encodeURIComponent(projectId);
            }
            url += '&mode=' + encodeURIComponent(processingMode);
            url += '&flow=' + encodeURIComponent(flowType);
            
            console.log('[Allocation] Navigating back to document analysis:', url);
            window.location.href = url;
        });
    }

    // Next button should go to index page (step-4)
    const toIndexBtn = document.getElementById('to-step-6');
    if (toIndexBtn) {
        toIndexBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Save current state before navigating
            const allocationData = window.allocationComponent.getAllocationData();
            saveStepData('allocation', allocationData);
            
            // Get URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const projectId = urlParams.get('id');
            const processingMode = urlParams.get('mode') || 'auto';
            const flowType = urlParams.get('flow') || 'standard';
            
            // Construct URL for index page with both mode and flow parameters
            let url = '/register/index/?step=4';
            if (projectId) {
                url += '&id=' + encodeURIComponent(projectId);
            }
            url += '&mode=' + encodeURIComponent(processingMode);
            url += '&flow=' + encodeURIComponent(flowType);
            
            console.log('[Allocation] Navigating to index page:', url);
            window.location.href = url;
        });
    }
}
