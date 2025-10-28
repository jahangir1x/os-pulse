#!/bin/bash
# Test script for sending events to the backend

BACKEND_URL="http://localhost:8080"

echo "Testing Event Reception Endpoint"
echo "================================="
echo ""

# Test 1: File Operation Event
echo "Test 1: Sending file_operation event..."
curl -X POST "${BACKEND_URL}/api/events" \
  -H "Content-Type: application/json" \
  -d '{
  "event_type": "file_operation",
  "timestamp": "2025-10-28T16:10:50.269774Z",
  "source": "os-pulse-controller",
  "data": {
    "handle": "0x8e8",
    "filePath": "\\\\?\\C:\\Users\\rocky\\AppData\\Roaming\\Microsoft\\Windows\\Recent\\AutomaticDestinations\\f01b4d95cf55d32a.automaticDestinations-ms",
    "bytesTransferred": 2,
    "content": "6F 01",
    "timestamp": "2025-10-28T16:10:46.230Z",
    "operation": "ReadFile",
    "metadata": {
      "sessionId": "test-session-123",
      "processName": "notepad.exe",
      "processId": 9700
    }
  }
}'

echo -e "\n\n"

# Test 2: Process Creation Event
echo "Test 2: Sending process_creation event..."
curl -X POST "${BACKEND_URL}/api/events" \
  -H "Content-Type: application/json" \
  -d '{
  "event_type": "process_creation",
  "timestamp": "2025-10-28T16:15:30.123456Z",
  "source": "os-pulse-controller",
  "data": {
    "processHandle": "0x1a4",
    "threadHandle": "0x1a8",
    "imagePath": "C:\\Windows\\System32\\notepad.exe",
    "commandLine": "notepad.exe test.txt",
    "currentDirectory": "C:\\Users\\rocky\\Desktop",
    "status": 0,
    "operation": "NtCreateUserProcess",
    "timestamp": "2025-10-28T16:15:30.100Z",
    "metadata": {
      "sessionId": "test-session-456",
      "processName": "explorer.exe",
      "processId": 1234
    }
  }
}'

echo -e "\n\n"

# Test 3: Write Operation Event
echo "Test 3: Sending WriteFile event..."
curl -X POST "${BACKEND_URL}/api/events" \
  -H "Content-Type: application/json" \
  -d '{
  "event_type": "file_operation",
  "timestamp": "2025-10-28T16:20:15.987654Z",
  "source": "os-pulse-controller",
  "data": {
    "handle": "0x2f4",
    "filePath": "C:\\Users\\rocky\\Desktop\\test.txt",
    "bytesTransferred": 13,
    "content": "48 65 6C 6C 6F 20 57 6F 72 6C 64 21 0A",
    "timestamp": "2025-10-28T16:20:15.950Z",
    "operation": "WriteFile",
    "metadata": {
      "sessionId": "test-session-789",
      "processName": "notepad.exe",
      "processId": 5678
    }
  }
}'

echo -e "\n\n"
echo "================================="
echo "Tests completed!"
