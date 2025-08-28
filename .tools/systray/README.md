# System Tray Example Application

A comprehensive Python example demonstrating how to create a Windows system tray application with a rich menu interface and various functionality.

## Features

- **System Tray Integration**: Runs in the Windows system tray with a custom icon
- **Rich Menu System**: Comprehensive right-click menu with multiple submenus
- **Settings Management**: Persistent settings with JSON storage
- **System Information**: Display system details, network status, and process monitoring
- **GUI Windows**: Main window and preferences dialog using tkinter
- **Notifications**: System notifications with toggle functionality
- **Logging**: Application logging capabilities
- **Auto-installation**: Automatically installs required dependencies

## Menu Structure

The system tray icon provides the following menu structure:

```
Status: Active
─────────────────
Show Main Window
Open Log File
Check for Updates
─────────────────
Settings
├── Notifications ✓
├── Auto Start
├── ─────────────
├── Preferences...
└── Reset Settings
Tools
├── System Information
├── Network Status
├── Process Monitor
├── ─────────────
├── Open Task Manager
└── Open Control Panel
Help
├── Documentation
├── About
├── Report Bug
├── ─────────────
└── Check for Updates
─────────────────
Exit
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or let the script auto-install them:
   ```bash
   python systray_example.py
   ```

2. **Run the Application**:
   ```bash
   python systray_example.py
   ```

## Usage

1. **Start the Application**: Run the script and look for the system tray icon
2. **Access Menu**: Right-click the system tray icon to see the menu
3. **Main Window**: Click "Show Main Window" to open the main application interface
4. **Settings**: Use the Settings submenu to configure the application
5. **Tools**: Access system information and utilities through the Tools submenu
6. **Exit**: Use the Exit option to properly close the application

## Files

- `systray_example.py` - Main application script
- `app-logo.ico` - Application icon (will create default if missing)
- `requirements.txt` - Python dependencies
- `settings.json` - Application settings (created automatically)
- `app.log` - Application log file (created automatically)

## Customization

### Icon
- Replace `app-logo.ico` with your own icon file
- The script will create a default blue icon if no .ico file is found

### Menu Items
- Modify the `create_icon()` method to add/remove menu items
- Add new functionality by creating new methods and menu items

### Settings
- Extend the settings system by adding new keys to the `default_settings` dictionary
- Settings are automatically saved to `settings.json`

## Dependencies

- **pystray**: System tray functionality
- **pillow**: Image processing for icons
- **psutil**: System and process monitoring (optional)
- **tkinter**: GUI windows (built-in with Python)

## Troubleshooting

1. **Icon not appearing**: Check if the .ico file exists and is valid
2. **Menu not working**: Ensure pystray is properly installed
3. **Process monitor not working**: Install psutil with `pip install psutil`
4. **Permission errors**: Run as administrator if needed for system tools

## Development

The application is structured as a single class `SystemTrayApp` with methods for each menu item. To add new functionality:

1. Create a new method in the class
2. Add a menu item in the `create_icon()` method
3. Connect the menu item to your new method

## License

This is an example application. Feel free to modify and use as needed.
