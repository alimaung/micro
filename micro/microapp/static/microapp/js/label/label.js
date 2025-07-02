// Label Management JavaScript

class LabelManager {
    constructor() {
        this.selectedUncompletedRolls = new Set();
        this.selectedCompletedRolls = new Set();
        this.generatedLabels = [];
        this.labelsByRoll = new Map(); // Map of roll_id -> {normal: label, angled: label}
        this.printQueue = [];
        this.uncompletedRolls = [];
        this.completedRolls = [];
        this.customLabels = { normal: null, angled: null }; // Store custom generated labels
        this.init();
    }
    
    init() {
        console.log('Label Manager initialized');
        this.bindEvents();
        this.loadInitialData();
    }
    
    bindEvents() {
        // Custom Label Section
        const openCustomLabelBtn = document.getElementById('open-custom-label');
        if (openCustomLabelBtn) {
            openCustomLabelBtn.addEventListener('click', () => {
                this.toggleCustomLabelSection(true);
            });
        }
        
        const closeCustomLabelBtn = document.getElementById('close-custom-label');
        if (closeCustomLabelBtn) {
            closeCustomLabelBtn.addEventListener('click', () => {
                this.toggleCustomLabelSection(false);
            });
        }
        
        // Custom Label Form Inputs
        const customOrderId = document.getElementById('custom-order-id');
        if (customOrderId) {
            customOrderId.addEventListener('input', () => {
                this.formatOrderId(customOrderId);
                this.validateCustomForm();
            });
        }
        
        const customFilmNumber = document.getElementById('custom-film-number');
        if (customFilmNumber) {
            customFilmNumber.addEventListener('input', this.validateCustomForm.bind(this));
        }
        
        const customDocType = document.getElementById('custom-doc-type');
        if (customDocType) {
            customDocType.addEventListener('input', () => {
                this.updateDocTypeCharCount();
                this.validateCustomForm();
            });
        }
        
        // Generate Custom Label Button
        const generateCustomLabelBtn = document.getElementById('generate-custom-label');
        if (generateCustomLabelBtn) {
            generateCustomLabelBtn.addEventListener('click', () => {
                this.generateCustomLabels();
            });
        }
        
        // Custom Label Actions
        const viewCustomNormalBtn = document.getElementById('view-custom-normal');
        if (viewCustomNormalBtn) {
            viewCustomNormalBtn.addEventListener('click', () => {
                this.viewCustomLabel('normal');
            });
        }
        
        const downloadCustomNormalBtn = document.getElementById('download-custom-normal');
        if (downloadCustomNormalBtn) {
            downloadCustomNormalBtn.addEventListener('click', () => {
                this.downloadCustomLabel('normal');
            });
        }
        
        const printCustomNormalBtn = document.getElementById('print-custom-normal');
        if (printCustomNormalBtn) {
            printCustomNormalBtn.addEventListener('click', () => {
                this.printCustomLabel('normal');
            });
        }
        
        const viewCustomAngledBtn = document.getElementById('view-custom-angled');
        if (viewCustomAngledBtn) {
            viewCustomAngledBtn.addEventListener('click', () => {
                this.viewCustomLabel('angled');
            });
        }
        
        const downloadCustomAngledBtn = document.getElementById('download-custom-angled');
        if (downloadCustomAngledBtn) {
            downloadCustomAngledBtn.addEventListener('click', () => {
                this.downloadCustomLabel('angled');
            });
        }
        
        const printCustomAngledBtn = document.getElementById('print-custom-angled');
        if (printCustomAngledBtn) {
            printCustomAngledBtn.addEventListener('click', () => {
                this.printCustomLabel('angled');
            });
        }
        
        // Refresh buttons
        const refreshUncompletedBtn = document.getElementById('refresh-uncompleted-rolls');
        if (refreshUncompletedBtn) {
            refreshUncompletedBtn.addEventListener('click', () => {
                this.loadRolls();
            });
        }
        
        const refreshCompletedBtn = document.getElementById('refresh-completed-rolls');
        if (refreshCompletedBtn) {
            refreshCompletedBtn.addEventListener('click', () => {
            this.loadRolls();
        });
        }
        
        const refreshQueueBtn = document.getElementById('refresh-queue');
        if (refreshQueueBtn) {
            refreshQueueBtn.addEventListener('click', () => {
                this.loadGeneratedLabels();
        });
        }
        
        // Bulk actions for uncompleted rolls
        const selectAllUncompletedBtn = document.getElementById('select-all-uncompleted');
        if (selectAllUncompletedBtn) {
            selectAllUncompletedBtn.addEventListener('click', () => {
                this.selectAllUncompleted();
        });
        }
        
        const clearUncompletedSelectionBtn = document.getElementById('clear-uncompleted-selection');
        if (clearUncompletedSelectionBtn) {
            clearUncompletedSelectionBtn.addEventListener('click', () => {
                this.clearUncompletedSelection();
        });
        }
        
        const generateUncompletedBtn = document.getElementById('generate-uncompleted');
        if (generateUncompletedBtn) {
            generateUncompletedBtn.addEventListener('click', () => {
                this.generateUncompletedLabels();
            });
        }
        
        // Bulk actions for completed rolls
        const selectAllCompletedBtn = document.getElementById('select-all-completed');
        if (selectAllCompletedBtn) {
            selectAllCompletedBtn.addEventListener('click', () => {
                this.selectAllCompleted();
            });
        }
        
        const clearCompletedSelectionBtn = document.getElementById('clear-completed-selection');
        if (clearCompletedSelectionBtn) {
            clearCompletedSelectionBtn.addEventListener('click', () => {
                this.clearCompletedSelection();
            });
        }
        
        const viewCompletedLabelsBtn = document.getElementById('view-completed-labels');
        if (viewCompletedLabelsBtn) {
            viewCompletedLabelsBtn.addEventListener('click', () => {
                this.viewSelectedCompletedLabels();
        });
        }
        
        const clearGeneratedBtn = document.getElementById('clear-generated');
        if (clearGeneratedBtn) {
            clearGeneratedBtn.addEventListener('click', () => {
            this.clearGeneratedLabels();
        });
        }
        
        const showAllLabelsBtn = document.getElementById('show-all-labels');
        if (showAllLabelsBtn) {
            showAllLabelsBtn.addEventListener('click', () => {
                this.showAllLabels();
            });
        }
        
        // Download actions
        const downloadAllNormalBtn = document.getElementById('download-all-normal');
        if (downloadAllNormalBtn) {
            downloadAllNormalBtn.addEventListener('click', () => {
                this.downloadAllLabels('normal');
            });
        }
        
        const downloadAllAngledBtn = document.getElementById('download-all-angled');
        if (downloadAllAngledBtn) {
            downloadAllAngledBtn.addEventListener('click', () => {
                this.downloadAllLabels('angled');
            });
        }
        
        // Print actions
        const printAllNormalBtn = document.getElementById('print-all-normal');
        if (printAllNormalBtn) {
            printAllNormalBtn.addEventListener('click', () => {
                this.printAllLabels('normal');
            });
        }
        
        const printAllAngledBtn = document.getElementById('print-all-angled');
        if (printAllAngledBtn) {
            printAllAngledBtn.addEventListener('click', () => {
                this.printAllLabels('angled');
            });
        }
        
        // Dynamic event delegation for roll cards and label actions
        document.addEventListener('click', (e) => {
            if (e.target.closest('.roll-card')) {
                this.handleRollClick(e.target.closest('.roll-card'));
            }
            
            if (e.target.closest('.download-label')) {
                this.downloadLabel(e.target.closest('.download-label').dataset.labelId, e.target.closest('.download-label').dataset.version);
            }
            
            if (e.target.closest('.view-label')) {
                this.viewLabel(e.target.closest('.view-label').dataset.labelId, e.target.closest('.view-label').dataset.version);
            }
            
            if (e.target.closest('.open-label')) {
                this.openLabel(e.target.closest('.open-label').dataset.labelId, e.target.closest('.open-label').dataset.version);
            }
            
            if (e.target.closest('.print-label')) {
                this.printLabel(e.target.closest('.print-label').dataset.labelId, e.target.closest('.print-label').dataset.version);
            }
        });
    }
    
    // Custom Label Methods
    toggleCustomLabelSection(show) {
        const section = document.getElementById('custom-label-section');
        if (section) {
            section.style.display = show ? 'block' : 'none';
            
            // Reset form and preview when opening
            if (show) {
                this.resetCustomLabelForm();
            }
        }
    }
    
    resetCustomLabelForm() {
        const orderIdInput = document.getElementById('custom-order-id');
        const filmNumberInput = document.getElementById('custom-film-number');
        const docTypeInput = document.getElementById('custom-doc-type');
        const preview = document.getElementById('custom-label-preview');
        
        if (orderIdInput) orderIdInput.value = '';
        if (filmNumberInput) filmNumberInput.value = '';
        if (docTypeInput) docTypeInput.value = '';
        if (preview) preview.style.display = 'none';
        
        this.updateDocTypeCharCount();
        this.validateCustomForm();
        
        // Reset stored custom labels
        this.customLabels = { normal: null, angled: null };
    }
    
    updateDocTypeCharCount() {
        const docTypeInput = document.getElementById('custom-doc-type');
        const charCountSpan = document.getElementById('doc-type-char-count');
        
        if (docTypeInput && charCountSpan) {
            const currentLength = docTypeInput.value.length;
            charCountSpan.textContent = currentLength;
            
            // Add visual feedback if approaching limit
            if (currentLength > 200) {
                charCountSpan.style.color = 'var(--color-warning)';
            } else {
                charCountSpan.style.color = '';
            }
        }
    }
    
    validateCustomForm() {
        const orderIdInput = document.getElementById('custom-order-id');
        const filmNumberInput = document.getElementById('custom-film-number');
        const docTypeInput = document.getElementById('custom-doc-type');
        const generateBtn = document.getElementById('generate-custom-label');
        
        let isValid = true;
        
        // Order ID validation (RRD followed by XXX-YYYY format)
        if (orderIdInput) {
            const orderIdPattern = /^RRD[0-9]{3}-[0-9]{4}$/;
            const isOrderIdValid = orderIdPattern.test(orderIdInput.value);
            orderIdInput.classList.toggle('invalid', !isOrderIdValid);
            isValid = isValid && isOrderIdValid;
        }
        
        // Film Number validation (must be either 8 digits starting with 1 or 3, or 6 digits)
        if (filmNumberInput) {
            const filmNumberPattern = /^([13][0-9]{7}|[0-9]{6})$/;
            const isFilmNumberValid = filmNumberPattern.test(filmNumberInput.value);
            filmNumberInput.classList.toggle('invalid', !isFilmNumberValid);
            isValid = isValid && isFilmNumberValid;
        }
        
        // Document Type validation (must not be empty and <= 250 chars)
        if (docTypeInput) {
            const isDocTypeValid = docTypeInput.value.trim().length > 0 && 
                                  docTypeInput.value.length <= 250;
            docTypeInput.classList.toggle('invalid', !isDocTypeValid);
            isValid = isValid && isDocTypeValid;
        }
        
        // Enable/disable generate button based on validation
        if (generateBtn) {
            generateBtn.disabled = !isValid;
        }
        
        return isValid;
    }
    
    // Add a new method to format the order ID field
    formatOrderId(input) {
        // If the input doesn't start with "RRD", add it
        if (!input.value.startsWith('RRD')) {
            input.value = 'RRD' + input.value.replace(/^RRD/, '');
        }
        
        // Extract just the digits
        const digits = input.value.replace(/[^0-9]/g, '');
        
        // Format as RRDxxx-yyyy if we have enough digits
        if (digits.length > 3) {
            const part1 = digits.substring(0, 3);
            const part2 = digits.substring(3, 7);
            input.value = `RRD${part1}-${part2}`;
        } else if (digits.length > 0) {
            // Just add RRD prefix to the digits
            input.value = `RRD${digits}`;
        }
    }
    
    async generateCustomLabels() {
        if (!this.validateCustomForm()) {
            this.showNotification('warning', 'Invalid Input', 'Please check the form fields and try again.');
            return;
        }
        
        const orderIdInput = document.getElementById('custom-order-id');
        const filmNumberInput = document.getElementById('custom-film-number');
        const docTypeInput = document.getElementById('custom-doc-type');
        
        // Use the order ID value directly (RRD is already included)
        const archiveId = orderIdInput.value;
        const filmNumber = filmNumberInput.value;
        const docType = docTypeInput.value;
        
        try {
            this.showNotification('info', 'Generating Labels', 'Creating custom labels...');
            
            const response = await fetch('/api/labels/generate-custom/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    archive_id: archiveId,
                    film_number: filmNumber,
                    doc_type: docType
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'Labels Generated', 'Custom labels created successfully');
                
                // Store the generated labels
                this.customLabels = {
                    normal: data.labels.normal,
                    angled: data.labels.angled
                };
                
                // Show the preview section
                const previewSection = document.getElementById('custom-label-preview');
                if (previewSection) {
                    previewSection.style.display = 'block';
                }
            } else {
                throw new Error(data.error || 'Failed to generate custom labels');
            }
        } catch (error) {
            console.error('Error generating custom labels:', error);
            this.showNotification('error', 'Generation Failed', `Failed to generate custom labels: ${error.message}`);
        }
    }
    
    async viewCustomLabel(version) {
        if (!this.customLabels[version]) {
            this.showNotification('warning', 'No Label', `No ${version} label has been generated yet.`);
            return;
        }
        
        try {
            const labelData = this.customLabels[version];
            
            // Open the PDF in a new tab
            const blob = this.base64ToBlob(labelData.content, 'application/pdf');
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
            
            // Clean up URL object after a delay
            setTimeout(() => URL.revokeObjectURL(url), 1000);
            
        } catch (error) {
            console.error(`Error viewing ${version} custom label:`, error);
            this.showNotification('error', 'View Error', `Failed to view ${version} label: ${error.message}`);
        }
    }
    
    async downloadCustomLabel(version) {
        if (!this.customLabels[version]) {
            this.showNotification('warning', 'No Label', `No ${version} label has been generated yet.`);
            return;
        }
        
        try {
            const labelData = this.customLabels[version];
            const orderIdInput = document.getElementById('custom-order-id');
            const filmNumberInput = document.getElementById('custom-film-number');
            
            // Create filename based on input values (RRD is already in orderIdInput.value)
            const archiveId = orderIdInput.value;
            const filmNumber = filmNumberInput.value;
            const filename = `custom_label_${archiveId}_${filmNumber}_${version}.pdf`;
            
            // Download the PDF
            const blob = this.base64ToBlob(labelData.content, 'application/pdf');
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            // Clean up URL object
            URL.revokeObjectURL(url);
            
            this.showNotification('success', 'Downloaded', `${version} label downloaded successfully`);
            
        } catch (error) {
            console.error(`Error downloading ${version} custom label:`, error);
            this.showNotification('error', 'Download Error', `Failed to download ${version} label: ${error.message}`);
        }
    }
    
    async printCustomLabel(version) {
        if (!this.customLabels[version]) {
            this.showNotification('warning', 'No Label', `No ${version} label has been generated yet.`);
            return;
        }
        
        try {
            const labelData = this.customLabels[version];
            
            // Convert base64 to Blob
            const blob = this.base64ToBlob(labelData.content, 'application/pdf');
            const url = URL.createObjectURL(blob);
            
            // Create an iframe to load the PDF
            const printFrame = document.createElement('iframe');
            printFrame.className = 'print-frame';
            printFrame.src = url;
            
            // When the iframe loads, print it and then remove it
            printFrame.onload = () => {
                try {
                    // Wait a moment for the PDF to render in the iframe
                    setTimeout(() => {
                        printFrame.contentWindow.focus();
                        printFrame.contentWindow.print();
                        
                        // Clean up after printing dialog closes
                        setTimeout(() => {
                            document.body.removeChild(printFrame);
                            URL.revokeObjectURL(url);
                        }, 1000);
                    }, 500);
                } catch (err) {
                    console.error('Error during printing:', err);
                    this.showNotification('error', 'Print Error', 'Failed to open print dialog. Try downloading the PDF instead.');
                    document.body.removeChild(printFrame);
                    URL.revokeObjectURL(url);
                }
            };
            
            // Add iframe to document to trigger load
            document.body.appendChild(printFrame);
            
            this.showNotification('info', 'Opening Print Dialog', 'The print dialog should open shortly.');
            
        } catch (error) {
            console.error(`Error printing ${version} custom label:`, error);
            this.showNotification('error', 'Print Error', `Failed to print ${version} label: ${error.message}`);
        }
    }
    
    // Utility method to convert base64 to Blob
    base64ToBlob(base64, mimeType) {
        const byteCharacters = atob(base64);
        const byteArrays = [];
        
        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
            const slice = byteCharacters.slice(offset, offset + 512);
            
            const byteNumbers = new Array(slice.length);
            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }
            
            const byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }
        
        return new Blob(byteArrays, { type: mimeType });
    }
    
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadRolls(),
                this.loadGeneratedLabels(),
                this.loadPrinterStatus()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('error', 'Error', 'Failed to load dashboard data');
        }
    }
    
    async loadRolls() {
        try {
            const response = await fetch('/api/labels/rolls/');
            const data = await response.json();
            
            if (data.success) {
                // Separate rolls into uncompleted and completed
                this.uncompletedRolls = data.rolls.filter(roll => !roll.label_completed);
                this.completedRolls = data.rolls.filter(roll => roll.label_completed);
                
                this.renderUncompletedRolls(this.uncompletedRolls);
                this.renderCompletedRolls(this.completedRolls);
                this.updateUncompletedSelectionInfo();
                this.updateCompletedSelectionInfo();
            } else {
                throw new Error(data.error || 'Failed to load rolls');
            }
        } catch (error) {
            console.error('Error loading rolls:', error);
            this.showNotification('error', 'Error', 'Failed to load developed rolls');
        }
    }
    
    renderUncompletedRolls(rolls) {
        const container = document.getElementById('uncompleted-rolls-grid');
        
        if (rolls.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-film"></i>
                    <p>No rolls ready for label generation</p>
                    <small>Complete development first or all rolls already have labels</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = rolls.map(roll => {
            const isSelected = this.selectedUncompletedRolls.has(roll.id);
            const canGenerate = roll.can_generate_label;
            
            return `
                <div class="roll-card uncompleted ${isSelected ? 'selected' : ''} ${!canGenerate ? 'disabled' : ''}" data-roll-id="${roll.id}">
                    <div class="roll-header">
                        <div class="roll-title">
                            <div class="roll-film-number">${roll.film_number}</div>
                            <div class="roll-film-type">${roll.film_type}</div>
                        </div>
                        <div class="roll-status-badge ${canGenerate ? 'ready' : 'disabled'}">
                            ${canGenerate ? 'Ready to Generate' : 'Cannot Generate'}
                        </div>
                    </div>
                    
                    <div class="roll-details">
                        <div class="detail-item">
                            <span class="label">Project:</span>
                            <span class="value">${roll.project_name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Archive ID:</span>
                            <span class="value">${roll.archive_id}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Doc Type:</span>
                            <span class="value">${roll.doc_type}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Pages:</span>
                            <span class="value">${roll.pages_used}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Developed:</span>
                            <span class="value">${this.formatDateTime(roll.development_completed_at)}</span>
                        </div>
                    </div>
                    
                    ${canGenerate ? `
                        <div class="roll-action-hint">
                            <i class="fas fa-plus"></i>
                            <span>Click to generate labels</span>
                        </div>
                    ` : ''}
                    
                    ${!canGenerate ? `
                        <div class="roll-overlay disabled">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>Cannot Generate Labels</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    }
    
    renderCompletedRolls(rolls) {
        const container = document.getElementById('completed-rolls-grid');
        
        if (rolls.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-check-circle"></i>
                    <p>No completed labels yet</p>
                    <small>Generate labels first to see them here</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = rolls.map(roll => {
            const isSelected = this.selectedCompletedRolls.has(roll.id);
            
            return `
                <div class="roll-card completed ${isSelected ? 'selected' : ''}" data-roll-id="${roll.id}">
                    <div class="roll-header">
                        <div class="roll-title">
                            <div class="roll-film-number">${roll.film_number}</div>
                            <div class="roll-film-type">${roll.film_type}</div>
                        </div>
                        <div class="roll-status-badge completed">
                            Labels Available
                        </div>
                    </div>
                    
                    <div class="roll-details">
                        <div class="detail-item">
                            <span class="label">Project:</span>
                            <span class="value">${roll.project_name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Archive ID:</span>
                            <span class="value">${roll.archive_id}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Doc Type:</span>
                            <span class="value">${roll.doc_type}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Pages:</span>
                            <span class="value">${roll.pages_used}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Label Status:</span>
                            <span class="value text-success">${roll.label_status}</span>
                        </div>
                    </div>
                    
                    <div class="roll-action-hint">
                        <i class="fas fa-eye"></i>
                        <span>Click to view labels</span>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    handleRollClick(card) {
        const rollId = parseInt(card.dataset.rollId);
        const isCompleted = card.classList.contains('completed');
        const isUncompleted = card.classList.contains('uncompleted');
        
        if (isUncompleted) {
            const roll = this.uncompletedRolls.find(r => r.id === rollId);
        
        if (!roll || !roll.can_generate_label) {
            this.showNotification('warning', 'Cannot Select', 'This roll cannot generate labels (missing film number or archive ID)');
            return;
        }
        
            if (this.selectedUncompletedRolls.has(rollId)) {
                this.selectedUncompletedRolls.delete(rollId);
                card.classList.remove('selected');
            } else {
                this.selectedUncompletedRolls.add(rollId);
                card.classList.add('selected');
            }
            
            this.updateUncompletedSelectionInfo();
        } else if (isCompleted) {
            const roll = this.completedRolls.find(r => r.id === rollId);
            
            if (!roll) {
                this.showNotification('warning', 'Cannot Select', 'Roll not found');
            return;
        }
        
            if (this.selectedCompletedRolls.has(rollId)) {
                this.selectedCompletedRolls.delete(rollId);
            card.classList.remove('selected');
        } else {
                this.selectedCompletedRolls.add(rollId);
            card.classList.add('selected');
        }
        
            this.updateCompletedSelectionInfo();
        }
    }
    
    selectAllUncompleted() {
        this.selectedUncompletedRolls.clear();
        this.uncompletedRolls.forEach(roll => {
            if (roll.can_generate_label) {
                this.selectedUncompletedRolls.add(roll.id);
            }
        });
        this.updateUncompletedRollSelection();
        this.updateUncompletedSelectionInfo();
    }
    
    selectAllCompleted() {
        this.selectedCompletedRolls.clear();
        this.completedRolls.forEach(roll => {
            this.selectedCompletedRolls.add(roll.id);
        });
        this.updateCompletedRollSelection();
        this.updateCompletedSelectionInfo();
    }
    
    clearUncompletedSelection() {
        this.selectedUncompletedRolls.clear();
        this.updateUncompletedRollSelection();
        this.updateUncompletedSelectionInfo();
    }
    
    clearCompletedSelection() {
        this.selectedCompletedRolls.clear();
        this.updateCompletedRollSelection();
        this.updateCompletedSelectionInfo();
    }
    
    updateUncompletedRollSelection() {
        document.querySelectorAll('.roll-card.uncompleted').forEach(card => {
            const rollId = parseInt(card.dataset.rollId);
            if (this.selectedUncompletedRolls.has(rollId)) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }
    
    updateCompletedRollSelection() {
        document.querySelectorAll('.roll-card.completed').forEach(card => {
            const rollId = parseInt(card.dataset.rollId);
            if (this.selectedCompletedRolls.has(rollId)) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }
    
    updateUncompletedSelectionInfo() {
        const count = this.selectedUncompletedRolls.size;
        document.getElementById('uncompleted-selection-count').textContent = `${count} roll${count !== 1 ? 's' : ''} selected`;
        
        const generateBtn = document.getElementById('generate-uncompleted');
        if (generateBtn) {
            generateBtn.disabled = count === 0;
    }
    }
    
    updateCompletedSelectionInfo() {
        const count = this.selectedCompletedRolls.size;
        document.getElementById('completed-selection-count').textContent = `${count} roll${count !== 1 ? 's' : ''} selected`;
        
        const viewBtn = document.getElementById('view-completed-labels');
        if (viewBtn) {
            viewBtn.disabled = count === 0;
        }
    }
    
    async loadGeneratedLabels() {
        try {
            const response = await fetch('/api/labels/generated/');
            const data = await response.json();
            
            if (data.success) {
                this.generatedLabels = data.labels;
                console.log('Raw generated labels from API:', this.generatedLabels);
                
                // Organize labels by roll
                this.labelsByRoll.clear();
                this.generatedLabels.forEach(label => {
                    console.log('Processing label:', label);
                    if (!this.labelsByRoll.has(label.roll_id)) {
                        this.labelsByRoll.set(label.roll_id, {});
                    }
                    console.log('Setting label version:', label.version, 'for roll:', label.roll_id);
                    this.labelsByRoll.get(label.roll_id)[label.version] = label;
                });
                
                console.log('Final labelsByRoll structure:', this.labelsByRoll);
                this.renderGeneratedLabels();
            } else {
                throw new Error(data.error || 'Failed to load generated labels');
            }
        } catch (error) {
            console.error('Error loading generated labels:', error);
            this.showNotification('error', 'Error', 'Failed to load generated labels');
        }
    }
    
    renderGeneratedLabels() {
        const container = document.getElementById('generated-labels');
        console.log('Rendering generated labels, container:', container);
        console.log('Labels by roll:', this.labelsByRoll);
        
        if (!container) {
            console.error('Generated labels container not found!');
            return;
        }
        
        if (this.labelsByRoll.size === 0) {
            console.log('No labels to display, showing empty state');
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-file-pdf"></i>
                    <p>No labels generated yet</p>
                    <small>Select rolls above and click "Generate Labels"</small>
                </div>
            `;
            return;
        }
        
        console.log('Generating HTML for', this.labelsByRoll.size, 'roll(s)');
        
        const rollsHtml = Array.from(this.labelsByRoll.entries()).map(([rollId, versions]) => {
            console.log('Processing roll', rollId, 'versions:', versions);
            const normalLabel = versions.normal;
            const angledLabel = versions.angled;
            console.log('normalLabel:', normalLabel, 'angledLabel:', angledLabel);
            
            // Use the first available label for roll info - try any version
            const rollInfo = normalLabel || angledLabel || Object.values(versions)[0];
            
            // Skip if no labels exist for this roll
            if (!rollInfo) {
                console.log('Skipping roll', rollId, 'no rollInfo. versions keys:', Object.keys(versions));
                // Let's try to get any label from the versions object
                const anyLabel = Object.values(versions)[0];
                console.log('First available label:', anyLabel);
                return '';
            }
            
            console.log('Rendering roll', rollId, 'with rollInfo:', rollInfo);
            
            // Get all available versions dynamically
            const allVersions = Object.entries(versions);
            console.log('All versions for roll', rollId, ':', allVersions);
            
            return `
                <div class="roll-label-container">
                    <div class="roll-label-header">
                        <h4>${rollInfo.film_number} - ${rollInfo.archive_id}</h4>
                        <p>${rollInfo.doc_type}</p>
                        <small>Generated: ${this.formatDateTime(rollInfo.generated_at)}</small>
                    </div>
                    
                    <div class="version-containers">
                        ${allVersions.map(([versionName, label]) => `
                            <div class="version-container ${versionName}">
                                <div class="version-header">
                                    <h5><i class="fas fa-${versionName === 'angled' ? 'drafting-compass' : 'table'}"></i> ${versionName.charAt(0).toUpperCase() + versionName.slice(1)} Version</h5>
                                    <div class="version-status ${label.status}">${this.getStatusDisplayText(label.status)}</div>
                    </div>
                                <div class="version-actions">
                                    <button class="btn btn-secondary btn-small download-label" data-label-id="${label.label_id}" data-version="${versionName}">
                        <i class="fas fa-download"></i> Download ${label.download_count > 0 ? `(${label.download_count})` : ''}
                    </button>
                                    <button class="btn btn-info btn-small view-label" data-label-id="${label.label_id}" data-version="${versionName}">
                                        <i class="fas fa-eye"></i> View
                                    </button>
                                    <button class="btn btn-outline btn-small open-label" data-label-id="${label.label_id}" data-version="${versionName}">
                                        <i class="fas fa-folder-open"></i> Reveal
                        </button>
                                    <button class="btn btn-primary btn-small print-label" data-label-id="${label.label_id}" data-version="${versionName}">
                        <i class="fas fa-print"></i> Print ${label.print_count > 0 ? `(${label.print_count})` : ''}
                    </button>
                                </div>
                                ${label.printed_at ? `<small class="print-info">Printed: ${this.formatDateTime(label.printed_at)}</small>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }).filter(html => html !== '').join('');
        
        console.log('Final HTML length:', rollsHtml.length);
        container.innerHTML = rollsHtml;
        console.log('Labels rendered successfully');
    }
    
    clearGeneratedLabels() {
        // Note: This now only clears the UI, not the database records
        this.generatedLabels = [];
        this.labelsByRoll.clear();
        this.renderGeneratedLabels();
        this.showNotification('info', 'View Cleared', 'Generated labels view cleared (labels still saved in database)');
    }
    
    // Stub methods for bulk actions (not currently implemented in UI)
    downloadAllLabels(version) {
        this.showNotification('info', 'Not Available', 'Bulk download is not available in the current interface. Use individual download buttons.');
    }
    
    printAllLabels(version) {
        this.showNotification('info', 'Not Available', 'Bulk print is not available in the current interface. Use individual print buttons.');
    }
    
    async downloadLabel(labelId, version) {
        try {
            const response = await fetch(`/api/labels/download/${labelId}/?version=${version}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `film_label_${labelId}_${version}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showNotification('success', 'Downloaded', 'Label PDF downloaded successfully');
                
                // Reload generated labels to show updated download count
                this.loadGeneratedLabels();
            } else {
                throw new Error('Failed to download label');
            }
        } catch (error) {
            console.error('Error downloading label:', error);
            this.showNotification('error', 'Error', 'Failed to download label');
        }
    }
    
    async viewLabel(labelId, version) {
        try {
            const response = await fetch(`/api/labels/download/${labelId}/?version=${version}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                
                // Open PDF in new tab for viewing
                window.open(url, '_blank');
                
                this.showNotification('success', 'Opened', 'Label PDF opened in new tab');
                
                // Clean up the URL after a delay to allow the browser to load it
                setTimeout(() => {
                    window.URL.revokeObjectURL(url);
                }, 1000);
                
                // Reload generated labels to show updated download count
                this.loadGeneratedLabels();
            } else {
                throw new Error('Failed to view label');
            }
        } catch (error) {
            console.error('Error viewing label:', error);
            this.showNotification('error', 'Error', 'Failed to view label');
        }
    }
    
    async openLabel(labelId, version) {
        try {
            // Call the reveal API endpoint
            const response = await fetch(`/api/labels/reveal/${labelId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'File Revealed', 'Label file revealed in Windows Explorer');
            } else {
                // If file not found on disk, fall back to download
                if (data.error.includes('not found on disk')) {
                    this.showNotification('warning', 'File Not Saved', 'Label only exists in cache. Downloading instead...');
                    // Fall back to download
                    await this.downloadLabel(labelId, version);
                } else {
                    throw new Error(data.error);
                }
            }
        } catch (error) {
            console.error('Error revealing label in explorer:', error);
            this.showNotification('error', 'Error', 'Failed to reveal label in explorer');
        }
    }
    
    async addToQueue(labelId) {
        try {
            const response = await fetch('/api/labels/print-queue/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    label_ids: [labelId]
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.loadPrintQueue();
                this.loadGeneratedLabels(); // Reload to show updated status
                this.showNotification('success', 'Added to Queue', data.message);
            } else {
                throw new Error(data.error || 'Failed to add to queue');
            }
        } catch (error) {
            console.error('Error adding to queue:', error);
            this.showNotification('error', 'Error', 'Failed to add to print queue');
        }
    }
    
    async loadPrintQueue() {
        try {
            const response = await fetch('/api/labels/print-queue/');
            const data = await response.json();
            
            if (data.success) {
                this.printQueue = data.queue;
                this.renderPrintQueue();
            } else {
                throw new Error(data.error || 'Failed to load print queue');
            }
        } catch (error) {
            console.error('Error loading print queue:', error);
            this.showNotification('error', 'Error', 'Failed to load print queue');
        }
    }
    
    async loadPrinterStatus() {
        try {
            const response = await fetch('/api/labels/printer-status/');
            const data = await response.json();
            
            if (data.success) {
                this.updatePrinterStatusDisplay(data.printer_status);
            } else {
                throw new Error(data.error || 'Failed to load printer status');
            }
        } catch (error) {
            console.error('Error loading printer status:', error);
            this.updatePrinterStatusDisplay({
                default_printer: null,
                available_printers: [],
                system: { windows: false, linux: false, mac: false }
            });
        }
    }
    
    updatePrinterStatusDisplay(status) {
        const statusText = document.getElementById('printer-status-text');
        const detailsText = document.getElementById('printer-details');
        
        if (statusText && detailsText) {
        if (status.default_printer) {
            statusText.textContent = 'Printing Method: Server-Side Direct Printing';
            detailsText.innerHTML = `
                <strong>Default Printer:</strong> ${status.default_printer}<br>
                <strong>Available Printers:</strong> ${status.available_printers.length} found<br>
                <strong>System:</strong> ${this.getSystemName(status.system)}
            `;
        } else {
            statusText.textContent = 'Printing Method: No Printer Configured';
            detailsText.innerHTML = `
                <span style="color: var(--color-warning);">
                    <i class="fas fa-exclamation-triangle"></i>
                    No default printer found. Please configure a printer in your system settings.
                </span>
            `;
            }
        }
    }
    
    getSystemName(system) {
        if (system.windows) return 'Windows';
        if (system.linux) return 'Linux';
        if (system.mac) return 'macOS';
        return 'Unknown';
    }
    
    async printLabel(labelId, version) {
        // Server-side printing - no user interaction required
        try {
            this.showNotification('info', 'Printing Label', 'Sending label to printer...');
            
            const response = await fetch(`/api/labels/print/${labelId}/?version=${version}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    copies: 1  // Default to 1 copy, could be made configurable
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'Label Printed', 
                    `Label printed successfully to ${data.printer} using ${data.method}`);
                
                // Reload data to show updated status
                this.loadGeneratedLabels();
                this.loadRolls(); // Update roll status too
            } else {
                throw new Error(data.error || 'Failed to print label');
            }
            
        } catch (error) {
            console.error('Error printing label:', error);
            
            if (error.message.includes('expired')) {
                this.showNotification('warning', 'Label Expired', 'This label has expired from cache. Please regenerate it and try printing again.');
            } else {
                this.showNotification('error', 'Print Error', `Failed to print label: ${error.message}`);
            }
        }
    }
    
    // Utility methods
    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString();
    }
    
    getStatusDisplayText(status) {
        const statusMap = {
            'generated': 'Generated',
            'downloaded': 'Downloaded',
            'queued': 'Queued',
            'printed': 'Printed',
            'completed': 'Completed'
        };
        return statusMap[status] || status;
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    
    showNotification(type, title, message) {
        const container = document.getElementById('notifications-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <i class="fas fa-${icons[type]}" style="color: var(--color-${type === 'error' ? 'error' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'primary'});"></i>
                <strong style="color: var(--color-text-primary);">${title}</strong>
            </div>
            <div style="color: var(--color-text-secondary); font-size: 0.9rem;">${message}</div>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 8 seconds (increased from 5)
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 8000);
    }
    
    async generateUncompletedLabels() {
        if (this.selectedUncompletedRolls.size === 0) return;
        
        const rollIds = Array.from(this.selectedUncompletedRolls);
        
        try {
            this.showNotification('info', 'Generating Labels', 'Creating both Normal and Angled PDF labels for selected rolls...');
            
            const response = await fetch('/api/labels/generate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    roll_ids: rollIds,
                    generate_both_versions: true
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'Labels Generated', data.message);
                
                // Clear selection after successful generation
                this.clearUncompletedSelection();
                
                // Reload all data to show updated status
                await this.loadInitialData();
            } else {
                throw new Error(data.error || 'Failed to generate labels');
            }
        } catch (error) {
            console.error('Error generating labels:', error);
            this.showNotification('error', 'Error', 'Failed to generate labels');
        }
    }
    
    async viewSelectedCompletedLabels() {
        if (this.selectedCompletedRolls.size === 0) {
            this.showNotification('warning', 'No Selection', 'Please select completed rolls first to view their labels.');
            return;
        }
        
        const rollIds = Array.from(this.selectedCompletedRolls);
        console.log('Viewing labels for roll IDs:', rollIds);
        
        try {
            // First, ensure we have the latest generated labels
            await this.loadGeneratedLabels();
            console.log('All generated labels:', this.generatedLabels);
            
            // Filter existing labels to show only selected rolls
            const filteredLabels = this.generatedLabels.filter(label => 
                rollIds.includes(label.roll_id)
            );
            
            console.log('Filtered labels:', filteredLabels);
            
            if (filteredLabels.length === 0) {
                this.showNotification('warning', 'No Labels Found', 'No generated labels found for selected rolls. They may need to be regenerated.');
                return;
            }
            
            // Organize filtered labels by roll
            const filteredLabelsByRoll = new Map();
            filteredLabels.forEach(label => {
                if (!filteredLabelsByRoll.has(label.roll_id)) {
                    filteredLabelsByRoll.set(label.roll_id, {});
                }
                filteredLabelsByRoll.get(label.roll_id)[label.version] = label;
            });
            
            console.log('Filtered labels by roll:', filteredLabelsByRoll);
            
            // Replace with filtered labels
            this.labelsByRoll = filteredLabelsByRoll;
            
            // Render the filtered labels
            this.renderGeneratedLabels();
            
            this.showNotification('success', 'Labels Displayed', `Showing labels for ${rollIds.length} selected roll${rollIds.length !== 1 ? 's' : ''}. Click "Show All Labels" to see all generated labels.`);
            
        } catch (error) {
            console.error('Error viewing completed labels:', error);
            this.showNotification('error', 'Error', 'Failed to view selected labels: ' + error.message);
        }
    }
    
    async showAllLabels() {
        try {
            // Reload all generated labels
            await this.loadGeneratedLabels();
            this.showNotification('success', 'All Labels Displayed', 'Showing all generated labels');
        } catch (error) {
            console.error('Error showing all labels:', error);
            this.showNotification('error', 'Error', 'Failed to load all labels');
        }
    }
}

// Initialize label manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.labelManager = new LabelManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.labelManager) {
        console.log('Label Manager cleanup');
    }
}); 
