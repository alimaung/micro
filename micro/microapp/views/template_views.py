"""
Template rendering views for the microapp.
These views are simple and mainly return rendered templates with minimal logic.
"""

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.utils import translation
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from ..models import Project
from pathlib import Path
import os
import mimetypes
import markdown as md


# Directory to read documentation files from (basis: Flask app)
DOCS_PATH = Path(r"C:\Users\bearb\Desktop\micro\übergabe\documentation")

# Folders to ignore in the drive explorer
IGNORE_FOLDERS = {'System Volume Information', '$RECYCLE.BIN'}

# Drive explorer configuration
DRIVE_ROOT = Path(r"X:/")
ALLOWED_DIRS = {'.temp', '.labels', '.export'}
ALLOWED_ROOT_FILE_EXTS = {'.xls', '.xlsx', '.xlsb', '.xslb', '.xlsm'}

def _is_within(base: Path, target: Path) -> bool:
    try:
        base_resolved = base.resolve(strict=False)
        target_resolved = target.resolve(strict=False)
    except Exception:
        return False
    return str(target_resolved).startswith(str(base_resolved))

def _is_downloadable(file_path: Path) -> bool:
    """Check if a file is allowed to be downloaded/viewed.
    
    Rules:
    1. All files recursively in .temp, .labels, .export folders (anywhere in tree)
       e.g., X:\project1\.temp\file.txt or X:\project1\.labels\subfolder\file.pdf
    2. Excel files in X:\ root (e.g., X:\file.xlsx)
    3. Excel files in the root of any top-level folder (e.g., X:\ProjectFolder\file.xlsx)
    """
    try:
        # Rule 1: Check if file is within any .temp, .labels, or .export folder
        # Walk up the path to see if any parent folder is in ALLOWED_DIRS
        current = file_path.parent
        while current != DRIVE_ROOT and current != current.parent:
            if current.name in ALLOWED_DIRS:
                # Verify it's actually under DRIVE_ROOT
                if _is_within(DRIVE_ROOT, file_path):
                    return True
            current = current.parent
        
        # Rule 2: Excel files directly in X:\ root
        if file_path.parent.resolve(strict=False) == DRIVE_ROOT.resolve(strict=False):
            if file_path.suffix.lower() in ALLOWED_ROOT_FILE_EXTS:
                return True
        
        # Rule 3: Excel files in the root of any top-level folder
        # Check if file is exactly one level deep from DRIVE_ROOT
        try:
            relative = file_path.relative_to(DRIVE_ROOT)
            parts = relative.parts
            # If it has exactly 2 parts (folder/file.xlsx), it's in a top-level folder root
            if len(parts) == 2 and file_path.suffix.lower() in ALLOWED_ROOT_FILE_EXTS:
                return True
        except ValueError:
            pass
        
    except Exception:
        pass
    
    return False

def _build_tree_html(base_dir: Path) -> str:
    """Build an interactive collapsible directory tree under base_dir."""
    if not base_dir.exists() or not base_dir.is_dir():
        return "<p class=\"subtitle\">Folder not found or not a directory.</p>"

    def esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
        )

    def render_dir(d: Path, depth: int = 0) -> str:
        try:
            entries = sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except Exception:
            entries = []
        
        parts = ['<ul class="docs-tree">']
        
        for p in entries:
            name = esc(p.name)
            rel = (p.relative_to(DRIVE_ROOT)).as_posix()
            
            if p.is_dir():
                # Folder with collapsible children
                parts.append(f'<li class="docs-tree-item docs-tree-folder">')
                parts.append(f'<div class="docs-tree-folder-header" onclick="this.parentElement.classList.toggle(\'expanded\')">')
                parts.append(f'<i class="fas fa-chevron-right docs-tree-toggle"></i>')
                parts.append(f'<i class="fas fa-folder docs-tree-folder-icon"></i>')
                parts.append(f'<span class="docs-tree-folder-name">{name}</span>')
                parts.append('</div>')
                parts.append('<div class="docs-tree-children">')
                parts.append(render_dir(p, depth + 1))
                parts.append('</div>')
                parts.append('</li>')
            else:
                # File - clickable if downloadable, greyed out otherwise
                downloadable = _is_downloadable(p)
                disabled_class = '' if downloadable else ' disabled'
                
                if downloadable:
                    view_url = f"/docs/view/?path={rel}"
                    dl_url = f"/docs/download/?path={rel}"
                    # Build: <li><div class="file-wrapper"><icon><name><actions with view+download btns></div></li>
                    parts.append(f'<li class="docs-tree-item docs-tree-file{disabled_class}">')
                    parts.append('<div class="docs-tree-file-wrapper">')
                    parts.append('<i class="fas fa-file docs-tree-file-icon"></i>')
                    parts.append(f'<span class="docs-tree-file-name">{name}</span>')
                    parts.append('<span class="docs-tree-file-actions">')
                    parts.append(f'<a href="{view_url}" target="_blank" class="docs-btn docs-btn-sm docs-btn-secondary" title="View file">')
                    parts.append('<i class="fas fa-eye"></i>')
                    parts.append('</a>')
                    parts.append(f'<a href="{dl_url}" class="docs-btn docs-btn-sm docs-btn-primary" title="Download file">')
                    parts.append('<i class="fas fa-download"></i>')
                    parts.append('</a>')
                    parts.append('</span>')  # Close actions span
                    parts.append('</div>')  # Close file wrapper
                else:
                    parts.append(f'<li class="docs-tree-item docs-tree-file{disabled_class}">')
                    parts.append('<i class="fas fa-file docs-tree-file-icon"></i>')
                    parts.append(f'<span class="docs-tree-file-name">{name}</span>')
                
                parts.append('</li>')
        
        parts.append('</ul>')
        return "".join(parts)

    header = f"<h2 style=\"margin-top:0;\"><i class=\"fas fa-folder-open\" style=\"color:var(--color-primary);\"></i> {esc(base_dir.name)}</h2>"
    return header + render_dir(base_dir)


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


@login_required
def admin(request):
    """Admin page view with embedded Django admin."""
    return render(request, 'microapp/admin.html')


@login_required
def docs(request):
    """Documentation page with sidebar and file viewer.
    Lists .md and .txt files under DOCS_PATH and renders selected file.
    """
    files = []
    if DOCS_PATH.exists():
        for f in DOCS_PATH.rglob("*"):
            if f.is_file() and f.suffix.lower() in [".md", ".txt"]:
                rel = f.relative_to(DOCS_PATH).as_posix()  # forward slashes for URLs
                files.append(rel)
        files.sort()

    file_name = request.GET.get("file")
    content_html = ""

    if file_name:
        candidate = (DOCS_PATH / file_name).resolve()
        base = DOCS_PATH.resolve()
        # Prevent path traversal
        if str(candidate).startswith(str(base)) and candidate.exists() and candidate.is_file():
            try:
                text = candidate.read_text(encoding="utf-8")
            except Exception:
                text = ""
            if candidate.suffix.lower() == ".md" and md is not None:
                try:
                    content_html = md.markdown(text, extensions=["fenced_code", "tables", "toc"])
                except Exception:
                    content_html = "<pre>" + text + "</pre>"
            else:
                content_html = "<pre>" + text + "</pre>"

    # Build drive explorer data
    drive_folders = []
    if DRIVE_ROOT.exists():
        try:
            for item in DRIVE_ROOT.iterdir():
                if item.is_dir() and item.name not in IGNORE_FOLDERS:
                    drive_folders.append(item.name)
        except Exception:
            pass
    drive_folders.sort(key=lambda x: x.lower())

    selected_folder = request.GET.get("folder")
    folder_tree_html = ""
    if selected_folder:
        candidate = (DRIVE_ROOT / selected_folder)
        if _is_within(DRIVE_ROOT, candidate) and candidate.exists() and candidate.is_dir():
            folder_tree_html = _build_tree_html(candidate)

    return render(request, 'microapp/docs/docs.html', {
        'files': files,
        'content': content_html,
        'selected': file_name,
        'drive_folders': drive_folders,
        'selected_folder': selected_folder,
        'folder_tree_html': folder_tree_html,
    })


@login_required
def docs_download(request):
    rel_path = request.GET.get('path')
    if not rel_path:
        raise Http404()
    candidate = (DRIVE_ROOT / rel_path).resolve(strict=False)
    if not _is_within(DRIVE_ROOT, candidate) or not candidate.exists() or not candidate.is_file():
        raise Http404()
    if not _is_downloadable(candidate):
        return HttpResponseForbidden("Downloading this file is not permitted.")
    mime, _ = mimetypes.guess_type(str(candidate))
    response = FileResponse(open(candidate, 'rb'), content_type=mime or 'application/octet-stream')
    response["Content-Disposition"] = f"attachment; filename=\"{candidate.name}\""
    return response


@login_required
def docs_view(request):
    rel_path = request.GET.get('path')
    if not rel_path:
        raise Http404()
    candidate = (DRIVE_ROOT / rel_path).resolve(strict=False)
    if not _is_within(DRIVE_ROOT, candidate) or not candidate.exists() or not candidate.is_file():
        raise Http404()
    if not _is_downloadable(candidate):
        return HttpResponseForbidden("Viewing this file is not permitted.")
    mime, _ = mimetypes.guess_type(str(candidate))
    response = FileResponse(open(candidate, 'rb'), content_type=mime or 'application/octet-stream')
    # inline view
    response["Content-Disposition"] = f"inline; filename=\"{candidate.name}\""
    return response


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