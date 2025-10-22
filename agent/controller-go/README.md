# OS-Pulse Controller (Go)

A Go-based controller for the OS-Pulse Windows system monitoring framework, using the Frida Go API for dynamic instrumentation.

## Features

- **Process Management**: Spawn new processes or attach to existing ones
- **Real-time Monitoring**: File operations and process creation events
- **API Integration**: Immediate event forwarding to remote APIs (no queuing/buffering)
- **Simple CLI**: Easy-to-use command-line interface

## Prerequisites

- Go 1.21 or higher
- Frida installed on the system
- Windows (target platform)

## Installation

1. Initialize Go module and download dependencies:
```powershell
cd controller-go
go mod tidy
```

2. Build the controller:
```powershell
go build -o os-pulse.exe
```

## Usage

### List Processes
```powershell
./os-pulse.exe list --filter notepad
```

### Spawn Process with Monitoring
```powershell
./os-pulse.exe spawn --executable "C:\Windows\System32\notepad.exe"
```

### Attach to Existing Process
```powershell
./os-pulse.exe attach --process-name notepad.exe
```

### With API Integration
```powershell
./os-pulse.exe spawn --executable "C:\Windows\System32\notepad.exe" --enable-api --api-endpoint "http://localhost:8080/api" --api-key "your-key"
```

## API Integration

The Go controller sends events immediately to the configured API endpoint with no queuing or buffering:

- **Immediate Sending**: Events are sent as soon as they're received
- **Fire-and-Forget**: Uses goroutines for non-blocking API calls
- **Simple HTTP**: Standard JSON POST requests to `/events` endpoint

### Event Format
```json
{
  "event_type": "file_operation",
  "timestamp": "2025-10-22T12:00:00Z",
  "source": "os-pulse-controller-go",
  "data": {
    "operation": "WriteFile",
    "filePath": "C:\\Users\\user\\document.txt",
    "bytesTransferred": 256,
    "content": "Hello, World!"
  }
}
```

## Development

### Project Structure
```
controller-go/
├── main.go              # CLI entry point and commands
├── frida_controller.go  # Core Frida session management
├── message_handler.go   # Event processing and API forwarding
├── go.mod              # Go module dependencies
└── README.md           # This file
```

### Key Components

1. **FridaController**: Manages Frida sessions, device connections, and script injection
2. **MessageHandler**: Processes events from injector and forwards to API
3. **CLI Commands**: Cobra-based command structure for easy usage

### Building
```powershell
go build -o os-pulse.exe
```

### Running Tests
```powershell
go test ./...
```

## Comparison with Python Controller

| Feature | Python Controller | Go Controller |
|---------|------------------|---------------|
| Performance | Moderate | Higher (compiled) |
| Dependencies | Many (Frida, aiohttp, etc) | Minimal (Frida-go, color, cobra) |
| Deployment | Requires Python runtime | Single executable |
| Memory Usage | Higher | Lower |
| Event Handling | Complex async/queue system | Simple immediate sending |
| API Integration | Batching/buffering | Fire-and-forget |

## Configuration

Environment variables (optional):
- `OSPULSE_API_ENDPOINT`: Default API endpoint
- `OSPULSE_API_KEY`: Default API key

Command-line flags take precedence over environment variables.