from flask import Flask, request, jsonify
import subprocess
import threading
import orchestrator
import os
import argparse

app = Flask(__name__)
API_KEY = "microfilm_secure_key"  # Change this to a secure key

active_jobs = {}

def validate_api_key(request):
    provided_key = request.headers.get('X-API-Key')
    return provided_key == API_KEY

@app.route('/start_process', methods=['POST'])
def start_process():
    if not validate_api_key(request):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    folder_path = data.get('folder_path')
    template = data.get('template', '16')
    filmnumber = data.get('filmnumber')
    recovery = data.get('recovery', False)
    
    # Start processing in a separate thread
    job_id = str(len(active_jobs) + 1)
    thread = threading.Thread(
        target=orchestrator.process_folder,
        args=(folder_path, template, filmnumber, recovery)
    )
    thread.start()
    
    active_jobs[job_id] = {
        'folder': folder_path,
        'status': 'running',
        'thread': thread
    }
    
    return jsonify({"job_id": job_id, "status": "started", "message": f"Started processing folder: {folder_path}"})

@app.route('/status', methods=['GET'])
def get_status():
    if not validate_api_key(request):
        return jsonify({"error": "Unauthorized"}), 401
        
    # Filter out thread objects for JSON serialization
    status_info = {}
    for job_id, job_info in active_jobs.items():
        status_info[job_id] = {
            'folder': job_info['folder'],
            'status': job_info['status'] if job_info['thread'].is_alive() else 'completed'
        }
        
    return jsonify({"active_jobs": status_info})

if __name__ == '__main__':
    # Default to port 5000, but allow configuration
    parser = argparse.ArgumentParser(description="Remote SMA Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    args = parser.parse_args()
    
    print(f"Starting server on 192.168.1.96:{args.port}")
    print(f"Use API key '{API_KEY}' for authentication")
    app.run(host='0.0.0.0', port=args.port) 