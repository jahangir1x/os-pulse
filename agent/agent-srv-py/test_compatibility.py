"""
Test script to verify agent-srv-py compatibility with backend
"""
import requests
import json

BASE_URL = "http://localhost:7000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_list_processes():
    """Test list processes endpoint (GET and POST)"""
    print("Testing /api/list-processes endpoint (GET)...")
    response = requests.get(f"{BASE_URL}/api/list-processes")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    print(f"First 3 processes: {data[:3]}")
    print()
    
    print("Testing /api/list-processes endpoint (POST)...")
    response = requests.post(f"{BASE_URL}/api/list-processes", json={})
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    print(f"First 3 processes: {data[:3]}")
    print()

def test_start_monitor_mode1():
    """Test start monitor - Mode 1 (All Processes)"""
    print("Testing /api/start-monitor endpoint (Mode 1)...")
    payload = {
        "sessionId": "test-session-123",
        "mode": 1,
        "fileName": "notepad.exe"
    }
    response = requests.post(
        f"{BASE_URL}/api/start-monitor",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_start_monitor_mode2():
    """Test start monitor - Mode 2 (Specific Processes)"""
    print("Testing /api/start-monitor endpoint (Mode 2)...")
    payload = {
        "sessionId": "test-session-456",
        "mode": 2,
        "processes": [1234, 5678]
    }
    response = requests.post(
        f"{BASE_URL}/api/start-monitor",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_start_monitor_mode3():
    """Test start monitor - Mode 3 (Spawn Uploaded)"""
    print("Testing /api/start-monitor endpoint (Mode 3)...")
    payload = {
        "sessionId": "test-session-789",
        "mode": 3,
        "fileName": "notepad.exe"  # Assuming notepad.exe is uploaded
    }
    response = requests.post(
        f"{BASE_URL}/api/start-monitor",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_stop_monitor():
    """Test stop monitor endpoint"""
    print("Testing /api/stop-monitor endpoint...")
    payload = {
        "sessionId": "test-session-123"
    }
    response = requests.post(
        f"{BASE_URL}/api/stop-monitor",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_upload_file():
    """Test file upload endpoint"""
    print("Testing /api/upload-file endpoint...")
    # Create a dummy file
    files = {
        'file': ('test.txt', b'Hello World', 'text/plain')
    }
    response = requests.post(f"{BASE_URL}/api/upload-file", files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Agent Service Compatibility Test")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_list_processes()
        test_upload_file()
        # test_start_monitor_mode1()
        # test_stop_monitor()
        
        print("=" * 60)
        print("Basic tests completed!")
        print("Uncomment other tests to test monitoring functionality")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to agent service.")
        print(f"Make sure the service is running on {BASE_URL}")
    except Exception as e:
        print(f"ERROR: {e}")
