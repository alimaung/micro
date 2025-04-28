/**
 * validation.js - Validation logic for Transfer module
 * Handles validation of fields, paths, and requirements
 */

// Make the class available globally
window.ValidationService = class ValidationService {
    constructor() {
        // Validation patterns
        this.patterns = {
            archiveId: /^RRD\d{3}-\d{4}$/,
            validLocations: ['OU', 'DW']
        };
    }
    
    /**
     * Validate a specific field
     * @param {string} fieldId - ID of the field to validate
     * @param {string} value - Value to validate
     * @returns {Object} - Validation result with isValid and errorMessage
     */
    validateField(fieldId, value) {
        let isValid = false;
        let errorMessage = '';
        
        switch(fieldId) {
            case 'archive-id':
                // Check if Archive ID matches pattern RRDxxx-yyyy
                isValid = this.patterns.archiveId.test(value);
                if (!isValid) {
                    errorMessage = 'Invalid format. Must be RRDxxx-yyyy';
                }
                break;
                
            case 'location':
                // Check if location is either OU or DW
                isValid = this.patterns.validLocations.includes(value);
                if (!isValid) {
                    errorMessage = 'Must be either OU or DW';
                }
                break;
                
            case 'document-type':
                // Check if document type is not empty
                isValid = value.length > 0;
                if (!isValid) {
                    errorMessage = 'Document type cannot be empty';
                }
                break;
                
            default:
                errorMessage = 'Unknown field';
                break;
        }
        
        return {
            isValid,
            errorMessage
        };
    }
    
    /**
     * Validate project status
     * @param {Object} projectInfo - Project info object
     * @param {string} sourcePath - Source path
     * @param {string} destinationPath - Destination path
     * @returns {Object} - Validation result with isValid, errorType, and errorMessage
     */
    validateProjectStatus(projectInfo, sourcePath, destinationPath) {
        // Check individual field validations
        const archiveIdValid = this.validateField('archive-id', projectInfo.archiveId).isValid;
        const locationValid = this.validateField('location', projectInfo.location).isValid;
        const docTypeValid = this.validateField('document-type', projectInfo.documentType).isValid;
        
        // Check if source path is set
        const sourceValid = sourcePath && sourcePath !== '';
        
        // Check if destination path is set
        const destinationValid = destinationPath && destinationPath !== '';
        
        // Project info is valid if all three editable fields are valid
        const projectInfoValid = archiveIdValid && locationValid && docTypeValid;
        
        let errorType = null;
        let errorMessage = '';
        
        if (!sourceValid) {
            errorType = 'source';
            errorMessage = 'Source invalid';
        } else if (!destinationValid) {
            errorType = 'destination';
            errorMessage = 'Destination invalid';
        } else if (!projectInfoValid) {
            errorType = 'project-info';
            errorMessage = 'Project invalid';
        }
        
        return {
            isValid: sourceValid && destinationValid && projectInfoValid,
            errorType,
            errorMessage
        };
    }
    
    /**
     * Validate all requirements before starting transfer
     * @param {Object} state - Current state object
     * @returns {Object} - Validation result with valid flag, errors object, and message
     */
    validateAllRequirements(state) {
        const result = {
            valid: true,
            errors: {},
            message: ''
        };
        
        // Extract relevant state for validation
        const { 
            sourceData, 
            destinationPath, 
            projectInfo, 
            pdfWarningDisplay,
            comlistWarningDisplay 
        } = state;
        
        // Check source path
        if (!sourceData.path) {
            result.valid = false;
            result.errors['source'] = 'Source folder not selected';
            result.message += 'Source folder required. ';
        }
        
        // Check destination path
        if (!destinationPath) {
            result.valid = false;
            result.errors['destination'] = 'Destination path not set';
            result.message += 'Destination path required. ';
        }
        
        // Check archive ID
        const archiveIdValidation = this.validateField('archive-id', projectInfo.archiveId);
        if (!archiveIdValidation.isValid) {
            result.valid = false;
            result.errors['archive-id'] = 'Invalid Archive ID format';
            result.message += 'Valid Archive ID required. ';
        }
        
        // Check location
        const locationValidation = this.validateField('location', projectInfo.location);
        if (!locationValidation.isValid) {
            result.valid = false;
            result.errors['location'] = 'Location must be OU or DW';
            result.message += 'Valid Location required. ';
        }
        
        // Check document type
        const docTypeValidation = this.validateField('document-type', projectInfo.documentType);
        if (!docTypeValidation.isValid) {
            result.valid = false;
            result.errors['document-type'] = 'Document type required';
            result.message += 'Document type required. ';
        }
        
        // Check PDF warning display if provided
        if (pdfWarningDisplay && pdfWarningDisplay.className === "warning-message error") {
            result.valid = false;
            result.errors['pdf-folder'] = 'PDF folder error';
            result.message += 'Fix PDF folder errors. ';
        }
        
        // Check COMList warning display if provided
        if (comlistWarningDisplay && comlistWarningDisplay.className === "warning-message error") {
            result.valid = false;
            result.errors['comlist-file'] = 'COMList file error';
            result.message += 'Fix COMList file errors. ';
        }
        
        return result;
    }
}
