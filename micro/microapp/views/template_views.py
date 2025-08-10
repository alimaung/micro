"""
Template rendering views for the microapp.
These views are simple and mainly return rendered templates with minimal logic.
"""

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.utils import translation
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from ..models import Project


def home(request):
    """Home page view."""
    return render(request, 'microapp/home.html')


@login_required
def transfer(request):
    """Transfer main page view."""
    return render(request, 'microapp/transfer/transfer_main.html')


@login_required
def register(request):
    """Welcome/entry page for register workflow."""
    return render(request, 'microapp/register/welcome.html')


# Register workflow step views
@login_required
def register_project(request):
    """Project registration step view."""
    return render(request, 'microapp/register/workflow_pages/project.html')


@login_required
def register_document(request):
    """Document registration step view."""
    return render(request, 'microapp/register/workflow_pages/document.html')


@login_required
def register_workflow(request):
    """Workflow selection step view."""
    return render(request, 'microapp/register/workflow_pages/workflow.html')


@login_required
def register_references(request):
    """References step view."""
    return render(request, 'microapp/register/workflow_pages/references.html')


@login_required
def register_allocation(request):
    """Allocation step view."""
    return render(request, 'microapp/register/workflow_pages/allocation.html')


@login_required
def register_index(request):
    """Index step view."""
    return render(request, 'microapp/register/workflow_pages/index.html')


@login_required
def register_filmnumber(request):
    """Film number step view."""
    return render(request, 'microapp/register/workflow_pages/filmnumber.html')


@login_required
def register_distribution(request):
    """Distribution step view."""
    return render(request, 'microapp/register/workflow_pages/distribution.html')


@login_required
def register_export(request):
    """Export step view."""
    return render(request, 'microapp/register/workflow_pages/export.html')


@login_required
def film(request):
    """Film page view."""
    return render(request, 'microapp/film/film.html')


@login_required
def analyze(request):
    """Analyze page view."""
    from .analyze_views import analyze_dashboard
    return analyze_dashboard(request)


@login_required
def sma_filming(request):
    """SMA Filming interface view."""
    return render(request, 'microapp/film/sma_filming.html')


@login_required
def develop(request):
    """Develop page view."""
    from .development_views import develop_dashboard
    return develop_dashboard(request)


@login_required
def label(request):
    """Label page view."""
    return render(request, 'microapp/label/label.html')


@login_required
def control(request):
    """Control page view."""
    return render(request, 'microapp/control/control.html')


@login_required
def handoff(request):
    """Handoff page view."""
    return render(request, 'microapp/handoff/handoff.html')


@login_required
def explore(request):
    """Explore page view with simple statistics."""
    # Get counts for each entity
    total_projects = Project.objects.filter(owner=request.user).count()
    total_rolls = 0  # Will be updated when Roll model is created
    total_documents = 0  # Will be updated when Document model is created

    return render(request, 'microapp/explore/explore.html', {
        'total_projects': total_projects,
        'total_rolls': total_rolls,
        'total_documents': total_documents
    })


@login_required
def report(request):
    """Report page view."""
    return render(request, 'microapp/report.html')


@login_required
def settings_view(request):
    """Settings page view."""
    return render(request, 'microapp/settings.html')


def login(request):
    """Login page view and authentication handler."""
    error = None
    next_url = request.POST.get('next') or request.GET.get('next') or settings.LOGIN_REDIRECT_URL

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember') == 'on'

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Session expiry: if not remember, expire on browser close
            if not remember:
                request.session.set_expiry(0)
            return redirect(next_url or settings.LOGIN_REDIRECT_URL)
        else:
            error = 'Invalid username or password'

    return render(request, 'microapp/login.html', {
        'error': error,
        'next': next_url,
    })


def logout_view(request):
    """Log out the current user and redirect to login, preserving next if provided."""
    next_url = request.GET.get('next') or request.POST.get('next') or settings.LOGOUT_REDIRECT_URL
    auth_logout(request)
    return redirect(next_url)


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


def oldfilm(request):
    """Deprecated film page view."""
    return render(request, 'microapp/film_old.html')


def oldhandoff(request):
    """Deprecated handoff page view."""
    return render(request, 'microapp/handoff_old.html')


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