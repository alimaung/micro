#!/usr/bin/env python3
"""
Setup script for the microfilm comparison tool.
Checks dependencies and provides installation guidance.
"""

import subprocess
import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"✓ Python version: {sys.version}")
    return True


def check_package(package_name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False


def install_requirements():
    """Install requirements from requirements.txt."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("Error: requirements.txt not found")
        return False
    
    print("Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("✓ Python packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install packages: {e}")
        return False


def check_system_dependencies():
    """Check system dependencies like Tesseract."""
    print("\nChecking system dependencies...")
    
    # Check Tesseract
    try:
        subprocess.run(["tesseract", "--version"], capture_output=True, check=True)
        print("✓ Tesseract OCR is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Tesseract OCR is NOT installed")
        print("  Install instructions:")
        print("  - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  - Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  - macOS: brew install tesseract")
    
    # Check poppler (for pdf2image)
    try:
        subprocess.run(["pdftoppm", "-h"], capture_output=True, check=True)
        print("✓ Poppler (pdftoppm) is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Poppler is NOT installed")
        print("  Install instructions:")
        print("  - Windows: https://github.com/oschwartz10612/poppler-windows")
        print("  - Ubuntu/Debian: sudo apt-get install poppler-utils")
        print("  - macOS: brew install poppler")


def main():
    """Main setup function."""
    print("Microfilm Comparison Tool Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    print("\nChecking Python packages...")
    
    # Key packages to check
    packages = [
        ("numpy", "numpy"),
        ("opencv-python", "cv2"),
        ("scikit-image", "skimage"),
        ("pdf2image", "pdf2image"),
        ("pytesseract", "pytesseract"),
        ("matplotlib", "matplotlib"),
        ("Pillow", "PIL")
    ]
    
    missing_packages = []
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    # Install missing packages
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        response = input("Install missing packages? (y/n): ").lower().strip()
        if response == 'y':
            if not install_requirements():
                return False
        else:
            print("Skipping package installation")
    else:
        print("✓ All Python packages are installed")
    
    # Check system dependencies
    check_system_dependencies()
    
    print("\n" + "=" * 40)
    print("Setup complete!")
    print("\nTo test the tool, run:")
    print("  python test_comparison.py")
    print("\nTo compare documents manually, run:")
    print("  python compare_documents.py --original path/to/original.pdf --microfilm path/to/scan.pdf")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

