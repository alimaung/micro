"""
Import all views from their respective modules to maintain backward compatibility.
This allows existing URL patterns to continue working without modifications.
"""

# Re-export all views from their respective modules
from .template_views import (
    home, transfer, register, register_project, register_document, register_workflow,
    register_references, register_allocation, register_index, register_filmnumber,
    register_distribution, register_export, film, sma_filming, develop, label, control, handoff, explore, report,
    settings_view, login, oldcontrol, oldregister, oldtransfer, oldexplore, oldfilm, oldhandoff,
    toggle_language
)

from .machine_views import (
    check_port, check_machine_state, get_machine_stats
)

from .relay_views import (
    control_relay, get_relay_status, get_system_stats, get_all_states, esp32_config
)

from .filesystem_views import (
    browse_local_folders, create_folder, list_drives, list_drive_contents,
    get_file_statistics, reveal_in_explorer
)

from .transfer_views import (
    transfer_files, transfer_progress
)

from .project_views import (
    create_project, list_projects, get_project, update_project, delete_project,
    get_database_stats, get_document_types, get_locations, get_project_history,
    get_project_rolls, get_project_documents, export_projects_excel, export_projects_pdf
)

from .roll_views import (
    get_project_rolls, update_roll_filming_status, get_roll_details
)

from .document_views import (
    analyze_documents, get_analysis_status, get_analysis_results,
    calculate_references, select_workflow
)

from .allocation_views import (
    allocate_film, get_allocation_status, get_allocation_results
)

from .index_views import (
    initialize_index, update_index, get_index_status, get_index_results
)

from .filmnumber_views import (
    film_number_view, roll_detail_view, results_view, 
    start_film_number_allocation, get_film_number_status, process_film_number_allocation
)

# Import distribution views
from .distribution_views import (
    distribution_status, distribute_documents, generate_reference_sheets
)

from .reference_views import (
    get_processed_documents, copy_to_output, clean_temporary_files, 
    reference_sheet_status, generate_reference_sheets, get_reference_sheets,
    get_reference_sheet_pdf, insert_reference_sheets, get_document_ranges,
    generate_readable_descriptions, calculate_adjusted_ranges
)

# Import export views
from .export_views import (
    export_project_data, generate_exports, download_export_zip, 
    download_specific_export, get_available_exports
)

# Import SMA views
from .sma_views import (
    SMAFilmingView, SMASessionView, recover_session, session_logs,
    session_statistics, mark_roll_filmed, cleanup_sessions,
    project_rolls, session_history, start_filming, control_filming,
    filming_status, filming_logs, filming_progress, active_sessions,
    machine_status, test_sma_connection
)

# Import notification views
from .notification_views import (
    send_notification, get_notifications, mark_notification_read, mark_all_read,
    get_unread_count, delete_notification, send_firebase_notification,
    send_websocket_notification, notification_settings, update_notification_settings
)

# Import roll views
from .roll_views import (
    get_project_rolls, update_roll_filming_status, get_roll_details
)

from .development_views import (
    develop_dashboard, get_rolls_for_development, get_chemical_status,
    start_development, complete_development, get_development_progress,
    reset_chemical_batch, get_development_history, insert_chemicals,
    save_density_measurement, get_density_measurements, get_active_development_session
)

from .label_views import (
    get_rolls_for_labels, generate_film_labels, download_label_pdf,
    get_print_queue, add_to_print_queue, remove_from_print_queue,
    get_generated_labels, mark_label_printed, print_label_server_side,
    get_printer_status, print_multiple_labels, reveal_label_in_explorer,
    generate_custom_film_labels, print_custom_label
)

# Import handoff views
from .handoff_views import (
    get_projects_for_handoff, get_project_validation_data, validate_project_index,
    generate_handoff_files, send_handoff_email, test_handoff_endpoint, test_post_endpoint,
    preview_email_template, preview_original_template
)

# Import explore views for CRUD operations used by the explore page
from .explore_views import (
    create_roll, list_rolls, get_roll, update_roll, delete_roll,
    export_rolls_excel, export_rolls_pdf
)