/**
 * file-finders.js - File finding utilities for Transfer module
 * Handles auto-discovery of PDF folders and COMList files
 */

// Make the class available globally
window.FileFinders = class FileFinders {
    constructor(eventManager) {
        this.eventManager = eventManager;
        this._findingPdfFolder = false;
        this._findingComlistFile = false;
    }
    
    /**
     * Find PDF folder within source folder structure
     * @param {Object} sourceData - Source data with path and folder structure
     * @param {Object} projectInfo - Project info with archiveId
     */
    findPdfFolder(sourceData, projectInfo) {
        // Prevent duplicate processing
        if (this._findingPdfFolder) {
            console.log("[PDF DEBUG] Already searching for PDF folder, skipping duplicate call");
            return;
        }
        
        this._findingPdfFolder = true;
        
        // Add short delay to allow UI updates
        setTimeout(() => {
            this._findingPdfFolder = false;
            
            if (!this.validatePdfFinderPrerequisites(sourceData, projectInfo)) {
                return;
            }
            
            // Use consistent path formatting
            const normSourcePath = sourceData.path.replace(/\\/g, '\\');
            
            // Get archive ID and base part (RRDxxx)
            const archiveId = projectInfo.archiveId;
            const archiveIdBase = this.extractArchiveIdBase(archiveId);
            
            // Debug logs
            console.log("[PDF DEBUG] Searching for PDF folder in source path:", normSourcePath);
            console.log("[PDF DEBUG] Using Archive ID:", archiveId, "Base ID:", archiveIdBase);
            console.log("[PDF DEBUG] Folder structure:", sourceData.folderStructure);
            
            // Collect folder candidates
            const folderCandidates = this.collectPdfFolderCandidates(
                normSourcePath, 
                sourceData.folderStructure, 
                archiveId, 
                archiveIdBase
            );
            
            // Handle case where no candidates were found
            if (folderCandidates.length === 0) {
                this.eventManager.publish('pdf-folder-not-found', {
                    message: "No folders with PDF files found in the source folder or its subfolders"
                });
                return;
            }
            
            // Score and sort candidates
            this.scorePdfFolderCandidates(folderCandidates);
            
            // Get best match and decide if it's good enough
            this.selectBestPdfFolderMatch(folderCandidates);
            
        }, 100);
    }
    
    /**
     * Validate prerequisites for PDF folder finding
     * @param {Object} sourceData - Source data with path and folder structure
     * @param {Object} projectInfo - Project info with archiveId
     * @returns {boolean} - Whether prerequisites are valid
     */
    validatePdfFinderPrerequisites(sourceData, projectInfo) {
        // Check source path
        if (!sourceData.path) {
            this.eventManager.publish('pdf-folder-not-found', {
                message: "Cannot find PDF folder: Source path not set",
                error: true
            });
            return false;
        }
        
        // Check archive ID
        if (!projectInfo.archiveId) {
            this.eventManager.publish('pdf-folder-not-found', {
                message: "Cannot find PDF folder: Archive ID not set",
                error: true
            });
            return false;
        }
        
        // Check if folder structure exists
        if (!sourceData.folderStructure || !sourceData.folderStructure.folders) {
            this.eventManager.publish('pdf-folder-not-found', {
                message: "Cannot find PDF folder: No folder structure information available",
                error: true
            });
            return false;
        }
        
        return true;
    }
    
    /**
     * Collect possible PDF folder candidates
     * @param {string} sourcePath - Source path
     * @param {Object} folderStructure - Folder structure
     * @param {string} archiveId - Archive ID
     * @param {string} archiveIdBase - Base part of archive ID
     * @returns {Array} - Array of folder candidates
     */
    collectPdfFolderCandidates(sourcePath, folderStructure, archiveId, archiveIdBase) {
        const folderCandidates = [];
        
        // Check root folder for PDF files
        const rootPdfCount = this.countPdfFilesInFolder(folderStructure.files || []);
        if (rootPdfCount > 0) {
            folderCandidates.push({
                name: "Root",
                path: sourcePath,
                pdfCount: rootPdfCount,
                isPdfFolder: rootPdfCount > 0,
                inSubfolder: false,
                containsArchiveId: false,
                containsPdfKeyword: false
            });
        }
        
        // Check subfolders
        if (folderStructure.folders && Array.isArray(folderStructure.folders)) {
            folderStructure.folders.forEach(folder => {
                const folderPath = `${sourcePath}\\${folder}`;
                const results = this.analyzePdfSubfolderCandidate(
                    folder, 
                    folderPath, 
                    folderStructure, 
                    archiveId, 
                    archiveIdBase
                );
                if (results) {
                    folderCandidates.push(results);
                }
                
                // Also check deeper subfolders
                this.checkDeeperPdfSubfolders(
                    sourcePath,
                    folder,
                    folderStructure,
                    archiveId,
                    archiveIdBase,
                    folderCandidates
                );
            });
        }
        
        console.log("[PDF DEBUG] All folder candidates:", folderCandidates);
        return folderCandidates;
    }
    
    /**
     * Analyze a subfolder as a potential PDF folder
     * @param {string} folder - Folder name
     * @param {string} folderPath - Full folder path
     * @param {Object} folderStructure - Folder structure
     * @param {string} archiveId - Archive ID
     * @param {string} archiveIdBase - Base part of archive ID
     * @returns {Object|null} - Folder candidate object or null
     */
    analyzePdfSubfolderCandidate(folder, folderPath, folderStructure, archiveId, archiveIdBase) {
        console.log("[PDF DEBUG] Checking folder:", folder);
        
        // Try to count PDF files in this folder
        let pdfCount = 0;
        let hasFilesInfo = false;
        
        // Try to get PDF file count from fullStructure if available
        if (folderStructure.fullStructure && 
            folderStructure.fullStructure[folder] &&
            folderStructure.fullStructure[folder].files) {
            
            const folderFiles = folderStructure.fullStructure[folder].files;
            pdfCount = this.countPdfFilesInFolder(folderFiles);
            hasFilesInfo = true;
            
            console.log("[PDF DEBUG] Found", pdfCount, "PDF files in folder", folder);
        }
        
        // Check if folder name contains keywords
        const folderNameLower = folder.toLowerCase();
        const containsPdfKeyword = folderNameLower.includes('pdf');
        
        // Check if folder contains archive ID
        const containsArchiveId = archiveId && (
            folder === archiveId ||
            folder.startsWith(archiveId + '_') ||
            folder.includes('_' + archiveId) ||
            folder.endsWith('_' + archiveId)
        );
        
        const containsArchiveIdBase = archiveIdBase && (
            folder.startsWith(archiveIdBase + '_') ||
            folder.includes('_' + archiveIdBase) ||
            folder.endsWith('_' + archiveIdBase)
        );
        
        console.log("[PDF DEBUG] Folder stats:", {
            folder,
            pdfCount,
            containsPdfKeyword,
            containsArchiveId,
            containsArchiveIdBase
        });
        
        // Only create a candidate if it meets at least one criterion
        if (pdfCount > 0 || containsPdfKeyword || containsArchiveId || containsArchiveIdBase) {
            return {
                name: folder,
                path: folderPath,
                pdfCount: pdfCount,
                isPdfFolder: pdfCount > 0 || containsPdfKeyword,
                inSubfolder: true,
                containsArchiveId: containsArchiveId || containsArchiveIdBase,
                containsPdfKeyword: containsPdfKeyword,
                isEstimate: pdfCount === 0 && containsPdfKeyword
            };
        }
        
        return null;
    }
    
    /**
     * Check deeper subfolders for PDF files
     * @param {string} sourcePath - Source path
     * @param {string} parentFolder - Parent folder name
     * @param {Object} folderStructure - Folder structure
     * @param {string} archiveId - Archive ID
     * @param {string} archiveIdBase - Base part of archive ID
     * @param {Array} folderCandidates - Array of folder candidates to add to
     */
    checkDeeperPdfSubfolders(sourcePath, parentFolder, folderStructure, archiveId, archiveIdBase, folderCandidates) {
        const folderPath = `${sourcePath}\\${parentFolder}`;
        
        if (folderStructure.folders[parentFolder] && 
            typeof folderStructure.folders[parentFolder] === 'object' && 
            folderStructure.folders[parentFolder].folders) {
            
            Object.keys(folderStructure.folders[parentFolder].folders).forEach(subfolder => {
                const subfolderPath = `${folderPath}\\${subfolder}`;
                const subfolderFiles = folderStructure.folders[parentFolder].folders[subfolder].files || [];
                
                console.log("[PDF DEBUG] Checking deeper subfolder:", subfolder, "Files:", subfolderFiles);
                
                // Count PDF files in this subfolder
                const subfolderPdfCount = this.countPdfFilesInFolder(subfolderFiles);
                
                // Check if subfolder name contains keywords
                const subfolderNameLower = subfolder.toLowerCase();
                const subfolderContainsPdfKeyword = subfolderNameLower.includes('pdf');
                
                // Check if subfolder contains archive ID
                const subfolderContainsArchiveId = archiveId && (
                    subfolder === archiveId ||
                    subfolder.startsWith(archiveId + '_') ||
                    subfolder.includes('_' + archiveId) ||
                    subfolder.endsWith('_' + archiveId)
                );
                
                const subfolderContainsArchiveIdBase = archiveIdBase && (
                    subfolder.startsWith(archiveIdBase + '_') ||
                    subfolder.includes('_' + archiveIdBase) ||
                    subfolder.endsWith('_' + archiveIdBase)
                );
                
                if (subfolderPdfCount > 0) {
                    folderCandidates.push({
                        name: `${parentFolder}\\${subfolder}`,
                        path: subfolderPath,
                        pdfCount: subfolderPdfCount,
                        isPdfFolder: true,
                        inSubfolder: true,
                        deepSubfolder: true,
                        containsArchiveId: subfolderContainsArchiveId || subfolderContainsArchiveIdBase,
                        containsPdfKeyword: subfolderContainsPdfKeyword
                    });
                }
            });
        }
    }
    
    /**
     * Score and sort PDF folder candidates
     * @param {Array} folderCandidates - Array of folder candidates
     */
    scorePdfFolderCandidates(folderCandidates) {
        folderCandidates.forEach(folder => {
            folder.score = this.scorePdfFolder(folder);
            console.log("[PDF DEBUG] Scored folder:", folder.name, "Score:", folder.score);
        });
        
        // Sort by score (highest first)
        folderCandidates.sort((a, b) => b.score - a.score);
    }
    
    /**
     * Select best PDF folder match and publish result
     * @param {Array} folderCandidates - Array of folder candidates
     */
    selectBestPdfFolderMatch(folderCandidates) {
        // Get highest scored folder
        const bestMatch = folderCandidates[0];
        console.log("[PDF DEBUG] Best match:", bestMatch);
        
        // Decide whether to use the folder based on score threshold
        const minimumScore = 2; // Needs to at least have PDFs and meet some criteria
        
        if (bestMatch.score >= minimumScore) {
            const warningInfo = this.generatePdfWarningInfo(bestMatch);
            
            this.eventManager.publish('pdf-folder-found', {
                path: bestMatch.path,
                score: bestMatch.score,
                warningInfo
            });
        } else {
            this.eventManager.publish('pdf-folder-not-found', {
                message: "No suitable PDF folder found matching criteria",
                error: true
            });
        }
    }
    
    /**
     * Generate warning info for PDF folder match
     * @param {Object} match - Best folder match
     * @returns {Object} - Warning info object
     */
    generatePdfWarningInfo(match) {
        if (match.score >= 5) {
            // Perfect match
            return {
                hasWarning: false,
                message: ""
            };
        }
        
        // Construct warning message
        let warningMsg = "AutoPDF: ";
        if (!match.containsPdfKeyword) warningMsg += "no 'pdf' in name; ";
        if (!match.containsArchiveId) warningMsg += "no archive ID in name; ";
        if (match.deepSubfolder) warningMsg += "located in deep subfolder; ";
        else if (match.inSubfolder) warningMsg += "located in subfolder; ";
        if (match.pdfCount < 5) warningMsg += `contains ${match.pdfCount} files; `;
        if (match.isEstimate) warningMsg += "file count is estimated; ";
        
        return {
            hasWarning: true,
            message: warningMsg,
            type: "warning" // Could be "warning" or "error"
        };
    }
    
    /**
     * Find COMList file within source folder
     * @param {Object} sourceData - Source data with path and folder structure 
     * @param {Object} projectInfo - Project info with archiveId
     */
    findComlistFile(sourceData, projectInfo) {
        // Prevent duplicate processing
        if (this._findingComlistFile) return;
        this._findingComlistFile = true;
        
        setTimeout(() => {
            this._findingComlistFile = false;
            
            if (!this.validateComlistFinderPrerequisites(sourceData, projectInfo)) {
                return;
            }
            
            // Get archive ID and base part
            const archiveId = projectInfo.archiveId;
            const archiveIdBase = this.extractArchiveIdBase(archiveId);
            
            // Use consistent path formatting
            const normSourcePath = sourceData.path.replace(/\\/g, '\\');
            
            // Debug logs
            console.log("[COMLIST DEBUG] Source path:", normSourcePath);
            console.log("[COMLIST DEBUG] Archive ID:", archiveId, "Base:", archiveIdBase);
            console.log("[COMLIST DEBUG] Folder structure:", sourceData.folderStructure);
            
            // Collect file candidates
            const fileCandidates = this.collectComlistFileCandidates(
                normSourcePath, 
                sourceData.folderStructure, 
                archiveId, 
                archiveIdBase
            );
            
            // Handle case where no candidates were found
            if (fileCandidates.length === 0) {
                this.eventManager.publish('comlist-file-not-found', {
                    message: "No Excel files found in the source folder or its subfolders",
                    error: true
                });
                return;
            }
            
            // Score and sort candidates
            this.scoreComlistFileCandidates(fileCandidates);
            
            // Get best match and decide if it's good enough
            this.selectBestComlistFileMatch(fileCandidates);
            
        }, 100);
    }
    
    /**
     * Validate prerequisites for COMList file finding
     * @param {Object} sourceData - Source data with path and folder structure
     * @param {Object} projectInfo - Project info with archiveId
     * @returns {boolean} - Whether prerequisites are valid
     */
    validateComlistFinderPrerequisites(sourceData, projectInfo) {
        // Check source path
        if (!sourceData.path) {
            this.eventManager.publish('comlist-file-not-found', {
                message: "Cannot find COMList file: Source path not set",
                error: true
            });
            return false;
        }
        
        // Check archive ID
        if (!projectInfo.archiveId) {
            this.eventManager.publish('comlist-file-not-found', {
                message: "Cannot find COMList file: Archive ID not set",
                error: true
            });
            return false;
        }
        
        // Check if folder structure exists
        if (!sourceData.folderStructure) {
            this.eventManager.publish('comlist-file-not-found', {
                message: "Cannot find COMList file: No folder structure information available",
                error: true
            });
            return false;
        }
        
        return true;
    }
    
    /**
     * Collect possible COMList file candidates
     * @param {string} sourcePath - Source path
     * @param {Object} folderStructure - Folder structure
     * @param {string} archiveId - Archive ID
     * @param {string} archiveIdBase - Base part of archive ID
     * @returns {Array} - Array of file candidates
     */
    collectComlistFileCandidates(sourcePath, folderStructure, archiveId, archiveIdBase) {
        const fileCandidates = [];
        
        // Check files in the root folder
        if (folderStructure.files && Array.isArray(folderStructure.files)) {
            console.log("[COMLIST DEBUG] Checking files in root folder:", folderStructure.files);
            
            folderStructure.files.forEach(file => {
                this.analyzeComlistFileCandidate(file, sourcePath, false, archiveId, archiveIdBase, fileCandidates);
            });
        }
        
        // Check subfolders
        if (folderStructure.folders) {
            if (Array.isArray(folderStructure.folders)) {
                console.log("[COMLIST DEBUG] Folders is an array with", folderStructure.folders.length, "entries");
                
                folderStructure.folders.forEach(folderName => {
                    this.checkComlistInSubfolder(sourcePath, folderName, folderStructure, archiveId, archiveIdBase, fileCandidates);
                });
            } else {
                // Alternative format - when folders is an object
                Object.keys(folderStructure.folders).forEach(subfolder => {
                    const subfolderPath = `${sourcePath}\\${subfolder}`;
                    const subfolderFiles = folderStructure.folders[subfolder].files || [];
                    
                    console.log("[COMLIST DEBUG] Checking subfolder:", subfolder, "Files:", subfolderFiles);
                    
                    subfolderFiles.forEach(file => {
                        this.analyzeComlistFileCandidate(file, subfolderPath, true, archiveId, archiveIdBase, fileCandidates);
                    });
                });
            }
        }
        
        console.log("[COMLIST DEBUG] All file candidates:", fileCandidates);
        return fileCandidates;
    }
    
    /**
     * Analyze a file as a potential COMList file
     * @param {string} file - File name
     * @param {string} basePath - Base path
     * @param {boolean} inSubfolder - Whether file is in subfolder
     * @param {string} archiveId - Archive ID
     * @param {string} archiveIdBase - Base part of archive ID
     * @param {Array} fileCandidates - Array of file candidates to add to
     */
    analyzeComlistFileCandidate(file, basePath, inSubfolder, archiveId, archiveIdBase, fileCandidates) {
        const filePath = `${basePath}\\${file}`;
        const extension = file.split('.').pop().toLowerCase();
        
        // Check if it's an Excel file
        const isExcelFile = extension === 'xlsx' || extension === 'xls';
        
        // Check if filename contains keywords
        const containsComlistKeyword = file.toLowerCase().includes('comlist');
        
        // Check if file contains archive ID
        const containsArchiveId = archiveId && (
            file === archiveId + '.xlsx' || 
            file === archiveId + '.xls' ||
            file.startsWith(archiveId + '_') ||
            file.includes('_' + archiveId)
        );
        
        const containsArchiveIdBase = archiveIdBase && (
            file.startsWith(archiveIdBase + '_') ||
            file.includes('_' + archiveIdBase)
        );
        
        console.log("[COMLIST DEBUG] Checking file:", file, 
                  "Path:", filePath,
                  "Extension:", extension,
                  "Is Excel:", isExcelFile,
                  "Contains COMList:", containsComlistKeyword,
                  "Contains Archive ID:", containsArchiveId);
        
        if (isExcelFile) {
            fileCandidates.push({
                name: file,
                path: filePath,
                isExcelFile: true,
                inSubfolder: inSubfolder,
                containsArchiveId: containsArchiveId || containsArchiveIdBase,
                containsComlistKeyword: containsComlistKeyword
            });
        }
    }
    
    /**
     * Check a subfolder for potential COMList files
     * @param {string} sourcePath - Source path
     * @param {string} folderName - Folder name
     * @param {Object} folderStructure - Folder structure
     * @param {string} archiveId - Archive ID
     * @param {string} archiveIdBase - Base part of archive ID
     * @param {Array} fileCandidates - Array of file candidates to add to
     */
    checkComlistInSubfolder(sourcePath, folderName, folderStructure, archiveId, archiveIdBase, fileCandidates) {
        console.log("[COMLIST DEBUG] Examining folder:", folderName);
        
        // If the folder name contains the archive ID, it's likely the right folder
        const folderMatchesArchiveId = archiveId && (
            folderName === archiveId ||
            folderName.startsWith(archiveId + '_') ||
            folderName.includes('_' + archiveId)
        );
        
        const folderMatchesArchiveIdBase = archiveIdBase && (
            folderName.startsWith(archiveIdBase + '_') ||
            folderName.includes('_' + archiveIdBase)
        );
        
        // If this is likely the archive folder, suggest potential COMList file locations
        if (folderMatchesArchiveId || folderMatchesArchiveIdBase) {
            console.log("[COMLIST DEBUG] Found potential archive folder:", folderName);
            
            // Create potential COMList filename variations
            const potentialComlistName = `${archiveId}_comlist.xlsx`;
            const filePath = `${sourcePath}\\${folderName}\\${potentialComlistName}`;
            
            // Add a suggested location
            fileCandidates.push({
                name: potentialComlistName,
                path: filePath,
                isExcelFile: true,
                inSubfolder: true,
                containsArchiveId: true,
                containsComlistKeyword: true,
                isSuggested: true // Flag to indicate this is a suggestion, not a confirmed file
            });
        }
    }
    
    /**
     * Score and sort COMList file candidates
     * @param {Array} fileCandidates - Array of file candidates
     */
    scoreComlistFileCandidates(fileCandidates) {
        fileCandidates.forEach(file => {
            file.score = this.scoreComlistFile(file);
            console.log("[COMLIST DEBUG] Scored file:", file.name, "Score:", file.score);
        });
        
        // Sort by score (highest first)
        fileCandidates.sort((a, b) => b.score - a.score);
    }
    
    /**
     * Select best COMList file match and publish result
     * @param {Array} fileCandidates - Array of file candidates
     */
    selectBestComlistFileMatch(fileCandidates) {
        // Get highest scored file
        const bestMatch = fileCandidates[0];
        console.log("[COMLIST DEBUG] Best match:", bestMatch);
        
        // Decide whether to use the file based on score threshold
        const minimumScore = 2; // Needs to at least be an Excel file with either comlist keyword or archiveID
        
        if (bestMatch.score >= minimumScore) {
            const warningInfo = this.generateComlistWarningInfo(bestMatch);
            
            this.eventManager.publish('comlist-file-found', {
                path: bestMatch.path,
                score: bestMatch.score,
                warningInfo
            });
        } else {
            this.eventManager.publish('comlist-file-not-found', {
                message: "No suitable COMList file found matching criteria",
                error: true
            });
        }
    }
    
    /**
     * Generate warning info for COMList file match
     * @param {Object} match - Best file match
     * @returns {Object} - Warning info object
     */
    generateComlistWarningInfo(match) {
        if (match.score >= 4 && !match.isSuggested) {
            // Perfect match
            return {
                hasWarning: false,
                message: ""
            };
        }
        
        // Construct warning message
        let warningMsg = "AutoCOM: ";
        if (!match.containsComlistKeyword) warningMsg += "no 'comlist' keyword; ";
        if (!match.containsArchiveId) warningMsg += "no archive ID match; ";
        if (match.inSubfolder) warningMsg += "located in subfolder; ";
        if (match.isSuggested) warningMsg += "suggested location only; ";
        
        return {
            hasWarning: true,
            message: warningMsg,
            type: "warning" // Could be "warning" or "error"
        };
    }
    
    /**
     * Helper function to count PDF files in a folder
     * @param {Array} files - Array of filenames
     * @returns {number} - Count of PDF files
     */
    countPdfFilesInFolder(files) {
        if (!files || !Array.isArray(files)) return 0;
        
        return files.filter(file => 
            file.toLowerCase().endsWith('.pdf')
        ).length;
    }
    
    /**
     * Score a folder candidate for being a PDF folder (0-5)
     * @param {Object} folderCandidate - Folder candidate
     * @returns {number} - Score (0-5)
     */
    scorePdfFolder(folderCandidate) {
        let score = 0;
        
        // Must have PDF files to be considered
        if (folderCandidate.isPdfFolder) {
            score += 1;
            
            // Contains pdf keyword in name
            if (folderCandidate.containsPdfKeyword) {
                score += 1;
            }
            
            // Contains archive ID in name
            if (folderCandidate.containsArchiveId) {
                score += 1;
            }
            
            // Not in a subfolder (directly in source)
            if (!folderCandidate.inSubfolder) {
                score += 1;
            }
            
            // Has significant number of PDF files
            if (folderCandidate.pdfCount >= 5) {
                score += 1;
            }
        }
        
        return score;
    }
    
    /**
     * Score a file candidate for being a COMList file (0-4)
     * @param {Object} fileCandidate - File candidate
     * @returns {number} - Score (0-4)
     */
    scoreComlistFile(fileCandidate) {
        let score = 0;
        
        // Must be an Excel file to be considered
        if (fileCandidate.isExcelFile) {
            score += 1;
            
            // Contains comlist keyword
            if (fileCandidate.containsComlistKeyword) {
                score += 1;
            }
            
            // Contains archive ID 
            if (fileCandidate.containsArchiveId) {
                score += 1;
            }
            
            // Not in a subfolder (directly in source)
            if (!fileCandidate.inSubfolder) {
                score += 1;
            }
        }
        
        return score;
    }
    
    /**
     * Extract base part of archive ID (e.g., "RRD017" from "RRD017-2022")
     * @param {string} archiveId - Full archive ID
     * @returns {string} - Base part of archive ID
     */
    extractArchiveIdBase(archiveId) {
        if (!archiveId) return '';
        
        const match = archiveId.match(/^([A-Z0-9]+)-?[A-Z0-9]*/i);
        return match ? match[1] : '';
    }
}
