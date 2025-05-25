/**
 * temp-roll-details.js - Temp roll details functionality
 * Handles displaying detailed information about temp rolls
 */

class TempRollDetails {
    constructor() {
        this.dbService = new DatabaseService();
        this.currentTempRollId = null;
    }

    /**
     * Initialize the temp roll details module
     */
    initialize() {
        // Set up event listeners for detail modal
        this.setupEventListeners();
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Listen for showTempRollDetails events
        document.addEventListener('showTempRollDetails', (event) => {
            const { tempRollId } = event.detail;
            this.showDetails(tempRollId);
        });

        // Close modal events
        document.querySelectorAll('.close-modal').forEach(button => {
            button.addEventListener('click', () => {
                this.hideDetails();
            });
        });

        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.target.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });

        // Edit button
        document.getElementById('edit-temp-roll').addEventListener('click', () => {
            if (this.currentTempRollId) {
                const editEvent = new CustomEvent('editTempRoll', {
                    detail: { tempRollId: this.currentTempRollId }
                });
                document.dispatchEvent(editEvent);
                this.hideDetails();
            }
        });
    }

    /**
     * Show temp roll details in modal
     * @param {number|string} tempRollId - Temp Roll ID
     */
    async showDetails(tempRollId) {
        this.currentTempRollId = tempRollId;
        
        try {
            // Fetch temp roll data
            const response = await this.dbService.getTempRoll(tempRollId);
            
            // Handle different response structures
            let tempRoll;
            if (response.temp_roll) {
                // Response has a 'temp_roll' property
                tempRoll = response.temp_roll;
            } else if (response.temp_roll_id || response.id) {
                // Response is the temp roll object directly
                tempRoll = response;
            } else {
                throw new Error('Invalid response structure: no temp roll data found');
            }
            
            // Validate that we have a temp roll object
            if (!tempRoll) {
                throw new Error('Temp roll data is null or undefined');
            }
            
            console.log('Temp roll data received:', tempRoll); // Debug log
            
            // Update modal title
            const tempRollTitle = `Temp Roll #${tempRoll.temp_roll_id || tempRoll.id}`;
            document.getElementById('temp-roll-modal-title').textContent = `${tempRollTitle} Details`;
            
            // Populate details tab
            this.populateDetailsTab(tempRoll);
            
            // Load related items
            this.loadRelatedItems(tempRollId);
            
            // Load history
            this.loadHistory(tempRollId);
            
            // Show modal
            document.getElementById('temp-roll-detail-modal').style.display = 'flex';
            
            // Switch to details tab by default
            this.switchTab('details');
            
        } catch (error) {
            console.error('Error loading temp roll details:', error);
            console.error('Temp Roll ID:', tempRollId); // Debug log
            alert(`Error loading temp roll details: ${error.message || 'Unknown error'}`);
        }
    }

    /**
     * Hide the details modal
     */
    hideDetails() {
        document.getElementById('temp-roll-detail-modal').style.display = 'none';
        this.currentTempRollId = null;
    }

    /**
     * Switch between tabs in the modal
     * @param {string} tabName - Tab name (details, related, history)
     */
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-pane').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`temp-roll-${tabName}-tab`).classList.add('active');
    }

    /**
     * Populate the details tab with temp roll information
     * @param {Object} tempRoll - Temp roll data
     */
    populateDetailsTab(tempRoll) {
        const detailsContainer = document.querySelector('#temp-roll-details-tab .detail-properties');
        
        // Validate temp roll object
        if (!tempRoll) {
            detailsContainer.innerHTML = '<div class="error-message">No temp roll data available</div>';
            return;
        }
        
        // Calculate utilization with null checks
        const capacity = tempRoll.capacity || 0;
        const usableCapacity = tempRoll.usable_capacity || 0;
        const utilization = capacity > 0 ? (usableCapacity / capacity * 100).toFixed(1) : 100;
        
        // Safe property access with fallbacks
        const tempRollId = tempRoll.temp_roll_id || tempRoll.id || 'N/A';
        const filmType = tempRoll.film_type || 'Unknown';
        const status = tempRoll.status || 'Unknown';
        const creationDate = tempRoll.creation_date || 'N/A';
        const sourceRollId = tempRoll.source_roll_id || tempRoll.source_roll?.id || null;
        const sourceRollNumber = tempRoll.source_roll?.roll_id || tempRoll.source_roll_number || null;
        const usedByRollId = tempRoll.used_by_roll_id || tempRoll.used_by_roll?.id || null;
        const usedByRollNumber = tempRoll.used_by_roll?.roll_id || tempRoll.used_by_roll_number || null;
        
        detailsContainer.innerHTML = `
            <div class="temp-roll-detail-grid">
                <div class="temp-roll-detail-section">
                    <h3>Basic Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Temp Roll ID:</span>
                        <span class="detail-value">${tempRollId}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Film Type:</span>
                        <span class="detail-value">
                            <span class="temp-roll-film-type-badge" data-type="${filmType}">${filmType}</span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Status:</span>
                        <span class="detail-value">
                            <span class="temp-roll-status-badge ${status}">${status}</span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Creation Date:</span>
                        <span class="detail-value">${creationDate}</span>
                    </div>
                </div>
                
                <div class="temp-roll-detail-section">
                    <h3>Capacity Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Total Capacity:</span>
                        <span class="detail-value">${capacity} pages</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Usable Capacity:</span>
                        <span class="detail-value">${usableCapacity} pages</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Efficiency:</span>
                        <span class="detail-value">
                            <div class="temp-roll-capacity-display">
                                <div class="temp-roll-capacity-bar">
                                    <div class="temp-roll-capacity-fill" style="width: ${utilization}%"></div>
                                </div>
                                <span class="temp-roll-capacity-text">${utilization}%</span>
                            </div>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Capacity Difference:</span>
                        <span class="detail-value">${capacity - usableCapacity} pages</span>
                    </div>
                </div>
                
                <div class="temp-roll-detail-section">
                    <h3>Roll Relationships</h3>
                    <div class="detail-row">
                        <span class="detail-label">Source Roll:</span>
                        <span class="detail-value">
                            ${sourceRollId ? 
                                `<button class="view-related" data-id="${sourceRollId}" data-type="roll">
                                    Roll ${sourceRollNumber || sourceRollId}
                                </button>` : 
                                'No source roll'
                            }
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Used By Roll:</span>
                        <span class="detail-value">
                            ${usedByRollId ? 
                                `<button class="view-related" data-id="${usedByRollId}" data-type="roll">
                                    Roll ${usedByRollNumber || usedByRollId}
                                </button>` : 
                                'Not used yet'
                            }
                        </span>
                    </div>
                </div>
                
                <div class="temp-roll-detail-section">
                    <h3>Availability</h3>
                    <div class="detail-row">
                        <span class="detail-label">Can Accommodate:</span>
                        <span class="detail-value">
                            ${status === 'available' ? 
                                `Documents up to ${usableCapacity} pages` : 
                                'Not available for use'
                            }
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Recommended Use:</span>
                        <span class="detail-value">
                            ${usableCapacity > 100 ? 'Large documents' : 
                              usableCapacity > 50 ? 'Medium documents' : 
                              'Small documents'}
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners to view buttons
        document.querySelectorAll('.view-related').forEach(button => {
            button.addEventListener('click', (e) => {
                const id = e.target.closest('.view-related').getAttribute('data-id');
                const type = e.target.closest('.view-related').getAttribute('data-type');
                
                if (type === 'roll') {
                    const showRollEvent = new CustomEvent('showRollDetails', {
                        detail: { rollId: id }
                    });
                    document.dispatchEvent(showRollEvent);
                }
            });
        });
    }

    /**
     * Load related items (source roll, used by roll, etc.)
     * @param {number|string} tempRollId - Temp Roll ID
     */
    async loadRelatedItems(tempRollId) {
        const relatedContainer = document.querySelector('#temp-roll-related-tab .related-items');
        
        relatedContainer.innerHTML = `
            <div class="loading-message">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading related items...</p>
            </div>
        `;
        
        try {
            let relatedHtml = '<div class="temp-roll-related-items-container">';
            
            // Get the current temp roll data to extract relationship information
            const tempRollResponse = await this.dbService.getTempRoll(tempRollId);
            let tempRoll;
            if (tempRollResponse.temp_roll) {
                tempRoll = tempRollResponse.temp_roll;
            } else if (tempRollResponse.temp_roll_id || tempRollResponse.id) {
                tempRoll = tempRollResponse;
            } else {
                throw new Error('Invalid temp roll data structure');
            }
            
            // Source Roll Section
            try {
                console.log(`Loading source roll information for temp roll ${tempRollId}...`);
                
                relatedHtml += `
                    <div class="temp-roll-related-category">
                        <div class="temp-roll-related-category-header">
                            <h3 class="temp-roll-category-title">
                                <div class="temp-roll-category-icon">
                                    <i class="fas fa-film"></i>
                                </div>
                                Source Roll
                            </h3>
                            <span class="temp-roll-category-count">${tempRoll.source_roll_id ? '1' : '0'}</span>
                        </div>
                `;
                
                if (tempRoll.source_roll_id) {
                    try {
                        const rollResponse = await this.dbService.getRoll(tempRoll.source_roll_id);
                        let roll;
                        if (rollResponse.roll) {
                            roll = rollResponse.roll;
                        } else if (rollResponse.id || rollResponse.roll_id) {
                            roll = rollResponse;
                        }
                        
                        if (roll) {
                            // Calculate utilization
                            const capacity = roll.capacity || 0;
                            const pagesUsed = roll.pages_used || 0;
                            const utilization = capacity > 0 ? (pagesUsed / capacity * 100).toFixed(1) : 0;
                            
                            // Determine status
                            let statusClass = 'active';
                            let statusDisplay = roll.status || 'Active';
                            
                            if (roll.is_full) {
                                statusDisplay = 'Full';
                                statusClass = 'full';
                            } else if (roll.is_partial) {
                                statusDisplay = 'Partial';
                                statusClass = 'partial';
                            }
                            
                            relatedHtml += `
                                <div class="temp-roll-related-items-grid">
                                    <div class="temp-roll-related-item roll-item">
                                        <div class="temp-roll-related-item-header">
                                            <div class="temp-roll-related-item-main">
                                                <div class="temp-roll-related-item-title">${roll.film_number || 'No Film Number'}</div>
                                                <div class="temp-roll-related-item-subtitle">Roll ID: ${roll.roll_id || roll.id} - ${roll.film_type || 'Unknown'}</div>
                                            </div>
                                            <div class="temp-roll-related-item-id">Source</div>
                                        </div>
                                        <div class="temp-roll-related-item-meta">
                                            <span class="temp-roll-meta-tag film-type">${roll.film_type || 'Unknown'}</span>
                                            <span class="temp-roll-meta-tag capacity">${pagesUsed}/${capacity} pages</span>
                                            <span class="temp-roll-meta-tag status-${statusClass}">${statusDisplay}</span>
                                            <span class="temp-roll-meta-tag utilization">${utilization}% used</span>
                                        </div>
                                        <div class="temp-roll-related-item-actions">
                                            <button class="temp-roll-view-related" data-id="${roll.id || roll.roll_id}" data-type="roll">
                                                <i class="fas fa-eye"></i>
                                                View Roll
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            throw new Error('Source roll data not found');
                        }
                    } catch (rollError) {
                        console.log('Error fetching source roll details:', rollError.message || 'Unknown error');
                        relatedHtml += `
                            <div class="temp-roll-related-items-grid">
                                <div class="temp-roll-related-item roll-item">
                                    <div class="temp-roll-related-item-header">
                                        <div class="temp-roll-related-item-main">
                                            <div class="temp-roll-related-item-title">Roll ID: ${tempRoll.source_roll_id}</div>
                                            <div class="temp-roll-related-item-subtitle">Details unavailable</div>
                                        </div>
                                        <div class="temp-roll-related-item-id">Source</div>
                                    </div>
                                    <div class="temp-roll-related-item-meta">
                                        <span class="temp-roll-meta-tag error">Details unavailable</span>
                                    </div>
                                    <div class="temp-roll-related-item-actions">
                                        <button class="temp-roll-view-related" data-id="${tempRoll.source_roll_id}" data-type="roll">
                                            <i class="fas fa-eye"></i>
                                            View Roll
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                } else {
                    relatedHtml += `
                        <div class="temp-roll-empty-related">
                            <i class="fas fa-film temp-roll-empty-related-icon"></i>
                            <div class="temp-roll-empty-related-title">No Source Roll</div>
                            <div class="temp-roll-empty-related-subtitle">This temp roll was not created from an existing roll.</div>
                        </div>
                    `;
                }
                
                relatedHtml += '</div>'; // Close related-category
                
            } catch (sourceRollError) {
                console.error('Error loading source roll information:', sourceRollError);
                relatedHtml += `
                    <div class="temp-roll-related-category">
                        <div class="temp-roll-related-category-header">
                            <h3 class="temp-roll-category-title">
                                <div class="temp-roll-category-icon">
                                    <i class="fas fa-film"></i>
                                </div>
                                Source Roll
                            </h3>
                            <span class="temp-roll-category-count">Error</span>
                        </div>
                        <div class="error-message">
                            <p>Error loading source roll information: ${sourceRollError.message || 'Unknown error'}</p>
                        </div>
                    </div>
                `;
            }
            
            // Used By Roll Section
            try {
                console.log(`Loading used by roll information for temp roll ${tempRollId}...`);
                
                relatedHtml += `
                    <div class="temp-roll-related-category">
                        <div class="temp-roll-related-category-header">
                            <h3 class="temp-roll-category-title">
                                <div class="temp-roll-category-icon">
                                    <i class="fas fa-arrow-right"></i>
                                </div>
                                Used By Roll
                            </h3>
                            <span class="temp-roll-category-count">${tempRoll.used_by_roll_id ? '1' : '0'}</span>
                        </div>
                `;
                
                if (tempRoll.used_by_roll_id) {
                    try {
                        const rollResponse = await this.dbService.getRoll(tempRoll.used_by_roll_id);
                        let roll;
                        if (rollResponse.roll) {
                            roll = rollResponse.roll;
                        } else if (rollResponse.id || rollResponse.roll_id) {
                            roll = rollResponse;
                        }
                        
                        if (roll) {
                            // Calculate utilization
                            const capacity = roll.capacity || 0;
                            const pagesUsed = roll.pages_used || 0;
                            const utilization = capacity > 0 ? (pagesUsed / capacity * 100).toFixed(1) : 0;
                            
                            // Determine status
                            let statusClass = 'active';
                            let statusDisplay = roll.status || 'Active';
                            
                            if (roll.is_full) {
                                statusDisplay = 'Full';
                                statusClass = 'full';
                            } else if (roll.is_partial) {
                                statusDisplay = 'Partial';
                                statusClass = 'partial';
                            }
                            
                            relatedHtml += `
                                <div class="temp-roll-related-items-grid">
                                    <div class="temp-roll-related-item roll-item">
                                        <div class="temp-roll-related-item-header">
                                            <div class="temp-roll-related-item-main">
                                                <div class="temp-roll-related-item-title">${roll.film_number || 'No Film Number'}</div>
                                                <div class="temp-roll-related-item-subtitle">Roll ID: ${roll.roll_id || roll.id} - ${roll.film_type || 'Unknown'}</div>
                                            </div>
                                            <div class="temp-roll-related-item-id">Consumer</div>
                                        </div>
                                        <div class="temp-roll-related-item-meta">
                                            <span class="temp-roll-meta-tag film-type">${roll.film_type || 'Unknown'}</span>
                                            <span class="temp-roll-meta-tag capacity">${pagesUsed}/${capacity} pages</span>
                                            <span class="temp-roll-meta-tag status-${statusClass}">${statusDisplay}</span>
                                            <span class="temp-roll-meta-tag utilization">${utilization}% used</span>
                                        </div>
                                        <div class="temp-roll-related-item-actions">
                                            <button class="temp-roll-view-related" data-id="${roll.id || roll.roll_id}" data-type="roll">
                                                <i class="fas fa-eye"></i>
                                                View Roll
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            throw new Error('Used by roll data not found');
                        }
                    } catch (rollError) {
                        console.log('Error fetching used by roll details:', rollError.message || 'Unknown error');
                        relatedHtml += `
                            <div class="temp-roll-related-items-grid">
                                <div class="temp-roll-related-item roll-item">
                                    <div class="temp-roll-related-item-header">
                                        <div class="temp-roll-related-item-main">
                                            <div class="temp-roll-related-item-title">Roll ID: ${tempRoll.used_by_roll_id}</div>
                                            <div class="temp-roll-related-item-subtitle">Details unavailable</div>
                                        </div>
                                        <div class="temp-roll-related-item-id">Consumer</div>
                                    </div>
                                    <div class="temp-roll-related-item-meta">
                                        <span class="temp-roll-meta-tag error">Details unavailable</span>
                                    </div>
                                    <div class="temp-roll-related-item-actions">
                                        <button class="temp-roll-view-related" data-id="${tempRoll.used_by_roll_id}" data-type="roll">
                                            <i class="fas fa-eye"></i>
                                            View Roll
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                } else {
                    relatedHtml += `
                        <div class="temp-roll-empty-related">
                            <i class="fas fa-arrow-right temp-roll-empty-related-icon"></i>
                            <div class="temp-roll-empty-related-title">Not Used Yet</div>
                            <div class="temp-roll-empty-related-subtitle">This temp roll is available and has not been used by any roll yet.</div>
                        </div>
                    `;
                }
                
                relatedHtml += '</div>'; // Close related-category
                
            } catch (usedByRollError) {
                console.error('Error loading used by roll information:', usedByRollError);
                relatedHtml += `
                    <div class="temp-roll-related-category">
                        <div class="temp-roll-related-category-header">
                            <h3 class="temp-roll-category-title">
                                <div class="temp-roll-category-icon">
                                    <i class="fas fa-arrow-right"></i>
                                </div>
                                Used By Roll
                            </h3>
                            <span class="temp-roll-category-count">Error</span>
                        </div>
                        <div class="error-message">
                            <p>Error loading used by roll information: ${usedByRollError.message || 'Unknown error'}</p>
                        </div>
                    </div>
                `;
            }
            
            // Temp Roll Statistics Section
            relatedHtml += `
                <div class="temp-roll-related-category">
                    <div class="temp-roll-related-category-header">
                        <h3 class="temp-roll-category-title">
                            <div class="temp-roll-category-icon">
                                <i class="fas fa-chart-bar"></i>
                            </div>
                            Temp Roll Statistics
                        </h3>
                        <span class="temp-roll-category-count">Info</span>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${tempRoll.capacity || 0}</div>
                            <div class="stat-label">Total Capacity</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${tempRoll.usable_capacity || 0}</div>
                            <div class="stat-label">Usable Capacity</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${(tempRoll.capacity || 0) - (tempRoll.usable_capacity || 0)}</div>
                            <div class="stat-label">Padding</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${tempRoll.capacity > 0 ? ((tempRoll.usable_capacity || 0) / tempRoll.capacity * 100).toFixed(1) : 0}%</div>
                            <div class="stat-label">Efficiency</div>
                        </div>
                    </div>
                </div>
            `;
            
            relatedHtml += '</div>'; // Close related-items-container
            
            relatedContainer.innerHTML = relatedHtml;
            
            // Add event listeners to view buttons
            document.querySelectorAll('.temp-roll-view-related').forEach(button => {
                if (!button.disabled) {
                    button.addEventListener('click', (e) => {
                        const id = e.target.closest('.temp-roll-view-related').getAttribute('data-id');
                        const type = e.target.closest('.temp-roll-view-related').getAttribute('data-type');
                        
                        if (type === 'roll') {
                            const showRollEvent = new CustomEvent('showRollDetails', {
                                detail: { rollId: id }
                            });
                            document.dispatchEvent(showRollEvent);
                        }
                    });
                }
            });
            
        } catch (error) {
            console.error('Error loading related items:', error);
            relatedContainer.innerHTML = `
                <div class="temp-roll-related-items-container">
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Error loading related items: ${error.message || 'Unknown error'}</p>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Load temp roll history
     * @param {number|string} tempRollId - Temp Roll ID
     */
    async loadHistory(tempRollId) {
        const historyContainer = document.querySelector('#temp-roll-history-tab .history-timeline');
        
        historyContainer.innerHTML = `
            <div class="loading-message">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading history...</p>
            </div>
        `;
        
        try {
            // For now, show a placeholder
            historyContainer.innerHTML = `
                <div class="coming-soon-message">
                    <i class="fas fa-history"></i>
                    <p>Temp roll history tracking coming soon!</p>
                </div>
            `;
        } catch (error) {
            console.error('Error loading temp roll history:', error);
            historyContainer.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading history</p>
                </div>
            `;
        }
    }
}

// Export the class for use in the main module
window.TempRollDetails = TempRollDetails; 