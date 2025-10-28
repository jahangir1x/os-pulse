# OS-Pulse

**A comprehensive real-time system monitoring platform with web-based dashboard for security research and behavior analysis.**

OS-Pulse is a modern, full-stack system monitoring solution that combines real-time Windows API instrumentation, network monitoring, and an intuitive web dashboard. Built for security researchers, malware analysts, and system administrators who need deep insights into system behavior.

## 🚀 Features

- **Real-time System Monitoring**: Track file operations, process creation, network activity, and system calls
- **Web-based Dashboard**: Modern React frontend with real-time event visualization
- **Dynamic Instrumentation**: Frida-based runtime process injection with TypeScript agents
- **Network Traffic Analysis**: HTTP and raw network packet interception
- **Multi-Agent Architecture**: Modular design with specialized monitoring components
- **GORM Database**: PostgreSQL backend with automatic migrations and JSONB support
- **Session Management**: File upload, monitoring control, and event tracking per session
- **Performance Optimized**: Low-overhead monitoring with configurable data extraction limits

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Agents      │
│   (React)       │◄──►│   (Go/GORM)    │◄──►│   (Multiple)    │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • REST API      │    │ • Frida Agent   │
│ • Controls      │    │ • Session Mgmt  │    │ • HTTP Monitor  │
│ • Event Tables  │    │ • Event Storage │    │ • Net Monitor   │
│ • Process List  │    │ • PostgreSQL    │    │ • File Monitor  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
os-pulse/
├── frontend/                 # React web dashboard
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── types/           # TypeScript types
│   │   └── lib/             # Utilities
│   ├── noVNC/               # VNC viewer integration
│   └── package.json
├── backend/                  # Go backend with GORM
│   ├── internal/
│   │   ├── models/          # GORM models
│   │   ├── handlers/        # HTTP handlers
│   │   ├── repository/      # Data access layer
│   │   ├── service/         # Business logic
│   │   └── database/        # GORM setup
│   └── main.go
├── agent/                    # Monitoring agents
│   ├── controller/          # Python controller
│   ├── injector/            # Frida TypeScript agent
│   ├── network-monitor/     # Network monitoring
│   └── controller-go/       # Go controller (alternative)
└── utils/                   # Native utilities
    └── build/               # C++ compiled tools
```

## 🛠 Components

### Frontend (React Dashboard)

Modern web dashboard built with React, TypeScript, and Tailwind CSS:

- **Real-time Event Visualization**: Live tables showing file operations, network activity
- **Process Monitoring**: Interactive process list with detailed information
- **VNC Integration**: Embedded virtual machine display with zoom controls
- **Session Management**: File upload, monitoring controls, and session tracking
- **Responsive Design**: Works on desktop and mobile devices

### Backend (Go + GORM)

High-performance REST API server with PostgreSQL database:

- **GORM ORM**: Automatic migrations, relationships, and query optimization
- **Session Management**: Track monitoring sessions with time-based event filtering
- **Event Processing**: Store and serve events with pagination and marking
- **Agent Integration**: Forward requests to monitoring agents
- **PostgreSQL**: JSONB support for flexible event data storage

### Agent System (Multi-Component)

Modular monitoring system with specialized agents:

#### Controller (Python/Go)
- **Session Coordination**: Manage monitoring lifecycle
- **Agent Orchestration**: Control multiple monitoring components
- **API Integration**: Communicate with backend services

#### Injector (Frida + TypeScript)
- **Dynamic Instrumentation**: Runtime API hooking without process restart
- **File Operations**: ReadFile/WriteFile with content extraction
- **Process Creation**: NtCreateUserProcess, NtCreateProcess monitoring
- **Configurable Monitoring**: Adjustable content limits and hook depth

#### Network Monitor (Python)
- **HTTP Interception**: Capture and analyze HTTP/HTTPS traffic
- **Raw Packet Analysis**: Low-level network packet inspection
### Utils (Native Utilities)

C++ utilities for direct system operations and advanced monitoring tools:

- **Command Execution**: Execute system commands and capture output
- **File Operations**: Low-level file read/write operations
- **Process Monitor**: Advanced system monitoring capabilities

## 🔧 Prerequisites

### Full Stack Development
- **Node.js 18+** with npm/yarn (Frontend)
- **Go 1.21+** (Backend)
- **PostgreSQL 12+** (Database)
- **Python 3.8+** with pip (Agents)
- **Administrator privileges** (Windows monitoring)

### Development Tools
- **Visual Studio Code** (recommended)
- **Git** for version control
- **Docker** (optional, for PostgreSQL)

## 🚀 Quick Start

### 1. Database Setup
```bash
# Using Docker (recommended)
cd backend
docker-compose up -d postgres

# Or install PostgreSQL manually and create database
createdb ospulse
```

### 2. Backend Setup
```bash
cd backend
go mod tidy
go run main.go
# Server starts on http://localhost:3003
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Dashboard available at http://localhost:5173
```

### 4. Agent Setup
```bash
cd agent/controller
pip install -r requirements.txt
python main.py
# Agent service starts on http://localhost:7000
```

### 5. Access Dashboard
- Open browser to `http://localhost:5173`
- Upload a file to create a monitoring session
- Start monitoring and interact with the target system
- View real-time events in the dashboard

## 📊 Usage Workflow

### 1. Session Creation
```bash
# Upload target file through web interface
# System creates unique session ID
# File is forwarded to agent service
```

### 2. Start Monitoring
```bash
# Select monitoring mode:
# - All Processes: Monitor entire system
# - Specific Processes: Choose target processes
# - Spawn Uploaded: Execute uploaded file
```

### 3. Real-time Analysis
```bash
# View live events in dashboard:
# - File operations (read/write)
# - Process creation/termination
# - Network activity (HTTP/raw)
# - System calls and API interactions
```

### 4. Data Export
```bash
# Events stored in PostgreSQL
# JSON format for easy analysis
# Time-based filtering and pagination
```

## 🏗 System Architecture

### Data Flow
```
User → Frontend → Backend → Database
             ↓         ↑
           Agent ← Controller
             ↓
        Target System
```

### Technology Stack
- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: Go, Echo framework, GORM ORM
- **Database**: PostgreSQL with JSONB support
- **Agents**: Python, Frida, TypeScript
- **Monitoring**: Windows API hooks, Network interception
## 🛠 Development Guidelines

### Code Organization
- **Modular Architecture**: Each component is independently testable and deployable
- **Type Safety**: Full TypeScript typing for frontend, strict Go typing for backend
- **Error Handling**: Graceful failure modes and recovery across all layers
- **Configuration**: Environment-based configuration for all services

### Development Workflow
```bash
# Backend development
cd backend
go run main.go          # Start with hot-reload
go test ./...           # Run all tests

# Frontend development  
cd frontend
npm run dev             # Start with hot-reload
npm run build           # Production build

# Agent development
cd agent/controller
python main.py          # Start agent service
python -m pytest       # Run test suite
```

### Testing Strategy
```bash
# Unit tests
npm test                # Frontend
go test ./...           # Backend
python -m pytest       # Agent

# Integration tests
npm run test:e2e        # End-to-end
python test_api_integration.py  # API tests
```

### Performance Considerations
- **Memory Management**: Bounded buffer sizes prevent memory leaks
- **Database Optimization**: GORM with proper indexing and connection pooling
- **Real-time Updates**: Efficient WebSocket communication
- **CPU Overhead**: Selective monitoring reduces system impact

## 🔍 Monitoring Capabilities

### File System Operations
- Read/Write operations with content preview
- File creation, deletion, and metadata changes
- Handle-to-path resolution for system files
- Directory enumeration tracking

### Process Management
- Process creation with full command line arguments
- Parent-child relationship mapping
- Process termination and exit codes
- Module loading and DLL injection detection

### Network Activity
- HTTP request/response interception
- Raw socket communication monitoring
- SSL/TLS handshake analysis
- Protocol-specific parsing (HTTP, FTP, etc.)

### Registry Operations
- Registry key creation, modification, deletion
- Value read/write operations
- Registry tree traversal patterns
- Security descriptor changes

## � API Documentation

### Backend Endpoints
```bash
GET    /api/events              # List events with pagination
POST   /api/events              # Create new event
GET    /api/events/:id          # Get specific event
GET    /api/sessions            # List sessions
POST   /api/sessions            # Create session
GET    /api/processes           # List processes
POST   /api/files               # Upload file
```

### Agent API
```bash
POST   /start                   # Start monitoring
POST   /stop                    # Stop monitoring
GET    /status                  # Get monitoring status
POST   /upload                  # Upload target file
```

### Event Format
```json
{
  "id": "uuid",
  "session_id": "uuid", 
  "timestamp": "2024-01-01T12:00:00.000Z",
  "event_type": "file_operation",
  "process_id": 1234,
  "process_name": "notepad.exe",
  "details": {
    "operation": "CreateFile",
    "path": "C:\\document.txt",
    "access_mode": "READ_WRITE"
  }
}
```

## 🚧 Current Limitations

- **Windows Only**: Currently supports Windows systems exclusively
- **Privilege Requirements**: Requires administrator rights for system monitoring
- **Performance Impact**: High-frequency monitoring may affect system performance
- **Single Machine**: Designed for single-machine monitoring

## 🔮 Future Enhancements

- **Cross-platform Support**: Linux and macOS compatibility
- **Machine Learning**: Anomaly detection in behavioral patterns
- **Distributed Monitoring**: Multi-system coordination
- **Advanced Analytics**: Statistical analysis and reporting tools
- **Real-time Alerts**: Configurable alerting system

## 🔒 Security & Privacy

⚠️ **Important Security Considerations:**
- This tool captures sensitive data from monitored processes
- File operation content and process command lines are logged
- Requires code injection capabilities and elevated privileges
- Use responsibly and in compliance with applicable laws and policies

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

For support and questions:

- **Issues**: [GitHub Issues](https://github.com/jahangir1x/os-pulse/issues)
- **Documentation**: Check component-specific README files in each directory
- **Architecture**: Refer to individual component READMEs for detailed documentation

---

**Note**: This tool is designed for legitimate security research, system administration, and debugging purposes. Users are responsible for complying with applicable laws and regulations in their jurisdiction.
