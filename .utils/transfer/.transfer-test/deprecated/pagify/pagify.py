"""

This script provides functionality to analyze PDF files in a specified folder,
counting the number of pages and identifying oversized files based on user-defined
thresholds. It features a command-line interface with a menu for configuration
options, including language selection, display settings, and PDF processing options.

"""

import os, sys, time, json, math, threading, keyboard, subprocess, fitz, tqdm, PyPDF2, tkinter as tk
import figlet as fg, curses as cs, fade as fd # custom dependencies
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

class TimerUpdatedTqdm:
    """Context manager for a progress bar with a timer."""
    
    def __init__(self, total_files, desc="Processing...", update_interval=1.0, **kwargs):
        self.total = total_files  # Total number of files to process
        self.kwargs = kwargs
        self.desc = desc
        self.lock = threading.Lock()  # Lock for thread safety
        self.files_processed = 0
        self.pbar = None
        self.update_interval = update_interval
        self.timer_thread = None
        self.stop_timer = threading.Event()
        self.current_file = "Starting..."
        
    def __enter__(self):
        self.pbar = tqdm.tqdm(total=self.total, desc=self.desc, **self.kwargs)  # Initialize progress bar
        self.start_timer_thread()  # Start the timer thread
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_timer.set()  # Signal the timer to stop
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join()  # Wait for the timer thread to finish
        if self.pbar:
            self.pbar.close()  # Close the progress bar
            
    def start_timer_thread(self):
        """Starts a separate thread to update the progress bar description."""
        def timer_update():
            while not self.stop_timer.is_set():
                with self.lock:
                    if self.pbar:
                        self.pbar.set_description(f"Processing...")  # Update description
                        self.pbar.refresh()
                time.sleep(self.update_interval)  # Wait for the update interval
                
        self.timer_thread = threading.Thread(target=timer_update, daemon=True)
        self.timer_thread.start()
            
    def update_file(self, filepath=None):
        """Updates the progress bar for a processed file."""
        with self.lock:
            if self.pbar:
                self.files_processed += 1  # Increment processed files count
                if filepath:
                    self.current_file = os.path.basename(filepath)  # Update current file name
                    self.pbar.set_description(f"Processing {self.current_file}...")  # Update description
                self.pbar.update(1)  # Update progress bar
                
    def set_current_file(self, filepath):
        """Sets the current file being processed."""
        with self.lock:
            if filepath:
                self.current_file = os.path.basename(filepath)  # Update current file name
                if self.pbar:
                    self.pbar.set_description(f"Processing...")  # Update description
                    self.pbar.refresh()

class PDFProcessor:
    """Class to handle PDF processing tasks."""

    COLORS = {
        "red": "\033[0;91m",
        "green": "\033[0;92m",
        "yellow": "\033[0;93m",
        "blue": "\033[0;94m",
        "magenta": "\033[0;95m",
        "cyan": "\033[0;96m",
        "white": "\033[0;97m",
        "reset": "\033[0m"
    }
  
    PAPER_SIZES = {
        # ISO A series
        'A0': (2384, 3370),
        'A1': (1684, 2384),
        'A2': (1191, 1684),
        'A3': (1191, 842),
        'A4': (595, 842),
        'A5': (420, 595),
        'A6': (297, 420),
        'A7': (210, 297),
        'A8': (148, 210),
        'A9': (105, 148),
        'A10': (74, 105),

        # ISO B series
        'B0': (2835, 4008),
        'B1': (2004, 2835),
        'B2': (1417, 2004),
        'B3': (1001, 1417),
        'B4': (709, 1001),
        'B5': (499, 709),
        'B6': (354, 499),
        'B7': (249, 354),
        'B8': (176, 249),
        'B9': (125, 176),
        'B10': (88, 125),

        # ISO C series (commonly used for envelopes)
        'C0': (2599, 3676),
        'C1': (1837, 2599),
        'C2': (1298, 1837),
        'C3': (918, 1298),
        'C4': (649, 918),
        'C5': (459, 649),
        'C6': (323, 459),
        'C7': (230, 323),
        'C8': (162, 230),
        'C9': (113, 162),
        'C10': (79, 113),

        # US Paper Sizes
        'Letter': (612, 792),      # 8.5 x 11 inches
        'Legal': (612, 1008),      # 8.5 x 14 inches
        'Tabloid': (792, 1224),    # 11 x 17 inches
        'Ledger': (1224, 792),     # 17 x 11 inches
        'Executive': (540, 720),   # 7.25 x 10.5 inches
        'Half Letter': (396, 612), # 5.5 x 8.5 inches
    }
    
    def __init__(self, config: dict):
        """Initializes the PDFProcessor with the given configuration.

        Args:
            config (dict): Configuration settings for PDF processing.
        """
        self.config = config  # Store configuration settings
    
    def colored_text(self, text, color):
        """Returns colored text based on the configuration."""
        if not self.config.get("simple_display", False):
            return f"{self.COLORS.get(color, self.COLORS['reset'])}{text}{self.COLORS['reset']}"
        return text
    
    def count_pdf_pages_fitz(self, pdf_path: str) -> tuple:
        """Counts pages in a PDF using the fitz library and checks for oversized pages.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            tuple: A tuple containing the total number of pages, a boolean indicating if there are oversized pages,
                   and a list of oversized dimensions.
        """
        try:
            doc = fitz.open(pdf_path)  # Open the PDF document
            page_count = doc.page_count  # Get the total number of pages
            oversized_sizes = []  # List to store oversized page dimensions

            if self.config.get("detect_oversized", True):
                threshold_size = self.get_threshold_size()  # Get threshold size
                for page in doc:
                    rect = page.rect  # Get the page rectangle
                    width = rect.width  # Get the page width
                    height = rect.height  # Get the page height

                    # Check if the page exceeds the threshold size
                    if width > threshold_size[0] and height > threshold_size[1]:
                        oversized_sizes.append((width, height))  # Add oversized dimensions
                return page_count, bool(oversized_sizes), oversized_sizes  # Return results
            return page_count, False, []  # Return results if not checking for oversized
        except Exception as e:
            raise PDFProcessingError(f"Error reading {pdf_path}: {e}")  # Raise custom exception
    
    def count_pdf_pages_pypdf2(self, pdf_path: str) -> tuple:
        """Counts pages in a PDF using the PyPDF2 library and checks for oversized pages.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            tuple: A tuple containing the total number of pages, a boolean indicating if there are oversized pages,
                   and a list of oversized dimensions.
        Example:
            page_count:int = 
     
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)  # Read the PDF file
                page_count = len(pdf_reader.pages)  # Get the total number of pages
                oversized_sizes = []  # List to store oversized page dimensions
                #print(pdf_path.split("/")[-1])
                if self.config.get("detect_oversized", True):
                    threshold_size = self.get_threshold_size()  # Get threshold size
                    for index, page in enumerate(pdf_reader.pages):
                        width = float(page.mediabox[2])  # Get the page width
                        height = float(page.mediabox[3])  # Get the page height
                        #print(f"original: H{height}, W{width}, WT{threshold_size[0]}, HT{threshold_size[1]}")
                        # Check if the page exceeds the threshold size

                        is_oversize_portrait = width > threshold_size[0] and height > threshold_size [1]
                        is_oversize_landscape =  width > threshold_size[1] and height > threshold_size [0]

                        if is_oversize_landscape or is_oversize_portrait:
                            oversized_sizes.append((width, height, index))
                            #print(self.colored_text(f"oversize: H{height}, W{width}", "red"))

                    return page_count, bool(oversized_sizes), oversized_sizes  # Return results
                return page_count, False, []  # Return results if not checking for oversized
        except Exception as e:
            raise PDFProcessingError(f"Error reading {pdf_path}: {e}")  # Raise custom exception
    
    def get_threshold_size(self) -> tuple:
        """Returns the threshold size for oversized pages based on configuration.

        Returns: 
            tuple: A tuple representing the width and height threshold for oversized pages.
        """
        return self.PAPER_SIZES.get(
            self.config.get("oversized_threshold", "A2"),
            self.PAPER_SIZES["A2"]
        )

class ConfigManager:
    """Class to manage application configuration."""
    
    def __init__(self):
        self.config_path = self.get_config_path()  # Get the config file path
        self.default_config = {
            "language": "deutsch",
            "simple_display": False,
            "max_workers": min(8, os.cpu_count() or 2),
            "title_fade": "purplepink",
            "success_fade": "brazilgreen",
            "error_fade": "pinkred",
            "title_font": "fraktur",
            "message_font": "ansi_regular",
            "detect_oversized": True,
            "auto_open_oversized": False,
            "oversized_threshold": "A3",
            "pdf_engine": "PyPDF2",
            "size_tolerance": 300,  # Default tolerance of 300 points
        }

    def get_config_path(self):
        """Returns the path to the configuration file."""
        username = os.getlogin()  # Get the current user's login name
        docs_path = os.path.join("C:\\Users", username, "Documents")  # Path to Documents
        config_dir = os.path.join(docs_path, "pagify")  # Directory for pagify config
        os.makedirs(config_dir, exist_ok=True)  # Create directory if it doesn't exist
        return os.path.join(config_dir, "config.json")  # Full path to config file

    def load_config(self):
        """Loads the configuration from a file or returns default settings."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)  # Load existing config
            return self.default_config  # Return default config if file doesn't exist
        except Exception:
            return self.default_config  # Return default config on error

    def save_config(self, config):
        """Saves the current configuration to a file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)  # Write config to file
            print("Configuration saved successfully.")
        except Exception as e:
            print(f"Error saving configuration: {e}")

class PDFProcessingError(Exception):
    """Custom exception for errors during PDF processing."""
    pass

class PDFPageCounter:
    """Class to count pages in PDF files and identify oversized files."""
    
    COLORS = {
        "red": "\033[0;91m",
        "green": "\033[0;92m",
        "yellow": "\033[0;93m",
        "blue": "\033[0;94m",
        "magenta": "\033[0;95m",
        "cyan": "\033[0;96m",
        "white": "\033[0;97m",
        "reset": "\033[0m"
    }
    
    FADE_STYLES = {
        "blackwhite": fd.blackwhite,
        "purplepink": fd.purplepink,
        "greenblue": fd.greenblue,
        "waterblue": fd.water,
        "firered": fd.fire,
        "pinkred": fd.pinkred,
        "purpleblue": fd.purpleblue,
        "brazilgreen": fd.brazil,
        "randomcolor": fd.random,
        "sunset": fd.sunset,
        "forest": fd.forest,
        "germanred": fd.german_red,
        "eintracht": fd.eintracht_frankfurt,
        "nothern_lights": fd.northern_lights,
        "gold_fever": fd.gold_fever,
        "ocean_depths": fd.ocean_depths,
        "ukraine": fd.ukraine,

    }
    
    FONTS = [
        "ansi_regular", "ansi_shadow", "big", "blocky", "dos_rebel", "elite",
        "larry3d", "bloody", "the_edge", "nscript", "fraktur", "electronic",
        "delta_corps_priest_1", "defleppard", "cricket", "big_money-ne",
        "roman", "calvin_s"
    ]
    
    PDF_ENGINES = [
        "fitz", 
        "PyPDF2", 
    ]

    LANGUAGE_TEXTS = {
            "english": {
                "intro": "Select the folder containing PDFs. Only reads files inside that directory and ignores subfolders.",
                "info": "A very useful tool to count the number of pages",
                "exit_any_time": "Press 'Esc' at any time to exit.",
                "press_space": "Press Space to scan a folder",
                "press_f1": "Press F1 to restart the application",
                "press_f2": "Press F2 to open settings menu",
                "selected_folder": "Selected Folder: ",
                "error_occurred": "An error occurred during PDF processing.",
                "press_esc": "Press Esc to exit or",
                "unexpected_error": "An unexpected error occurred: ",
                "press_space_retry": "Press Space to retry or Esc to exit...",
                "no_folder": "No folder was selcted or the window was closed",
                "no_oversize": "No documents with oversize pages detected",
                "process_time": "Total processing time:",
                "total_pages": "Total pages found:",
                "oversize_result": "Oversized documents found (larger than",
                "oversize_qty": "Total number of oversize pages:",
                "select": "Please select a folder in the new window:",
            },
            "deutsch": {
                "intro": "Wählen Sie den Ordner mit PDFs aus. Es werden nur  Dateien in jenem Verzeichnis gelesen, Unterordner werden ignoriert.",
                "info": "Ein sehr hilfreiches Werkzeug zum Zählen von Seiten",
                "exit_any_time": "Drücken Sie jederzeit 'Esc', um zu beenden.",
                "press_f1": "Drücken Sie F1 um das Programm neuzustarten",
                "press_space": "Drücken Sie Leertaste, um einen Ordner zu scannen",
                "press_f2": "Drücken Sie F2, um das Einstellungsmenü zu öffnen",
                "selected_folder": "Ausgewählter Ordner: ",
                "error_occurred": "Bei der Verarbeitung der PDF ist ein Fehler aufgetreten.",
                "press_esc": "Drücken Sie Esc zum Beenden oder...",
                "unexpected_error": "Ein unerwarteter Fehler ist aufgetreten: ",
                "press_space_retry": "Drücken Sie Leertaste, um es erneut zu versuchen, oder Esc, um zu beenden...",
                "no_folder": "Kein Ordner wurde ausgewählt oder das Fenster geschlossen",
                "no_oversize": "Keine Dokumente mit Übergrößen gefunden",
                "process_time": "Total processing time:",
                "total_pages": "Gesamtanzahl an Seiten gefunden:",
                "oversize_result": "Dokumente mit Übergrößen gefunden (größer als",
                "oversize_qty": "Gesamtanzahl an Seiten mit Übergrößen:",
                "select": "Bitte wähle einen Ordner im neuen Fenster aus:",
            },
            "cat": {
                "intro": "Plz select teh folder with teh PDFs. I only read teh files in dat folder, me no likey subfolders.",
                "info": "Dis toolz iz super helpful, it counts teh pages of PDFs. Much useful yes.",
                "exit_any_time": "Press 'Esc' anytime if you wanna run away.",
                "press_space": "Press Space to tell me where da folder is. Me ready.",
                "press_f1": "Press F1 to restart the application",
                "press_f2": "Press F2 to open da magical settings menu. So fancy.",
                "selected_folder": "U picked dis folder: ",
                "error_occurred": "Oh noes! Error happened while processing da PDFs. Bad things.",
                "press_esc": "Press Esc to escape or...",
                "unexpected_error": "UH OH. Unexpected error happened: ",
                "press_space_retry": "Press Space to try again or Esc to run away... pls don't make me do more work.",
                "no_folder": "Noes folders chowsen or teh window was gone",
                "no_oversize": "Noes pawges too big fouwnd",
                "process_time": "Towtal pwocessin teim:",
                "total_pages": "Total pages found:",
                "oversize_result": "Oversized documents found (larger than",
                "oversize_qty": "Total number of oversize pages:",
                "select": "Please select a folder in the new window:",
            },
            "pirate": {
                "intro": "Arrr, select ye folder filled with PDFs. I only read the scrolls in that folder, no subfolders allowed, ye scurvy dog.",
                "info": "This here tool be mighty useful, countin' the pages o' yer PDFs. Yarrr, much treasure.",
                "exit_any_time": "Hit 'Esc' anytime ye be wishin' to make yer escape.",
                "press_space": "Press Space to set sail and scan yer folder, ye landlubber.",
                "press_f1": "Arr, Press F1 to restart the magic scroll",
                "press_f2": "Press F2 to open yer settings menu, ye savvy?",
                "selected_folder": "Aye Aye Captian, Ye have selected this here folder: ",
                "error_occurred": "Blimey! An error be occurrin' whilst processin' yer PDFs.",
                "press_esc": "Press Esc to flee or...",
                "unexpected_error": "Shiver me timbers! An unexpected error be upon us: ",
                "press_space_retry": "Press Space to try again or Esc to abandon ship... Arrr!",
                "no_folder": "Aaaarrrrgggghhhh, ye did not select a folder and left me maroon!",
                "no_oversize": "Yo ho ho, no scrolls too big for my treasure there",
                "process_time": "Took me this long to read:",
                "total_pages": "Aye, so many pages here:",
                "oversize_result": "Oversized scolls found (larger than",
                "oversize_qty": "Total number of oversize pages:",
                "select": "Please select a folder in the new window:",
            },
            "hipster": {
                "intro": "Yo, select that folder with your PDFs, but only the files in it, man. Ain't doing extra digging",
                "info": "This tool is like, totally rad for counting pages in your PDFs and stuff.",
                "exit_any_time": "Tap 'Esc' if you wanna bounce anytime, no pressure.",
                "press_space": "Hit Space to scan your folder, dude.",
                "press_f1": "Press F1 to restart the application, yo",
                "press_f2": "Press F2 to open your settings menu, fam.",
                "selected_folder": "Lets go! You selected this folder: ",
                "error_occurred": "Damn bro, something went wrong while processing your PDFs.",
                "press_esc": "Press Esc to dip, or...",
                "unexpected_error": "Woah, some unexpected error vibes: ",
                "press_space_retry": "Press Space to give it another shot, or Esc to dip out yo...",
                "no_folder": "Yo bro, did you forget to chose a folder? Or did you bounce on me dude?",
                "no_oversize": "What? No oversize papers? Dang it",
                "process_time": "This is taking way too long yo:",
                "total_pages": "Total pages mate:",
                "oversize_result": "Oversized docs found (larger than",
                "oversize_qty": "Total number of oversize pages:",
                "select": "Please select a folder in the new window:",
            }
        }
    
    PAPER_SIZES = {
        # ISO A series
        'A0': (2384, 3370),
        'A1': (1684, 2384),
        'A2': (1191, 1684),
        'A3': (842, 1191),
        'A4': (595, 842),
        'A5': (420, 595),
        'A6': (297, 420)
    }
    
    def __init__(self):
        """Initializes the PDFPageCounter and loads the user configuration."""
        self.root = None  # Tkinter root window
        self.exit_flag = False  # Flag to exit the program
        self.config_manager = ConfigManager()  # Instantiate ConfigManager
        self.config = self.config_manager.load_config()  # Load user configuration
        self.menu_active = False  # Flag to track menu state
        self.menu_thread = None  # Thread for menu interface
        self.results_active = False
        self.results_thread = False
        self.oversize_files_state = False
        self.oversize_files_data = []
        self.pdf_processor = PDFProcessor(self.config)  # Instantiate PDFProcessor
    
    def colored_text(self, text, color):
        """Returns colored text based on the configuration."""
        if not self.config.get("simple_display", False):
            return f"{self.COLORS.get(color, self.COLORS['reset'])}{text}{self.COLORS['reset']}"
        return text
    
    def get_total_pdf_pages(self, folder_path):
        """Counts total pages in all PDFs in a specified folder and identifies oversized files.
        
        Args:
            folder_path (str): Path to the folder containing PDF files
            
        Returns:
            tuple: (total_pages, oversized_files_info, process_time)
        """
        # Find all PDF files in the folder
        pdf_files = self._find_pdf_files(folder_path)
        
        if not pdf_files:
            print(self.colored_text("\nNo PDFs found in the selected folder.", "red"))
            return 0, [], 0
        
        # Display processing message
        self._display_processing_message()
        
        start_time = time.time()
        
        try:
            # Process all PDF files and collect results
            total_pages, oversized_files_info = self._process_pdf_files(pdf_files)
        except Exception as e:
            print(f"Error during PDF page counting: {e}")
            return 0, [], 0
        
        process_time = time.time() - start_time
        return total_pages, oversized_files_info, process_time

    def _find_pdf_files(self, folder_path):
        """Find all PDF files in the specified folder.
        
        Args:
            folder_path (str): Path to search for PDF files
            
        Returns:
            list: List of paths to PDF files
        """
        return [entry.path for entry in os.scandir(folder_path) 
                if entry.is_file() and entry.name.endswith(".pdf")]

    def _display_processing_message(self):
        """Display a message indicating processing has started."""
        if not self.config.get("simple_display", False):
            print("\n")
            print(self.FADE_STYLES[self.config.get("success_fade", "brazilgreen")](
                fg.z("PROCESSING...\n", 
                    font=self.config.get("message_font", "ansi_regular"))))

    def _process_pdf_files(self, pdf_files):
        """Process all PDF files with the appropriate engine using thread pool.
        
        Args:
            pdf_files (list): List of PDF file paths to process
            
        Returns:
            tuple: (total_pages, oversized_files_info)
        """
        max_workers = self.config.get("max_workers", min(8, os.cpu_count() or 2))
        total_pages = 0
        oversized_files_info = []
        
        # Initialize progress tracker
        progress_tracker = self._create_progress_tracker(len(pdf_files))
        
        # Get the appropriate counting function based on configured PDF engine
        count_function = self._get_count_function()
        
        with progress_tracker, ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._process_single_file, pdf, count_function, progress_tracker): 
                Path(pdf).resolve() for pdf in pdf_files
            }
            
            for future in as_completed(futures):
                page_count, is_oversized, sizes = future.result()
                total_pages += page_count
                
                if is_oversized:
                    pdf_path = futures[future]
                    oversized_files_info.append((pdf_path, sizes))
        
        return total_pages, oversized_files_info

    def _create_progress_tracker(self, total_files):
        """Create a progress tracker for PDF processing.
        
        Args:
            total_files (int): Total number of files to process
            
        Returns:
            TimerUpdatedTqdm: Progress tracker instance
        """
        return TimerUpdatedTqdm(
            total_files=total_files,
            desc="Analyzing PDFs",
            update_interval=1.0,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            colour="green",
            dynamic_ncols=True
        )

    def _get_count_function(self):
        """Get the appropriate PDF page counting function based on configuration.
        
        Returns:
            function: The PDF counting function to use
        """
        pdf_engine = self.config.get("pdf_engine", "fitz")
        
        if pdf_engine == "fitz":
            return self.pdf_processor.count_pdf_pages_fitz
        elif pdf_engine == "PyPDF2":
            return self.pdf_processor.count_pdf_pages_pypdf2
        else:
            raise ValueError(f"Unsupported PDF engine: {pdf_engine}")

    def _process_single_file(self, pdf_path, count_function, progress_tracker):
        """Process a single PDF file and update the progress tracker.
        
        Args:
            pdf_path (str): Path to the PDF file
            count_function (function): Function to count pages
            progress_tracker (TimerUpdatedTqdm): Progress tracker to update
            
        Returns:
            tuple: (page_count, is_oversized, sizes)
        """
        try:
            progress_tracker.set_current_file(pdf_path)
            result = count_function(pdf_path)
            progress_tracker.update_file(pdf_path)
            return result
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            progress_tracker.update_file(pdf_path)
            return 0, False, []

    def select_folder(self, initial_dir=None):
        """Prompts the user to select a folder containing PDF files."""
        if self.exit_flag:
            return None
            
        # Check if we already have a Tkinter root instance and it's still valid
        if not hasattr(self, 'root') or self.root is None or not isinstance(self.root, tk.Tk):
            try:
                # Create a new root instance only if needed
                self.root = tk.Tk()
                self.root.withdraw()  # Hide the root window
            except Exception as e:
                print(f"Error creating Tkinter root: {e}")
                return None
        
        # Use the existing root that's already withdrawn
        initial_dir = initial_dir or os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
        
        try:
            folder = filedialog.askdirectory(
                parent=self.root,  # Explicitly set parent
                title="Select Folder Containing PDFs", 
                initialdir=initial_dir  # Set initial directory
            )
            return folder  # Return selected folder path
        except Exception as e:
            print(f"Error selecting folder: {e}")  # Print error message
            return None
        finally:
            # Don't destroy the root here - keep it for future use
            pass
            
    def cleanup_tkinter(self):
        """Cleans up Tkinter resources when the application is closing."""
        if hasattr(self, 'root') and self.root is not None:
            try:
                self.root.destroy()  # Destroy the Tkinter root window
                self.root = None  # Reset root reference
            except Exception as e:
                print(f"Error destroying Tkinter root: {e}")

    def show_menu(self):
        """Displays the configuration menu for the application."""
        if self.menu_active:
            return
        
        self.menu_active = True  # Set menu state to active
        self.menu_thread = threading.Thread(target=self._menu_interface)  # Start menu interface thread
        self.menu_thread.daemon = True
        self.menu_thread.start()

    def _menu_interface(self):
        """Handles the menu interface for user configuration."""
        try:
            stdscr = cs.initscr()  # Initialize curses screen
            cs.noecho()  # Disable echoing of input
            cs.cbreak()  # Enable cbreak mode
            cs.start_color()  # Start color support
            # Initialize color pairs for menu
            cs.init_pair(1, cs.COLOR_GREEN, cs.COLOR_BLACK)
            cs.init_pair(2, cs.COLOR_CYAN, cs.COLOR_BLACK)
            cs.init_pair(3, cs.COLOR_YELLOW, cs.COLOR_BLACK)
            cs.init_pair(4, cs.COLOR_MAGENTA, cs.COLOR_BLACK)
            cs.init_pair(5, cs.COLOR_WHITE, cs.COLOR_BLACK)
            stdscr.keypad(True)  # Enable keypad input

            # Define menu items
            menu_items = [
                f"Language: {self.config.get('language', 'english')}",
                f"Simple Display: {self.config.get('simple_display', False)}",
                f"Max Workers: {self.config.get('max_workers', min(8, os.cpu_count() or 2))}",
                f"Title Fade Style: {self.config.get('title_fade', 'firered')}",
                f"Success Fade Style: {self.config.get('success_fade', 'brazilgreen')}",
                f"Error Fade Style: {self.config.get('error_fade', 'pinkred')}",
                f"Title Font: {self.config.get('title_font', 'big_money-ne')}",
                f"Message Font: {self.config.get('message_font', 'ansi_regular')}",
                f"Detect Oversized Files: {self.config.get('detect_oversized', True)}",
                f"Auto-Open Oversized Files: {self.config.get('auto_open_oversized', True)} [EXPERIMENTAL]",
                f"Oversized Threshold: {self.config.get('oversized_threshold', 'A2')}",
                f"Size Tolerance: {self.config.get('size_tolerance', 300)} pts",  # New menu item
                f"PDF Engine: {self.config.get('pdf_engine', 'fitz')}",
                "Save and Restart",
                "Exit Menu"
            ]

            current_row = 0  # Track the currently selected menu item
            settings_changed = False  # Flag to track if settings have changed

            while True:
                stdscr.clear()  # Clear the screen
                h, w = stdscr.getmaxyx()  # Get screen dimensions

                title = "Pagify Configuration"  # Menu title
                stdscr.addstr(1, (w - len(title)) // 2, title, cs.color_pair(2) | cs.A_BOLD)  # Center title

                # Display menu items
                for idx, item in enumerate(menu_items):
                    x = w // 4
                    y = h // 4 + idx
                    if idx == current_row:
                        stdscr.addstr(y, x, item, cs.color_pair(1) | cs.A_REVERSE)  # Highlight selected item
                    else:
                        stdscr.addstr(y, x, item)  # Display item

                # Information text for the currently selected item
                info_texts = [
                    "Select the language for the application.",
                    "Toggle simple display mode.",
                    "Set the maximum number of workers for processing. Set to max for network drives",
                    "Select the fade style for titles.",
                    "Select the fade style for success messages.",
                    "Select the fade style for error messages.",
                    "Select the font for titles.",
                    "Select the font for messages.",
                    "Toggle detection of oversized files.",
                    "Toggle auto-opening of oversized files. Might be risky if there are many files.",
                    "Select the oversized threshold size.",
                    "Set tolerance in points when matching paper sizes (50-500). Lower is stricter.",  # New info text
                    "Select the pdf engine used for analyzing the pages. Use fitz for local files, PyPDF2 for files on network drives",
                    "Save the current settings and restart the application.",
                    "Exit the menu."
                ]
                stdscr.addstr(h - 4, (w - len(info_texts[current_row])) // 2, info_texts[current_row], cs.color_pair(3))  # Display info text

                footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"  # Footer instructions
                stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))  # Display footer

                stdscr.refresh()  # Refresh the screen

                key = stdscr.getch()  # Get user input

                # Handle user input for navigation and selection
                if key == cs.KEY_UP and current_row > 0:
                    current_row -= 1
                elif key == cs.KEY_DOWN and current_row < len(menu_items) - 1:
                    current_row += 1
                elif key == cs.KEY_ENTER or key in [10, 13]:
                    if current_row == len(menu_items) - 2:
                        self._save_config()  # Save configuration

                        if settings_changed:
                            stdscr.clear()
                            stdscr.addstr(h // 2, (w - len("Restarting application...\n\n\n\n")) // 2, "Restarting application...\n\n\n\n")
                            stdscr.refresh()
                            time.sleep(1)
                            self.restart_application()  # Restart application
                        break
                    elif current_row == len(menu_items) - 1:
                        return False  # Exit menu
                    else:
                        option_changed = self._change_option(stdscr, current_row, menu_items)  # Change selected option
                        if option_changed:
                            settings_changed = True  # Mark settings as changed
                elif key == 27:
                    break  # Exit menu on ESC
                elif key == ord('b'):
                    return False  # Exit menu on 'b'
                elif key == ord('s'):
                    self._save_config()  # Save configuration
                    stdscr.addstr(h - 3, (w - len("Configuration Saved! Restarting...")) // 2, "Configuration Saved! Restarting...", cs.color_pair(1))
                    stdscr.refresh()
                    time.sleep(1)
                    self.restart_application()  # Restart application

        except Exception as e:
            print(f"Error in menu interface: {e}")  # Print error message
        finally:
            cs.endwin()  # End curses mode
            self.menu_active = False  # Mark menu as inactive

    def show_results(self):
        """Displays the results of oversize pages."""
        if self.results_active:
            return
        
        if not self.oversize_files_state:
            return
        
        self.results_active = True  # Set menu state to active
        self.results_thread = threading.Thread(target=self._oversize_picker)  # Start menu interface thread
        self.results_thread.daemon = True
        self.results_thread.start()

    def _change_option(self, stdscr, option_idx, menu_items):
        """Handles changes to the selected menu option."""
        h, w = stdscr.getmaxyx()  # Get screen dimensions
        prompt_y = h // 2  # Vertical position for prompts
        prompt_x = w // 4  # Horizontal position for prompts

        # Language selection
        if option_idx == 0:
            languages = ["english", "deutsch", "cat", "pirate", "hipster"]
            current_idx = languages.index(self.config.get("language", "english")) if self.config.get("language", "english") in languages else 0
            original_value = self.config.get("language", "english")

            stdscr.clear()
            stdscr.addstr(prompt_y, prompt_x, "Select Language: ")
            for idx, lang in enumerate(languages):
                if idx == current_idx:
                    stdscr.addstr(prompt_y + 2 + idx, prompt_x + 5, lang, cs.color_pair(1) | cs.A_REVERSE)  # Highlight selected language
                    footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"
                    stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))
                else:
                    stdscr.addstr(prompt_y + 2 + idx, prompt_x + 5, lang)  # Display language option

            footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"
            stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))

            stdscr.refresh()

            while True:
                key = stdscr.getch()  # Get user input
                if key == cs.KEY_UP and current_idx > 0: current_idx -= 1
                elif key == cs.KEY_DOWN and current_idx < len(languages) - 1: current_idx += 1
                elif key == cs.KEY_ENTER or key in [10, 13]:
                    self.config["language"] = languages[current_idx]  # Update selected language
                    break
                elif key == 27: break
                elif key == ord('b'): return False
                elif key == ord('s'):
                    self.config["language"] = languages[current_idx]  # Update selected language
                    self._save_config()  # Save configuration
                    stdscr.addstr(h - 3, (w - len("Configuration Saved!")) // 2, "Configuration Saved!", cs.color_pair(1))
                    stdscr.refresh()
                    time.sleep(1)
                    self.restart_application()  # Restart application

                for idx, lang in enumerate(languages):
                    if idx == current_idx:
                        stdscr.addstr(prompt_y + 2 + idx, prompt_x + 5, lang, cs.color_pair(1) | cs.A_REVERSE)  # Highlight selected language
                    else:
                        stdscr.addstr(prompt_y + 2 + idx, prompt_x + 5, lang)  # Display language option
                stdscr.refresh()

            menu_items[option_idx] = f"Language: {self.config['language']}"  # Update menu item
            return self.config["language"] != original_value  # Return if value changed

        # Simple display toggle
        elif option_idx == 1:
            original_value = self.config.get("simple_display", False)
            self.config["simple_display"] = not original_value  # Toggle simple display
            menu_items[option_idx] = f"Simple Display: {self.config['simple_display']}"  # Update menu item
            return True  # Indicate change

        # Max workers adjustment
        elif option_idx == 2:
            max_cpu = min(8, os.cpu_count() or 2)  # Maximum CPU cores
            current_value = self.config.get("max_workers", min(8, os.cpu_count() or 2))  # Get current max workers
            original_value = current_value

            stdscr.clear()
            stdscr.addstr(prompt_y, prompt_x, f"Max Workers (1-{max_cpu}): {current_value}")
            stdscr.addstr(prompt_y + 2, prompt_x, "Use ← and → to adjust, Enter to confirm")
            footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"
            stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))
            stdscr.refresh()

            while True:
                key = stdscr.getch()  # Get user input
                if key == cs.KEY_LEFT and current_value > 1: current_value -= 1
                elif key == cs.KEY_RIGHT and current_value < max_cpu: current_value += 1
                elif key == cs.KEY_ENTER or key in [10, 13]:
                    self.config["max_workers"] = current_value  # Update max workers
                    break
                elif key == 27: break
                elif key == ord('b'): return False
                elif key == ord('s'):
                    self.config["max_workers"] = current_value  # Update max workers
                    self._save_config()  # Save configuration
                    stdscr.addstr(h - 3, (w - len("Configuration Saved!")) // 2, "Configuration Saved!", cs.color_pair(1))
                    stdscr.refresh()
                    time.sleep(1)
                    self.restart_application()  # Restart application

                stdscr.addstr(prompt_y, prompt_x, f"Max Workers (1-{max_cpu}): {current_value}        ")  # Display current value
                stdscr.refresh()

            menu_items[option_idx] = f"Max Workers: {self.config['max_workers']}"  # Update menu item
            return self.config["max_workers"] != original_value  # Return if value changed
                
        # Fade style selection
        elif option_idx in [3, 4, 5]:
            fade_options = list(self.FADE_STYLES.keys())  # Get available fade styles
            option_names = {
                3: "title_fade",
                4: "success_fade",
                5: "error_fade"
            }
            option_name = option_names[option_idx]
            default_values = {
                "title_fade": "firered",
                "success_fade": "brazilgreen",
                "error_fade": "pinkred"
            }

            current_value = self.config.get(option_name, default_values[option_name])  # Get current fade style
            original_value = current_value
            current_idx = fade_options.index(current_value) if current_value in fade_options else 0  # Get index of current fade style

            stdscr.clear()
            stdscr.addstr(prompt_y, prompt_x, f"Select {option_name.replace('_', ' ').title()}: ")

            visible_options = 10  # Number of visible options
            start_idx = max(0, current_idx - visible_options // 2)  # Start index for visible options
            end_idx = min(len(fade_options), start_idx + visible_options)  # End index for visible options

            for i, idx in enumerate(range(start_idx, end_idx)):
                if idx == current_idx:
                    stdscr.addstr(prompt_y + 2 + i, prompt_x + 5, fade_options[idx], cs.color_pair(1) | cs.A_REVERSE)  # Highlight selected fade style
                    footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"
                    stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))
                else:
                    stdscr.addstr(prompt_y + 2 + i, prompt_x + 5, fade_options[idx])  # Display fade style option

            stdscr.refresh()

            while True:
                key = stdscr.getch()  # Get user input
                if key == cs.KEY_UP and current_idx > 0: current_idx -= 1
                elif key == cs.KEY_DOWN and current_idx < len(fade_options) - 1: current_idx += 1
                elif key == cs.KEY_ENTER or key in [10, 13]: 
                    self.config[option_name] = fade_options[current_idx]  # Update selected fade style
                    break
                elif key == 27: break
                elif key == ord('b'): return False
                elif key == ord('s'):
                    self.config[option_name] = fade_options[current_idx]  # Update selected fade style
                    self._save_config()  # Save configuration
                    stdscr.addstr(h - 3, (w - len("Configuration Saved!")) // 2, "Configuration Saved!", cs.color_pair(1))
                    stdscr.refresh()
                    time.sleep(1)
                    self.restart_application()  # Restart application

                if current_idx < start_idx:
                    start_idx = current_idx  # Update start index
                    end_idx = min(len(fade_options), start_idx + visible_options)  # Update end index
                elif current_idx >= end_idx:
                    end_idx = current_idx + 1  # Update end index
                    start_idx = max(0, end_idx - visible_options)  # Update start index

                stdscr.clear()
                stdscr.addstr(prompt_y, prompt_x, f"Select {option_name.replace('_', ' ').title()}: ")
                for i, idx in enumerate(range(start_idx, end_idx)):
                    if idx == current_idx:
                        footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"
                        stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))
                        stdscr.addstr(prompt_y + 2 + i, prompt_x + 5, fade_options[idx], cs.color_pair(1) | cs.A_REVERSE)  # Highlight selected fade style
                    else:
                        stdscr.addstr(prompt_y + 2 + i, prompt_x + 5, fade_options[idx])  # Display fade style option
                stdscr.refresh()

            menu_items[option_idx] = f"{option_name.replace('_', ' ').title()}: {self.config[option_name]}"  # Update menu item
            return self.config[option_name] != original_value  # Return if value changed

        # Font selection
        elif option_idx in [6, 7]:
            font_options = self.FONTS  # Get available fonts
            option_names = {
                6: "title_font",
                7: "message_font"
            }
            default_values = {
                "title_font": "big_money-ne",
                "message_font": "ansi_regular"
            }
            option_name = option_names[option_idx]
            current_value = self.config.get(option_name, default_values[option_name])  # Get current font
            original_value = current_value
            current_idx = font_options.index(current_value) if current_value in font_options else 0  # Get index of current font

            stdscr.clear()
            stdscr.addstr(prompt_y, prompt_x, f"Select {option_name.replace('_', ' ').title()}: ")

            visible_options = 10  # Number of visible options
            start_idx = max(0, current_idx - visible_options // 2)  # Start index for visible options
            end_idx = min(len(font_options), start_idx + visible_options)  # End index for visible options

            for i, idx in enumerate(range(start_idx, end_idx)):
                if idx == current_idx:
                    stdscr.addstr(prompt_y + 2 + i, prompt_x + 5, font_options[idx], cs.color_pair(1) | cs.A_REVERSE)  # Highlight selected font
                    footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"
                    stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))
                else:
                    stdscr.addstr(prompt_y + 2 + i, prompt_x + 5, font_options[idx])  # Display font option

            stdscr.refresh()

            while True:
                key = stdscr.getch()  # Get user input
                if key == cs.KEY_UP and current_idx > 0: current_idx -= 1
                elif key == cs.KEY_DOWN and current_idx < len(font_options) - 1: current_idx += 1
                elif key == cs.KEY_ENTER or key in [10, 13]:
                    self.config[option_name] = font_options[current_idx]  # Update selected font
                    break
                elif key == 27: break
                elif key == ord('b'): return False
                elif key == ord('s'):
                    self.config[option_name] = font_options[current_idx]  # Update selected font
                    self._save_config()  # Save configuration
                    stdscr.addstr(h - 3, (w - len("Configuration Saved!")) // 2, "Configuration Saved!", cs.color_pair(1))
                    stdscr.refresh()
                    time.sleep(1)
                    self.restart_application()  # Restart application

                if current_idx < start_idx:
                    start_idx = current_idx  # Update start index
                    end_idx = min(len(font_options), start_idx + visible_options)  # Update end index
                elif current_idx >= end_idx:
                    end_idx = current_idx + 1  # Update end index
                    start_idx = max(0, end_idx - visible_options)  # Update start index

                stdscr.clear()
                stdscr.addstr(prompt_y, prompt_x, f"Select {option_name.replace('_', ' ').title()}: ")
                for i, idx in enumerate(range(start_idx, end_idx)):
                    if idx == current_idx:
                        stdscr.addstr(prompt_y + 2 + i, prompt_x + 5, font_options[idx], cs.color_pair(1) | cs.A_REVERSE)  # Highlight selected font
                        footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"
                        stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))
                    else:
                        stdscr.addstr(prompt_y + 2 + i, prompt_x + 5, font_options[idx])  # Display font option
                stdscr.refresh()

            menu_items[option_idx] = f"{option_name.replace('_', ' ', 1).title()}: {self.config[option_name]}"  # Update menu item
            return self.config[option_name] != original_value  # Return if value changed
        
        # Detect oversized files toggle
        elif option_idx == 8:
            original_value = self.config.get("detect_oversized", False)
            self.config["detect_oversized"] = not original_value  # Toggle detection of oversized files
            menu_items[option_idx] = f"Detect Oversized Files: {self.config['detect_oversized']}"  # Update menu item
            return True  # Indicate change
        
        # Auto-open oversized files toggle
        elif option_idx == 9:
            original_value = self.config.get("auto_open_oversized", False)
            self.config["auto_open_oversized"] = not original_value  # Toggle auto-opening of oversized files
            menu_items[option_idx] = f"Auto-Open Oversized Files: {self.config['auto_open_oversized']} [EXPERIMENTAL]"  # Update menu item
            return True  # Indicate change

        # Oversized threshold selection
        elif option_idx == 10:
            size_options = list(self.PAPER_SIZES.keys())  # Get available paper sizes
            current_value = self.config.get("oversized_threshold", "A3")  # Get current oversized threshold
            original_value = current_value
            current_idx = size_options.index(current_value) if current_value in size_options else 0  # Get index of current threshold

            stdscr.clear()
            title = "Select Oversized Threshold Size:"
            stdscr.addstr(prompt_y, prompt_x, title)  # Display title

            for idx, size in enumerate(size_options):
                size_info = f"{size} ({self.PAPER_SIZES[size][0]}x{self.PAPER_SIZES[size][1]} pts)"  # Size info
                if idx == current_idx:
                    stdscr.addstr(prompt_y + 2 + idx, prompt_x + 5, size_info, cs.color_pair(1) | cs.A_REVERSE)  # Highlight selected size
                else:
                    stdscr.addstr(prompt_y + 2 + idx, prompt_x + 5, size_info)  # Display size option
                    
            footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"
            stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))  # Display footer
            stdscr.refresh()

            while True:
                key = stdscr.getch()  # Get user input
                if key == cs.KEY_UP and current_idx > 0: current_idx -= 1
                elif key == cs.KEY_DOWN and current_idx < len(size_options) - 1: current_idx += 1
                elif key == cs.KEY_ENTER or key in [10, 13]:
                    self.config["oversized_threshold"] = size_options[current_idx]  # Update selected threshold
                    break
                elif key == 27: break
                elif key == ord('b'): return False
                elif key == ord('s'):
                    self.config["oversized_threshold"] = size_options[current_idx]  # Update selected threshold
                    self._save_config()  # Save configuration
                    stdscr.addstr(h - 3, (w - len("Configuration Saved!")) // 2, "Configuration Saved!", cs.color_pair(1))
                    stdscr.refresh()
                    time.sleep(1)
                    self.restart_application()  # Restart application

                for idx, size in enumerate(size_options):
                    size_info = f"{size} ({self.PAPER_SIZES[size][0]}x{self.PAPER_SIZES[size][1]} pts)"  # Size info
                    if idx == current_idx:
                        stdscr.addstr(prompt_y + 2 + idx, prompt_x + 5, size_info, cs.color_pair(1) | cs.A_REVERSE)  # Highlight selected size
                    else:
                        stdscr.addstr(prompt_y + 2 + idx, prompt_x + 5, size_info)  # Display size option
                stdscr.refresh()

            menu_items[option_idx] = f"Oversized Threshold: {self.config['oversized_threshold']}"  # Update menu item
            return self.config["oversized_threshold"] != original_value  # Return if value changed
            
        # Size tolerance adjustment
        elif option_idx == 11:
            min_tolerance = 50   # Minimum tolerance value
            max_tolerance = 500  # Maximum tolerance value
            current_value = self.config.get("size_tolerance", 300)  # Get current tolerance
            original_value = current_value

            stdscr.clear()
            stdscr.addstr(prompt_y, prompt_x, f"Size Tolerance ({min_tolerance}-{max_tolerance}): {current_value}")
            stdscr.addstr(prompt_y + 2, prompt_x, "Use ← and → to adjust, Enter to confirm")
            stdscr.addstr(prompt_y + 3, prompt_x, "Lower values = stricter matching, higher values = more lenient")
            footer = "Navigate: ↑/↓ | Select: Enter | Back: B | Save and Restart: S"
            stdscr.addstr(h - 2, (w - len(footer)) // 2, footer, cs.color_pair(2))
            stdscr.refresh()

            while True:
                key = stdscr.getch()  # Get user input
                
                # Smaller adjustments with arrow keys
                if key == cs.KEY_LEFT and current_value > min_tolerance: 
                    current_value = max(min_tolerance, current_value - 10)
                elif key == cs.KEY_RIGHT and current_value < max_tolerance: 
                    current_value = min(max_tolerance, current_value + 10)
                # Larger adjustments with page up/down
                elif key == cs.KEY_PPAGE and current_value > min_tolerance:  # Page Up
                    current_value = max(min_tolerance, current_value - 50)
                elif key == cs.KEY_NPAGE and current_value < max_tolerance:  # Page Down
                    current_value = min(max_tolerance, current_value + 50)
                elif key == cs.KEY_ENTER or key in [10, 13]:
                    self.config["size_tolerance"] = current_value  # Update tolerance
                    break
                elif key == 27: break
                elif key == ord('b'): return False
                elif key == ord('s'):
                    self.config["size_tolerance"] = current_value  # Update tolerance
                    self._save_config()  # Save configuration
                    stdscr.addstr(h - 3, (w - len("Configuration Saved!")) // 2, "Configuration Saved!", cs.color_pair(1))
                    stdscr.refresh()
                    time.sleep(1)
                    self.restart_application()  # Restart application

                stdscr.addstr(prompt_y, prompt_x, f"Size Tolerance ({min_tolerance}-{max_tolerance}): {current_value}        ")
                stdscr.refresh()

            menu_items[option_idx] = f"Size Tolerance: {self.config['size_tolerance']} pts"  # Update menu item
            return self.config["size_tolerance"] != original_value  # Return if value changed
        
        # PDF engine toggle
        elif option_idx == 12:
            current_value = self.config.get("pdf_engine", "fitz")  # Get current PDF engine
            original_value = current_value

            if current_value == "fitz": 
                self.config["pdf_engine"] = "PyPDF2"  # Switch to PyPDF2
            else: 
                self.config["pdf_engine"] = "fitz"  # Switch to fitz

            menu_items[option_idx] = f"PDF Engine: {self.config['pdf_engine']}"  # Update menu item
            return self.config["pdf_engine"] != original_value  # Return if value changed
        
        return False  # No changes made
        
    def restart_application(self):
        """Restarts the application."""
        print(self.colored_text("Restarting application... Please wait...", "red"))
        keyboard.unhook_all()  # Unhook all keyboard listeners
        if self.root:
            try:
                self.root.destroy()  # Destroy the Tkinter root window
            except Exception:
                pass

        python = sys.executable  # Get the Python executable path
        try:
            os.execl(python, python, *sys.argv)  # Restart the application
        except:
            print(sys.executable)  # Print executable path
            print(*sys.argv)  # Print command line arguments

    def get_closest_paper_size(self, size, tolerance=None):
        """Finds the closest standard paper size to the given dimensions.
        
        Args:
            size: Tuple containing width and height of the page
            tolerance: Optional override for the configuration-based tolerance
            
        Returns:
            Tuple containing the name of the closest paper size and the difference
        """
        best_match = "Unknown"
        smallest_difference = float("inf")
        
        # Use the provided tolerance or get from config
        if tolerance is None:
            tolerance = self.config.get("size_tolerance", 300)

        for sizes, (w, h) in self.PAPER_SIZES.items():
            # Calculate Euclidean distance (square root of sum of squared differences)
            diff = math.sqrt((size[0][0] - w) ** 2 + (size[0][1] - h) ** 2)
            flipped_diff = math.sqrt((size[0][0] - h) ** 2 + (size[0][1] - w) ** 2)  # Account for rotation

            min_diff = min(diff, flipped_diff)

            if min_diff < smallest_difference:
                smallest_difference = min_diff
                best_match = sizes

        if smallest_difference <= tolerance:
            return best_match, smallest_difference
        return "Unknown", smallest_difference

    def run(self) -> None:
        """Main method to run the application."""
        self._setup_keyboard_shortcuts()
        self._display_welcome_screen()
        
        while not self.exit_flag:
            try:
                self._display_main_menu()
                
                if not self._wait_for_space_key():
                    continue
                    
                folder_path = self._get_folder_path()
                if not folder_path:
                    continue
                    
                self._process_folder(folder_path)
                    
            except Exception as e:
                self._handle_unexpected_error(e)
        
        self.exit_program()  # Exit the program

    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for the application."""
        keyboard.add_hotkey('f2', self.show_menu)  # Add hotkey for menu
        keyboard.add_hotkey('esc', self.exit_program)  # Add hotkey for exit
        keyboard.add_hotkey('f1', self.restart_application)
        #keyboard.add_hotkey('f3', self.show_results) # Add hotkey for oversize results menu

    def _display_welcome_screen(self):
        
        os.system('cls')

        """Display the welcome screen with title and introduction."""
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        print(self.FADE_STYLES[self.config.get("title_fade", "firered")](
            fg.z("pagify", font=self.config.get("title_font", ""))))
        
        lang = self.config.get("language", "english")
        texts = self.LANGUAGE_TEXTS.get(lang, self.LANGUAGE_TEXTS["english"])
        print(self.colored_text(texts["info"], "white"))
        print("\n\n\n")
        print(self.colored_text(texts["intro"], "white"))

    def _display_main_menu(self):
        """Display the main menu options."""
        lang = self.config.get("language", "english")
        texts = self.LANGUAGE_TEXTS.get(lang, self.LANGUAGE_TEXTS["english"])
        
        print("\n")
        print(self.colored_text(texts["press_space"], "green"))
        print(self.colored_text(texts["press_f1"], "blue"))
        print(self.colored_text(texts["press_f2"], "cyan"))
        print(self.colored_text(texts["exit_any_time"], "yellow"))

    def _wait_for_space_key(self):
        """Wait for the user to press the space key."""
        keyboard.wait('space')
        if self.menu_active:
            return False
        return True

    def _get_folder_path(self):
        """Get the folder path from the user."""
        lang = self.config.get("language", "english")
        texts = self.LANGUAGE_TEXTS.get(lang, self.LANGUAGE_TEXTS["english"])
        
        print(self.colored_text(texts["select"], "white"))
        folder_path = self.select_folder()
        
        if not folder_path or self.exit_flag:
            print(self.colored_text(texts["no_folder"], "red"))
            return None
            
        print("\n")
        print(self.colored_text(f"{texts['selected_folder']}{folder_path}", "white"))
        return folder_path

    def _process_folder(self, folder_path):

        os.system('cls')

        """Process the selected folder and display results."""
        lang = self.config.get("language", "english")
        texts = self.LANGUAGE_TEXTS.get(lang, self.LANGUAGE_TEXTS["english"])
        
        try:
            total_pages, oversized_files_info, process_time = self.get_total_pdf_pages(folder_path)
        except Exception as e:
            self._handle_pdf_processing_error(e)
            return
            
        print(self.colored_text(f"{texts['selected_folder']}{folder_path}", "white"))
        print(self.colored_text(f"{texts['process_time']} {process_time:.3f} seconds", "magenta"))
        print("\n")
        
        # Store data for potential later use
        self.oversize_files_data = oversized_files_info
        
        if oversized_files_info:
            self._display_oversized_files_results(total_pages, oversized_files_info, texts)
        else:
            self._display_no_oversized_files_results(total_pages, texts)

    def _handle_pdf_processing_error(self, error):
        """Handle errors that occur during PDF processing."""
        lang = self.config.get("language", "english")
        texts = self.LANGUAGE_TEXTS.get(lang, self.LANGUAGE_TEXTS["english"])
        
        if not self.config.get("simple_display", False):
            print("\n")
            print(self.FADE_STYLES[self.config.get("error_fade", "pinkred")](
                fg.z("NO PDFS", font=self.config.get("message_font", "ansi_regular"))))
        else:
            print(self.colored_text(f"{texts['unexpected_error']}{error}", "red"))

    def _display_oversized_files_results(self, total_pages, oversized_files_info, texts):
        """Display results when oversized files are found."""
        if not self.config.get("simple_display", False):
            self._display_detailed_oversized_results(total_pages, oversized_files_info, texts)
        else:
            self._display_simple_oversized_results(total_pages, oversized_files_info, texts)

    def _display_detailed_oversized_results(self, total_pages, oversized_files_info, texts):
        """Display detailed results for oversized files in fancy mode."""
        print("\n")
        oversize_qty = []
        files_not_a3 = 0
        print(self.colored_text(f"Dokumente mit Übergrößen: \n", "red"))
        
        for filepath, size in oversized_files_info:
            ps_link = f"file:///{str(filepath).replace('\\', '/')}"
            file = str(filepath).split("\\")[-1]
            page_dim = []
            
            for wi, he, page in size:
                dimension, diff = self.get_closest_paper_size(size)
                
                if dimension != "A3":
                    oversize_qty.append(dimension)
                    page_dim.append(f"{page + 1}")
                    
            if page_dim:
                files_not_a3 += 1
                dim_str = ", ".join(page_dim)
                print(self.colored_text(f" - \033]8;;{ps_link}\033\\{file}\033]8;;\033\\", "red"))
                print(f"\t\tSeitenzahlen: {dim_str}\n")
                
                if self.config.get("auto_open_oversized", True):
                    subprocess.Popen(["explorer", "/select,", filepath])
        
        print("\n")
        print(self.colored_text(f"{texts['total_pages']} {total_pages}", "green"))
        print(self.colored_text(f"{texts['oversize_result']} {self.config.get('oversized_threshold', 'A2')}): {files_not_a3}", "green"))
        print(self.colored_text(f"{texts['oversize_qty']} {len(oversize_qty)}", "green"))
        print("\n")
        
        if total_pages > 0:
            print(self.FADE_STYLES[self.config.get("success_fade", "brazilgreen")](
                fg.z(f"{total_pages} TOTAL", font=self.config.get("message_font", "ansi_regular"))))
        else:
            print(self.colored_text(texts["error_occurred"], "red"))
        
        print(self.FADE_STYLES[self.config.get("success_fade", "waterblue")](
            fg.z(f"/ {len(oversize_qty)} BIG", font=self.config.get("message_font", "ansi_regular"))))

    def _display_simple_oversized_results(self, total_pages, oversized_files_info, texts):
        """Display simple results for oversized files."""
        print(self.colored_text(f"{len(oversized_files_info)} {texts['oversize_result']} {self.config.get('oversized_threshold', 'A2')}):", "green"))
        for filepath, size in oversized_files_info:
            file = filepath.split("/")[-1]
            print(self.colored_text(f" - {file}", "green"))
        
        print(self.colored_text(f"{texts['total_pages']} {total_pages}", "green"))

    def _display_no_oversized_files_results(self, total_pages, texts):
        """Display results when no oversized files are found."""
        if total_pages > 0:
            if not self.config.get("simple_display", False):
                print(self.FADE_STYLES[self.config.get("success_fade", "brazilgreen")](
                    fg.z(f"{total_pages} TOTAL", font=self.config.get("message_font", "ansi_regular"))))
            else:
                print(self.colored_text(f"{texts['total_pages']} {total_pages}", "green"))
        else:
            print(self.colored_text(texts["error_occurred"], "red"))
        
        print(self.FADE_STYLES[self.config.get("error_fade", "")](
            fg.z("NO BIG", font=self.config.get("message_font", "ansi_regular"))))
        
        print(self.colored_text(f"{texts['total_pages']} {total_pages}", "green"))
        print(self.colored_text(texts["no_oversize"], "red"))

    def _handle_unexpected_error(self, error):
        """Handle unexpected errors that occur during execution."""
        lang = self.config.get("language", "english")
        texts = self.LANGUAGE_TEXTS.get(lang, self.LANGUAGE_TEXTS["english"])
        
        if not self.config.get("simple_display", False):
            print("\n")
            print(self.FADE_STYLES[self.config.get("error_fade", "pinkred")](
                fg.z("Error", font=self.config.get("message_font", "ansi_regular"))))
        print(self.colored_text(f"{texts['unexpected_error']}{error}", "red"))

    def exit_program(self) -> None:
        """Exits the application gracefully."""
        self.exit_flag = True  # Set exit flag
        if not self.config.get("simple_display", False):
            print(self.FADE_STYLES[self.config.get("title_fade", "firered")](
                fg.z("see ya!", font="roman")))  # Print goodbye message
        else:
            print(self.colored_text("Goodbye!", "cyan"))  # Print goodbye message in simple display
        time.sleep(1.5)  # Wait before exiting
        keyboard.unhook_all()  # Unhook all keyboard listeners
        if self.root:
            try:
                self.root.destroy()  # Destroy the Tkinter root window
            except Exception as e:
                print(f"Error during Tkinter root destruction: {e}")  # Print error message
        os._exit(0)  # Exit the program

    def _load_config(self) -> dict:
        """Loads the configuration from a file or returns default settings.

        Returns:
            dict: The loaded configuration settings.
        """
        return self.config_manager.load_config()  # Use ConfigManager to load config

    def _save_config(self) -> None:
        """Saves the current configuration to a file."""
        self.config_manager.save_config(self.config)  # Use ConfigManager to save config

    def _print_error(self, message: str) -> None:
        """Prints an error message in a formatted way.

        Args:
            message (str): The error message to print.
        """
        if not self.config.get("simple_display", False):
            print(self.FADE_STYLES[self.config.get("error_fade", "pinkred")](
                fg.z(message, font=self.config.get("message_font", "ansi_regular"))))
        else:
            print(self.colored_text(message, "red"))  # Print error message in simple display

    def _print_success(self, message: str) -> None:
        """Prints a success message in a formatted way.

        Args:
            message (str): The success message to print.
        """
        if not self.config.get("simple_display", False):
            print(self.FADE_STYLES[self.config.get("success_fade", "brazilgreen")](
                fg.z(message, font=self.config.get("message_font", "ansi_regular"))))
        else:
            print(self.colored_text(message, "green"))  # Print success message in simple display

if __name__ == "__main__":
    PDFPageCounter().run()  # Run the application