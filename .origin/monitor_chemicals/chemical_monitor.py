#!/usr/bin/env python3
import curses
import time
import math
from curses import textpad

class FilmChemicalTracker:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.max_y, self.max_x = stdscr.getmaxyx()
        curses.curs_set(0)  # Hide cursor
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)    # Green for good levels
        curses.init_pair(2, curses.COLOR_YELLOW, -1)   # Yellow for moderate levels
        curses.init_pair(3, curses.COLOR_RED, -1)      # Red for low levels
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)   # For title
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)  # For buttons
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)    # For alert
        
        # Initialize film data
        self.film_16mm_area = 0.488  # m²
        self.film_35mm_area = 1.068  # m²
        self.max_area = 10.0  # m² per 1L of chemicals
        
        # Initial state
        self.used_area = 0.0
        self.used_16mm_rolls = 0
        self.used_35mm_rolls = 0
        self.selected_option = 0  # 0 for 16mm, 1 for 35mm
        
        # Alert state
        self.show_alert = False
        
    def reset_chemicals(self):
        self.used_area = 0.0
        self.used_16mm_rolls = 0
        self.used_35mm_rolls = 0
        
    def calculate_remaining_capacity(self):
        return max(0, self.max_area - self.used_area)
    
    def get_chemical_level_percent(self):
        return 100 * (1 - self.used_area / self.max_area)
    
    def get_chemical_color(self):
        # Inverted color scheme: green when fresh, red when depleted
        percent = self.get_chemical_level_percent()
        if percent > 20:
            return curses.color_pair(1)  # Green when mostly fresh
        elif percent > 10:
            return curses.color_pair(2)  # Yellow when moderately used
        else:
            return curses.color_pair(3)  # Red when heavily used
            
    def would_exceed_capacity(self, film_type):
        next_area = self.film_16mm_area if film_type == 0 else self.film_35mm_area
        return (self.used_area + next_area) > self.max_area
            
    def add_film_roll(self, film_type):
        if film_type == 0:  # 16mm
            self.used_area += self.film_16mm_area
            self.used_16mm_rolls += 1
        else:  # 35mm
            self.used_area += self.film_35mm_area
            self.used_35mm_rolls += 1
            
        # Cap at maximum
        self.used_area = min(self.used_area, self.max_area)
    
    def draw_title(self):
        title = "FILM DEVELOPMENT CHEMICAL TRACKER"
        x = max(0, (self.max_x - len(title)) // 2)
        self.stdscr.addstr(1, x, title, curses.color_pair(4) | curses.A_BOLD)
        
    def draw_gauge(self):
        gauge_width = min(self.max_x - 8, 60)
        gauge_height = 3
        start_x = (self.max_x - gauge_width) // 2
        start_y = 5
        
        # Draw gauge title with chemical status
        remaining_pct = self.get_chemical_level_percent()
        status = "FRESH" if remaining_pct > 20 else "LOW" if remaining_pct > 10 else "CRITICAL"
        title = f"Chemical Capacity - {status}"
        self.stdscr.addstr(start_y - 1, start_x, title, self.get_chemical_color() | curses.A_BOLD)
        
        # Draw gauge border
        textpad.rectangle(self.stdscr, start_y, start_x, start_y + gauge_height, start_x + gauge_width)
        
        # Calculate remaining portion (unused area)
        remaining_width = int(gauge_width * (self.calculate_remaining_capacity() / self.max_area))
        
        # Fill the gauge to represent remaining chemicals (from right to left)
        for y in range(start_y + 1, start_y + gauge_height):
            # First fill the entire bar with "empty" indicators
            for x in range(start_x + 1, start_x + gauge_width):
                self.stdscr.addstr(y, x, "░")
                
            # Then fill with "remaining" indicators, from left to right
            for x in range(start_x + 1, start_x + remaining_width + 1):
                self.stdscr.addstr(y, x, "█", self.get_chemical_color())
        
        # Add visual markers for critical thresholds
        y_marker = start_y + gauge_height + 1
        x_10pct = start_x + int(gauge_width * 0.1)  # 10% remaining
        x_20pct = start_x + int(gauge_width * 0.2)  # 20% remaining
        self.stdscr.addstr(y_marker, x_20pct, "▲", curses.color_pair(2))  # Yellow threshold
        self.stdscr.addstr(y_marker, x_10pct, "▲", curses.color_pair(3))  # Red threshold
                
        # Add percentage text
        percent_text = f"{remaining_pct:.1f}% remaining"
        x = start_x + (gauge_width - len(percent_text)) // 2
        self.stdscr.addstr(start_y + gauge_height + 2, x, percent_text, self.get_chemical_color())
        
        # Add absolute values with breakdown
        abs_text = f"Used: {self.used_area:.3f} m² / Max: {self.max_area:.3f} m²"
        x = start_x + (gauge_width - len(abs_text)) // 2
        self.stdscr.addstr(start_y + gauge_height + 3, x, abs_text)
        
        # Show detailed roll counts and consumption
        roll_text = f"Used rolls: {self.used_16mm_rolls} x 16mm ({self.used_16mm_rolls * self.film_16mm_area:.3f} m²), " + \
                    f"{self.used_35mm_rolls} x 35mm ({self.used_35mm_rolls * self.film_35mm_area:.3f} m²)"
        x = max(1, (self.max_x - len(roll_text)) // 2)
        self.stdscr.addstr(start_y + gauge_height + 4, x, roll_text)
        
        # Show percentage consumption breakdown
        if self.used_area > 0:
            pct_16mm = (self.used_16mm_rolls * self.film_16mm_area / self.used_area) * 100 if self.used_16mm_rolls > 0 else 0
            pct_35mm = (self.used_35mm_rolls * self.film_35mm_area / self.used_area) * 100 if self.used_35mm_rolls > 0 else 0
            breakdown = f"Consumption: 16mm ({pct_16mm:.1f}%), 35mm ({pct_35mm:.1f}%)"
            x = max(1, (self.max_x - len(breakdown)) // 2)
            self.stdscr.addstr(start_y + gauge_height + 5, x, breakdown)
    
    def draw_options(self):
        start_y = 15
        
        # Display detailed roll information
        for i, (film_type, area) in enumerate([("16mm Film Roll", self.film_16mm_area), 
                                               ("35mm Film Roll", self.film_35mm_area)]):
            # Calculate consumption percentage
            consumption_pct = (area / self.max_area) * 100
            remaining_rolls = math.floor(self.calculate_remaining_capacity() / area)
            
            # Format the detailed information
            option = f"{film_type} - {area:.3f} m² ({consumption_pct:.1f}% capacity per roll)"
            x = max(1, (self.max_x - len(option)) // 2)
            
            # Highlight selected option
            style = curses.color_pair(5) if i == self.selected_option else curses.A_NORMAL
            self.stdscr.addstr(start_y + i*3, x, option, style)
            
            # Show capacity information
            capacity_info = f"Can process {remaining_rolls} more rolls with current chemicals"
            x_info = max(1, (self.max_x - len(capacity_info)) // 2)
            self.stdscr.addstr(start_y + i*3 + 1, x_info, capacity_info)
            
            # Add warning if this option would exceed capacity
            if self.would_exceed_capacity(i):
                warning = "⚠ Will exceed capacity! Change chemicals before processing!"
                warn_x = max(1, (self.max_x - len(warning)) // 2)
                self.stdscr.addstr(start_y + i*3 + 2, warn_x, warning, curses.color_pair(3))
    
    def draw_instructions(self):
        instructions = [
            "↑/↓: Select film type",
            "Enter: Add selected film roll",
            "r: Reset chemical bath",
            "q: Quit"
        ]
        
        start_y = self.max_y - len(instructions) - 2
        start_x = 5
        
        for i, instruction in enumerate(instructions):
            self.stdscr.addstr(start_y + i, start_x, instruction)
    
    def draw_alert(self):
        # Draw a popup in the center of the screen
        height, width = 7, 40
        start_y = (self.max_y - height) // 2
        start_x = (self.max_x - width) // 2
        
        # Create the popup window
        popup = curses.newwin(height, width, start_y, start_x)
        popup.bkgd(' ', curses.color_pair(6))
        popup.box()
        
        # Add text to the popup
        popup.addstr(1, 2, "WARNING", curses.A_BOLD)
        popup.addstr(2, 2, "Chemical capacity exceeded!")
        popup.addstr(3, 2, "Please change chemicals now.")
        popup.addstr(5, 2, "Press ENTER to confirm", curses.A_BOLD)
        
        popup.refresh()
        
        # Wait for user to press Enter
        while True:
            key = self.stdscr.getch()
            if key == curses.KEY_ENTER or key == 10 or key == 13:
                break
        
        self.reset_chemicals()
        self.show_alert = False
    
    def run(self):
        while True:
            self.stdscr.clear()
            
            # Draw UI components
            self.draw_title()
            self.draw_gauge()
            self.draw_options()
            self.draw_instructions()
            
            # Refresh the screen
            self.stdscr.refresh()
            
            # Show alert if needed
            if self.show_alert:
                self.draw_alert()
                continue
            
            # Get user input
            key = self.stdscr.getch()
            
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset_chemicals()
            elif key == curses.KEY_UP:
                self.selected_option = max(0, self.selected_option - 1)
            elif key == curses.KEY_DOWN:
                self.selected_option = min(1, self.selected_option + 1)
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                # Check if adding this roll would exceed capacity
                if self.would_exceed_capacity(self.selected_option):
                    self.show_alert = True
                else:
                    self.add_film_roll(self.selected_option)

def show_splash_screen(stdscr):
    """Show a splash screen when starting the application"""
    max_y, max_x = stdscr.getmaxyx()
    
    # Create a splash window in the center of the screen
    height, width = 12, 60
    start_y = (max_y - height) // 2
    start_x = (max_x - width) // 2
    
    splash = curses.newwin(height, width, start_y, start_x)
    splash.box()
    
    # Add title and version
    title = "FILM DEVELOPMENT CHEMICAL TRACKER"
    splash.addstr(2, (width - len(title)) // 2, title, curses.A_BOLD)
    version = "v1.0.0"
    splash.addstr(3, (width - len(version)) // 2, version)
    
    # Add formula information
    formula = "(0.488×n16 + 1.068×n35)/10"
    splash.addstr(5, (width - len("Chemical calculation formula:")) // 2, "Chemical calculation formula:")
    splash.addstr(6, (width - len(formula)) // 2, formula, curses.A_BOLD)
    
    # Add loading message
    msg = "Press any key to start..."
    splash.addstr(9, (width - len(msg)) // 2, msg)
    
    splash.refresh()
    stdscr.getch()  # Wait for keypress

def main(stdscr):
    # Initialize curses
    curses.start_color()
    curses.use_default_colors()
    
    # Show splash screen
    show_splash_screen(stdscr)
    
    # Create and run the tracker
    tracker = FilmChemicalTracker(stdscr)
    tracker.run()

if __name__ == "__main__":
    curses.wrapper(main)