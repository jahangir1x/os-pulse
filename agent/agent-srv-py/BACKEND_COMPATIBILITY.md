# Backend-Agent Compatibility Summary

## Fixed Compatibility Issues

### 1. Endpoint Path Mismatches
**Problem**: Backend was calling different endpoint paths than what Flask app provided.

**Solution**: Added dual route support to Flask app for backward and forward compatibility.

| Feature | Backend Calls | Flask Now Supports | Status |
|---------|--------------|-------------------|--------|
| Upload File | `/api/upload-file` | `/api/upload` + `/api/upload-file` | ✅ Fixed |
| List Processes | `/api/list-processes` (POST) | `/api/processes` (GET) + `/api/list-processes` (GET/POST) | ✅ Fixed |
| Start Monitor | `/api/start-monitor` | `/api/monitor/start` + `/api/start-monitor` | ✅ Fixed |
| Stop Monitor | `/api/stop-monitor` | `/api/monitor/stop` + `/api/stop-monitor` | ✅ Fixed |

### 2. Response Format Mismatch
**Problem**: List processes endpoint returned `{processes: [...], count: n}` but backend expected array directly.

**Before**:
```json
{
  "processes": [{"name": "notepad.exe", "pid": 1234}],
  "count": 1
}
```

**After**:
```json
[
  {"name": "notepad.exe", "pid": 1234}
]
```

**Solution**: Changed response format to return array directly.

### 3. Mode 3 File Path Issue
**Problem**: Mode 3 (Spawn Uploaded) wasn't properly constructing the file path.

**Before**:
```python
exec_path = app.config['UPLOAD_FOLDER'] / file_name  # Path object
cmd.extend(['spawn', '--executable', exec_path])
```

**After**:
```python
exec_path = str(app.config['UPLOAD_FOLDER'] / file_name)  # String
cmd.extend(['spawn', '--executable', exec_path])
```

**Solution**: Convert Path object to string before passing to subprocess.

## Request/Response Mapping

### CreateSession (Frontend → Backend → Agent)

**Frontend Request to Backend**:
```
POST /api/create-session
Content-Type: multipart/form-data
file: <binary>
```

**Backend Request to Agent**:
```
POST /api/upload-file
Content-Type: multipart/form-data
file: <binary>
```

**Agent Response**:
```json
{
  "message": "File uploaded successfully",
  "filename": "app.exe",
  "path": "C:\\Users\\...\\Desktop\\app.exe"
}
```

### StartMonitor (Frontend → Backend → Agent)

**Frontend Request to Backend**:
```json
POST /api/start-monitor
{
  "sessionId": "uuid",
  "mode": 1,
  "processes": [1234, 5678],  // Optional, for mode 2
  "fileName": "notepad.exe"   // Optional, for mode 1 filter or mode 3
}
```

**Backend Request to Agent** (backend adds fileName from session):
```json
POST /api/start-monitor
{
  "sessionId": "uuid",
  "mode": 1,
  "processes": [1234, 5678],
  "fileName": "app.exe"
}
```

**Agent Response**:
```json
{
  "message": "Monitoring started successfully",
  "sessionId": "uuid",
  "monitoringPid": 12345,
  "mode": 1
}
```

### StopMonitor (Frontend → Backend → Agent)

**Frontend Request to Backend**:
```json
POST /api/monitor/stop
{
  "sessionId": "uuid"
}
```

**Backend Request to Agent**:
```json
POST /api/stop-monitor
{
  "sessionId": "uuid"
}
```

**Agent Response**:
```json
{
  "message": "Monitoring stopped successfully",
  "sessionId": "uuid"
}
```

### ListProcesses (Frontend → Backend → Agent)

**Frontend Request to Backend**:
```json
POST /api/list-processes
{
  "sessionId": "uuid"
}
```

**Backend Request to Agent**:
```json
POST /api/list-processes
{}
```

**Agent Response**:
```json
[
  {"name": "notepad.exe", "pid": 1234},
  {"name": "chrome.exe", "pid": 5678}
]
```

**Backend Response to Frontend**:
```json
[
  {"pid": 1234, "name": "notepad.exe"},
  {"pid": 5678, "name": "chrome.exe"}
]
```

## Data Structure Alignment

### Go Backend Models → Python Flask

| Go Type | JSON Field | Python Type | Notes |
|---------|-----------|-------------|-------|
| `StartMonitorRequest` | | | |
| `string` | `sessionId` | `str` | ✅ |
| `string` | `fileName` | `str` | ✅ Optional |
| `int` | `mode` | `int` | ✅ 1, 2, or 3 |
| `[]int` | `processes` | `list[int]` | ✅ Optional |
| `StopMonitorRequest` | | | |
| `string` | `sessionId` | `str` | ✅ |
| `RunningProcess` | | | |
| `int` | `pid` | `int` | ✅ |
| `string` | `name` | `str` | ✅ |

## Testing

Run the compatibility test:
```bash
cd agent\agent-srv-py
python test_compatibility.py
```

This tests:
- Health check
- List processes (GET and POST)
- File upload
- Start/stop monitoring (commented out by default)

## Environment Configuration

**Backend** (`backend/.env`):
```
AGENT_SERVICE_URL=http://localhost:7000
```

**Agent** (`agent/agent-srv-py/.env`):
```
PORT=7000
FLASK_ENV=development
FLASK_DEBUG=True
```

## Excluded Processes

The controller now excludes the following processes when attaching to all:
- System critical: `System`, `csrss.exe`, `smss.exe`, `wininit.exe`, `services.exe`
- Development tools: `python.exe`, `go.exe`, `cloudflared.exe`

This prevents conflicts and errors when monitoring.

## Summary

✅ All endpoint paths are now compatible  
✅ Response formats match expected structures  
✅ File paths properly converted to strings  
✅ Dual route support for flexibility  
✅ Test script provided for verification  
✅ Documentation updated
