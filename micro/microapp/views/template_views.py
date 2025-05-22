"""
Template rendering views for the microapp.
These views are simple and mainly return rendered templates with minimal logic.
"""

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.utils import translation
from django.conf import settings
from ..models import Project

def home(request):
    """Home page view."""
    return render(request, 'microapp/home.html')

def transfer(request):
    """Transfer main page view."""
    return render(request, 'microapp/transfer/transfer_main.html')

def register(request):
    """Welcome/entry page for register workflow."""
    return render(request, 'microapp/register/welcome.html')

# Register workflow step views
def register_project(request):
    """Project registration step view."""
    return render(request, 'microapp/register/workflow_pages/project.html')

def register_document(request):
    """Document registration step view."""
    return render(request, 'microapp/register/workflow_pages/document.html')

def register_workflow(request):
    """Workflow selection step view."""
    return render(request, 'microapp/register/workflow_pages/workflow.html')

def register_references(request):
    """References step view."""
    return render(request, 'microapp/register/workflow_pages/references.html')

def register_allocation(request):
    """Allocation step view."""
    return render(request, 'microapp/register/workflow_pages/allocation.html')

def register_index(request):
    """Index step view."""
    return render(request, 'microapp/register/workflow_pages/index.html')

def register_filmnumber(request):
    """Film number step view."""
    return render(request, 'microapp/register/workflow_pages/filmnumber.html')

def register_distribution(request):
    """Distribution step view."""
    return render(request, 'microapp/register/workflow_pages/distribution.html')

def register_export(request):
    """Export step view."""
    return render(request, 'microapp/register/workflow_pages/export.html')

def film(request):
    """Film page view."""
    return render(request, 'microapp/film.html')

def control(request):
    """Control page view."""
    return render(request, 'microapp/control/control.html')

def handoff(request):
    """Handoff page view."""
    return render(request, 'microapp/handoff.html')

def explore(request):
    """Explore page view with simple statistics."""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # Redirect to admin login page with next parameter set to explore
        return redirect(f'/admin/login/?next=/explore/')
    
    # Get counts for each entity
    total_projects = Project.objects.filter(owner=request.user).count()
    total_rolls = 0  # Will be updated when Roll model is created
    total_documents = 0  # Will be updated when Document model is created
    
    return render(request, 'microapp/explore/explore.html', {
        'total_projects': total_projects,
        'total_rolls': total_rolls,
        'total_documents': total_documents
    })

def report(request):
    """Report page view."""
    return render(request, 'microapp/report.html')

def settings_view(request):
    """Settings page view."""
    return render(request, 'microapp/settings.html')

def login(request):
    """Login page view."""
    return render(request, 'microapp/login.html')

def language(request):
    """Language selection page view."""
    return render(request, 'microapp/language.html')

# Inactive views (old versions)
def oldcontrol(request):
    """Deprecated control page view."""
    return render(request, 'microapp/control_old.html')

def oldregister(request):
    """Deprecated register page view."""
    return render(request, 'microapp/register_old.html')

def oldtransfer(request):
    """Deprecated transfer page view."""
    return render(request, 'microapp/transfer_old.html')

def oldexplore(request):
    """Deprecated explore page view."""
    return render(request, 'microapp/explore_old.html')

# Language toggle function
def toggle_language(request):
    """
    Rotate through settings.LANGUAGES, store selection in
    session + cookie, then redirect back to the same page.
    """
    # Where to go after switching:
    next_url = request.GET.get('next') or request.META.get("HTTP_REFERER", "/")

    current_lang = translation.get_language()
    lang_codes   = [code for code, _ in settings.LANGUAGES]

    try:
        new_lang = lang_codes[(lang_codes.index(current_lang) + 1) % len(lang_codes)]
    except ValueError:          # current language not in list
        new_lang = lang_codes[0]

    translation.activate(new_lang)

    if hasattr(request, "session"):
        request.session['django_language'] = new_lang   # literal key

    response = HttpResponseRedirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, new_lang)
    return response 