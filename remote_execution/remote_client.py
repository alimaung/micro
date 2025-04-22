import requests
import argparse
import json

# Configuration
SERVER_URL = "http://192.168.1.96:5000"  # IP of PC1 (this PC)
API_KEY = "microfilm_secure_key"  # Must match the key on the server

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def start_processing(folder_path, template="16", filmnumber=None, recovery=False):
    """Send a request to start processing a folder"""
    payload = {
        "folder_path": folder_path,
        "template": template,
        "filmnumber": filmnumber,
        "recovery": recovery
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/start_process",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Server returned status code {response.status_code}", "details": response.text}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}

def get_status():
    """Get the status of all running jobs"""
    try:
        response = requests.get(
            f"{SERVER_URL}/status",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Server returned status code {response.status_code}", "details": response.text}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remote SMA Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start processing a folder")
    start_parser.add_argument("--folder", required=True, help="Folder path to process")
    start_parser.add_argument("--template", default="16", choices=["16", "35"], help="Template to use")
    start_parser.add_argument("--filmnumber", help="Film number")
    start_parser.add_argument("--recovery", action="store_true", help="Enable recovery mode")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check status of running jobs")
    
    args = parser.parse_args()
    
    if args.command == "start":
        result = start_processing(args.folder, args.template, args.filmnumber, args.recovery)
        print(json.dumps(result, indent=2))
    elif args.command == "status":
        result = get_status()
        print(json.dumps(result, indent=2))
    else:
        parser.print_help() 