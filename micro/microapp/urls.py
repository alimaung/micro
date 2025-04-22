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
]
