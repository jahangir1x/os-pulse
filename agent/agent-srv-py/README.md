# Agent Server - Python Flask

Flask-based HTTP server for OS-Pulse agent operations.

## Features

- **File Upload**: Upload files to Desktop
- **Process Listing**: List running processes
- **Monitor Control**: Start/stop process monitoring in 3 modes
  - Mode 1: Attach to all processes (with optional filter)
  - Mode 2: Attach to specific PIDs
  - Mode 3: Spawn and monitor uploaded executable

## Setup

1. Run setup script:
```bash
setup.bat
```

This will:
- Create a virtual environment
- Install all dependencies

## Running the Server

```bash
run.bat
```

Or manually:
```bash
.venv\Scripts\activate
python app.py
```

The server will start on `http://localhost:8080`

## API Endpoints

### 1. Upload File
```bash
POST /upload
Content-Type: multipart/form-data

curl -X POST http://localhost:8080/upload -F "file=@C:\path\to\file.exe"
```

### 2. List Processes
```bash
GET /processes

curl http://localhost:8080/processes
```

### 3. Start Monitor - Mode 1 (All Processes)
```bash
POST /monitor/start
Content-Type: application/json

# Without filter
curl -X POST http://localhost:8080/monitor/start \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\":\"session-123\",\"mode\":1}"

# With filter
curl -X POST http://localhost:8080/monitor/start \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\":\"session-123\",\"fileName\":\"notepad.exe\",\"mode\":1}"
```

### 4. Start Monitor - Mode 2 (Specific Processes)
```bash
POST /monitor/start
Content-Type: application/json

curl -X POST http://localhost:8080/monitor/start \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\":\"session-456\",\"mode\":2,\"processes\":[1234,5678]}"
```

### 5. Start Monitor - Mode 3 (Spawn Uploaded)
```bash
POST /monitor/start
Content-Type: application/json

curl -X POST http://localhost:8080/monitor/start \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\":\"session-789\",\"fileName\":\"myapp.exe\",\"mode\":3}"
```

### 6. Stop Monitor
```bash
POST /monitor/stop
Content-Type: application/json

curl -X POST http://localhost:8080/monitor/stop \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\":\"session-123\"}"
```

### 7. Health Check
```bash
GET /health

curl http://localhost:8080/health
```

## Environment Variables

- `PORT`: Server port (default: 8080)
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable debug mode (True/False)

## Dependencies

- Flask 3.1.0
- flask-cors 5.0.0
- Werkzeug 3.1.3

## Architecture

```
agent-srv-py/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── setup.bat          # Setup script
├── run.bat            # Run script
├── .env.example       # Environment variables example
└── README.md          # This file
```

## Monitoring Modes

### Mode 1: Attach to All Processes
Attaches Frida to all running processes, optionally filtered by process name.

### Mode 2: Attach to Specific PIDs
Attaches Frida to specified process IDs.

### Mode 3: Spawn Uploaded Executable
Spawns an uploaded executable and monitors it with Frida.

## Notes

- Files are uploaded to `~/Desktop`
- Maximum upload size: 100 MB
- Controller script: `../controller/main.py`
- Monitoring sessions are tracked by `sessionId`
- Processes are gracefully terminated (5s timeout before force kill)
