#!/usr/bin/env python3
"""
Advanced template updater for offline assets.
This script handles complex template replacements, especially for flag images.
"""

import os
import re
from pathlib import Path

# Base directory for the Django project
DJANGO_ROOT = Path(__file__).parent
TEMPLATES_ROOT = DJANGO_ROOT / "microapp" / "templates" / "microapp"

def update_base_template():
    """Update base.html template with proper flag image handling."""
    base_template = TEMPLATES_ROOT / "base.html"
    
    if not base_template.exists():
        print(f"Warning: {base_template} not found")
        return
    
    print(f"Updating {base_template.relative_to(DJANGO_ROOT)}...")
    
    with open(base_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace flag image section with offline version
    flag_section_pattern = r'<img\s+src="https://flagcdn\.com/20x15/[^"]*"\s+srcset="[^"]*"\s+width="20"\s+height="15"\s+alt="[^"]*">'
    
    new_flag_section = '''<img src="{% static 'microapp/offline/images/flags/' %}{% if LANGUAGE_CODE == 'en' %}us{% elif LANGUAGE_CODE == 'de' %}de{% else %}{{ LANGUAGE_CODE }}{% endif %}_20x15.png"
                srcset="{% static 'microapp/offline/images/flags/' %}{% if LANGUAGE_CODE == 'en' %}us{% elif LANGUAGE_CODE == 'de' %}de{% else %}{{ LANGUAGE_CODE }}{% endif %}_40x30.png 2x, {% static 'microapp/offline/images/flags/' %}{% if LANGUAGE_CODE == 'en' %}us{% elif LANGUAGE_CODE == 'de' %}de{% else %}{{ LANGUAGE_CODE }}{% endif %}_60x45.png 3x"
                width="20"
                height="15"
                alt="{{ LANGUAGE_CODE|upper }}">'''
    
    if re.search(flag_section_pattern, content):
        content = re.sub(flag_section_pattern, new_flag_section, content)
        
        with open(base_template, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✓ Updated flag images section")
    else:
        print("  - Flag images section not found or already updated")

def update_all_templates():
    """Update all templates with offline asset paths."""
    print("Updating all templates for offline use...")
    
    # Simple replacements
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
    }
    
    # Find all template files
    template_files = list(TEMPLATES_ROOT.rglob("*.html"))
    
    for template_file in template_files:
        print(f"  Processing: {template_file.relative_to(DJANGO_ROOT)}")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes_made = False
            
            # Apply replacements
            for old_url, new_path in replacements.items():
                if old_url in content:
                    content = content.replace(old_url, new_path)
                    changes_made = True
            
            # Remove Google Fonts preconnect (not needed for offline)
            if 'https://fonts.googleapis.com' in content:
                content = re.sub(r'<link[^>]*href="https://fonts\.googleapis\.com[^"]*"[^>]*>', '', content)
                changes_made = True
            
            # Only write if content changed
            if changes_made:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"    ✓ Updated")
            else:
                print(f"    - No changes needed")
                
        except Exception as e:
            print(f"    ✗ Error updating {template_file}: {e}")

def create_offline_css():
    """Create a CSS file to handle offline font loading."""
    css_content = """
/* Offline Font Loading */
@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 300;
    src: url('../fonts/Inter-Light.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 400;
    src: url('../fonts/Inter-Regular.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 500;
    src: url('../fonts/Inter-Medium.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 600;
    src: url('../fonts/Inter-SemiBold.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 700;
    src: url('../fonts/Inter-Bold.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 800;
    src: url('../fonts/Inter-ExtraBold.woff2') format('woff2');
}

/* Apply Inter font to body */
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
"""
    
    css_path = DJANGO_ROOT / "microapp" / "static" / "microapp" / "offline" / "css" / "offline-fonts.css"
    css_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"Created offline fonts CSS: {css_path.relative_to(DJANGO_ROOT)}")

def main():
    """Main function."""
    print("=== Advanced Template Updater for Offline Assets ===")
    print()
    
    # Update base template with proper flag handling
    update_base_template()
    print()
    
    # Update all other templates
    update_all_templates()
    print()
    
    # Create offline CSS
    create_offline_css()
    print()
    
    print("=== Template Update Complete ===")
    print("All templates have been updated for offline use.")

if __name__ == "__main__":
    main()
