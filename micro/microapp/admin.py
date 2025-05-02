from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'archive_id', 'location', 'doc_type', 'project_path', 'project_folder_name',
        'pdf_folder_path', 'comlist_path', 'output_dir', 'has_pdf_folder',
        'processing_complete', 'retain_sources', 'add_to_database', 'has_oversized',
        'total_pages', 'total_pages_with_refs', 'created_at', 'updated_at', 'owner'
    )
    list_filter = (
        'location', 'processing_complete', 'has_oversized', 'has_pdf_folder',
        'retain_sources', 'add_to_database'
    )
    search_fields = (
        'archive_id', 'project_folder_name', 'pdf_folder_path'
    )
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Project Identification', {
            'fields': ('archive_id', 'location', 'doc_type', 'owner')
        }),
        ('Path Information', {
            'fields': ('project_path', 'project_folder_name', 'pdf_folder_path', 'comlist_path', 'output_dir')
        }),
        ('Project Flags', {
            'fields': ('has_pdf_folder', 'processing_complete')
        }),
        ('Processing Settings', {
            'fields': ('retain_sources', 'add_to_database')
        }),
        ('Process Results', {
            'fields': ('has_oversized', 'total_pages', 'total_pages_with_refs')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
