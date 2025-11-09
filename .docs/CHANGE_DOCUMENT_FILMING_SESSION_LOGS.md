# Change Document: Remove FilmingSessionLog Database Storage
## Switch to Pure WebSocket Streaming for Filming Session Logs

**Date:** 2025-01-15  
**Status:** Proposed  
**Priority:** Medium  
**Impact:** Low (Frontend functionality preserved)

---

## Executive Summary

This document outlines the removal of the `FilmingSessionLog` database model and all associated database storage operations. The system will transition to a pure WebSocket streaming architecture where logs are only delivered in real-time to connected clients. No historical log storage or retrieval will be maintained.

### Key Changes
- Remove `FilmingSessionLog` model from database
- Remove all database write operations for logs
- Keep WebSocket broadcasting (already functional)
- Modify/remove API endpoints that query historical logs
- Frontend continues to work via WebSocket (no changes needed)

---

## Current Architecture

### Database Storage
- **Model:** `FilmingSessionLog` (lines 652-682 in `models.py`)
- **Storage:** All log entries saved to database with fields:
  - `session` (ForeignKey to FilmingSession)
  - `level` (debug, info, warning, error, critical)
  - `message` (Text)
  - `workflow_state` (CharField, optional)
  - `created_at` (DateTimeField)

### Log Flow
1. **Generation:** Logs created in `SMAProcessManager._monitor_logs()` and `_monitor_errors()`
2. **Storage:** `SMACallbackHandler._store_log_entry()` saves to database
3. **Broadcast:** `SMACallbackHandler._broadcast_log_entry()` sends via WebSocket
4. **Retrieval:** API endpoint `session_logs()` queries database for historical logs

### Log Data Structure
```python
log_entry = {
    'timestamp': '2025-01-15T10:30:45.123456',  # ISO format
    'level': 'info',  # 'debug', 'info', 'warning', 'error', 'critical'
    'message': 'Actual log message text',
    'source': 'sma_stdout' or 'sma_stderr',
    'workflow_state': 'monitoring'  # Optional
}
```

### Progress Data Structure
```python
progress_data = {
    'progress_percent': 25.5,  # Float 0-100
    'processed_documents': 123,  # Integer
    'total_documents': 500,  # Integer
    'timestamp': '2025-01-15T10:30:45.123456',  # ISO format
    'workflow_state': 'monitoring'  # Optional
}
```

---

## Proposed Architecture

### Pure WebSocket Streaming
- **No Database Storage:** Logs are never written to database
- **Real-time Only:** Clients receive logs from the moment they connect
- **No Historical Retrieval:** Past logs are not available after session ends
- **WebSocket Events:** All log types broadcast via existing WebSocket infrastructure

### Log Flow (New)
1. **Generation:** Logs created in `SMAProcessManager._monitor_logs()` and `_monitor_errors()`
2. **Broadcast Only:** `SMACallbackHandler._broadcast_log_entry()` sends via WebSocket
3. **No Storage:** `_store_log_entry()` becomes a no-op or is removed
4. **No Retrieval:** API endpoint returns empty or is removed

### WebSocket Message Types (Unchanged)
- `sma_log` - Log entries (real-time streaming)
- `sma_progress` - Progress updates (real-time streaming)
- `sma_workflow_state` - Workflow state changes
- `sma_error` - Error notifications
- `sma_completed` - Completion notifications

---

## Detailed Changes by File

### 1. `micro/microapp/models.py`

**Location:** Lines 652-682

**Action:** Remove entire `FilmingSessionLog` model class

**Code to Remove:**
```python
class FilmingSessionLog(models.Model):
    """Stores log entries for filming sessions."""
    LOG_LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    # Relationships
    session = models.ForeignKey(FilmingSession, on_delete=models.CASCADE, related_name='logs')
    
    # Log information
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, default='info')
    message = models.TextField(help_text="Log message content")
    workflow_state = models.CharField(max_length=20, blank=True, null=True, help_text="Workflow state when log was created")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', '-created_at']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"{self.session.session_id} [{self.level}]: {self.message[:50]}..."
```

**Impact:** 
- Removes database table
- Removes `session.logs` reverse relationship
- No other models depend on this

---

### 2. `micro/microapp/services/sma_processor/sma_process_manager.py`

**Location:** Lines 1099-1114

**Action:** Modify `_store_log_entry()` to remove database writes

**Current Code:**
```python
def _store_log_entry(self, log_data: Dict[str, Any]):
    """Store log entry in database."""
    try:
        from ...models import FilmingSession, FilmingSessionLog
        
        session = FilmingSession.objects.get(session_id=self.session_id)
        
        FilmingSessionLog.objects.create(
            session=session,
            level=log_data.get('level', 'info'),
            message=log_data.get('message', ''),
            workflow_state=log_data.get('workflow_state', session.workflow_state)
        )
        
    except Exception as e:
        logger.error(f"Error storing log entry: {e}")
```

**New Code:**
```python
def _store_log_entry(self, log_data: Dict[str, Any]):
    """Store log entry (no-op - logs are only streamed via WebSocket)."""
    # Logs are broadcast via WebSocket in _broadcast_log_entry()
    # No database storage needed for streaming-only architecture
    pass
```

**Alternative:** Remove the method entirely and update `on_log_entry()` to not call it.

**Location:** Line 957 in `on_log_entry()`

**Current Code:**
```python
def on_log_entry(self, log_data: Dict[str, Any]):
    """Handle log entries from SMA process."""
    try:
        # Store log entry in database
        self._store_log_entry(log_data)
        
        # Broadcast ALL log entries to WebSocket clients for real-time viewing
        self._broadcast_log_entry(log_data)
        
        # Check for error conditions
        log_level = log_data.get('level', 'info')
        if log_level in ['error', 'critical']:
            self._handle_error_condition(log_data)
        
    except Exception as e:
        logger.error(f"Error handling log entry: {e}")
```

**New Code:**
```python
def on_log_entry(self, log_data: Dict[str, Any]):
    """Handle log entries from SMA process."""
    try:
        # Broadcast ALL log entries to WebSocket clients for real-time viewing
        self._broadcast_log_entry(log_data)
        
        # Check for error conditions
        log_level = log_data.get('level', 'info')
        if log_level in ['error', 'critical']:
            self._handle_error_condition(log_data)
        
    except Exception as e:
        logger.error(f"Error handling log entry: {e}")
```

**Impact:**
- Removes database write operations
- WebSocket broadcasting continues unchanged
- Error handling continues unchanged

---

### 3. `micro/microapp/views/sma_views.py`

**Location:** Lines 22 (import), 456-530 (function)

**Action:** Remove import and modify/remove `session_logs()` endpoint

**Import to Remove:**
```python
from ..models import Project, Roll, FilmingSession, FilmingSessionLog
```

**New Import:**
```python
from ..models import Project, Roll, FilmingSession
```

**Current Function (Lines 456-530):**
```python
@csrf_exempt
@login_required
@require_http_methods(["GET"])
def session_logs(request, session_id):
    """Get logs for a filming session with enhanced filtering and pagination."""
    # ... full implementation that queries FilmingSessionLog.objects ...
```

**Option A - Return Empty (Recommended):**
```python
@csrf_exempt
@login_required
@require_http_methods(["GET"])
def session_logs(request, session_id):
    """Get logs for a filming session - streaming only, no historical logs."""
    try:
        # Validate session exists
        try:
            session = FilmingSession.objects.get(session_id=session_id)
        except FilmingSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Session not found'
            }, status=404)
        
        # Check user permissions
        session_result = SMAService.get_session_status(session_id)
        if session_result['success']:
            session_user_id = session_result['status'].get('user_id')
            if session_user_id and session_user_id != request.user.id and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Access denied'
                }, status=403)
        
        # Return empty logs with message
        return JsonResponse({
            'success': True,
            'logs': [],
            'message': 'Logs are streamed via WebSocket only. Connect to WebSocket for real-time logs.',
            'pagination': {
                'page': 1,
                'pages': 1,
                'per_page': 100,
                'total': 0,
                'has_next': False,
                'has_previous': False
            }
        })
        
    except Exception as e:
        logger.error(f"Error in session_logs: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

**Option B - Remove Endpoint Entirely:**
- Remove the function
- Remove URL route (see `urls.py` section)
- Frontend will need to handle 404 gracefully

**Impact:**
- API endpoint no longer returns historical logs
- Frontend `updateSessionLogs()` will receive empty array
- WebSocket streaming continues to work

---

### 4. `micro/microapp/services/sma_service.py`

**Location:** Line 22 (import), Lines 764-767 (log statistics)

**Action:** Remove import and log statistics calculation

**Import to Remove:**
```python
from ..models import FilmingSession, FilmingSessionLog, Project, Roll, TempRoll
```

**New Import:**
```python
from ..models import FilmingSession, Project, Roll, TempRoll
```

**Current Code (Lines 764-767):**
```python
# Log statistics
log_stats = FilmingSessionLog.objects.filter(session=session).values('level').annotate(
    count=models.Count('level')
)
stats['log_counts'] = {item['level']: item['count'] for item in log_stats}
```

**New Code:**
```python
# Log statistics removed - logs are stream-only via WebSocket
# stats['log_counts'] = {}  # Optional: return empty dict for API compatibility
```

**Impact:**
- `get_session_status()` no longer includes log counts
- API consumers expecting `log_counts` will get empty dict or missing key

---

### 5. `micro/microapp/admin.py`

**Location:** Line 7 (import), Lines 402-414 (admin class), Line 741 (registration)

**Action:** Remove all `FilmingSessionLog` references

**Import to Remove:**
```python
ProcessedDocument, FilmingSession, FilmingSessionLog,
```

**New Import:**
```python
ProcessedDocument, FilmingSession,
```

**Code to Remove (Lines 402-414):**
```python
class FilmingSessionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'level', 'workflow_state', 'message', 'created_at')
    search_fields = ('session__session_id', 'message')
    list_filter = ('level', 'workflow_state', 'created_at')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'session')
        }),
        ('Log Information', {
            'fields': ('level', 'workflow_state', 'message', 'created_at')
        }),
    )
```

**Registration to Remove (Line 741):**
```python
admin.site.register(FilmingSessionLog, FilmingSessionLogAdmin)
```

**Impact:**
- Admin interface no longer shows log entries
- No admin functionality lost (logs were read-only anyway)

---

### 6. `micro/microapp/management/commands/get_session_logs.py`

**Action:** Delete entire file

**Reason:** Management command is only for retrieving database logs, which no longer exist.

**Alternative:** Modify to show message that logs are stream-only:
```python
from django.core.management.base import BaseCommand, CommandError
from microapp.models import FilmingSession

class Command(BaseCommand):
    help = 'Get logs from a filming session (streaming only - no historical logs)'

    def add_arguments(self, parser):
        parser.add_argument(
            'session_id',
            type=str,
            help='The session ID to get logs for'
        )

    def handle(self, *args, **options):
        session_id = options['session_id']
        
        try:
            session = FilmingSession.objects.get(session_id=session_id)
        except FilmingSession.DoesNotExist:
            raise CommandError(f'Filming session with ID "{session_id}" does not exist')
        
        self.stdout.write(
            self.style.WARNING(
                'Logs are streamed via WebSocket only. '
                'No historical logs are stored. '
                'Connect to WebSocket endpoint for real-time logs.'
            )
        )
```

**Recommendation:** Delete the file entirely.

---

### 7. `micro/microapp/urls.py`

**Location:** Lines 253 and 331 (URL routes)

**Action:** Remove or comment out log-related routes

**Routes to Remove:**
```python
path('api/sma/logs/<str:session_id>/', views.filming_logs, name='filming_logs'),
path('api/sma/session/<str:session_id>/logs/', sma_views.session_logs, name='sma_session_logs'),
```

**Impact:**
- Frontend calls to these endpoints will 404
- If keeping Option A from `sma_views.py`, keep the routes but they return empty

**Recommendation:** Keep routes but return empty (Option A) for backward compatibility.

---

### 8. Database Migration

**Action:** Create new migration to drop `FilmingSessionLog` table

**Migration File:** `micro/microapp/migrations/XXXX_remove_filmingsessionlog.py`

**Migration Code:**
```python
# Generated migration
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('microapp', '0013_filmingsessionlog_and_more'),  # Adjust to your latest migration
    ]

    operations = [
        migrations.DeleteModel(
            name='FilmingSessionLog',
        ),
    ]
```

**Warning:** This will delete all existing log data. Ensure this is acceptable before running.

**Data Loss:**
- All historical log entries will be permanently deleted
- No recovery possible after migration runs
- Consider backup if historical logs are needed

---

## Frontend Impact Analysis

### Current Frontend Usage

**File:** `micro/microapp/static/microapp/js/film/sma-filming.js`

**Function:** `updateSessionLogs()` (Lines 1073-1093)

**Current Behavior:**
- Calls `/api/sma/session/${sessionId}/logs/`
- Renders logs in UI
- Also receives logs via WebSocket in `handleWebSocketUpdate()`

**After Change:**
- API call returns empty array
- WebSocket continues to work (primary source)
- UI may show "No log entries available" initially
- Logs populate as they stream via WebSocket

**Recommendation:** 
- Keep `updateSessionLogs()` but it will show empty initially
- WebSocket is primary log source (already working)
- Consider removing API call entirely and rely only on WebSocket

**File:** `micro/microapp/static/microapp/js/film_old.js`

**Function:** `viewFilmLog()` (Line 693)

**Current Behavior:**
- Calls `/api/sma/logs/${sessionId}/`
- Shows logs in modal

**After Change:**
- API returns empty or 404
- Function will show "No logs available" or error

**Recommendation:** 
- Update to show message: "Logs are stream-only. Connect during filming to view logs."
- Or remove the function if not actively used

---

## Testing Plan

### Unit Tests
1. **Model Removal:**
   - Verify `FilmingSessionLog` model no longer exists
   - Verify no imports reference it
   - Verify migrations run successfully

2. **Service Tests:**
   - Verify `_store_log_entry()` no longer writes to database
   - Verify `_broadcast_log_entry()` still works
   - Verify `on_log_entry()` handles logs correctly

3. **API Tests:**
   - Verify `session_logs()` returns empty array
   - Verify permissions still work
   - Verify error handling

### Integration Tests
1. **WebSocket Streaming:**
   - Connect WebSocket client
   - Verify logs stream in real-time
   - Verify progress updates stream
   - Verify all message types work

2. **Frontend:**
   - Load filming page
   - Verify WebSocket connects
   - Verify logs appear in UI via WebSocket
   - Verify API call doesn't break (returns empty)

3. **End-to-End:**
   - Start filming session
   - Connect multiple clients
   - Verify all receive logs simultaneously
   - Verify logs stop when session ends

### Regression Tests
1. **Filming Process:**
   - Start filming session
   - Verify logs appear
   - Complete session
   - Verify no errors

2. **Error Handling:**
   - Trigger error condition
   - Verify error logs stream
   - Verify error handling still works

---

## Rollback Plan

If issues arise, rollback steps:

1. **Database:**
   - Restore `FilmingSessionLog` model from backup
   - Run reverse migration
   - Restore data from backup (if available)

2. **Code:**
   - Revert all file changes
   - Restore `_store_log_entry()` database writes
   - Restore API endpoint functionality

3. **Deployment:**
   - Revert to previous deployment
   - Restore database from backup

**Note:** Once migration runs and deletes table, data cannot be recovered without backup.

---

## Migration Checklist

### Pre-Migration
- [ ] Review all changes in this document
- [ ] Backup database (especially `FilmingSessionLog` table)
- [ ] Test changes in development environment
- [ ] Verify WebSocket streaming works
- [ ] Update frontend if needed
- [ ] Notify users of change (if applicable)

### Migration Steps
1. [ ] Deploy code changes (all files except migration)
2. [ ] Run database migration: `python manage.py migrate`
3. [ ] Verify migration succeeded
4. [ ] Test WebSocket streaming
5. [ ] Test API endpoints
6. [ ] Monitor for errors

### Post-Migration
- [ ] Verify no errors in logs
- [ ] Verify WebSocket connections work
- [ ] Verify filming sessions work
- [ ] Monitor for 24 hours
- [ ] Document any issues

---

## Benefits

1. **Simplified Architecture:**
   - No database overhead for logs
   - No log cleanup needed
   - Simpler codebase

2. **Real-time Focus:**
   - Logs only when needed (during filming)
   - No storage concerns
   - Lower database load

3. **Frontend Compatibility:**
   - WebSocket already primary source
   - Minimal frontend changes needed
   - Existing functionality preserved

## Drawbacks

1. **No Historical Logs:**
   - Cannot retrieve logs after session ends
   - No audit trail in database
   - Debugging past sessions not possible

2. **Connection Required:**
   - Must be connected during filming to see logs
   - Reconnection loses previous logs
   - No offline log viewing

3. **No Log Analysis:**
   - Cannot query logs by level, time, etc.
   - No log statistics
   - No log export functionality

---

## Alternative Considerations

### Option 1: Hybrid Approach
- Store only error/critical logs in database
- Stream all logs via WebSocket
- Provides audit trail for errors only

### Option 2: Time-Limited Storage
- Store logs in memory/cache for 24 hours
- Allow API retrieval during this period
- Auto-cleanup after expiration

### Option 3: Optional Storage
- Make storage configurable per session
- Allow users to enable/disable log storage
- Default to streaming-only

**Recommendation:** Proceed with pure streaming (current plan) unless audit requirements demand storage.

---

## Documentation Updates Needed

1. **API Documentation:**
   - Update `session_logs` endpoint docs
   - Note streaming-only architecture
   - Update WebSocket documentation

2. **User Documentation:**
   - Explain logs are real-time only
   - Document WebSocket connection
   - Note no historical logs

3. **Developer Documentation:**
   - Update architecture diagrams
   - Document log flow
   - Update troubleshooting guides

---

## Approval

**Prepared By:** AI Assistant  
**Reviewed By:** [Pending]  
**Approved By:** [Pending]  
**Date:** [Pending]

---

## Change Log

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-01-15 | 1.0 | AI Assistant | Initial document creation |

