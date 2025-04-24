from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('film/', views.film, name='film'),
    path('control/', views.control, name='control'),
    path('handoff/', views.handoff, name='handoff'),
    path('explore/', views.explore, name='explore'),
    path('report/', views.report, name='report'),
    path('settings/', views.settings, name='settings'),
    path('login/', views.login, name='login'),
    path('language/', views.language, name='language'),
    
    path('control_relay/', views.control_relay, name='control_relay'),
    path('check_port/', views.check_port, name='check_port'),
    path('check_machine_state/', views.check_machine_state, name='check_machine_state'),
    
    # New endpoints for relay status and ESP32 stats
    path('get_relay_status/', views.get_relay_status, name='get_relay_status'),
    path('get_system_stats/', views.get_system_stats, name='get_system_stats'),
    path('get_all_states/', views.get_all_states, name='get_all_states'),
    
    # New URL pattern for machine stats
    path('get_machine_stats/', views.get_machine_stats, name='get_machine_stats'),
]
