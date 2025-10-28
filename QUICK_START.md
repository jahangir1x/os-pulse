# Quick Start Guide - Complete System Setup

This guide walks through starting all components of the OS-Pulse system.

## Component Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────────┐
│  Frontend   │─────▶│   Backend    │─────▶│  Agent-Srv  │─────▶│ Python Controller│
│ (React/Vite)│      │   (Go/Echo)  │      │  (Go/Echo)  │      │    (Frida)       │
│  Port 5173  │      │  Port 3003   │      │  Port 8080  │      │                  │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  PostgreSQL  │
                     │  Port 5432   │
                     └──────────────┘
```

## Prerequisites

- ✅ PostgreSQL 14+ (running)
- ✅ Go 1.21+
- ✅ Node.js 18+
- ✅ Python 3.8+
- ✅ Frida installed (`pip install frida frida-tools`)

## Step-by-Step Startup

### 1. Start PostgreSQL

```bash
# Using Docker
cd backend
docker-compose up -d

# Or start local PostgreSQL service
```

Verify: Check that PostgreSQL is running on port 5432

### 2. Start Agent Service

```bash
cd agent/agent-srv
go run .
```

Expected output:
```
Agent service starting on port 8080
```

### 3. Start Backend

```bash
cd backend
go run .
```

Expected output:
```
Server starting on port 3003
```

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

Expected output:
```
VITE ready in Xms
Local: http://localhost:5173/
```

### 5. Access the Application

Open browser: `http://localhost:5173`

## Configuration Files

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ospulse?sslmode=disable
AGENT_SERVICE_URL=http://localhost:8080
PORT=3003
```

### Agent-Srv (.env)
```env
AGENT_PORT=8080
```

## Testing the Flow

### 1. Upload File
- Click "Upload File" in frontend
- Select a Windows executable
- Backend saves to agent-srv
- Agent-srv saves to Desktop

### 2. List Processes
- Click "List Processes"
- Frontend → Backend → Agent-Srv → tasklist
- Returns running processes

### 3. Start Monitoring
- Select monitoring mode
- Select processes (if mode 2)
- Click "Start Monitoring"
- Backend → Agent-Srv → Python Controller → Frida

### 4. View Events
- Events appear in real-time
- Controller → Backend → PostgreSQL
- Frontend polls for updates

### 5. Stop Monitoring
- Click "Stop Monitoring"
- Backend → Agent-Srv → kills Python processes

## Troubleshooting

### Agent-Srv Won't Start
```bash
# Check if port 8080 is in use
netstat -ano | findstr :8080

# Change port
set AGENT_PORT=8081
go run .
```

### Backend Can't Connect to Agent-Srv
Check `AGENT_SERVICE_URL` in backend `.env`:
```env
AGENT_SERVICE_URL=http://localhost:8080
```

### Python Controller Not Starting
1. Check Python is in PATH: `python --version`
2. Verify controller exists: `dir ..\controller\main.py`
3. Check Frida installed: `pip list | findstr frida`

### File Upload Fails
1. Check Desktop directory exists
2. Verify write permissions
3. Check agent-srv logs for errors

### No Events Appearing
1. Verify monitoring started (check agent-srv logs)
2. Check Python controller is running: `tasklist | findstr python`
3. Verify Frida agent loaded successfully
4. Check backend database connection

## Development Workflow

### Terminal Layout (4 terminals)

**Terminal 1 - Backend:**
```bash
cd backend
go run .
```

**Terminal 2 - Agent-Srv:**
```bash
cd agent/agent-srv
go run .
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 4 - Database/Logs:**
```bash
# View PostgreSQL logs
docker-compose logs -f postgres

# Or check running processes
tasklist | findstr "python\|go\|node"
```

## Stopping All Services

### Option 1: Graceful Shutdown
Press `Ctrl+C` in each terminal window

### Option 2: Force Stop All
```bash
# Stop all Go processes
taskkill /F /IM go.exe

# Stop all Node processes
taskkill /F /IM node.exe

# Stop all Python processes
taskkill /F /IM python.exe

# Stop PostgreSQL
docker-compose down
```

## Port Summary

| Service    | Port | URL                      |
|------------|------|--------------------------|
| Frontend   | 5173 | http://localhost:5173    |
| Backend    | 3003 | http://localhost:3003    |
| Agent-Srv  | 8080 | http://localhost:8080    |
| PostgreSQL | 5432 | localhost:5432           |
| noVNC      | 6080 | ws://localhost:6080      |

## Service Health Checks

```bash
# Backend
curl http://localhost:3003/api/sessions

# Agent-Srv
curl http://localhost:8080/health

# Frontend (browser)
http://localhost:5173
```

## Common Issues

### "Port already in use"
Kill the process using the port or change the port number.

### "Database connection failed"
1. Verify PostgreSQL is running
2. Check DATABASE_URL in backend `.env`
3. Ensure database `ospulse` exists

### "Failed to forward to agent service"
1. Verify agent-srv is running on port 8080
2. Check AGENT_SERVICE_URL in backend `.env`
3. Test with: `curl http://localhost:8080/health`

### "Python controller not responding"
1. Check agent-srv logs for startup errors
2. Verify controller path is correct
3. Test manually: `python agent/controller/main.py --help`

## Next Steps

After successful startup:
1. Upload a test executable
2. Start monitoring in different modes
3. Observe events in real-time
4. Export data if needed
5. Stop monitoring when done

## Production Deployment

For production, consider:
- [ ] Use environment-specific configs
- [ ] Add authentication/authorization
- [ ] Enable HTTPS/TLS
- [ ] Set up reverse proxy (nginx)
- [ ] Configure systemd services (Linux) or Windows Services
- [ ] Set up monitoring and logging
- [ ] Implement health checks
- [ ] Add rate limiting
