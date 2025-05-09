from django.urls import path, include
from . import views
from django.views.i18n import JavaScriptCatalog
from . import api


urlpatterns = [
    # Active TemplateURLs
    path('', views.home, name='home'),
    path('transfer/', views.transfer, name='transfer'),
    path('register/', views.register, name='register'),
    
    # Register workflow step routes
    path('register/project/', views.register_project, name='register_project'),
    path('register/document/', views.register_document, name='register_document'),
    path('register/workflow/', views.register_workflow, name='register_workflow'),
    path('register/references/', views.register_references, name='register_references'),
    path('register/allocation/', views.register_allocation, name='register_allocation'),
    path('register/index/', views.register_index, name='register_index'),
    path('register/filmnumber/', views.register_filmnumber, name='register_filmnumber'),
    path('register/distribution/', views.register_distribution, name='register_distribution'),
    path('register/export/', views.register_export, name='register_export'),
    
    path('film/', views.film, name='film'),
    path('control/', views.control, name='control'),
    path('handoff/', views.handoff, name='handoff'),
    path('explore/', views.explore, name='explore'),
    path('report/', views.report, name='report'),
    path('settings/', views.settings_view, name='settings'),
    path('login/', views.login, name='login'),
    
    # Inactive TemplateURLs
    path('oldregister/', views.oldregister, name='oldregister'),
    path('oldcontrol/', views.oldcontrol, name='oldcontrol'),
    path('oldtransfer/', views.oldtransfer, name='oldtransfer'),
    path('oldexplore/', views.oldexplore, name='oldexplore'),
    
    # API Endpoints
    path('control_relay/', views.control_relay, name='control_relay'),
    path('check_port/', views.check_port, name='check_port'),
    path('check_machine_state/', views.check_machine_state, name='check_machine_state'),
    
    # New endpoints for relay status and ESP32 stats
    path('get_relay_status/', views.get_relay_status, name='get_relay_status'),
    path('get_system_stats/', views.get_system_stats, name='get_system_stats'),
    path('get_all_states/', views.get_all_states, name='get_all_states'),
    
    # New URL pattern for machine stats
    path('get_machine_stats/', views.get_machine_stats, name='get_machine_stats'),
    
    # File Transfer Endpoints
    path('transfer-files/', views.transfer_files, name='transfer_files'),
    path('transfer-progress/', views.transfer_progress, name='transfer_progress'),
    
    # I18N and language toggle
    path('i18n/', include('django.conf.urls.i18n')),
    path('language/toggle/', views.toggle_language, name='toggle_language'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
        
    # Drive folders
    path('browse-local-folders/', views.browse_local_folders, name='browse_local_folders'),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('list-drives/', views.list_drives, name='list_drives'),
    path('list-drive-contents/', views.list_drive_contents, name='list_drive_contents'),
    path('get-file-statistics/', views.get_file_statistics, name='get_file_statistics'),
    path('reveal-in-explorer/', views.reveal_in_explorer, name='reveal_in_explorer'),
    
    # New API endpoint
    path('api/projects/create/', views.create_project, name='create_project'),
    
    # New API endpoints for explore page
    path('api/projects/', views.list_projects, name='list_projects'),
    path('api/projects/<int:project_id>/', views.get_project, name='get_project'),
    path('api/projects/<int:project_id>/update/', views.update_project, name='update_project'),
    path('api/projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('api/statistics/', views.get_database_stats, name='get_database_stats'),
    path('api/documents/analyze', views.analyze_documents, name='analyze_documents'),
    
    # New API endpoints for document analysis
    path('api/documents/analysis-status', views.get_analysis_status, name='get_analysis_status'),
    path('api/documents/analysis-results', views.get_analysis_results, name='get_analysis_results'),
    path('api/documents/calculate-references', views.calculate_references, name='calculate_references'),
    path('api/workflow/select', views.select_workflow, name='select_workflow'),
    
    # New API endpoints for film allocation
    path('api/allocation/allocate-film', views.allocate_film, name='allocate_film'),
    path('api/allocation/allocation-status', views.get_allocation_status, name='get_allocation_status'),
    path('api/allocation/allocation-results', views.get_allocation_results, name='get_allocation_results'),
    
    # New API endpoints for index generation
    path('api/index/initialize-index', views.initialize_index, name='initialize_index'),
    path('api/index/update-index', views.update_index, name='update_index'),
    path('api/index/index-status', views.get_index_status, name='get_index_status'),
    path('api/index/index-results', views.get_index_results, name='get_index_results'),
    
    # Project endpoints
    path('api/projects/', api.get_projects, name='api_get_projects'),
    path('api/projects/<int:project_id>/', api.get_project, name='api_get_project'),
    path('api/projects/create/', api.create_project, name='api_create_project'),
    path('api/projects/<int:project_id>/process/', api.process_project, name='api_process_project'),
    path('api/projects/<int:project_id>/import-documents/', api.import_documents, name='api_import_documents'),
    path('api/projects/<int:project_id>/complete/', api.complete_project, name='api_complete_project'),
    path('api/projects/<int:project_id>/export-allocation/', api.export_allocation_data, name='api_export_allocation_data'),
    
    # Document endpoints
    path('api/documents/<str:doc_id>/', api.get_document, name='api_get_document'),
    path('api/documents/blip/<str:blip>/', api.lookup_blip, name='api_lookup_blip'),
    path('api/projects/<int:project_id>/bulk-import-documents/', api.bulk_import_documents, name='api_bulk_import_documents'),
    path('api/projects/<int:project_id>/documents/<str:doc_id>/split/', api.split_document, name='api_split_document'),
    
    # Roll endpoints
    path('api/projects/<int:project_id>/rolls/', api.get_rolls, name='api_get_rolls'),
    path('api/rolls/<int:roll_id>/', api.get_roll, name='api_get_roll'),
    path('api/rolls/<int:roll_id>/mark-scanned/', api.mark_roll_scanned, name='api_mark_roll_scanned'),
    path('api/rolls/merge/', api.merge_rolls, name='api_merge_rolls'),
    
    # Film number endpoints
    path('api/projects/<int:project_id>/allocate-film-numbers/', api.allocate_film_numbers, name='api_allocate_film_numbers'),
    
    # New FilmNumber view URLs
    path('filmnumber/', views.film_number_view, name='film_number_view'),
    path('filmnumber/project/<int:project_id>/', views.film_number_view, name='film_number_project_view'),
    path('filmnumber/roll/<int:roll_id>/', views.roll_detail_view, name='roll_detail_view'),
    path('filmnumber/results/<int:project_id>/', views.results_view, name='film_number_results'),
    
    # New FilmNumber API URLs
    path('api/filmnumber/allocate/', views.start_film_number_allocation, name='start_film_number_allocation'),
    path('api/filmnumber/status/', views.get_film_number_status, name='get_film_number_status'),
    
    # Reference Sheet API URLs
    path('api/references/status/<int:project_id>/', views.reference_sheet_status, name='reference_sheet_status'),
    path('api/references/generate/<int:project_id>/', views.generate_reference_sheets, name='generate_reference_sheets'),
    path('api/references/get/<int:project_id>/', views.get_reference_sheets, name='get_reference_sheets'),
    path('api/references/pdf/<int:reference_sheet_id>/', views.get_reference_sheet_pdf, name='get_reference_sheet_pdf'),
    path('api/references/insert/<int:project_id>/<str:document_id>/', views.insert_reference_sheets, name='insert_reference_sheets'),
    
    # Document ranges and readable descriptions API URLs
    path('api/references/ranges/<int:project_id>/<str:document_id>/', views.get_document_ranges, name='get_document_ranges'),
    path('api/references/descriptions/<int:project_id>/<str:document_id>/', views.generate_readable_descriptions, name='generate_readable_descriptions'),
    path('api/references/adjusted-ranges/<int:project_id>/<str:document_id>/', views.calculate_adjusted_ranges, name='calculate_adjusted_ranges'),
    
    # Processed documents API URLs
    path('api/references/processed/<int:project_id>/', views.get_processed_documents, name='get_processed_documents'),
    path('api/references/copy-output/<int:project_id>/', views.copy_to_output, name='copy_to_output'),
    path('api/references/clean-temp/<int:project_id>/', views.clean_temporary_files, name='clean_temporary_files'),
    
    # Distribution endpoints
    path('api/distribution/status/<int:project_id>/', views.distribution_status, name='distribution_status'),
    path('api/distribution/distribute/<int:project_id>/', views.distribute_documents, name='distribute_documents'),
    path('api/distribution/generate-references/<int:project_id>/', views.generate_reference_sheets, name='generate_reference_sheets'),
]