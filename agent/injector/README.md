# OS-Pulse Injector

The **Frida TypeScript agent** component of the OS-Pulse system. This module performs dynamic instrumentation of Windows API calls to monitor file operations and process creation activities in real-time.

## 🎯 Purpose

The injector is a sophisticated Frida agent that:
- **Hooks Windows APIs**: Intercepts ReadFile, WriteFile, and NtCreateUserProcess calls
- **Extracts Content**: Captures file content and process parameters
- **Sends Events**: Communicates with the controller via Frida's messaging system
- **Modular Design**: Easy to extend with additional monitoring capabilities

## 🏗️ Architecture

```
Target Process (notepad.exe)
├── ReadFile/WriteFile hooks ──┐
├── NtCreateUserProcess hooks ─┤
└── Memory operations ─────────┤
                               │
                               ▼
                    ┌─────────────────┐
                    │ Frida Agent     │
                    │ (_agent.js)     │
                    ├─────────────────┤
                    │ • File Monitor  │
                    │ • Process Mon.  │
                    │ • Event Sender  │
                    │ • Console Log   │
                    └─────────────────┘
                               │
                               ▼ send()
                    ┌─────────────────┐
                    │   Controller    │
                    │   (Python)      │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Node.js 16+** and npm
- **Python 3.8+** with Frida
- **Windows** target system

### Build the Agent

```bash
# Install dependencies
npm install

# Build the agent (creates _agent.js)
npm run build

# Or build in watch mode for development
npm run watch
```

### Test the Agent

The agent is designed to be used with the controller, but you can test it directly:

```bash
# Activate Python environment (from project root)
cd ..
& .\.pyenv\Scripts\Activate.ps1

# Attach to notepad (if running)
frida -n notepad.exe -l injector\_agent.js --no-pause

# Or spawn notepad with agent
frida -f "C:\Windows\System32\notepad.exe" -l injector\_agent.js --no-pause
```

## 📁 Source Structure

```
src/
├── index.ts              # Entry point and configuration
├── core/
│   └── system-monitor.ts # Main orchestrator
├── monitors/            # API hooking implementations
│   ├── file-operations.ts   # ReadFile/WriteFile hooks
│   └── process-creation.ts  # NtCreateUserProcess hooks
├── messaging/           # Event communication
│   └── event-sender.ts      # Frida send() wrapper
├── logging/             # Console output
│   └── console-logger.ts    # Structured logging
├── utils/               # Utilities
│   └── windows-api.ts       # Windows API helpers
└── types/
    └── index.ts             # TypeScript interfaces
```

## ⚙️ Configuration

Configure monitoring behavior in `src/index.ts`:

```typescript
const config: Partial<HookConfiguration> = {
    enableFileOperations: true,     // Monitor file I/O
    enableProcessCreation: true,    // Monitor process creation
    maxContentLength: 512,          // Max bytes to extract
    logBinaryData: false           // Log binary data as hex
};
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enableFileOperations` | boolean | `true` | Enable file I/O monitoring |
| `enableProcessCreation` | boolean | `true` | Enable process creation monitoring |
| `maxContentLength` | number | `512` | Maximum content bytes to capture |
| `logBinaryData` | boolean | `false` | Whether to log binary data as hex |

## 🔍 Monitoring Details

### File Operations Monitor
**APIs Hooked:**
- `kernel32.dll!ReadFile`
- `kernel32.dll!WriteFile`

**Captured Data:**
- File handle and resolved path
- Bytes transferred
- File content (up to `maxContentLength`)
- Operation timestamp

**Example Output:**
```json
{
  "type": "file_operation",
  "operation": "WriteFile",
  "data": {
    "handle": "0x12345678",
    "filePath": "C:\\Users\\user\\document.txt",
    "bytesTransferred": 256,
    "content": "Hello, World!",
    "timestamp": "2025-09-09T12:00:01.000Z"
  }
}
```

### Process Creation Monitor
**APIs Hooked:**
- `ntdll.dll!NtCreateUserProcess`
- `ntdll.dll!NtCreateProcess`
- `ntdll.dll!NtCreateProcessEx`

**Captured Data:**
- Process and thread handles
- Image path and command line
- Current directory
- Process creation flags
- Status codes

**Example Output:**
```json
{
  "type": "process_creation",
  "operation": "NtCreateUserProcess",
  "data": {
    "processHandle": "0x87654321",
    "imagePath": "C:\\Windows\\System32\\calc.exe",
    "commandLine": "calc.exe",
    "status": 0,
    "timestamp": "2025-09-09T12:00:02.000Z"
  }
}
```

## 🔧 Development

### Building and Testing

```bash
# Development build with watch
npm run watch

# Production build
npm run build

# Check TypeScript compilation
npx tsc --noEmit
```

### Adding New Monitors

1. Create monitor class in `src/monitors/`
2. Implement the monitoring interface
3. Add Frida interceptors for target APIs
4. Export from `src/monitors/index.ts`
5. Initialize in `SystemMonitor`

Example monitor structure:
```typescript
export class CustomMonitor {
    constructor(
        private logger: Logger,
        private config: HookConfiguration,
        private eventSender: EventSender
    ) {}

    initialize(): void {
        this.hookTargetAPI();
    }

    private hookTargetAPI(): void {
        const api = Process.getModuleByName("dll").findExportByName("API");
        Interceptor.attach(api, {
            onEnter: function(args) {
                // Capture parameters
            },
            onLeave: function(retval) {
                // Process results and send events
            }
        });
    }
}
```

### Message Communication

The agent uses Frida's native messaging system:

```typescript
// Send event to controller
send({
    type: 'custom_event',
    data: { ... },
    metadata: {
        sessionId: this.sessionId,
        processName: this.processName,
        processId: this.processId
    }
});

// Receive commands from controller
recv('command', (message) => {
    // Handle command
});
```

## 🐛 Debugging

### Console Logging
The agent outputs structured logs to console:
```
[INFO] Starting Windows System Monitor
[WriteFile] Path: C:\test.txt, Bytes: 13
[ERROR] Failed to resolve file path: Invalid handle
```

### Error Handling
All hooks are wrapped in try-catch blocks to prevent crashes:
```typescript
try {
    // Risky operation
    const result = dangerousOperation();
} catch (error) {
    this.logger.error(`Operation failed: ${error}`);
    // Continue execution
}
```

### Memory Safety
- All pointer operations are null-checked
- Memory access is wrapped in error handlers
- Buffer reads respect size limits

## 🛡️ Security Notes

- **Process Injection**: Requires appropriate privileges
- **API Hooking**: May trigger antivirus software
- **Content Capture**: May expose sensitive data
- **System Impact**: Minimal performance overhead

## 📊 Performance

- **Hook Overhead**: ~1-5μs per API call
- **Memory Usage**: ~1-2MB additional per process
- **Content Capture**: Configurable limits prevent memory exhaustion
- **Error Resilience**: Failed operations don't crash the agent

## 🔮 Future Enhancements

Planned monitoring capabilities:
- **Network Operations**: WinSock API hooks
- **Registry Operations**: RegCreateKey, RegSetValue
- **Memory Operations**: VirtualAlloc, HeapAlloc
- **Thread Operations**: CreateThread, SetThreadContext

## 🤝 Integration

This injector is designed to work with:
- **OS-Pulse Controller**: Python-based process manager
- **External APIs**: JSON event streaming
- **Monitoring Systems**: SIEM, logging platforms
- **Analysis Tools**: Behavioral analysis engines

### Development Workflow

```powershell
# Watch mode for continuous compilation
npm run watch

# Run with custom target
.\run-frida.ps1 -Target "calc.exe"

# Spawn new process instead of attaching
.\run-frida.ps1 -Target "notepad.exe" -Spawn
```

## ⚙️ Configuration

Customize monitoring behavior in `src/index.ts`:

```typescript
const config: Partial<HookConfiguration> = {
    enableFileOperations: true,     // Monitor file I/O
    enableProcessCreation: true,    // Monitor process creation
    maxContentLength: 512,          // Max content to log
    logBinaryData: false           // Log binary data as hex
};
```

## 📁 Project Structure

```
src/
├── core/system-monitor.ts       # Main orchestrator
├── monitors/
│   ├── file-operations.ts       # ReadFile/WriteFile monitoring
│   └── process-creation.ts      # Process creation monitoring
├── logging/console-logger.ts    # Structured logging
├── utils/windows-api.ts         # Windows API utilities
├── types/index.ts              # Type definitions
└── index.ts                    # Entry point
```

## 🔧 Features

### File Operations Monitoring
- **ReadFile/WriteFile** API interception
- **Content extraction** with configurable limits
- **Binary data** handling (hex output optional)
- **File path resolution** from handles

### Process Creation Monitoring
- **NtCreateUserProcess** tracking
- **NtCreateProcess/NtCreateProcessEx** support
- **Command line extraction** from process parameters
- **Process metadata** logging

### Clean Architecture
- **TypeScript** with full type safety
- **Modular design** following SOLID principles
- **Error handling** with graceful fallbacks
- **VS Code integration** with debug configurations

## 🛠️ Development

### Adding New Monitors
1. Create monitor in `src/monitors/`
2. Export from `src/monitors/index.ts`
3. Add to `SystemMonitor` in `src/core/`

### Custom Configuration
```typescript
interface HookConfiguration {
    enableFileOperations: boolean;
    enableProcessCreation: boolean;
    maxContentLength: number;
    logBinaryData: boolean;
}
```

### VS Code Debug
Use the included debug configurations for easy development and testing.

## 📊 Example Output

```
[FILE-READ] notepad.exe | C:\Users\user\document.txt | Content: Hello World...
[PROCESS-CREATE] explorer.exe | Command: "C:\Windows\System32\calc.exe"
[FILE-WRITE] calc.exe | C:\Users\user\AppData\Local\temp.dat | Size: 1024 bytes
```

## 🔄 Migration & Compatibility

This project evolved from a simple Frida script to a comprehensive monitoring platform:
- **Enterprise-ready** codebase
- **Maintainable** modular architecture  
- **Extensible** for additional monitoring needs

## 📝 Author

**jahangir1x** - Windows system monitoring with Frida

---

Built with ❤️ for the OS-Pulse monitoring platform
