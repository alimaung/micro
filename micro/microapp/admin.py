from django.contrib import admin
from .models import (
    Project, Document, DocumentDimension, DocumentRange, ReferencePage,
    Roll, TempRoll, DocumentSegment, RollReferenceInfo, DocumentReferenceInfo,
    RangeReferenceInfo, FilmAllocation, DocumentAllocationRequest35mm
)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'archive_id', 'location', 'doc_type', 'project_path', 'project_folder_name',
                    'pdf_folder_path', 'comlist_path', 'output_dir', 'has_pdf_folder', 'processing_complete',
                    'retain_sources', 'add_to_database', 'has_oversized', 'total_pages', 'total_pages_with_refs',
                    'documents_with_oversized', 'total_oversized', 'created_at', 'updated_at', 'owner',
                    'index_path', 'data_dir', 'film_allocation_complete', 'distribution_complete')
    search_fields = ('archive_id', 'location', 'project_folder_name')
    list_filter = ('processing_complete', 'has_pdf_folder', 'has_oversized', 'location')
    readonly_fields = ('id',)
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'archive_id', 'location', 'doc_type', 'owner')
        }),
        ('Paths', {
            'fields': ('project_path', 'project_folder_name', 'pdf_folder_path', 'comlist_path', 'output_dir', 
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
    readonly_fields = ('id',)
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
    list_display = ('roll_id', 'project', 'film_number', 'film_type', 'capacity', 'pages_used', 
                    'pages_remaining', 'status', 'has_split_documents', 'creation_date',
                    'is_partial', 'remaining_capacity', 'usable_capacity', 'film_number_source',
                    'source_temp_roll', 'created_temp_roll')
    search_fields = ('film_number', 'project__archive_id')
    list_filter = ('film_type', 'status', 'is_partial', 'has_split_documents')
    readonly_fields = ('roll_id',)
    fieldsets = (
        ('Identification', {
            'fields': ('roll_id', 'project', 'film_number', 'film_type')
        }),
        ('Capacity', {
            'fields': ('capacity', 'pages_used', 'pages_remaining', 'usable_capacity')
        }),
        ('Status', {
            'fields': ('status', 'has_split_documents', 'is_partial', 'remaining_capacity')
        }),
        ('Source Tracking', {
            'fields': ('film_number_source', 'source_temp_roll', 'created_temp_roll')
        }),
        ('Timestamps', {
            'fields': ('creation_date',)
        }),
    )

class TempRollAdmin(admin.ModelAdmin):
    list_display = ('temp_roll_id', 'film_type', 'capacity', 'usable_capacity', 
                    'status', 'creation_date', 'source_roll', 'used_by_roll')
    search_fields = ('temp_roll_id', 'film_type')
    list_filter = ('film_type', 'status')
    readonly_fields = ('temp_roll_id',)
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
    readonly_fields = ('id',)
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
    readonly_fields = ('id',)
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
