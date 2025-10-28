request /api/create-session POST FORM data
------WebKitFormBoundaryW1zl95AALPSDDLJx
Content-Disposition: form-data; name="file"; filename="asfdasd sdfasdfasd.txt"
Content-Type: text/plain

asfdasd sdfasdfasd
------WebKitFormBoundaryW1zl95AALPSDDLJx--

response:
{
  "sessionId": "<sessionId>"
}

request /api/monitor-modes GET
response:
[
  {
    "id": 1,
    "mode": "All Processes"
  },
  {
    "id": 2,
    "mode": "Specific Processes"
  },
  {
    "id": 3,
    "mode": "Spawn Uploaded"
  }
]

request /api/start-monitor POST
{
  "sessionId": "<sessionId>",
  "mode": 1
}

response:
{
  "message": "monitoring started successfully"
}

request /api/events/:sessionId GET
response:
[
  {
    "event_type": "file_operation",
    "data": {
      "filePath": "\\\\?\\C:\\Windows\\System32\\UIAutomationCore.dll",
      "bytesTransferred": 4,
      "content": "AB 02 01 30",
      "timestamp": "2025-10-22T16:03:11.372Z",
      "operation": "ReadFile",
      "metadata": {
        "processName": "Notead.exe",
        "processId": 800
      }
    }
  },
  {
    "event_type": "http_network_operation",
    "data": {
      "base64RequestBody": "somethingsomethingbase64",
      "bytesTransferred": 20,
      "base64Response": "somebase64response",
      "timestamp": "2025-10-22T16:03:11.372Z",
      "url": "something.com/some_endpoint",
      "method": "post",
      "metadata": {
        "processName": "Notepad.exe",
        "processId": 800
      }
    }
  },
  {
    "event_type": "raw_network_operation",
    "data": {
      "request": "AB CD 02 30",
      "bytesTransferred": 20,
      "response": "02 AB CD EF",
      "timestamp": "2025-10-22T16:03:11.372Z",
      "host": "192.168.100.100",
      "protocol": "tcp",
      "metadata": {
        "processName": "Notepad.exe",
        "processId": 800
      }
    }
  },
  {
    "event_type": "file_operation",
    "data": {
      "filePath": "\\\\?\\C:\\Windows\\System32\\UIAutomationCore.dll",
      "bytesTransferred": 2,
      "content": "AB DE FE 02 03",
      "timestamp": "2025-10-22T16:03:11.372Z",
      "operation": "WriteFile",
      "metadata": {
        "processName": "Notepad.exe",
        "processId": 800
      }
    }
  },
  {
    "event_type": "process_creation_operation",
    "data": {
      "filePath": "\\\\?\\C:\\Windows\\System32\\paint.exe",
      "args": "--some --arg1 --arg2",
      "timestamp": "2025-10-22T16:03:11.372Z",
      "metadata": {
        "processName": "Notepad.exe",
        "processId": 800
      }
    }
  }
]

request /api/monitor/stop POST
{
  "sessionId": "<sessionId>"
}