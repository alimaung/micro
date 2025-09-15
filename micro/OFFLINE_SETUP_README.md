# Django Offline Assets Setup

This guide helps you download all online assets (icons, images, fonts, JavaScript libraries) from your Django project so it can work completely offline.

## What Gets Downloaded

The following online resources will be downloaded and made available locally:

### 1. Font Awesome Icons
- **6.4.0**: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css`
- **6.0.0**: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css`
- All associated font files (woff, woff2, etc.)

### 2. JavaScript Libraries
- **jQuery 3.6.4**: `https://code.jquery.com/jquery-3.6.4.min.js`
- **Chart.js**: `https://cdn.jsdelivr.net/npm/chart.js`

### 3. Google Fonts
- **Inter Font Family**: `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap`
- All font weights and formats

### 4. Flag Images
- Country flags for language switching (US, DE, and others as needed)
- Multiple resolutions: 20x15, 40x30, 60x45 pixels

## Quick Start (Windows)

1. **Run the batch file** (easiest method):
   ```cmd
   cd micro
   download_offline_assets.bat
   ```

2. **Collect static files**:
   ```cmd
   python manage.py collectstatic
   ```

3. **Test your application** - it should now work offline!

## Manual Setup

### Step 1: Install Requirements
```bash
cd micro
pip install -r offline_requirements.txt
```

### Step 2: Download Assets
```bash
python download_offline_assets.py
```

### Step 3: Update Templates (Advanced)
```bash
python update_templates_for_offline.py
```

### Step 4: Collect Static Files
```bash
python manage.py collectstatic
```

## Directory Structure After Setup

```
micro/
├── microapp/
│   ├── static/
│   │   └── microapp/
│   │       └── offline/
│   │           ├── css/
│   │           │   ├── fontawesome-6.4.0.min.css
│   │           │   ├── fontawesome-6.0.0.min.css
│   │           │   ├── inter-font.css
│   │           │   └── offline-fonts.css
│   │           ├── js/
│   │           │   ├── jquery-3.6.4.min.js
│   │           │   └── chart.js
│   │           ├── fonts/
│   │           │   ├── fa-solid-900.woff2
│   │           │   ├── fa-regular-400.woff2
│   │           │   ├── Inter-Light.woff2
│   │           │   ├── Inter-Regular.woff2
│   │           │   └── ... (other font files)
│   │           └── images/
│   │               └── flags/
│   │                   ├── us_20x15.png
│   │                   ├── us_40x30.png
│   │                   ├── de_20x15.png
│   │                   └── ... (other flag files)
│   └── templates/
│       └── microapp/
│           └── (updated templates)
```

## What the Scripts Do

### `download_offline_assets.py`
- Downloads all external CSS, JS, and font files
- Extracts and downloads font files referenced in CSS
- Downloads flag images for language switching
- Updates templates to use local paths instead of online URLs
- Creates necessary directory structure

### `update_templates_for_offline.py`
- Advanced template updater for complex replacements
- Handles flag image template logic properly
- Creates offline font CSS files
- Removes unnecessary preconnect links

### `download_offline_assets.bat`
- Windows batch file for easy execution
- Checks for Python and required packages
- Runs the download script automatically

## Template Changes

The scripts will automatically update your templates to use local assets:

**Before:**
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
```

**After:**
```html
<link rel="stylesheet" href="{% static 'microapp/offline/css/fontawesome-6.4.0.min.css' %}">
<script src="{% static 'microapp/offline/js/jquery-3.6.4.min.js' %}"></script>
```

## Flag Images

Flag images for language switching are handled specially:

**Before:**
```html
<img src="https://flagcdn.com/20x15/us.png" alt="US">
```

**After:**
```html
<img src="{% static 'microapp/offline/images/flags/' %}{% if LANGUAGE_CODE == 'en' %}us{% elif LANGUAGE_CODE == 'de' %}de{% else %}{{ LANGUAGE_CODE }}{% endif %}_20x15.png" alt="{{ LANGUAGE_CODE|upper }}">
```

## Troubleshooting

### Common Issues

1. **"requests module not found"**
   ```bash
   pip install requests
   ```

2. **"Permission denied" errors**
   - Run as administrator (Windows)
   - Check file permissions

3. **Templates not updating**
   - Ensure you have write permissions to template files
   - Check that templates are in the correct location

4. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATIC_ROOT` in settings.py

### Adding More Languages

To add more flag images for additional languages:

1. Edit `download_offline_assets.py`
2. Add country codes to `FLAG_COUNTRIES` list:
   ```python
   FLAG_COUNTRIES = ['us', 'de', 'fr', 'es', 'it']  # Add more as needed
   ```
3. Re-run the download script

### Adding More External Resources

To download additional external resources:

1. Edit `download_offline_assets.py`
2. Add new resources to `ONLINE_RESOURCES` dictionary
3. Add template replacements to `replacements` dictionary
4. Re-run the scripts

## Verification

After running the scripts, verify everything works:

1. **Check offline directory structure** exists
2. **Test application without internet connection**
3. **Verify all icons, fonts, and images load correctly**
4. **Check browser developer tools** for any 404 errors

## Benefits

- ✅ **Complete offline functionality**
- ✅ **Faster loading** (no external requests)
- ✅ **Better reliability** (no dependency on external CDNs)
- ✅ **Improved security** (no external script execution)
- ✅ **Consistent performance** regardless of internet speed

## File Sizes

Approximate download sizes:
- Font Awesome: ~1.5 MB
- jQuery: ~90 KB
- Chart.js: ~200 KB
- Google Fonts (Inter): ~500 KB
- Flag images: ~50 KB total

**Total: ~2.3 MB** of offline assets

---

*This setup ensures your Django application works completely offline while maintaining all visual and functional elements.*
