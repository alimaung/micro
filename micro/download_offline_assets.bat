@echo off
echo === Django Offline Assets Downloader ===
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if requests module is available
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required Python packages...
    pip install requests
    if errorlevel 1 (
        echo Error: Failed to install requests module
        echo Please run: pip install requests
        pause
        exit /b 1
    )
)

echo Running offline assets downloader...
python download_offline_assets.py

echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo === Process Complete ===
echo.
echo Your Django application is now ready for offline use!
echo Test your application without internet connection.
echo.
pause
