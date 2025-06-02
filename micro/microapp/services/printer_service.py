"""
Printer service for server-side printing of PDF labels.
Handles direct printing to system printers without user interaction.
"""

import os
import sys
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import time

logger = logging.getLogger(__name__)

class PrinterService:
    """Service for handling server-side printing of PDF documents."""
    
    def __init__(self):
        self.default_printer = None
        self._detect_system()
    
    def _detect_system(self):
        """Detect the operating system and set up appropriate printing methods."""
        self.is_windows = sys.platform.startswith('win')
        self.is_linux = sys.platform.startswith('linux')
        self.is_mac = sys.platform == 'darwin'
        
        if self.is_windows:
            self._setup_windows_printing()
        elif self.is_linux:
            self._setup_linux_printing()
        elif self.is_mac:
            self._setup_mac_printing()
    
    def _setup_windows_printing(self):
        """Set up Windows-specific printing configuration."""
        logger.info("Setting up Windows printing configuration")
        try:
            # Try to get default printer using PowerShell
            logger.info("Attempting to detect default printer using PowerShell")
            result = subprocess.run([
                'powershell', '-Command', 
                'Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default=$true" | Select-Object Name'
            ], capture_output=True, text=True, timeout=10)
            
            logger.info(f"PowerShell printer detection result: returncode={result.returncode}")
            logger.info(f"PowerShell stdout: {result.stdout}")
            logger.info(f"PowerShell stderr: {result.stderr}")
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('Name') and not line.startswith('----'):
                        self.default_printer = line.strip()
                        logger.info(f"Found default printer: {self.default_printer}")
                        break
            
            if not self.default_printer:
                logger.warning("No default printer found in PowerShell output")
            
        except Exception as e:
            logger.error(f"Could not detect Windows default printer: {e}")
            
        logger.info(f"Windows printer setup complete. Default printer: {self.default_printer}")
    
    def _setup_linux_printing(self):
        """Set up Linux-specific printing configuration."""
        try:
            # Try to get default printer using lpstat
            result = subprocess.run(['lpstat', '-d'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                output = result.stdout.strip()
                if 'system default destination:' in output:
                    self.default_printer = output.split('system default destination:')[1].strip()
            
            logger.info(f"Linux default printer: {self.default_printer}")
        except Exception as e:
            logger.warning(f"Could not detect Linux default printer: {e}")
    
    def _setup_mac_printing(self):
        """Set up macOS-specific printing configuration."""
        try:
            # Try to get default printer using lpstat
            result = subprocess.run(['lpstat', '-d'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                output = result.stdout.strip()
                if 'system default destination:' in output:
                    self.default_printer = output.split('system default destination:')[1].strip()
            
            logger.info(f"macOS default printer: {self.default_printer}")
        except Exception as e:
            logger.warning(f"Could not detect macOS default printer: {e}")
    
    def get_available_printers(self) -> List[str]:
        """Get a list of available printers on the system."""
        printers = []
        
        try:
            if self.is_windows:
                # Use PowerShell to get printer list
                result = subprocess.run([
                    'powershell', '-Command', 
                    'Get-WmiObject -Query "SELECT Name FROM Win32_Printer" | Select-Object -ExpandProperty Name'
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    printers = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            
            elif self.is_linux or self.is_mac:
                # Use lpstat to get printer list
                result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('printer '):
                            printer_name = line.split(' ')[1]
                            printers.append(printer_name)
        
        except Exception as e:
            logger.error(f"Error getting printer list: {e}")
        
        return printers
    
    def print_pdf(self, pdf_content: bytes, printer_name: Optional[str] = None, 
                  copies: int = 1, **kwargs) -> Dict[str, Any]:
        """
        Print a PDF document to the specified printer.
        
        Args:
            pdf_content: The PDF content as bytes
            printer_name: Name of the printer (uses default if None)
            copies: Number of copies to print
            **kwargs: Additional printing options
        
        Returns:
            Dict with success status and message
        """
        logger.info(f"Starting print_pdf: printer_name={printer_name}, copies={copies}")
        
        if not pdf_content:
            logger.error("No PDF content provided")
            return {'success': False, 'error': 'No PDF content provided'}
        
        # Use specified printer or default
        target_printer = printer_name or self.default_printer
        logger.info(f"Target printer: {target_printer} (default: {self.default_printer})")
        
        if not target_printer:
            logger.error("No printer available")
            return {'success': False, 'error': 'No printer available'}
        
        # Create temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_pdf_path = temp_file.name
        
        logger.info(f"Created temporary PDF file: {temp_pdf_path}")
        
        try:
            if self.is_windows:
                logger.info("Using Windows printing methods")
                return self._print_pdf_windows(temp_pdf_path, target_printer, copies, **kwargs)
            elif self.is_linux:
                logger.info("Using Linux printing methods")
                return self._print_pdf_linux(temp_pdf_path, target_printer, copies, **kwargs)
            elif self.is_mac:
                logger.info("Using macOS printing methods")
                return self._print_pdf_mac(temp_pdf_path, target_printer, copies, **kwargs)
            else:
                logger.error(f"Unsupported operating system: {sys.platform}")
                return {'success': False, 'error': 'Unsupported operating system'}
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_pdf_path)
                logger.info(f"Cleaned up temporary file: {temp_pdf_path}")
            except Exception as e:
                logger.warning(f"Could not delete temporary file {temp_pdf_path}: {e}")
    
    def _print_pdf_windows(self, pdf_path: str, printer_name: str, copies: int, **kwargs) -> Dict[str, Any]:
        """Print PDF on Windows using win32print only."""
        
        logger.info(f"Attempting to print PDF using win32print: {pdf_path} to printer: {printer_name}")
        
        try:
            import win32print
            import win32api
            
            # Open the printer
            printer_handle = win32print.OpenPrinter(printer_name)
            
            try:
                # Start a print job
                job_info = win32print.StartDocPrinter(printer_handle, 1, ("PDF Label", None, "RAW"))
                
                try:
                    # Start a page
                    win32print.StartPagePrinter(printer_handle)
                    
                    # Read the PDF file and send it to printer
                    with open(pdf_path, 'rb') as f:
                        pdf_data = f.read()
                    
                    # Send the PDF data to printer
                    win32print.WritePrinter(printer_handle, pdf_data)
                    
                    # End the page
                    win32print.EndPagePrinter(printer_handle)
                    
                    logger.info(f"Successfully sent PDF to printer using win32print")
                    
                    return {
                        'success': True,
                        'message': f'Printed to {printer_name} using win32print',
                        'method': 'win32print'
                    }
                    
                finally:
                    # End the document
                    win32print.EndDocPrinter(printer_handle)
                    
            finally:
                # Close the printer
                win32print.ClosePrinter(printer_handle)
                
        except ImportError:
            logger.error("win32print not available - install pywin32 package")
            return {'success': False, 'error': 'win32print not available - install pywin32 package'}
        except Exception as e:
            logger.error(f"win32print printing failed: {e}")
            return {'success': False, 'error': f'win32print printing failed: {str(e)}'}
    
    def _print_pdf_linux(self, pdf_path: str, printer_name: str, copies: int, **kwargs) -> Dict[str, Any]:
        """Print PDF on Linux using lp command."""
        try:
            cmd = ['lp', '-d', printer_name, '-n', str(copies)]
            
            # Add any additional options
            if kwargs.get('orientation') == 'landscape':
                cmd.extend(['-o', 'landscape'])
            
            cmd.append(pdf_path)
            
            result = subprocess.run(cmd, timeout=30, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True, 
                    'message': f'Printed to {printer_name} using lp command',
                    'method': 'lp'
                }
            else:
                return {
                    'success': False, 
                    'error': f'lp command failed: {result.stderr}'
                }
        
        except Exception as e:
            return {'success': False, 'error': f'Linux printing failed: {str(e)}'}
    
    def _print_pdf_mac(self, pdf_path: str, printer_name: str, copies: int, **kwargs) -> Dict[str, Any]:
        """Print PDF on macOS using lp command."""
        try:
            cmd = ['lp', '-d', printer_name, '-n', str(copies)]
            
            # Add any additional options
            if kwargs.get('orientation') == 'landscape':
                cmd.extend(['-o', 'landscape'])
            
            cmd.append(pdf_path)
            
            result = subprocess.run(cmd, timeout=30, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True, 
                    'message': f'Printed to {printer_name} using lp command',
                    'method': 'lp'
                }
            else:
                return {
                    'success': False, 
                    'error': f'lp command failed: {result.stderr}'
                }
        
        except Exception as e:
            return {'success': False, 'error': f'macOS printing failed: {str(e)}'}
    
    def print_label_from_file(self, file_path: str, printer_name: Optional[str] = None, 
                             copies: int = 1) -> Dict[str, Any]:
        """
        Print a PDF label from a file path.
        
        Args:
            file_path: Path to the PDF file
            printer_name: Name of the printer (uses default if None)
            copies: Number of copies to print
        
        Returns:
            Dict with success status and message
        """
        try:
            with open(file_path, 'rb') as f:
                pdf_content = f.read()
            
            return self.print_pdf(pdf_content, printer_name, copies)
        
        except Exception as e:
            return {'success': False, 'error': f'Could not read PDF file: {str(e)}'}
    
    def get_printer_status(self) -> Dict[str, Any]:
        """Get the current printer status and configuration."""
        return {
            'default_printer': self.default_printer,
            'available_printers': self.get_available_printers(),
            'system': {
                'windows': self.is_windows,
                'linux': self.is_linux,
                'mac': self.is_mac
            }
        }


# Global printer service instance
printer_service = PrinterService() 