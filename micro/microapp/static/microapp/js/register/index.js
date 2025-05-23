// index.js - Handles indexing and categorization of microfilm

document.addEventListener('DOMContentLoaded', function() {
    // Initialize index component
    initIndexComponent();
});

function initIndexComponent() {
    console.log('Index component initialized');
    
    // Get index elements
    const indexForm = document.querySelector('#index-form');
    const addKeywordBtn = document.querySelector('#add-keyword');
    const keywordsList = document.querySelector('#keywords-list');
    const categorySelect = document.querySelector('#category-select');
    
    // Add event listeners
    if (indexForm) {
        indexForm.addEventListener('submit', handleIndexSubmit);
    }
    
    if (addKeywordBtn) {
        addKeywordBtn.addEventListener('click', handleAddKeyword);
    }
    
    if (categorySelect) {
        categorySelect.addEventListener('change', handleCategoryChange);
    }
    
    // Initialize delete buttons for existing keywords
    initDeleteButtons();
    
    // --- Add Generate Index Button Logic ---
    const generateIndexBtn = document.getElementById('generate-index');
    if (generateIndexBtn) {
        generateIndexBtn.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

            setTimeout(() => {
                // Update table with sample data
                const tableBody = document.querySelector('.index-table tbody');
                if (tableBody) tableBody.innerHTML = '';

                // Generate sample index data
                const indexFormat = document.getElementById('index-format')?.value;
                const detailLevel = document.getElementById('index-detail')?.value;

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

                    if (tableBody) tableBody.appendChild(row);
                }

                // Show pagination if present
                const pagination = document.querySelector('.table-pagination');
                if (pagination) pagination.classList.remove('hidden');

                // Update status badge
                const statusBadge = document.querySelector('#step-4 .status-badge');
                if (statusBadge) {
                    statusBadge.className = 'status-badge completed';
                    statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Index Generated';
                }

                // Enable navigation to next step
                const toStep5Btn = document.getElementById('to-step-5');
                if (toStep5Btn) {
                    toStep5Btn.disabled = false;
                    toStep5Btn.removeAttribute('disabled');
                    // Also force enable visually
                    toStep5Btn.classList.remove('disabled');
                    toStep5Btn.style.pointerEvents = 'auto';
                    toStep5Btn.style.opacity = '1';
                }

                // Show notification
                if (typeof showNotification === 'function') {
                    showNotification('Index generated successfully!', 'success');
                }

                // Reset button
                this.innerHTML = '<i class="fas fa-file-alt"></i> Generate Index';
                this.disabled = false;
            }, 1500);
        });
    }
    
    // Event handlers
    function handleAddKeyword() {
        const keywordInput = document.querySelector('#new-keyword');
        
        if (keywordInput && keywordInput.value.trim() !== '' && keywordsList) {
            // Create new keyword element
            const keywordItem = document.createElement('div');
            keywordItem.className = 'keyword-item';
            keywordItem.innerHTML = `
                <span class="keyword-text">${keywordInput.value.trim()}</span>
                <button type="button" class="delete-keyword">×</button>
                <input type="hidden" name="keywords[]" value="${keywordInput.value.trim()}">
            `;
            
            // Add to keywords list
            keywordsList.appendChild(keywordItem);
            
            // Add delete event listener
            const deleteBtn = keywordItem.querySelector('.delete-keyword');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', handleDeleteKeyword);
            }
            
            // Clear input
            keywordInput.value = '';
        }
    }
    
    function handleIndexSubmit(event) {
        event.preventDefault();
        console.log('Index form submitted');
        // Process index data
        
        // Notify progress component
        if (window.progressComponent) {
            window.progressComponent.setActiveStep(3); // Index is step 4 (index 3)
        }
    }
    
    function handleCategoryChange(event) {
        const category = event.target.value;
        console.log('Category changed to:', category);
        
        // Update subcategory options based on selected category
        updateSubcategories(category);
    }
    
    function handleDeleteKeyword(event) {
        const keywordItem = event.target.closest('.keyword-item');
        if (keywordItem && keywordsList) {
            keywordsList.removeChild(keywordItem);
        }
    }
    
    function updateSubcategories(category) {
        const subcategorySelect = document.querySelector('#subcategory-select');
        
        if (!subcategorySelect) return;
        
        // Clear existing options
        subcategorySelect.innerHTML = '<option value="">Select a subcategory</option>';
        
        // Sample mapping of categories to subcategories (would come from server in real app)
        const subcategories = {
            'historical': ['Government', 'Social', 'Military', 'Economic'],
            'technical': ['Equipment', 'Processes', 'Research', 'Development'],
            'educational': ['Training', 'Documentation', 'Instruction', 'Reference']
        };
        
        // Add new options based on selected category
        if (category in subcategories) {
            subcategories[category].forEach(sub => {
                const option = document.createElement('option');
                option.value = sub.toLowerCase();
                option.textContent = sub;
                subcategorySelect.appendChild(option);
            });
        }
    }
    
    function initDeleteButtons() {
        const deleteButtons = document.querySelectorAll('.delete-keyword');
        deleteButtons.forEach(button => {
            button.addEventListener('click', handleDeleteKeyword);
        });
    }
    
    // Expose public methods
    window.indexComponent = {
        getKeywords: () => {
            const keywords = [];
            const items = document.querySelectorAll('.keyword-item input[name="keywords[]"]');
            
            items.forEach(item => {
                keywords.push(item.value);
            });
            
            return keywords;
        },
        getSelectedCategory: () => categorySelect ? categorySelect.value : null
    };
}
