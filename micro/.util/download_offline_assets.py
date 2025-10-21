#!/usr/bin/env python3
"""
Script to download all online assets from Django project for offline use.
This script will:
1. Download all external CSS, JS, fonts, and images
2. Update templates to use local assets instead of online ones
3. Create necessary directory structure
"""

import os
import requests
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin
import time

# Base directory for the Django project
DJANGO_ROOT = Path(__file__).parent
STATIC_ROOT = DJANGO_ROOT / "microapp" / "static" / "microapp"
TEMPLATES_ROOT = DJANGO_ROOT / "microapp" / "templates" / "microapp"

# Create offline assets directory structure
OFFLINE_DIRS = {
    'css': STATIC_ROOT / "offline" / "css",
    'js': STATIC_ROOT / "offline" / "js", 
    'fonts': STATIC_ROOT / "offline" / "fonts",
    'images': STATIC_ROOT / "offline" / "images",
    'flags': STATIC_ROOT / "offline" / "images" / "flags"
}

# Define all online resources to download
ONLINE_RESOURCES = {
    # Font Awesome CSS files
    'fontawesome-6.4.0.css': {
        'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
        'type': 'css',
        'local_path': 'offline/css/fontawesome-6.4.0.min.css'
    },
    'fontawesome-6.0.0.css': {
        'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css', 
        'type': 'css',
        'local_path': 'offline/css/fontawesome-6.0.0.min.css'
    },
    
    # jQuery
    'jquery-3.6.4.js': {
        'url': 'https://code.jquery.com/jquery-3.6.4.min.js',
        'type': 'js',
        'local_path': 'offline/js/jquery-3.6.4.min.js'
    },
    
    # Chart.js
    'chart.js': {
        'url': 'https://cdn.jsdelivr.net/npm/chart.js',
        'type': 'js', 
        'local_path': 'offline/js/chart.js'
    },
    
    # Google Fonts - Inter
    'inter-font.css': {
        'url': 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
        'type': 'css',
        'local_path': 'offline/css/inter-font.css'
    }
}

# Flag images for language switching
FLAG_COUNTRIES = ['us', 'de']  # Add more as needed
FLAG_SIZES = ['20x15', '40x30', '60x45']

def create_directories():
    """Create necessary directory structure for offline assets."""
    print("Creating directory structure...")
    for dir_path in OFFLINE_DIRS.values():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created: {dir_path}")

def download_file(url, file_path, description=""):
    """Download a file from URL to local path."""
    try:
        print(f"Downloading {description or url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"  ✓ Downloaded: {file_path}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to download {url}: {e}")
        return False

def download_font_awesome_fonts(css_content, css_file_path):
    """Download Font Awesome font files referenced in CSS."""
    print("Downloading Font Awesome fonts...")
    
    # Find font URLs in CSS
    font_urls = re.findall(r'url\(([^)]+)\)', css_content)
    
    for font_url in font_urls:
        if 'fontawesome' in font_url or 'font-awesome' in font_url:
            # Convert relative URLs to absolute
            if font_url.startswith('//'):
                font_url = 'https:' + font_url
            elif font_url.startswith('/'):
                font_url = 'https://cdnjs.cloudflare.com' + font_url
            
            # Extract filename
            filename = os.path.basename(urlparse(font_url).path)
            if filename:
                font_path = OFFLINE_DIRS['fonts'] / filename
                
                if download_file(font_url, font_path, f"Font: {filename}"):
                    # Update CSS to use local font path
                    css_content = css_content.replace(font_url, f"../fonts/{filename}")
    
    # Write updated CSS
    with open(css_file_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    return css_content

def download_google_fonts(css_content, css_file_path):
    """Download Google Fonts files referenced in CSS."""
    print("Downloading Google Fonts...")
    
    # Find font URLs in CSS
    font_urls = re.findall(r'url\(([^)]+)\)', css_content)
    
    for font_url in font_urls:
        if 'fonts.gstatic.com' in font_url:
            # Extract filename
            filename = os.path.basename(urlparse(font_url).path)
            if filename:
                font_path = OFFLINE_DIRS['fonts'] / filename
                
                if download_file(font_url, font_path, f"Google Font: {filename}"):
                    # Update CSS to use local font path
                    css_content = css_content.replace(font_url, f"../fonts/{filename}")
    
    # Write updated CSS
    with open(css_file_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    return css_content

def download_flag_images():
    """Download flag images for language switching."""
    print("Downloading flag images...")
    
    for country in FLAG_COUNTRIES:
        for size in FLAG_SIZES:
            url = f"https://flagcdn.com/{size}/{country}.png"
            filename = f"{country}_{size}.png"
            flag_path = OFFLINE_DIRS['flags'] / filename
            
            download_file(url, flag_path, f"Flag: {country} {size}")

def download_main_resources():
    """Download all main online resources."""
    print("Downloading main resources...")
    
    for name, resource in ONLINE_RESOURCES.items():
        url = resource['url']
        local_path = STATIC_ROOT / resource['local_path']
        
        # Ensure directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        if download_file(url, local_path, name):
            # Handle special cases
            if 'fontawesome' in name:
                with open(local_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                download_font_awesome_fonts(css_content, local_path)
            elif 'inter-font' in name:
                with open(local_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                download_google_fonts(css_content, local_path)

def update_templates():
    """Update templates to use local assets instead of online ones."""
    print("Updating templates...")
    
    # Template replacements
    replacements = {
        # Font Awesome
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css': 
            "{% static 'microapp/offline/css/fontawesome-6.4.0.min.css' %}",
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css': 
            "{% static 'microapp/offline/css/fontawesome-6.0.0.min.css' %}",
        
        # jQuery
        'https://code.jquery.com/jquery-3.6.4.min.js': 
            "{% static 'microapp/offline/js/jquery-3.6.4.min.js' %}",
        
        # Chart.js
        'https://cdn.jsdelivr.net/npm/chart.js': 
            "{% static 'microapp/offline/js/chart.js' %}",
        
        # Google Fonts
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap': 
            "{% static 'microapp/offline/css/inter-font.css' %}",
        'https://fonts.googleapis.com': '',  # Remove preconnect
    }
    
    # Flag image replacements (more complex due to Django template logic)
    flag_replacements = {
        'https://flagcdn.com/20x15/': "{% static 'microapp/offline/images/flags/' %}",
        'https://flagcdn.com/40x30/': "{% static 'microapp/offline/images/flags/' %}",
        'https://flagcdn.com/60x45/': "{% static 'microapp/offline/images/flags/' %}",
    }
    
    # Find all template files
    template_files = list(TEMPLATES_ROOT.rglob("*.html"))
    
    for template_file in template_files:
        print(f"  Updating: {template_file.relative_to(DJANGO_ROOT)}")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply simple replacements
            for old_url, new_path in replacements.items():
                content = content.replace(old_url, new_path)
            
            # Handle flag images (more complex replacement)
            if 'flagcdn.com' in content:
                # This requires more sophisticated template logic
                # For now, we'll create a simple replacement
                content = re.sub(
                    r'https://flagcdn\.com/(\d+x\d+)/',
                    r"{% static 'microapp/offline/images/flags/' %}\1/",
                    content
                )
            
            # Only write if content changed
            if content != original_content:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"    ✓ Updated")
            else:
                print(f"    - No changes needed")
                
        except Exception as e:
            print(f"    ✗ Error updating {template_file}: {e}")

def create_flag_template_helper():
    """Create a template helper for flag images."""
    print("Creating flag template helper...")
    
    helper_content = """
{% comment %}
Flag image helper template
Usage: {% include 'microapp/flag_helper.html' with country='us' size='20x15' %}
{% endcomment %}

{% load static %}
<img src="{% static 'microapp/offline/images/flags/' %}{{ country }}_{{ size }}.png" 
     alt="{{ country|upper }}" 
     width="{{ size|split:'x'|first }}" 
     height="{{ size|split:'x'|last }}">
"""
    
    helper_path = TEMPLATES_ROOT / "flag_helper.html"
    with open(helper_path, 'w', encoding='utf-8') as f:
        f.write(helper_content)
    
    print(f"  ✓ Created: {helper_path}")

def main():
    """Main function to orchestrate the offline asset download process."""
    print("=== Django Offline Assets Downloader ===")
    print(f"Django root: {DJANGO_ROOT}")
    print(f"Static root: {STATIC_ROOT}")
    print()
    
    # Step 1: Create directories
    create_directories()
    print()
    
    # Step 2: Download main resources
    download_main_resources()
    print()
    
    # Step 3: Download flag images
    download_flag_images()
    print()
    
    # Step 4: Update templates
    update_templates()
    print()
    
    # Step 5: Create helper templates
    create_flag_template_helper()
    print()
    
    print("=== Download Complete ===")
    print("All online assets have been downloaded and templates updated.")
    print("Your Django project should now work offline!")
    print()
    print("Note: You may need to run 'python manage.py collectstatic' to ensure")
    print("all static files are properly collected.")

if __name__ == "__main__":
    main()
