// filmnumber.js - Handles film numbering scheme and assignments

document.addEventListener('DOMContentLoaded', function() {
    initFilmNumberComponent();
});

function initFilmNumberComponent() {
    console.log('Film Numbering component initialized');

    // Elements
    const applyNumberingBtn = document.getElementById('apply-numbering');
    const resetNumberingBtn = document.getElementById('reset-numbering');
    const statusBadge = document.querySelector('#step-5 .status-badge');
    const toStep6Btn = document.getElementById('to-step-6');

    // Form fields
    const prefixInput = document.getElementById('numbering-prefix');
    const includeYearInput = document.getElementById('include-year');
    const yearInput = document.getElementById('numbering-year');
    const digitsInput = document.getElementById('sequence-digits');
    const separatorInput = document.getElementById('separation-char');
    const startingNumberInput = document.getElementById('starting-number');

    // Preview fields
    const filmIDDisplays = document.querySelectorAll('.film-id-display');

    // --- Live preview logic ---
    function updateFilmIDPreview() {
        const prefix = prefixInput.value;
        const includeYear = includeYearInput.checked;
        const year = includeYear ? yearInput.value : '';
        const digits = parseInt(digitsInput.value);
        const separator = separatorInput.value;
        const startingNumber = parseInt(startingNumberInput.value);

        let filmID16mm = prefix;
        let filmID35mm = prefix;
        const sepChar = getSeparatorChar(separator);

        if (includeYear) {
            filmID16mm += sepChar + year;
            filmID35mm += sepChar + year;
        }
        filmID16mm += sepChar + String(startingNumber).padStart(digits, '0');
        filmID35mm += sepChar + String(startingNumber).padStart(digits, '0') + 'L';

        if (filmIDDisplays.length > 0) filmIDDisplays[0].textContent = filmID16mm;
        if (filmIDDisplays.length > 1) filmIDDisplays[1].textContent = filmID35mm;

        // Update diagram film IDs if present
        document.querySelectorAll('.diagram-film .film-id').forEach((elem, index) => {
            if (index === 0) {
                elem.textContent = filmID16mm;
            } else if (index === 1) {
                elem.textContent = prefix + sepChar + year + sepChar + String(startingNumber + 1).padStart(digits, '0');
            } else if (index === 2) {
                elem.textContent = filmID35mm;
            }
        });

        // Update data panel (pending state)
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

    // --- Apply numbering logic ---
    if (applyNumberingBtn) {
        applyNumberingBtn.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Applying...';

            if (statusBadge) {
                statusBadge.className = 'status-badge in-progress';
                statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Applying Numbering Scheme';
            }

            setTimeout(() => {
                // Gather form values
                const prefix = prefixInput.value;
                const includeYear = includeYearInput.checked;
                const year = includeYear ? yearInput.value : '';
                const digits = parseInt(digitsInput.value);
                const separator = separatorInput.value;
                const startingNumber = parseInt(startingNumberInput.value);
                const sepChar = getSeparatorChar(separator);

                // Generate assignments for 16mm films
                const assignments16mm = [];
                const rolls16mmContainer = document.getElementById('16mm-rolls');
                const filmRolls16mm = rolls16mmContainer ? rolls16mmContainer.querySelectorAll('.film-roll:not(.add-roll-button)') : [];
                filmRolls16mm.forEach((roll, index) => {
                    const sequenceNumber = startingNumber + index;
                    let filmId = prefix;
                    if (includeYear) filmId += sepChar + year;
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
                const filmRolls35mm = rolls35mmContainer ? rolls35mmContainer.querySelectorAll('.film-roll:not(.add-roll-button)') : [];
                filmRolls35mm.forEach((roll, index) => {
                    const sequenceNumber = startingNumber + index;
                    let filmId = prefix;
                    if (includeYear) filmId += sepChar + year;
                    filmId += sepChar + String(sequenceNumber).padStart(digits, '0') + 'L';
                    assignments35mm.push({
                        originalId: roll.querySelector('.roll-id').textContent,
                        assignedId: filmId,
                        documentCount: parseInt(roll.querySelector('.document-count').textContent)
                    });
                });

                // Update data panel
                updateNumberingData('completed', {
                    prefix,
                    includeYear,
                    year: year.toString(),
                    sequenceDigits: digits,
                    separator,
                    startingNumber
                }, assignments16mm, assignments35mm);

                // Enable navigation to next step
                if (toStep6Btn) toStep6Btn.disabled = false;

                // Update status badge
                if (statusBadge) {
                    statusBadge.className = 'status-badge completed';
                    statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Numbering Applied';
                }

                // Reset button
                this.innerHTML = '<i class="fas fa-check"></i> Apply Numbering Scheme';
                this.disabled = false;

                // Show notification
                if (typeof showNotification === 'function') {
                    showNotification('Film numbering scheme applied successfully!', 'success');
                }
            }, 1500);
        });
    }

    // --- Reset numbering logic ---
    if (resetNumberingBtn) {
        resetNumberingBtn.addEventListener('click', function() {
            // Reset form fields to defaults
            prefixInput.value = 'MF';
            includeYearInput.checked = true;
            yearInput.value = '2023';
            digitsInput.value = '4';
            separatorInput.value = 'dash';
            startingNumberInput.value = '1';
            yearInput.disabled = false;
            updateFilmIDPreview();
            if (typeof showNotification === 'function') {
                showNotification('Numbering scheme reset to defaults', 'info');
            }
        });
    }

    // --- Enable/disable year input based on checkbox ---
    if (includeYearInput && yearInput) {
        includeYearInput.addEventListener('change', function() {
            yearInput.disabled = !this.checked;
            updateFilmIDPreview();
        });
    }

    // --- Add event listeners for live preview ---
    [prefixInput, yearInput, digitsInput, separatorInput, startingNumberInput].forEach(input => {
        if (input) {
            input.addEventListener('input', updateFilmIDPreview);
            input.addEventListener('change', updateFilmIDPreview);
        }
    });

    // --- Data panel update helper ---
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
        const dataOutput = document.querySelector('#step-5 .data-output');
        if (dataOutput) {
            dataOutput.textContent = JSON.stringify(numberingData, null, 2);
        }
    }

    // --- Initialize with default values ---
    updateNumberingData('pending', {
        prefix: 'MF',
        includeYear: true,
        year: '2023',
        sequenceDigits: 4,
        separator: 'dash',
        startingNumber: 1
    });

    updateFilmIDPreview();

    // Expose public methods if needed
    window.filmNumberComponent = {
        updateFilmIDPreview
    };
}
