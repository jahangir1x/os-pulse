# Agent Service

Go-based agent service that handles file uploads, process management, and monitoring control.

## Overview

This service acts as an intermediary between the backend and the Python controller, handling:
- File uploads (saves to Desktop)
- Process listing (using tasklist)
- Starting monitoring (spawns Python controller)
- Stopping monitoring (kills Python processes)

## Prerequisites

- Go 1.21+
- Python 3.8+ (for controller)
- Windows OS (uses tasklist and taskkill)

## Setup

1. Install dependencies:
```bash
go mod download
```

2. Build the service:
```bash
go build -o agent-srv.exe .
```

Or use the build script:
```bash
.\build.bat
```

## Running

### Option 1: Direct Run
```bash
go run .
```

### Option 2: Build and Run
```bash
.\build.bat
.\agent-srv.exe
```

### Option 3: Using Run Script
```bash
.\run.bat
```

## Configuration

Set environment variable for custom port:
```bash
set AGENT_PORT=8080
go run .
```

Default port: `8080`

## API Endpoints

### 1. Health Check
```
GET /health
```

Response:
```json
{
  "status": "ok"
}
```

### 2. Upload File
```
POST /api/upload-file
Content-Type: multipart/form-data
```

Request:
- `file`: File to upload (multipart form data)

Response:
```json
{
  "message": "File uploaded successfully",
  "path": "C:\\Users\\username\\Desktop\\malware.exe"
}
```

The file is saved to the user's Desktop directory.

### 3. List Processes
```
POST /api/list-processes
```

Response:
```json
[
  {
    "pid": 1234,
    "name": "notepad.exe"
  },
  {
    "pid": 5678,
    "name": "chrome.exe"
  }
]
```

Uses Windows `tasklist` command to get running processes.

### 4. Start Monitor
```
POST /api/start-monitor
Content-Type: application/json
```

Request:
```json
{
  "sessionId": "session-123",
  "fileName": "malware.exe",
  "mode": 1,
  "processes": [1234, 5678]
}
```

**Modes:**
- `1`: All Processes (with optional fileName as filter)
- `2`: Specific Processes (requires processes array)
- `3`: Spawn Uploaded (requires fileName)

Response:
```json
{
  "message": "Monitoring started successfully",
  "sessionId": "session-123",
  "monitoringPid": 9876
}
```

**Behavior:**
- Mode 1: Runs `python main.py attach --all [--filter fileName]`
- Mode 2: Runs `python main.py attach --pids 1234 5678`
- Mode 3: Runs `python main.py spawn --executable Desktop/malware.exe`

Sets `SESSION_ID` environment variable for the controller process.

### 5. Stop Monitor
```
POST /api/stop-monitor
Content-Type: application/json
```

Request:
```json
{
  "sessionId": "session-123"
}
```

Response:
```json
{
  "message": "Monitoring stopped successfully"
}
```

**Behavior:**
Kills all Python processes using `taskkill /F /IM python.exe`.

## Integration with Backend

The backend service should set `AGENT_SERVICE_URL` to point to this service:

```env
AGENT_SERVICE_URL=http://localhost:8080
```

Backend endpoints that interact with agent-srv:
1. `POST /api/create-session` → calls `/api/upload-file`
2. `POST /api/list-processes` → calls `/api/list-processes`
3. `POST /api/start-monitor` → calls `/api/start-monitor`
4. `POST /api/monitor/stop` → calls `/api/stop-monitor`

## File Structure

```
agent-srv/
├── main.go           # Entry point, Echo server setup
├── handler.go        # Request handlers
├── go.mod            # Go module dependencies
├── build.bat         # Build script
├── run.bat           # Run script
└── README.md         # This file
```

## Architecture Flow

```
Frontend → Backend → Agent-Srv → Python Controller → Frida Agent
                                ↓
                           Desktop (file storage)
                                ↓
                           tasklist (process list)
```

## Troubleshooting

### "Failed to get user home directory"
- Ensure user profile environment variables are set
- Check permissions

### "Failed to start monitoring"
- Verify Python is in PATH
- Check `../controller/main.py` exists
- Ensure controller dependencies installed

### "Failed to kill python processes"
- May require administrator privileges
- Check if Python processes are actually running

### Port already in use
- Change port with `AGENT_PORT` environment variable
- Kill process using the port: `netstat -ano | findstr :8080`

## Development

### Adding New Endpoints

1. Add handler method in `handler.go`
2. Register route in `main.go`
3. Update this README

### Testing

Test individual endpoints:

```bash
# Health check
curl http://localhost:8080/health

# Upload file
curl -X POST -F "file=@test.exe" http://localhost:8080/api/upload-file

# List processes
curl -X POST http://localhost:8080/api/list-processes

# Start monitoring
curl -X POST -H "Content-Type: application/json" \
  -d '{"sessionId":"test-123","mode":1}' \
  http://localhost:8080/api/start-monitor

# Stop monitoring
curl -X POST -H "Content-Type: application/json" \
  -d '{"sessionId":"test-123"}' \
  http://localhost:8080/api/stop-monitor
```

## Security Considerations

⚠️ **Warning:** This service has minimal security measures:
- No authentication
- No input validation
- Kills ALL Python processes (not session-specific)
- Saves files directly to Desktop
- Intended for local development only

For production use, implement:
- Authentication/authorization
- Input validation and sanitization
- Session-specific process tracking
- Configurable file storage location
- Rate limiting
- HTTPS/TLS
