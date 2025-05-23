// distribution.js - Handles document distribution and export simulation

document.addEventListener('DOMContentLoaded', function() {
    initDistributionComponent();
});

function initDistributionComponent() {
    console.log('Distribution component initialized');

    // Elements
    const startDistributionBtn = document.getElementById('start-distribution');
    const statusBadge = document.querySelector('#step-7 .status-badge');
    const toStep8Btn = document.getElementById('to-step-8');
    const folderStructureInput = document.getElementById('folder-structure');
    const namingPatternInput = document.getElementById('naming-pattern');
    const includeOriginalsInput = document.getElementById('include-originals');
    const copyIndexInput = document.getElementById('copy-index-folders');
    const folderTree = document.querySelector('.folder-tree');
    const progressSection = document.querySelector('.distribution-progress');
    const progressBar = document.querySelector('#step-7 .progress-bar-fill');
    const progressPercentage = document.querySelector('#step-7 .progress-percentage');
    const operationLog = document.querySelector('.operation-log');

    // --- Live preview logic ---
    function updateFolderPreview() {
        const structure = folderStructureInput.value;
        const pattern = namingPatternInput.value;

        // Update the folder tree based on the selected structure
        if (!folderTree) return;
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

        // Update data panel (pending state)
        updateDistributionData(
            'pending',
            structure,
            pattern,
            {
                includeOriginals: includeOriginalsInput.checked,
                copyIndexToFolders: copyIndexInput.checked
            }
        );
    }

    // --- Distribution options change handlers ---
    if (folderStructureInput) folderStructureInput.addEventListener('change', updateFolderPreview);
    if (namingPatternInput) namingPatternInput.addEventListener('change', updateFolderPreview);
    if (includeOriginalsInput) includeOriginalsInput.addEventListener('change', updateDistributionOptions);
    if (copyIndexInput) copyIndexInput.addEventListener('change', updateDistributionOptions);

    function updateDistributionOptions() {
        updateDistributionData(
            'pending',
            folderStructureInput.value,
            namingPatternInput.value,
            {
                includeOriginals: includeOriginalsInput.checked,
                copyIndexToFolders: copyIndexInput.checked
            }
        );
    }

    // --- Start Distribution Button ---
    if (startDistributionBtn) {
        startDistributionBtn.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

            if (statusBadge) {
                statusBadge.className = 'status-badge in-progress';
                statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Distribution In Progress';
            }

            if (progressSection) progressSection.classList.remove('hidden');
            if (operationLog) operationLog.innerHTML = '';

            // Get distribution options
            const structure = folderStructureInput.value;
            const pattern = namingPatternInput.value;
            const includeOriginals = includeOriginalsInput.checked;
            const copyIndexToFolders = copyIndexInput.checked;

            // Simulate distribution process
            let progress = 0;
            let totalFolders = 0;
            let totalFiles = 0;

            const distributionInterval = setInterval(() => {
                progress += 5;
                if (progressBar) progressBar.style.width = `${progress}%`;
                if (progressPercentage) progressPercentage.textContent = `${progress}%`;

                // Add log entries based on progress
                if (operationLog) {
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
                }

                if (progress >= 100) {
                    clearInterval(distributionInterval);

                    // Add final log entries
                    addLogEntry('Distribution completed successfully', 'success');

                    // Calculate total size (for demo)
                    const avgFileSize = 220; // KB
                    const totalSize = Math.round(totalFiles * avgFileSize / 100) / 10; // MB

                    // Update data panel with final statistics
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
                    if (statusBadge) {
                        statusBadge.className = 'status-badge completed';
                        statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Distribution Complete';
                    }

                    // Reset button
                    startDistributionBtn.innerHTML = '<i class="fas fa-play"></i> Start Distribution';
                    startDistributionBtn.disabled = false;

                    // Enable navigation to next step
                    if (toStep8Btn) toStep8Btn.disabled = false;

                    // Show notification
                    if (typeof showNotification === 'function') {
                        showNotification('Document distribution completed successfully!', 'success');
                    }
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
                if (fileOps) fileOps.scrollTop = fileOps.scrollHeight;
            }
        });
    }

    // --- Data panel update helper ---
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
        const dataOutput = document.querySelector('#step-7 .data-output');
        if (dataOutput) {
            dataOutput.textContent = JSON.stringify(distData, null, 2);
        }
    }

    // --- Initialize preview and data panel ---
    updateFolderPreview();
    updateDistributionData('pending', folderStructureInput.value, namingPatternInput.value, {
        includeOriginals: includeOriginalsInput.checked,
        copyIndexToFolders: copyIndexInput.checked
    });

    // Expose public methods if needed
    window.distributionComponent = {
        updateFolderPreview
    };
}
