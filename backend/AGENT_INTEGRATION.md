# Backend Configuration for Agent-Srv Integration

## Environment Variables

The backend needs to be configured to communicate with the agent-srv.

### Required Configuration

Create or update `backend/.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/ospulse?sslmode=disable

# Agent Service URL (IMPORTANT: must point to agent-srv)
AGENT_SERVICE_URL=http://localhost:8080

# Backend Server Port
PORT=3003
```

### Key Changes

**Before:**
The `AGENT_SERVICE_URL` was not properly utilized or pointed to a non-existent service.

**After:**
The `AGENT_SERVICE_URL` now points to the agent-srv running on port 8080, which:
1. Receives file uploads and saves to Desktop
2. Lists running processes via tasklist
3. Starts Python controller with appropriate arguments
4. Stops monitoring by killing Python processes

## Service Integration Flow

### 1. File Upload Flow
```
Frontend → Backend (session_service.go:65)
    ↓
Agent-Srv (/api/upload-file)
    ↓
Desktop (file saved)
```

**Backend Code:**
```go
// session_service.go line 65
err = s.uploadFileToAgent(fileName, fileContent)
```

### 2. List Processes Flow
```
Frontend → Backend (session_service.go:120)
    ↓
Agent-Srv (/api/list-processes)
    ↓
tasklist command
    ↓
JSON response
```

**Backend Code:**
```go
// session_service.go line 120 (updated)
func (s *SessionService) GetRunningProcesses(sessionID string) ([]*models.RunningProcess, error) {
    resp, err := http.Post(
        s.agentServiceURL+"/api/list-processes",
        "application/json",
        bytes.NewBuffer([]byte("{}")),
    )
    // ... parse response
}
```

### 3. Start Monitoring Flow
```
Frontend → Backend (event_service.go:81)
    ↓
Agent-Srv (/api/start-monitor)
    ↓
Python Controller (main.py with args)
    ↓
Frida Agent
```

**Backend Code:**
```go
// event_service.go line 81
func (s *EventService) StartMonitoring(req *models.StartMonitorRequest) error {
    // ... update session time
    return s.forwardStartMonitorRequest(req)
}
```

### 4. Stop Monitoring Flow
```
Frontend → Backend (event_service.go:92)
    ↓
Agent-Srv (/api/stop-monitor)
    ↓
taskkill /F /IM python.exe
```

**Backend Code:**
```go
// event_service.go line 92
func (s *EventService) StopMonitoring(req *models.StopMonitorRequest) error {
    // ... update session time
    return s.forwardStopMonitorRequest(req)
}
```

## Testing Integration

### 1. Verify Agent-Srv is Running
```bash
curl http://localhost:8080/health
```

Expected response:
```json
{"status":"ok"}
```

### 2. Test File Upload
```bash
# Start backend
cd backend
go run .

# In another terminal, test upload
curl -X POST -F "file=@test.txt" http://localhost:3003/api/create-session
```

### 3. Test Process Listing
```bash
curl -X POST http://localhost:3003/api/list-processes
```

### 4. Test Start Monitoring
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"sessionId":"test-123","mode":1}' \
  http://localhost:3003/api/start-monitor
```

### 5. Test Stop Monitoring
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"sessionId":"test-123"}' \
  http://localhost:3003/api/monitor/stop
```

## Troubleshooting

### "Failed to forward to agent service"

**Cause:** Backend cannot reach agent-srv

**Solutions:**
1. Verify agent-srv is running: `curl http://localhost:8080/health`
2. Check `AGENT_SERVICE_URL` in backend `.env`
3. Ensure no firewall blocking port 8080

### "Agent service returned error"

**Cause:** Agent-srv received request but encountered an error

**Solutions:**
1. Check agent-srv logs for error details
2. Verify Python is in PATH (for start-monitor)
3. Check file paths are correct
4. Ensure controller exists at `../controller/main.py`

### "Failed to get session"

**Cause:** Session not found when starting monitoring

**Solutions:**
1. Ensure session was created via `/api/create-session`
2. Verify session ID is correct
3. Check database connection

## Code Changes Summary

### `session_service.go`
- ✅ Line 65: `uploadFileToAgent()` already forwards to agent-srv `/api/upload-file`
- ✅ Line 120: `GetRunningProcesses()` **UPDATED** to call agent-srv `/api/list-processes`

### `event_service.go`
- ✅ Line 81: `StartMonitoring()` already forwards to agent-srv `/api/start-monitor`
- ✅ Line 92: `StopMonitoring()` already forwards to agent-srv `/api/stop-monitor`
- ✅ Line 108: `forwardStartMonitorRequest()` fetches fileName from session and includes in request

## Complete Startup Sequence

1. **Start PostgreSQL**
   ```bash
   cd backend
   docker-compose up -d
   ```

2. **Start Agent-Srv**
   ```bash
   cd agent/agent-srv
   go run .
   ```
   Wait for: `Agent service starting on port 8080`

3. **Start Backend**
   ```bash
   cd backend
   go run .
   ```
   Wait for: `Server starting on port 3003`

4. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   Wait for: `Local: http://localhost:5173/`

5. **Access Application**
   Open browser: `http://localhost:5173`

## Port Configuration

| Service    | Port | Environment Variable | Config File |
|------------|------|---------------------|-------------|
| Backend    | 3003 | `PORT`              | `.env`      |
| Agent-Srv  | 8080 | `AGENT_PORT`        | `.env`      |
| PostgreSQL | 5432 | In `DATABASE_URL`   | `.env`      |

## Important Notes

1. **Agent-Srv Must Be Running**: The backend will fail requests if agent-srv is not running
2. **Python in PATH**: Agent-srv needs Python accessible to start controller
3. **Controller Path**: Agent-srv looks for `../controller/main.py` relative to agent-srv directory
4. **File Storage**: Files are saved to user's Desktop directory (configurable in agent-srv)
5. **Process Killing**: Stop monitoring kills ALL Python processes, not session-specific

## Next Steps

After configuration:
1. ✅ Verify all services start without errors
2. ✅ Test file upload through UI
3. ✅ Test process listing
4. ✅ Test monitoring start/stop
5. ✅ Verify events are captured and displayed
