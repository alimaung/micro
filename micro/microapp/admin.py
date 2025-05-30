from django.contrib import admin
from .models import (
    Project, Document, DocumentDimension, DocumentRange, ReferencePage,
    Roll, TempRoll, DocumentSegment, RollReferenceInfo, DocumentReferenceInfo,
    RangeReferenceInfo, FilmAllocation, DocumentAllocationRequest35mm,
    DistributionResult, ReferenceSheet, ReadablePageDescription, AdjustedRange,
    ProcessedDocument, FilmingSession, FilmingSessionLog,
    DevelopmentSession, ChemicalBatch, DevelopmentLog
)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'archive_id', 'name', 'location', 'doc_type', 'project_path', 'project_folder_name',
                    'folder_path', 'pdf_folder_path', 'comlist_path', 'output_dir', 'has_pdf_folder', 'processing_complete',
                    'retain_sources', 'add_to_database', 'has_oversized', 'total_pages', 'total_pages_with_refs',
                    'documents_with_oversized', 'total_oversized', 'created_at', 'updated_at', 'owner',
                    'index_path', 'data_dir', 'film_allocation_complete', 'distribution_complete')
    search_fields = ('archive_id', 'name', 'location', 'project_folder_name')
    list_filter = ('processing_complete', 'has_pdf_folder', 'has_oversized', 'location', 'film_allocation_complete', 'distribution_complete')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'archive_id', 'name', 'location', 'doc_type', 'owner')
        }),
        ('Paths', {
            'fields': ('project_path', 'folder_path', 'project_folder_name', 'pdf_folder_path', 'comlist_path', 'output_dir', 
                       'index_path', 'data_dir')
        }),
        ('Status', {
            'fields': ('has_pdf_folder', 'processing_complete', 'film_allocation_complete', 'distribution_complete')
        }),
        ('Processing Settings', {
            'fields': ('retain_sources', 'add_to_database')
        }),
        ('Statistics', {
            'fields': ('has_oversized', 'total_pages', 'total_pages_with_refs', 'documents_with_oversized', 'total_oversized')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'doc_id', 'path', 'com_id', 'pages', 'has_oversized', 
                    'total_oversized', 'total_references', 'is_split', 'roll_count', 
                    'created_at', 'updated_at')
    search_fields = ('doc_id', 'project__archive_id')
    list_filter = ('has_oversized', 'is_split')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'doc_id', 'project', 'com_id', 'path')
        }),
        ('Page Information', {
            'fields': ('pages', 'has_oversized', 'total_oversized', 'total_references')
        }),
        ('Film Allocation', {
            'fields': ('is_split', 'roll_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

class DocumentDimensionAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'page_idx', 'width', 'height', 'percent_over')
    search_fields = ('document__doc_id',)
    list_filter = ('document',)
    readonly_fields = ('id',)

class DocumentRangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'start_page', 'end_page')
    search_fields = ('document__doc_id',)
    list_filter = ('document',)
    readonly_fields = ('id',)

class ReferencePageAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'position')
    search_fields = ('document__doc_id',)
    list_filter = ('document',)
    readonly_fields = ('id',)

class RollAdmin(admin.ModelAdmin):
    list_display = ('id', 'roll_id', 'project', 'roll_number', 'film_number', 'film_type', 'capacity', 'pages_used', 
                    'pages_remaining', 'status', 'filming_status', 'filming_progress_percent', 'development_status',
                    'development_progress_percent', 'has_split_documents', 'creation_date',
                    'is_partial', 'remaining_capacity', 'usable_capacity', 'film_number_source',
                    'source_temp_roll', 'created_temp_roll', 'output_directory')
    search_fields = ('film_number', 'roll_number', 'project__archive_id', 'output_directory', 'filming_session_id')
    list_filter = ('film_type', 'status', 'filming_status', 'development_status', 'is_partial', 'has_split_documents', 'film_number_source')
    readonly_fields = ('roll_id', 'creation_date')
    fieldsets = (
        ('Identification', {
            'fields': ('roll_id', 'project', 'roll_number', 'film_number', 'film_type')
        }),
        ('Capacity', {
            'fields': ('capacity', 'pages_used', 'pages_remaining', 'usable_capacity')
        }),
        ('Status', {
            'fields': ('status', 'has_split_documents', 'is_partial', 'remaining_capacity')
        }),
        ('Filming Status', {
            'fields': ('filming_status', 'filming_session_id', 'filming_progress_percent', 
                      'filming_started_at', 'filming_completed_at')
        }),
        ('Development Status', {
            'fields': ('development_status', 'development_progress_percent',
                      'development_started_at', 'development_completed_at')
        }),
        ('Output', {
            'fields': ('output_directory',)
        }),
        ('Source Tracking', {
            'fields': ('film_number_source', 'source_temp_roll', 'created_temp_roll')
        }),
        ('Timestamps', {
            'fields': ('creation_date', 'filmed_at')
        }),
    )

class TempRollAdmin(admin.ModelAdmin):
    list_display = ('temp_roll_id', 'film_type', 'capacity', 'usable_capacity', 
                    'status', 'creation_date', 'source_roll', 'used_by_roll')
    search_fields = ('temp_roll_id', 'film_type')
    list_filter = ('film_type', 'status')
    readonly_fields = ('temp_roll_id', 'creation_date')
    fieldsets = (
        ('Identification', {
            'fields': ('temp_roll_id', 'film_type')
        }),
        ('Capacity', {
            'fields': ('capacity', 'usable_capacity')
        }),
        ('Status', {
            'fields': ('status', 'creation_date')
        }),
        ('Relationships', {
            'fields': ('source_roll', 'used_by_roll')
        }),
    )

class DocumentSegmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'roll', 'pages', 'start_page', 'end_page', 
                    'start_frame', 'end_frame', 'document_index', 'has_oversized',
                    'blip', 'blipend', 'created_at')
    search_fields = ('document__doc_id', 'roll__film_number')
    list_filter = ('has_oversized',)
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'document', 'roll', 'document_index')
        }),
        ('Page Information', {
            'fields': ('pages', 'start_page', 'end_page', 'start_frame', 'end_frame')
        }),
        ('Metadata', {
            'fields': ('has_oversized', 'blip', 'blipend', 'created_at')
        }),
    )

class RollReferenceInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'roll', 'is_new_roll', 'previous_project', 
                    'last_blipend', 'last_frame_position')
    search_fields = ('roll__film_number',)
    list_filter = ('is_new_roll',)
    readonly_fields = ('id',)

class DocumentReferenceInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'roll', 'is_split')
    search_fields = ('document__doc_id', 'roll__film_number')
    list_filter = ('is_split',)
    readonly_fields = ('id',)

class RangeReferenceInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_reference', 'range_start', 'range_end', 
                   'position', 'frame_start', 'blip', 'blipend')
    search_fields = ('document_reference__document__doc_id',)
    readonly_fields = ('id',)

class FilmAllocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'total_rolls_16mm', 'total_pages_16mm',
                   'total_partial_rolls_16mm', 'total_split_documents_16mm',
                   'total_rolls_35mm', 'total_pages_35mm',
                   'total_partial_rolls_35mm', 'total_split_documents_35mm',
                   'creation_date', 'updated_at')
    search_fields = ('project__archive_id',)
    readonly_fields = ('id', 'creation_date', 'updated_at')
    fieldsets = (
        ('Project', {
            'fields': ('id', 'project')
        }),
        ('16mm Statistics', {
            'fields': ('total_rolls_16mm', 'total_pages_16mm', 'total_partial_rolls_16mm', 'total_split_documents_16mm')
        }),
        ('35mm Statistics', {
            'fields': ('total_rolls_35mm', 'total_pages_35mm', 'total_partial_rolls_35mm', 'total_split_documents_35mm')
        }),
        ('Timestamps', {
            'fields': ('creation_date', 'updated_at')
        }),
    )

class DocumentAllocationRequest35mmAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'document', 'pages', 'start_page', 
                   'end_page', 'processed')
    search_fields = ('document__doc_id', 'project__archive_id')
    list_filter = ('processed',)
    readonly_fields = ('id',)

class DistributionResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'processed_count', 'error_count', 'output_dir',
                   'reference_sheets', 'documents_with_references', 'oversized_documents_extracted',
                   'processed_35mm_documents', 'copied_35mm_documents',
                   'processed_16mm_documents', 'copied_16mm_documents',
                   'completed_at', 'status')
    search_fields = ('project__archive_id',)
    list_filter = ('status',)
    readonly_fields = ('id', 'completed_at')
    fieldsets = (
        ('Project', {
            'fields': ('id', 'project', 'output_dir')
        }),
        ('Processing Results', {
            'fields': ('processed_count', 'error_count', 'status')
        }),
        ('Reference Processing', {
            'fields': ('reference_sheets', 'documents_with_references')
        }),
        ('Document Processing', {
            'fields': ('oversized_documents_extracted', 
                      'processed_35mm_documents', 'copied_35mm_documents',
                      'processed_16mm_documents', 'copied_16mm_documents')
        }),
        ('Timestamps', {
            'fields': ('completed_at',)
        }),
    )

class ReferenceSheetAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'document_range', 'range_start', 'range_end',
                   'path', 'blip_35mm', 'film_number_35mm', 'human_range', 'created_at')
    search_fields = ('document__doc_id', 'film_number_35mm')
    list_filter = ('created_at',)
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Document Information', {
            'fields': ('id', 'document', 'document_range')
        }),
        ('Range Information', {
            'fields': ('range_start', 'range_end', 'human_range')
        }),
        ('Reference Sheet', {
            'fields': ('path', 'blip_35mm', 'film_number_35mm')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

class ReadablePageDescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'range_index', 'description')
    search_fields = ('document__doc_id', 'description')
    list_filter = ('document',)
    readonly_fields = ('id',)

class AdjustedRangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'original_start', 'original_end', 
                   'adjusted_start', 'adjusted_end')
    search_fields = ('document__doc_id',)
    list_filter = ('document',)
    readonly_fields = ('id',)

class ProcessedDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'processing_type', 'path', 
                   'start_page', 'end_page', 'roll', 'segment',
                   'processed_at', 'copied_to_output', 'output_path')
    search_fields = ('document__doc_id', 'path')
    list_filter = ('processing_type', 'copied_to_output')
    readonly_fields = ('id', 'processed_at')
    fieldsets = (
        ('Document Information', {
            'fields': ('id', 'document', 'processing_type', 'path')
        }),
        ('Page Range', {
            'fields': ('start_page', 'end_page')
        }),
        ('Roll Information', {
            'fields': ('roll', 'segment')
        }),
        ('Output Status', {
            'fields': ('processed_at', 'copied_to_output', 'output_path')
        }),
    )

class FilmingSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_id', 'project', 'roll', 'film_type', 'status', 'workflow_state', 
                    'progress_percent', 'total_documents', 'processed_documents', 'recovery_mode',
                    'started_at', 'completed_at', 'created_at', 'updated_at')
    search_fields = ('session_id', 'project__archive_id', 'roll__film_number', 'roll__roll_number')
    list_filter = ('status', 'workflow_state', 'film_type', 'recovery_mode', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'session_id', 'project', 'roll', 'user')
        }),
        ('Configuration', {
            'fields': ('film_type', 'recovery_mode')
        }),
        ('Status & Progress', {
            'fields': ('status', 'workflow_state', 'progress_percent', 'total_documents', 'processed_documents')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration')
        }),
        ('Error Handling', {
            'fields': ('error_message',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
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

class DevelopmentSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_id', 'roll', 'status', 'progress_percent', 
                    'development_duration_minutes', 'started_at', 'completed_at', 
                    'estimated_completion', 'user', 'created_at')
    search_fields = ('session_id', 'roll__film_number', 'roll__roll_number', 'user__username')
    list_filter = ('status', 'roll__film_type', 'created_at', 'started_at', 'completed_at')
    readonly_fields = ('id', 'session_id', 'created_at', 'updated_at', 'duration_display')
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'session_id', 'roll', 'user')
        }),
        ('Development Configuration', {
            'fields': ('development_duration_minutes', 'estimated_completion', 'duration_display')
        }),
        ('Status & Progress', {
            'fields': ('status', 'progress_percent')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('roll', 'user')
    
    def duration_display(self, obj):
        """Display the actual duration if completed"""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return f"{duration.total_seconds() / 60:.1f} minutes"
        return "Not completed"
    duration_display.short_description = "Actual Duration"

class ChemicalBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch_id', 'chemical_type', 'capacity_display', 'usage_display', 
                    'status_display', 'is_active', 'created_at', 'replaced_at')
    search_fields = ('batch_id', 'chemical_type')
    list_filter = ('chemical_type', 'is_active', 'created_at', 'replaced_at')
    readonly_fields = ('id', 'created_at', 'capacity_display', 'usage_display', 'status_display')
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'batch_id', 'chemical_type', 'is_active')
        }),
        ('Capacity Information', {
            'fields': ('max_area', 'used_area', 'capacity_display')
        }),
        ('Usage Statistics', {
            'fields': ('used_16mm_rolls', 'used_35mm_rolls', 'usage_display')
        }),
        ('Status Indicators', {
            'fields': ('status_display',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'replaced_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')
    
    def capacity_display(self, obj):
        """Display capacity with visual indicator"""
        # Calculate capacity percentage safely
        if obj.max_area > 0:
            percent = ((obj.max_area - obj.used_area) / obj.max_area) * 100
            remaining = obj.max_area - obj.used_area
        else:
            percent = 0
            remaining = 0
            
        if percent > 80:
            color = "green"
        elif percent > 40:
            color = "orange"
        else:
            color = "red"
        return f'<span style="color: {color}; font-weight: bold;">{percent:.1f}% ({remaining:.2f} m² remaining)</span>'
    capacity_display.short_description = "Capacity Status"
    capacity_display.allow_tags = True
    
    def usage_display(self, obj):
        """Display usage statistics"""
        return f"{obj.used_16mm_rolls} × 16mm, {obj.used_35mm_rolls} × 35mm"
    usage_display.short_description = "Roll Usage"
    
    def status_display(self, obj):
        """Display status with color coding"""
        # Calculate status based on remaining capacity
        if obj.max_area > 0:
            percent = ((obj.max_area - obj.used_area) / obj.max_area) * 100
        else:
            percent = 0
            
        if percent < 20:
            return '<span style="color: red; font-weight: bold;">CRITICAL</span>'
        elif percent < 40:
            return '<span style="color: orange; font-weight: bold;">LOW</span>'
        else:
            return '<span style="color: green; font-weight: bold;">GOOD</span>'
    status_display.short_description = "Status"
    status_display.allow_tags = True

class DevelopmentLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'level', 'message', 'created_at')
    search_fields = ('session__session_id', 'session__roll__film_number', 'message')
    list_filter = ('level', 'created_at')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'session')
        }),
        ('Log Information', {
            'fields': ('level', 'message', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'session__roll')

# Register all models
admin.site.register(Project, ProjectAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentDimension, DocumentDimensionAdmin)
admin.site.register(DocumentRange, DocumentRangeAdmin)
admin.site.register(ReferencePage, ReferencePageAdmin)
admin.site.register(Roll, RollAdmin)
admin.site.register(TempRoll, TempRollAdmin)
admin.site.register(DocumentSegment, DocumentSegmentAdmin)
admin.site.register(RollReferenceInfo, RollReferenceInfoAdmin)
admin.site.register(DocumentReferenceInfo, DocumentReferenceInfoAdmin)
admin.site.register(RangeReferenceInfo, RangeReferenceInfoAdmin)
admin.site.register(FilmAllocation, FilmAllocationAdmin)
admin.site.register(DocumentAllocationRequest35mm, DocumentAllocationRequest35mmAdmin)
admin.site.register(DistributionResult, DistributionResultAdmin)
admin.site.register(ReferenceSheet, ReferenceSheetAdmin)
admin.site.register(ReadablePageDescription, ReadablePageDescriptionAdmin)
admin.site.register(AdjustedRange, AdjustedRangeAdmin)
admin.site.register(ProcessedDocument, ProcessedDocumentAdmin)
admin.site.register(FilmingSession, FilmingSessionAdmin)
admin.site.register(FilmingSessionLog, FilmingSessionLogAdmin)
admin.site.register(DevelopmentSession, DevelopmentSessionAdmin)
admin.site.register(ChemicalBatch, ChemicalBatchAdmin)
admin.site.register(DevelopmentLog, DevelopmentLogAdmin)
