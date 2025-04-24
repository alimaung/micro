# Microfilm Remote Execution System

This system allows PC2 (controller) to remotely trigger the SMA scanning process on PC1.

## Setup Instructions

### On PC1 (192.168.1.96) - Where the scanner/SMA is installed

1. Run the setup script:
   ```
   python remote_setup.py
   ```
   Select option `1` when prompted

2. If prompted about firewall settings, run the command in an administrator command prompt:
   ```
   netsh advfirewall firewall add rule name="Microfilm Remote Server" dir=in action=allow protocol=TCP localport=5000
   ```

3. Start the server:
   ```
   python remote_server.py
   ```
   Keep this window open while you want to accept remote commands.

### On PC2 (192.168.1.111) - The controller PC

1. Copy the `remote_client.py` file to PC2
2. Run the setup script:
   ```
   python remote_setup.py
   ```
   Select option `2` when prompted

## Usage

### From PC2 (Controller)

To start processing a folder:
```
python remote_client.py start --folder "F:\path\to\folder" --template 16
```

Additional options:
- `--template` (optional): Use "16" or "35" (default is "16")
- `--filmnumber` (optional): Specify a film number
- `--recovery` (optional): Add this flag to enable recovery mode

To check status of running jobs:
```
python remote_client.py status
```

## Security Notes

- The system uses a simple API key for authentication (`microfilm_secure_key`)
- Communication is restricted to your local network
- It's recommended to change the API key in both `remote_server.py` and `remote_client.py` files

## Troubleshooting

1. **Cannot connect to server**:
   - Ensure server is running on PC1
   - Check firewall settings on PC1
   - Verify both PCs are on the same network

2. **Server crashes during processing**:
   - Check logs for errors
   - Make sure all dependencies are installed
   
3. **Cannot start server on PC1**:
   - Ensure Flask is installed (`pip install flask`)
   - Try a different port if 5000 is in use 