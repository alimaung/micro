"""
Import all views from their respective modules to maintain backward compatibility.
This allows existing URL patterns to continue working without modifications.
"""

# Re-export all views from their respective modules
from .template_views import *

from .machine_views import *

from .relay_views import *

from .filesystem_views import *

from .transfer_views import *

from .project_views import *

from .roll_views import *

from .document_views import *

from .allocation_views import *

from .index_views import *

from .filmnumber_views import *

# Import distribution views
from .distribution_views import *

from .reference_views import *

# Import export views
from .export_views import *

# Import SMA views
from .sma_views import *

# Import notification views
from .notification_views import *

# Import roll views
from .roll_views import *

from .development_views import *

from .label_views import *

# Import handoff views
from .handoff_views import *

# Import explore views for CRUD operations used by the explore page
from .explore_views import *