"""
Import all views from their respective modules to maintain backward compatibility.
This allows existing URL patterns to continue working without modifications.
"""

# Re-export all views from their respective modules
from .template_views import (
    home, transfer, register, register_project, register_document, register_workflow,
    register_references, register_allocation, register_index, register_filmnumber,
    register_distribution, register_export, film, control, handoff, explore, report,
    settings_view, login, oldcontrol, oldregister, oldtransfer, oldexplore, language,
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
    get_database_stats
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

from .filmnumber import (
    film_number_view, roll_detail_view, results_view, 
    start_film_number_allocation, get_film_number_status, process_film_number_allocation
)
