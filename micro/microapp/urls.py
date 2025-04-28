from django.urls import path, include
from . import views
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    # Active TemplateURLs
    path('', views.home, name='home'),
    path('transfer/', views.transfer, name='transfer'),
    path('register/', views.register, name='register'),
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
    
    # I18N and language toggle
    path('i18n/', include('django.conf.urls.i18n')),
    path('language/toggle/', views.toggle_language, name='toggle_language'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
        
    # Drive folders
    path('list-drive-folders/', views.list_drive_folders, name='list_drive_folders'),
    path('browse-local-folders/', views.browse_local_folders, name='browse_local_folders'),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('list-drives/', views.list_drives, name='list_drives'),
]