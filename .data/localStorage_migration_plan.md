# localStorage to Backend Storage Migration Plan

## Overview

This document outlines the comprehensive migration strategy for replacing localStorage with backend storage in the microfilm register workflow system. The current localStorage-based approach is hitting storage quota limits with large datasets, requiring a move to a backend-centric storage solution.

## Current localStorage Usage Analysis

### Primary Workflow Keys

The register module heavily relies on localStorage for storing workflow state data across multiple steps:

| Key | Purpose | Size Impact | Usage Pattern |
|-----|---------|-------------|---------------|
| `microfilmWorkflowState` | Central workflow state and navigation | Medium | Read/Write across all modules |
| `microfilmProjectState` | Project configuration and setup data | Small | Set once, read throughout workflow |
| `microfilmAnalysisData` | Document analysis results | **Large** | Set after analysis, read by allocation/references |
| `microfilmAllocationData` | Film allocation results | **Large** | Set after allocation, read by film numbers/references |
| `microfilmIndexData` | Index generation data | **Large** | Set after indexing, read by references |
| `microfilmFilmNumberResults` | Film number allocation results | **Large** | Set after film numbering, read by references |
| `microfilmDistributionResults` | Distribution processing results | Medium | Set after distribution, read by export |
| `microfilmReferenceSheets` | Reference sheet generation data | **Large** | Set after references, read by export |

### Secondary Keys

| Key | Purpose | Size Impact |
|-----|---------|-------------|
| `microfilmFilmData` | Film-specific data | Medium |
| `microfilmUpdatedIndexData` | Updated index information | Large |
| `dark-mode` | UI preferences | Tiny |
| `projectDetailsCollapsed` | UI state | Tiny |

### Current Usage Patterns

1. **Multi-step workflow persistence** - Data flows through 7+ workflow steps
2. **Cross-module data sharing** - Data stored in one module is used by others
3. **Large dataset storage** - Storing complete document analysis, allocation results
4. **Session recovery** - Users can continue work after browser restart
5. **Backend API integration** - localStorage data is sent to backend for processing

### Files with localStorage Dependencies

Based on grep analysis, the following files have localStorage dependencies:

#### High Priority (Heavy Usage)
- `register/register.js` - Main controller with state management
- `register/welcome.js` - Initial workflow setup
- `register/references/utils.js` - Central workflow state utilities
- `register/references/core.js` - Core reference functionality
- `register/references/api.js` - Backend API integration
- `register/project/project-core.js` - Project state management

#### Medium Priority (Moderate Usage)
- `register/index/index-core.js` - Index data management
- `register/index/index-events.js` - Index event handling
- `register/filmnumber/filmnumber-core.js` - Film number state
- `register/filmnumber/filmnumber-api.js` - Film number API calls

#### Low Priority (Light Usage)
- `register/progress.js` - Progress state
- `register/export.js` - Export functionality
- `register/workflow.js` - Workflow navigation

## The Problem

### Storage Quota Limits
- Browser localStorage typically limited to 5-10MB
- Large projects easily exceed these limits with:
  - Thousands of document analysis results
  - Complete allocation data with roll mappings
  - Detailed index information with page-level data
  - Film number results with comprehensive mapping

### Additional Issues
- **Data Loss Risk** - Browser storage can be cleared
- **No Backup** - Data exists only in browser
- **Single Browser Limitation** - Can't switch browsers/devices
- **No Multi-User Support** - Each user needs their own state
- **Debug Difficulty** - Hard to inspect/debug workflow state

## Proposed Solution: Backend-Centric Storage

### 1. Database Schema - New WorkflowSession Model

```python
# models.py

class WorkflowSession(models.Model):
    """
    Stores workflow state data that was previously in localStorage.
    Replaces client-side storage with backend persistence.
    """
    # Core identification
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='workflow_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    
    # Workflow state data (JSON fields for flexibility)
    workflow_state = models.JSONField(
        default=dict, 
        help_text="Central workflow state (replaces microfilmWorkflowState)"
    )
    project_state = models.JSONField(
        default=dict, 
        help_text="Project configuration data (replaces microfilmProjectState)"
    )
    analysis_data = models.JSONField(
        default=dict, 
        help_text="Document analysis results (replaces microfilmAnalysisData)"
    )
    allocation_data = models.JSONField(
        default=dict, 
        help_text="Film allocation results (replaces microfilmAllocationData)"
    )
    index_data = models.JSONField(
        default=dict, 
        help_text="Index generation data (replaces microfilmIndexData)"
    )
    film_number_results = models.JSONField(
        default=dict, 
        help_text="Film number allocation results (replaces microfilmFilmNumberResults)"
    )
    distribution_results = models.JSONField(
        default=dict, 
        help_text="Distribution results (replaces microfilmDistributionResults)"
    )
    reference_sheets = models.JSONField(
        default=dict, 
        help_text="Reference sheet data (replaces microfilmReferenceSheets)"
    )
    
    # UI state (optional, for user experience)
    ui_preferences = models.JSONField(
        default=dict,
        help_text="UI state like dark-mode, collapsed sections, etc."
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this is the user's active session for this project"
    )
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['project', 'user', 'is_active']),
            models.Index(fields=['session_id']),
            models.Index(fields=['last_accessed']),
        ]
        # Ensure only one active session per user per project
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'user'],
                condition=models.Q(is_active=True),
                name='unique_active_session_per_user_project'
            )
        ]
    
    def __str__(self):
        return f"Workflow session for {self.user.username} - {self.project.archive_id}"
    
    def save(self, *args, **kwargs):
        # If this session is being marked as active, deactivate others
        if self.is_active:
            WorkflowSession.objects.filter(
                project=self.project,
                user=self.user,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
```

### 2. Backend API Endpoints

```python
# views/workflow_views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json
import uuid
from microapp.models import Project, WorkflowSession

@login_required
def get_workflow_session(request, project_id):
    """
    Get or create workflow session for the current user and project.
    """
    if request.method == 'GET':
        try:
            project = get_object_or_404(Project, pk=project_id)
            
            # Get or create active session for this user/project
            session, created = WorkflowSession.objects.get_or_create(
                project=project,
                user=request.user,
                is_active=True,
                defaults={
                    'session_id': uuid.uuid4()
                }
            )
            
            return JsonResponse({
                'session_id': str(session.session_id),
                'workflow_state': session.workflow_state,
                'project_state': session.project_state,
                'analysis_data': session.analysis_data,
                'allocation_data': session.allocation_data,
                'index_data': session.index_data,
                'film_number_results': session.film_number_results,
                'distribution_results': session.distribution_results,
                'reference_sheets': session.reference_sheets,
                'ui_preferences': session.ui_preferences,
                'created': created,
                'updated_at': session.updated_at.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def update_workflow_session(request, session_id):
    """
    Update specific fields in the workflow session.
    Supports partial updates to avoid overwriting other concurrent changes.
    """
    if request.method == 'PATCH':
        try:
            session = get_object_or_404(
                WorkflowSession,
                session_id=session_id,
                user=request.user
            )
            
            data = json.loads(request.body)
            
            # Map localStorage keys to model fields
            field_mapping = {
                'microfilmWorkflowState': 'workflow_state',
                'microfilmProjectState': 'project_state',
                'microfilmAnalysisData': 'analysis_data',
                'microfilmAllocationData': 'allocation_data',
                'microfilmIndexData': 'index_data',
                'microfilmFilmNumberResults': 'film_number_results',
                'microfilmDistributionResults': 'distribution_results',
                'microfilmReferenceSheets': 'reference_sheets',
                'ui_preferences': 'ui_preferences'
            }
            
            # Update only the provided fields
            updated_fields = []
            for key, value in data.items():
                if key in field_mapping:
                    field_name = field_mapping[key]
                    setattr(session, field_name, value)
                    updated_fields.append(field_name)
            
            # Save with only updated fields for efficiency
            session.save(update_fields=updated_fields + ['updated_at', 'last_accessed'])
            
            return JsonResponse({
                'status': 'success',
                'updated_fields': updated_fields,
                'updated_at': session.updated_at.isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def clear_workflow_session(request, session_id):
    """
    Clear workflow session data (equivalent to localStorage.clear).
    """
    if request.method == 'POST':
        try:
            session = get_object_or_404(
                WorkflowSession,
                session_id=session_id,
                user=request.user
            )
            
            # Clear all workflow data
            session.workflow_state = {}
            session.project_state = {}
            session.analysis_data = {}
            session.allocation_data = {}
            session.index_data = {}
            session.film_number_results = {}
            session.distribution_results = {}
            session.reference_sheets = {}
            
            session.save()
            
            return JsonResponse({'status': 'success', 'message': 'Session cleared'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def migrate_localstorage_data(request, project_id):
    """
    Migration endpoint to transfer localStorage data to backend session.
    This is a one-time migration helper.
    """
    if request.method == 'POST':
        try:
            project = get_object_or_404(Project, pk=project_id)
            data = json.loads(request.body)
            
            # Get or create session
            session, created = WorkflowSession.objects.get_or_create(
                project=project,
                user=request.user,
                is_active=True,
                defaults={'session_id': uuid.uuid4()}
            )
            
            # Migrate data from localStorage structure
            if 'microfilmWorkflowState' in data:
                session.workflow_state = data['microfilmWorkflowState']
            if 'microfilmProjectState' in data:
                session.project_state = data['microfilmProjectState']
            if 'microfilmAnalysisData' in data:
                session.analysis_data = data['microfilmAnalysisData']
            if 'microfilmAllocationData' in data:
                session.allocation_data = data['microfilmAllocationData']
            if 'microfilmIndexData' in data:
                session.index_data = data['microfilmIndexData']
            if 'microfilmFilmNumberResults' in data:
                session.film_number_results = data['microfilmFilmNumberResults']
            if 'microfilmDistributionResults' in data:
                session.distribution_results = data['microfilmDistributionResults']
            if 'microfilmReferenceSheets' in data:
                session.reference_sheets = data['microfilmReferenceSheets']
            
            session.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'LocalStorage data migrated successfully',
                'session_id': str(session.session_id)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
```

### 3. Frontend Storage Service

```javascript
// storage-service.js

/**
 * WorkflowStorageService - Replaces localStorage with backend storage
 * Provides the same interface as localStorage but with backend persistence
 */
class WorkflowStorageService {
    constructor(projectId, userId) {
        this.projectId = projectId;
        this.userId = userId;
        this.sessionId = null;
        this.cache = new Map(); // Local cache for frequent reads
        this.pendingWrites = new Map(); // Debounced writes
        this.isInitialized = false;
        this.initPromise = null;
        
        // Configuration
        this.writeDebounceMs = 500; // Debounce writes by 500ms
        this.cacheTimeout = 30000; // Cache timeout 30 seconds
        this.retryAttempts = 3;
    }

    /**
     * Initialize the storage service - must be called before use
     */
    async initialize() {
        if (this.isInitialized) return;
        if (this.initPromise) return this.initPromise;

        this.initPromise = this._doInitialize();
        await this.initPromise;
        this.isInitialized = true;
    }

    async _doInitialize() {
        try {
            // Get or create workflow session
            const response = await fetch(`/api/workflow/session/${this.projectId}/`, {
                method: 'GET',
                headers: this.getHeaders()
            });
            
            if (response.ok) {
                const sessionData = await response.json();
                this.sessionId = sessionData.session_id;
                this.populateCache(sessionData);
                
                console.log('[StorageService] Initialized with session:', this.sessionId);
                
                // If this is a new session, try to migrate localStorage data
                if (sessionData.created) {
                    await this.migrateLocalStorageData();
                }
            } else {
                throw new Error(`Failed to initialize session: ${response.statusText}`);
            }
        } catch (error) {
            console.error('[StorageService] Initialization failed:', error);
            // Fallback to localStorage-only mode
            this.sessionId = null;
        }
    }

    /**
     * Set an item in storage (replaces localStorage.setItem)
     */
    async setItem(key, value) {
        // Ensure initialized
        await this.initialize();
        
        // Update local cache immediately for responsive UI
        this.cache.set(key, {
            value: value,
            timestamp: Date.now()
        });
        
        // Also update localStorage as fallback
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('[StorageService] localStorage setItem failed:', e);
        }
        
        // Debounce backend writes to avoid excessive requests
        if (this.sessionId) {
            this.debounceWrite(key, value);
        }
    }

    /**
     * Get an item from storage (replaces localStorage.getItem)
     */
    async getItem(key) {
        // Ensure initialized
        await this.initialize();
        
        // Try cache first (most recent data)
        const cached = this.cache.get(key);
        if (cached && this.isCacheValid(cached)) {
            return cached.value;
        }
        
        // If no session, fallback to localStorage
        if (!this.sessionId) {
            return this.getLocalStorageItem(key);
        }
        
        // For initial load, we should have the data from initialization
        // For subsequent reads, use cache or localStorage fallback
        return this.getLocalStorageItem(key);
    }

    /**
     * Remove an item from storage (replaces localStorage.removeItem)
     */
    async removeItem(key) {
        await this.initialize();
        
        // Remove from cache
        this.cache.delete(key);
        
        // Remove from localStorage
        localStorage.removeItem(key);
        
        // Clear from backend
        if (this.sessionId) {
            this.debounceWrite(key, null);
        }
    }

    /**
     * Clear all storage (replaces localStorage.clear)
     */
    async clear() {
        await this.initialize();
        
        // Clear cache
        this.cache.clear();
        
        // Clear localStorage items we manage
        const keysToRemove = [
            'microfilmWorkflowState',
            'microfilmProjectState', 
            'microfilmAnalysisData',
            'microfilmAllocationData',
            'microfilmIndexData',
            'microfilmFilmNumberResults',
            'microfilmDistributionResults',
            'microfilmReferenceSheets'
        ];
        
        keysToRemove.forEach(key => localStorage.removeItem(key));
        
        // Clear backend session
        if (this.sessionId) {
            try {
                await fetch(`/api/workflow/session/${this.sessionId}/clear/`, {
                    method: 'POST',
                    headers: this.getHeaders()
                });
            } catch (error) {
                console.error('[StorageService] Failed to clear backend session:', error);
            }
        }
    }

    /**
     * Debounce writes to backend to avoid excessive requests
     */
    debounceWrite(key, value) {
        // Clear existing timeout
        if (this.pendingWrites.has(key)) {
            clearTimeout(this.pendingWrites.get(key));
        }

        // Set new timeout
        const timeoutId = setTimeout(async () => {
            await this.writeToBackend(key, value);
            this.pendingWrites.delete(key);
        }, this.writeDebounceMs);

        this.pendingWrites.set(key, timeoutId);
    }

    /**
     * Write data to backend with retry logic
     */
    async writeToBackend(key, value, attempt = 1) {
        if (!this.sessionId) return;

        try {
            const payload = {};
            payload[key] = value;

            const response = await fetch(`/api/workflow/session/${this.sessionId}/update/`, {
                method: 'PATCH',
                headers: this.getHeaders(),
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Backend write failed: ${response.statusText}`);
            }

            console.log(`[StorageService] Successfully wrote ${key} to backend`);

        } catch (error) {
            console.error(`[StorageService] Write attempt ${attempt} failed:`, error);
            
            // Retry with exponential backoff
            if (attempt < this.retryAttempts) {
                const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s
                setTimeout(() => {
                    this.writeToBackend(key, value, attempt + 1);
                }, delay);
            } else {
                console.error(`[StorageService] Failed to write ${key} after ${this.retryAttempts} attempts`);
            }
        }
    }

    /**
     * Populate local cache from session data
     */
    populateCache(sessionData) {
        const keyMapping = {
            'workflow_state': 'microfilmWorkflowState',
            'project_state': 'microfilmProjectState',
            'analysis_data': 'microfilmAnalysisData',
            'allocation_data': 'microfilmAllocationData',
            'index_data': 'microfilmIndexData',
            'film_number_results': 'microfilmFilmNumberResults',
            'distribution_results': 'microfilmDistributionResults',
            'reference_sheets': 'microfilmReferenceSheets'
        };

        Object.entries(keyMapping).forEach(([backendKey, frontendKey]) => {
            if (sessionData[backendKey] && Object.keys(sessionData[backendKey]).length > 0) {
                this.cache.set(frontendKey, {
                    value: sessionData[backendKey],
                    timestamp: Date.now()
                });
            }
        });
    }

    /**
     * Migrate existing localStorage data to backend
     */
    async migrateLocalStorageData() {
        const dataToMigrate = {};
        const keysToMigrate = [
            'microfilmWorkflowState',
            'microfilmProjectState',
            'microfilmAnalysisData',
            'microfilmAllocationData',
            'microfilmIndexData',
            'microfilmFilmNumberResults',
            'microfilmDistributionResults',
            'microfilmReferenceSheets'
        ];

        // Collect localStorage data
        keysToMigrate.forEach(key => {
            const value = this.getLocalStorageItem(key);
            if (value !== null) {
                dataToMigrate[key] = value;
            }
        });

        // If we have data to migrate, send it to backend
        if (Object.keys(dataToMigrate).length > 0) {
            try {
                const response = await fetch(`/api/workflow/session/${this.projectId}/migrate/`, {
                    method: 'POST',
                    headers: this.getHeaders(),
                    body: JSON.stringify(dataToMigrate)
                });

                if (response.ok) {
                    console.log('[StorageService] Successfully migrated localStorage data');
                } else {
                    console.error('[StorageService] Migration failed:', response.statusText);
                }
            } catch (error) {
                console.error('[StorageService] Migration error:', error);
            }
        }
    }

    /**
     * Helper methods
     */
    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken()
        };
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    isCacheValid(cacheEntry) {
        return (Date.now() - cacheEntry.timestamp) < this.cacheTimeout;
    }

    getLocalStorageItem(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error(`[StorageService] Error parsing localStorage item ${key}:`, error);
            return null;
        }
    }
}

// Global storage service instance
let workflowStorage = null;

/**
 * Initialize storage service for the current project
 */
async function initializeWorkflowStorage(projectId, userId) {
    if (!workflowStorage) {
        workflowStorage = new WorkflowStorageService(projectId, userId);
        await workflowStorage.initialize();
    }
    return workflowStorage;
}

/**
 * Get the current storage service instance
 */
function getWorkflowStorage() {
    if (!workflowStorage) {
        throw new Error('Workflow storage not initialized. Call initializeWorkflowStorage() first.');
    }
    return workflowStorage;
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WorkflowStorageService, initializeWorkflowStorage, getWorkflowStorage };
}
```

### 4. Migration Utilities

```javascript
// migration-utils.js

/**
 * Utility functions to help migrate from localStorage to backend storage
 */

/**
 * Update a JavaScript file to use WorkflowStorageService instead of localStorage
 */
class LocalStorageMigrator {
    constructor() {
        this.replacements = [
            // localStorage.setItem calls
            {
                pattern: /localStorage\.setItem\(\s*['"`]([^'"`]+)['"`]\s*,\s*JSON\.stringify\(([^)]+)\)\s*\)/g,
                replacement: 'await workflowStorage.setItem(\'$1\', $2)'
            },
            // localStorage.getItem calls with JSON.parse
            {
                pattern: /JSON\.parse\(\s*localStorage\.getItem\(\s*['"`]([^'"`]+)['"`]\s*\)\s*\|\|\s*['"`]({[^}]*})['"`]\s*\)/g,
                replacement: '(await workflowStorage.getItem(\'$1\')) || $2'
            },
            // Simple localStorage.getItem calls
            {
                pattern: /localStorage\.getItem\(\s*['"`]([^'"`]+)['"`]\s*\)/g,
                replacement: 'await workflowStorage.getItem(\'$1\')'
            },
            // localStorage.removeItem calls
            {
                pattern: /localStorage\.removeItem\(\s*['"`]([^'"`]+)['"`]\s*\)/g,
                replacement: 'await workflowStorage.removeItem(\'$1\')'
            }
        ];
    }

    /**
     * Generate migration instructions for a specific file
     */
    generateMigrationInstructions(filePath, currentContent) {
        const instructions = {
            file: filePath,
            changes: [],
            requiresAsyncConversion: false,
            addImports: []
        };

        // Check what localStorage calls exist
        this.replacements.forEach(({ pattern, replacement }) => {
            const matches = currentContent.match(pattern);
            if (matches) {
                instructions.changes.push({
                    pattern: pattern.source,
                    replacement,
                    occurrences: matches.length
                });
                
                if (replacement.includes('await')) {
                    instructions.requiresAsyncConversion = true;
                }
            }
        });

        // Check if storage service import is needed
        if (instructions.changes.length > 0) {
            instructions.addImports.push(
                'import { getWorkflowStorage } from \'../storage-service.js\';'
            );
        }

        return instructions;
    }

    /**
     * Apply automatic migrations where possible
     */
    applyAutomaticMigration(content) {
        let migratedContent = content;
        
        this.replacements.forEach(({ pattern, replacement }) => {
            migratedContent = migratedContent.replace(pattern, replacement);
        });

        return migratedContent;
    }
}

/**
 * Backward compatibility wrapper for localStorage calls
 * Use this during transition period
 */
class StorageCompatibilityLayer {
    constructor() {
        this.storage = null;
        this.fallbackToLocalStorage = true;
    }

    async init(projectId, userId) {
        try {
            this.storage = await initializeWorkflowStorage(projectId, userId);
            this.fallbackToLocalStorage = false;
        } catch (error) {
            console.warn('[StorageCompat] Failed to init backend storage, using localStorage:', error);
            this.fallbackToLocalStorage = true;
        }
    }

    async setItem(key, value) {
        if (this.storage && !this.fallbackToLocalStorage) {
            return await this.storage.setItem(key, value);
        } else {
            localStorage.setItem(key, JSON.stringify(value));
        }
    }

    async getItem(key) {
        if (this.storage && !this.fallbackToLocalStorage) {
            return await this.storage.getItem(key);
        } else {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        }
    }

    async removeItem(key) {
        if (this.storage && !this.fallbackToLocalStorage) {
            return await this.storage.removeItem(key);
        } else {
            localStorage.removeItem(key);
        }
    }

    async clear() {
        if (this.storage && !this.fallbackToLocalStorage) {
            return await this.storage.clear();
        } else {
            // Clear only our keys
            const keysToRemove = [
                'microfilmWorkflowState',
                'microfilmProjectState',
                'microfilmAnalysisData',
                'microfilmAllocationData',
                'microfilmIndexData',
                'microfilmFilmNumberResults',
                'microfilmDistributionResults',
                'microfilmReferenceSheets'
            ];
            keysToRemove.forEach(key => localStorage.removeItem(key));
        }
    }
}

// Export utilities
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LocalStorageMigrator, StorageCompatibilityLayer };
}
```

## Implementation Plan

### Phase 1: Infrastructure Setup (Days 1-3)

#### Day 1: Database and Models
1. **Create Django Migration**
   ```bash
   python manage.py makemigrations --name add_workflow_session
   python manage.py migrate
   ```

2. **Add URL Routes**
   ```python
   # urls.py
   path('api/workflow/session/<int:project_id>/', views.get_workflow_session, name='get_workflow_session'),
   path('api/workflow/session/<uuid:session_id>/update/', views.update_workflow_session, name='update_workflow_session'),
   path('api/workflow/session/<uuid:session_id>/clear/', views.clear_workflow_session, name='clear_workflow_session'),
   path('api/workflow/session/<int:project_id>/migrate/', views.migrate_localstorage_data, name='migrate_localstorage_data'),
   ```

#### Day 2: Backend API Implementation
1. Create `views/workflow_views.py` with all endpoints
2. Add error handling and validation
3. Test API endpoints with Postman/curl

#### Day 3: Frontend Storage Service
1. Create `storage-service.js` 
2. Implement caching and debouncing logic
3. Create migration utilities
4. Unit test the storage service

### Phase 2: Module Migration (Days 4-10)

Migration priority based on localStorage usage intensity:

#### Day 4: Core Utilities (High Priority)
- **`register/references/utils.js`** - Central workflow state management
  - Replace `saveToWorkflowState()` and `loadFromWorkflowState()` functions
  - Convert to async/await pattern
  
#### Day 5: Main Controllers (High Priority)  
- **`register/register.js`** - Main controller
- **`register/welcome.js`** - Initial workflow setup
  - Update initialization logic
  - Convert clear operations to storage service

#### Day 6: References Module (High Priority)
- **`register/references/core.js`** - Core reference functionality
- **`register/references/api.js`** - Backend API integration
  - Update `loadDataFromLocalStorage()` method
  - Convert API data collection to storage service

#### Day 7: Project Module (Medium Priority)
- **`register/project/project-core.js`** - Project state management
  - Convert project state persistence
  - Update state restoration logic

#### Day 8: Index Module (Medium Priority)
- **`register/index/index-core.js`** - Index data management  
- **`register/index/index-events.js`** - Index event handling
  - Convert index data storage
  - Update event handlers

#### Day 9: Film Number Module (Medium Priority)
- **`register/filmnumber/filmnumber-core.js`** - Film number state
- **`register/filmnumber/filmnumber-api.js`** - Film number API calls
  - Convert film number results storage
  - Update API response handling

#### Day 10: Supporting Modules (Low Priority)
- **`register/progress.js`** - Progress state
- **`register/export.js`** - Export functionality  
- **`register/workflow.js`** - Workflow navigation

### Phase 3: Testing and Optimization (Days 11-14)

#### Day 11-12: Integration Testing
1. Test complete workflow end-to-end
2. Test browser refresh/recovery scenarios
3. Test with large datasets
4. Test concurrent user scenarios

#### Day 13: Performance Optimization
1. Optimize caching strategies
2. Tune debounce timing
3. Add performance monitoring
4. Database index optimization

#### Day 14: Migration and Cleanup
1. Deploy migration scripts
2. Remove localStorage fallbacks
3. Clean up unused code
4. Documentation updates

## Migration Process for Each Module

### Standard Migration Pattern

For each JavaScript file:

1. **Add Storage Service Import**
   ```javascript
   import { getWorkflowStorage } from '../storage-service.js';
   ```

2. **Convert Function Signatures to Async**
   ```javascript
   // Before
   function saveData() {
       localStorage.setItem('key', JSON.stringify(data));
   }
   
   // After  
   async function saveData() {
       const storage = getWorkflowStorage();
       await storage.setItem('key', data);
   }
   ```

3. **Update localStorage Calls**
   ```javascript
   // Before
   const data = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
   localStorage.setItem('microfilmWorkflowState', JSON.stringify(state));
   localStorage.removeItem('microfilmAnalysisData');
   
   // After
   const storage = getWorkflowStorage();
   const data = await storage.getItem('microfilmProjectState') || {};
   await storage.setItem('microfilmWorkflowState', state);
   await storage.removeItem('microfilmAnalysisData');
   ```

4. **Update Function Calls to Await**
   ```javascript
   // Before
   saveData();
   const result = loadData();
   
   // After
   await saveData();
   const result = await loadData();
   ```

### Example Migration: `references/utils.js`

**Before:**
```javascript
function saveToWorkflowState(data) {
    try {
        const state = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        const newState = { ...state, ...data };
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(newState));
    } catch (error) {
        console.error('Error saving to workflow state:', error);
    }
}

function loadFromWorkflowState() {
    try {
        return JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
    } catch (error) {
        console.error('Error loading from workflow state:', error);
        return {};
    }
}
```

**After:**
```javascript
import { getWorkflowStorage } from '../storage-service.js';

async function saveToWorkflowState(data) {
    try {
        const storage = getWorkflowStorage();
        const state = await storage.getItem('microfilmWorkflowState') || {};
        const newState = { ...state, ...data };
        await storage.setItem('microfilmWorkflowState', newState);
    } catch (error) {
        console.error('Error saving to workflow state:', error);
    }
}

async function loadFromWorkflowState() {
    try {
        const storage = getWorkflowStorage();
        return await storage.getItem('microfilmWorkflowState') || {};
    } catch (error) {
        console.error('Error loading from workflow state:', error);
        return {};
    }
}
```

## Benefits of the New Architecture

### 1. **No Storage Limits**
- Database can handle any project size
- No browser quota restrictions
- Supports massive datasets with thousands of documents

### 2. **Cross-Browser Persistence** 
- Data survives browser changes
- Users can switch between devices
- No data loss from browser storage clearing

### 3. **Multi-User Support**
- Each user gets their own workflow session
- Concurrent users on same project supported
- Proper user isolation

### 4. **Backup and Recovery**
- Data automatically backed up in database
- Point-in-time recovery possible
- No risk of data loss

### 5. **Performance Improvements**
- Debounced writes reduce server load
- Local caching for responsive UI
- Optimized for large datasets

### 6. **Analytics and Monitoring**
- Track workflow completion rates
- Monitor performance bottlenecks
- Debug user issues more easily

### 7. **Data Integrity**
- ACID compliance from database
- Proper error handling
- Retry logic for failed operations

## Risk Mitigation

### 1. **Backward Compatibility**
- Gradual migration with localStorage fallback
- Migration utilities for existing data
- Rollback plan if issues arise

### 2. **Performance Monitoring**
- Database query optimization
- Response time monitoring
- Cache hit rate tracking

### 3. **Error Handling**
- Graceful degradation to localStorage
- Retry logic for network failures
- User-friendly error messages

### 4. **Testing Strategy**
- Unit tests for storage service
- Integration tests for full workflow
- Load testing with large datasets
- Browser compatibility testing

## Maintenance and Operations

### 1. **Database Maintenance**
- Regular cleanup of old sessions
- Index optimization
- Performance monitoring

### 2. **Session Management**
- Automatic session cleanup after 30 days
- Session timeout handling
- Multiple session support per user

### 3. **Monitoring**
- API response time alerts
- Database performance monitoring  
- Error rate tracking
- User session analytics

### 4. **Backup Strategy**
- Daily database backups
- Point-in-time recovery
- Session data export tools

## Conclusion

This migration plan provides a comprehensive approach to replacing localStorage with a robust backend storage solution. The phased implementation ensures minimal disruption while delivering significant improvements in reliability, scalability, and user experience.

The new architecture will support:
- ✅ Unlimited storage capacity for large projects
- ✅ Cross-browser and cross-device persistence  
- ✅ Multi-user concurrent workflows
- ✅ Automatic backup and recovery
- ✅ Performance optimization with caching
- ✅ Analytics and monitoring capabilities

The implementation timeline of 14 days provides a structured approach to migrate all modules while maintaining system stability and user experience.