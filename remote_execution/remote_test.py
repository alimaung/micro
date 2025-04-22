import requests
import json
import time

# Configuration
SERVER_URL = "http://192.168.1.96:5000"  # IP of PC1 (this PC)
API_KEY = "microfilm_secure_key"  # Must match the key on the server

# Test folder path and template
TEST_FOLDER = r"F:\microfilm+\microfilm\testing\RRD017-2024_OU_GROSS\.output"
TEST_TEMPLATE = "16"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def check_server():
    """Check if the server is running and ready"""
    print("Checking if server is running...")
    try:
        response = requests.get(f"{SERVER_URL}/status", headers=headers, timeout=5)
        if response.status_code == 200:
            print("Server is running and ready!")
            return True
        else:
            print(f"Server returned unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {str(e)}")
        return False

def start_test_job():
    """Start the test job with the predefined folder and template"""
    print(f"Starting test job on folder: {TEST_FOLDER}")
    print(f"Using template: {TEST_TEMPLATE}")
    
    payload = {
        "folder_path": TEST_FOLDER,
        "template": TEST_TEMPLATE,
        "filmnumber": None,
        "recovery": False
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/start_process",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Job started successfully!")
            print(f"Job ID: {result.get('job_id')}")
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            return result.get('job_id')
        else:
            print(f"Failed to start job. Server returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {str(e)}")
        return None

def check_job_status(job_id):
    """Check the status of a running job"""
    print(f"Checking status of job {job_id}...")
    
    try:
        response = requests.get(
            f"{SERVER_URL}/status",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            jobs = result.get('active_jobs', {})
            
            if job_id in jobs:
                status = jobs[job_id]
                print(f"Job {job_id} status: {status}")
                return status
            else:
                print(f"Job {job_id} not found in active jobs")
                return None
        else:
            print(f"Failed to get status. Server returned status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {str(e)}")
        return None

if __name__ == "__main__":
    print("=== Remote SMA Test Script ===")
    print(f"Target folder: {TEST_FOLDER}")
    print(f"Template: {TEST_TEMPLATE}")
    print("----------------------------")
    
    # First check if server is running
    if not check_server():
        print("Cannot connect to server. Is it running?")
        exit(1)
    
    # Start the test job
    job_id = start_test_job()
    if not job_id:
        print("Failed to start test job")
        exit(1)
    
    # Check status a few times
    print("\nMonitoring job status (press Ctrl+C to stop):")
    try:
        while True:
            status = check_job_status(job_id)
            if status == "completed":
                print("Job completed successfully!")
                break
            time.sleep(10)  # Wait 10 seconds between status checks
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        
    print("\nTest completed!") 