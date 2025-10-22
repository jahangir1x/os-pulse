# GitHub Copilot Instructions for OS-Pulse

## Project Overview

**OS-Pulse** is a sophisticated Windows system monitoring framework with enterprise-grade API integration capabilities. The system provides real-time monitoring of file operations and process creation activities through dynamic instrumentation, with comprehensive event forwarding to external analytics platforms.

### 🏗️ Enhanced Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Controller    │    │    Injector     │    │ Target Process  │    │  External APIs  │
│   (Python)      │    │ (TypeScript/JS) │    │   (notepad.exe) │    │ (SIEM/Analytics)│
├─────────────────┤    ├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Process Mgmt  │    │ • File Hooks    │    │ • ReadFile()    │    │ • Elasticsearch │
│ • Event Display │◄──►│ • Process Hooks │    │ • WriteFile()   │    │ • Splunk        │
│ • API Client    │    │ • Event Sender  │    │ • NtCreateProc()│◄──►│ • Custom APIs   │
│ • Async Queue   │    │ • Frida send()  │    │ • Hooked APIs   │    │ • Threat Intel  │
│ • Batch Process │    │ • Error Handler │    │                 │    │ • Dashboards    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🎯 Core Capabilities
- **Real-time Windows API monitoring** through dynamic instrumentation with Frida
- **File operation tracking** (ReadFile/WriteFile with intelligent content extraction)
- **Process creation monitoring** (NtCreateUserProcess and legacy APIs)
- **Event streaming** from injector to controller via Frida messaging
- **🆕 API Integration** - Simple HTTP client for immediate external API forwarding (no queuing/buffering)
- **🆕 Enterprise Features** - SIEM integration, analytics pipelines, and threat detection platforms
- **🚧 Go Controller** - Future Go-based alternative controller implementation
- **Extensible architecture** for additional monitoring capabilities

## Component Details

### 1. Injector (`injector/`)
**Technology**: TypeScript compiled to JavaScript via `frida-compile`
**Runtime**: Frida JavaScript engine injected into Windows processes
**Platform**: Windows (32-bit and 64-bit processes)

#### Key Characteristics
- **Modular Design**: Clean separation of concerns with dependency injection
- **Type Safety**: Full TypeScript with strict mode and modern ES2022 features
- **Performance**: Minimal overhead API hooking with configurable content limits
- **Error Resilience**: Comprehensive error handling to prevent target process crashes
- **Event Streaming**: Structured JSON events with rich metadata for external processing

#### Module Structure
```
injector/src/
├── index.ts                 # Entry point with configuration
├── core/
│   └── system-monitor.ts    # Main orchestrator and lifecycle manager
├── monitors/               # API hooking implementations
│   ├── file-operations.ts  # ReadFile/WriteFile hooks with path resolution
│   └── process-creation.ts # NtCreateUserProcess hooks with parameter extraction
├── messaging/
│   └── event-sender.ts     # Frida send() wrapper for host communication
├── logging/
│   └── console-logger.ts   # Structured console output with color coding
├── utils/
│   └── windows-api.ts      # Windows API utilities and memory operations
└── types/
    └── index.ts           # TypeScript interfaces and type definitions
```

#### Windows API Monitoring
- **File Operations** (`kernel32.dll`):
  - `ReadFile`: File read operations with content extraction and path resolution
  - `WriteFile`: File write operations with content extraction and path resolution
  - Features: Handle-to-path resolution, binary data handling, configurable limits, smart content filtering

- **Process Creation** (`ntdll.dll`):
  - `NtCreateUserProcess`: Modern Windows process creation (Vista+)
  - `NtCreateProcess`: Legacy process creation
  - `NtCreateProcessEx`: Extended process creation with flags
  - Features: Command line extraction, process parameters, parent-child relationships, status tracking

#### Build System
```bash
npm run build    # TypeScript → _agent.js via frida-compile
npm run watch    # Continuous compilation for development
npm run type-check # TypeScript validation without compilation
```

### 2. Controller (`controller/`)
**Technology**: Python 3.8+ with Frida libraries and async HTTP client
**Purpose**: Process management, event processing, and API integration hub

#### Key Characteristics
- **CLI Interface**: Comprehensive argparse-based command system
- **Process Management**: Spawn new processes or attach to existing ones
- **Event Processing**: Real-time message handling with colorful console output
- **🆕 API Integration**: Async HTTP client with batching, retry logic, and health monitoring
- **🆕 External Connectivity**: SIEM, log aggregation, and analytics platform integration
- **Performance Optimized**: Non-blocking operations with configurable batch processing

#### Enhanced Module Structure
```
controller/
├── 🐍 Core Components
│   ├── main.py              # CLI entry point with argparse
│   ├── frida_controller.py  # Core Frida session management with async cleanup
│   ├── message_handler.py   # Event processing, display, and API forwarding
│   └── config.py           # Configuration management with environment variables
├── 🌐 API Integration (SIMPLIFIED)
│   ├── api_client.py        # Async HTTP client (legacy - still functional)
│   ├── message_handler.py   # Now uses requests library for immediate sending
│   ├── test_api_integration.py # Comprehensive API integration test suite
│   ├── test_api_server.py   # Mock Flask API server for testing
│   └── API_INTEGRATION.md   # Comprehensive API integration documentation
├── 🚧 Future Go Controller
│   ├── main.go             # CLI entry point with Cobra
│   ├── frida_controller.go # Frida session management
│   ├── message_handler.go  # Event processing & API forwarding
│   ├── go.mod              # Go module dependencies
│   └── README.md           # Go controller documentation
├── 🧪 Testing & Validation
│   ├── test_controller.py   # Core functionality test suite
│   └── test-api.bat        # Quick API integration test script
├── 🚀 Quick Launchers
│   ├── setup.bat           # Automated environment setup
│   ├── spawn-notepad.bat   # Quick spawn launcher
│   └── attach-notepad.bat  # Quick attach launcher
└── 📦 Dependencies
    └── requirements.txt     # Python dependencies (includes requests, aiohttp, flask)
```

## Development Workflows

### Injector Development
```bash
cd injector
npm install              # Install dependencies
npm run build           # Build _agent.js
npm run watch           # Development mode with auto-rebuild
npm run type-check      # TypeScript validation
```

### Controller Development
```bash
cd controller
setup.bat               # One-time setup (creates .pyenv, installs deps)
.\.pyenv\Scripts\activate.bat
python test_controller.py  # Validate setup
python test_api_integration.py # Test API integration
python main.py --help   # Explore CLI options
```

### Integration Testing
```bash
# Terminal 1: Build injector with watch mode
cd injector && npm run watch

# Terminal 2: Start test API server
cd controller && python test_api_server.py

# Terminal 3: Run controller with API integration
cd controller
$env:OSPULSE_API_ENABLED="true"
$env:OSPULSE_API_ENDPOINT="http://localhost:8080/api/events"
python main.py spawn --executable "C:\Windows\System32\notepad.exe"
```

## 🆕 API Integration Features (SIMPLIFIED)

### Configuration Management

**Environment Variables:**
```powershell
# API Integration (Simplified)
$env:OSPULSE_API_ENABLED="true"           # Enable API forwarding
$env:OSPULSE_API_ENDPOINT="http://..."    # API endpoint URL
$env:OSPULSE_API_KEY="your-key"           # Authentication key
$env:OSPULSE_API_TIMEOUT="10"             # Request timeout (seconds)

# Logging
$env:OSPULSE_LOG_LEVEL="DEBUG"            # DEBUG, INFO, WARNING, ERROR
```

**Configuration in `controller/config.py`:**
```python
# API Configuration with environment variable fallbacks
api_enabled: bool = os.getenv('OSPULSE_API_ENABLED', 'false').lower() == 'true'
api_endpoint: str = os.getenv('OSPULSE_API_ENDPOINT', '')
api_key: str = os.getenv('OSPULSE_API_KEY', '')
api_timeout: int = int(os.getenv('OSPULSE_API_TIMEOUT', '10'))
api_retry_count: int = int(os.getenv('OSPULSE_API_RETRY_COUNT', '3'))
api_retry_delay: int = int(os.getenv('OSPULSE_API_RETRY_DELAY', '1'))
api_batch_size: int = int(os.getenv('OSPULSE_API_BATCH_SIZE', '10'))
api_batch_timeout: int = int(os.getenv('OSPULSE_API_BATCH_TIMEOUT', '5'))
```

### API Client Architecture (`controller/api_client.py`)

**AsyncHttpClient Features:**
- **Async Operations**: Non-blocking HTTP requests using aiohttp
- **Batch Processing**: Configurable event batching for optimal performance
- **Retry Logic**: Exponential backoff with configurable retry attempts
- **Health Monitoring**: Connection testing and performance statistics
- **Error Handling**: Graceful degradation on API failures

**Key Classes:**
```python
class ApiClient:
    """Async HTTP client for external API integration"""
    
    async def send_event(self, event: Dict[str, Any]) -> bool
    async def send_file_operation(self, operation: str, file_path: str, ...) -> bool
    async def send_process_creation(self, operation: str, command_line: str, ...) -> bool
    async def flush_events(self) -> int
    async def get_stats(self) -> Dict[str, Any]
    async def test_connection(self) -> bool
    async def disconnect(self) -> None

class ApiClientManager:
    """Global API client lifecycle manager"""
    
    def get_client(self) -> Optional[ApiClient]
    async def initialize_client(self, endpoint: str, api_key: str) -> ApiClient
    async def shutdown_all(self) -> None
```

### Message Handler Integration (`controller/message_handler.py`)

**Simplified MessageHandler Features:**
- **Simple HTTP Integration**: Uses requests library for immediate event forwarding
- **Dual Output**: Console display + API forwarding simultaneously
- **Event Enrichment**: Adds metadata and timestamps to events
- **Background Threading**: Non-blocking event sending via daemon threads
- **Error Resilience**: Graceful handling of API failures without blocking monitoring

**Key Methods:**
```python
class MessageHandler:
    def _send_to_api(self, event_type: str, event_data: Dict[str, Any]) -> None
    def _send_api_event(self, event_type: str, event_data: Dict[str, Any]) -> None
    def shutdown(self) -> None
    def flush_api_events(self) -> int  # No-op since no buffering
```

## Message Flow and Communication

### Event Communication Pattern
1. **Injector** hooks Windows APIs using Frida interceptors
2. **Event Data** is structured with rich metadata and sent via `send()` to host
3. **Controller** receives events through Frida message handlers
4. **Message Handler** processes events for console display AND API forwarding
5. **🆕 HTTP Client** sends events immediately to external APIs with fire-and-forget pattern
6. **🆕 External Systems** receive structured events for analysis and storage

### Enhanced Event Structure
```typescript
// File operation event with rich metadata
{
  type: 'file_operation',
  operation: 'WriteFile',
  data: {
    handle: '0x12345678',
    filePath: 'C:\\Users\\user\\document.txt',
    bytesTransferred: 256,
    content: 'Hello, World!',
    timestamp: '2025-09-11T12:00:01.000Z'
  },
  metadata: {
    sessionId: 'session-abc123',
    processName: 'notepad.exe',
    processId: 1234,
    environment: 'production',
    datacenter: 'dc1'
  }
}

// Process creation event with command line details
{
  type: 'process_creation',
  operation: 'NtCreateUserProcess',
  data: {
    processHandle: '0x87654321',
    threadHandle: '0x12345678',
    processId: 5678,
    threadId: 9999,
    imagePath: 'C:\\Windows\\System32\\calc.exe',
    commandLine: 'calc.exe',
    currentDirectory: 'C:\\Users\\user',
    status: 0,
    timestamp: '2025-09-11T12:00:02.000Z'
  },
  metadata: {
    sessionId: 'session-abc123',
    processName: 'explorer.exe',
    processId: 1234
  }
}
```

### Bidirectional Communication
```typescript
// Controller → Injector (commands)
recv('ping', (message) => {
    send({ type: 'pong', timestamp: new Date().toISOString() });
});

recv('config_update', (message) => {
    const newConfig = message as HookConfiguration;
    systemMonitor.updateConfiguration(newConfig);
});

recv('get_status', (message) => {
    send({ 
        type: 'status_response', 
        data: {
            sessionId: sessionId,
            processName: Process.getCurrentProcess().name,
            processId: Process.getCurrentProcess().id,
            status: 'active',
            timestamp: new Date().toISOString()
        }
    });
});
```

## 🚧 Go Controller (Future Implementation)

### Overview
The `controller-go/` directory contains a future Go-based alternative to the Python controller, offering:

**Benefits:**
- **Single Executable**: No runtime dependencies - just copy and run
- **Better Performance**: Compiled native performance vs interpreted Python
- **Lower Memory Usage**: More efficient resource utilization
- **Simpler Deployment**: No Python environment or virtual environment setup needed

**Architecture:**
```go
// main.go - CLI interface using Cobra
func main() {
    rootCmd := &cobra.Command{
        Use: "os-pulse",
        Short: "OS-Pulse Windows System Monitor Controller",
    }
    rootCmd.AddCommand(createSpawnCommand(), createAttachCommand())
    rootCmd.Execute()
}

// frida_controller.go - Core Frida session management
type FridaController struct {
    deviceManager *frida.DeviceManager
    session       *frida.Session
    script        *frida.Script
    messageHandler *MessageHandler
}

// message_handler.go - Event processing with immediate API forwarding
type MessageHandler struct {
    httpClient  *http.Client
    apiEnabled  bool
    apiEndpoint string
}
```

**Current Status:**
- ✅ Project structure and CLI interface complete
- ✅ HTTP client for API integration implemented
- ✅ Message handler with immediate sending (no buffering)
- 🚧 Frida Go bindings integration (pending stable release)
- 🚧 Complete feature parity with Python controller

**Usage (When Complete):**
```bash
cd controller-go
go build -o os-pulse.exe
./os-pulse.exe spawn -e "C:\Windows\System32\notepad.exe" --enable-api
```

## 🆕 Testing and Validation Infrastructure

### API Integration Testing (`controller/test_api_integration.py`)

**Comprehensive Test Suite:**
```python
async def test_api_client():
    """Test basic API client functionality with mock endpoints"""
    # Tests: event sending, file operations, process creation, stats, health checks

async def test_message_handler():
    """Test message handler with API integration"""
    # Tests: API initialization, event processing, statistics, lifecycle management

async def main():
    """Complete integration test suite"""
    # Validates end-to-end API integration workflow
```

### Mock API Server (`controller/test_api_server.py`)

**Flask-based Test Server:**
- **Event Reception**: Receives and validates OS-Pulse events
- **Real-time Display**: Color-coded console output for received events
- **Statistics Tracking**: Event counts, types, and performance metrics
- **Health Endpoints**: `/api/health`, `/api/events`, `/api/events/clear`
- **RESTful API**: Standard HTTP endpoints for integration testing

### Quick Test Scripts

**`controller/test-api.bat`:**
```batch
@echo off
REM Quick API integration test with environment setup
set OSPULSE_API_ENABLED=true
set OSPULSE_API_ENDPOINT=http://localhost:8080/api/events
set OSPULSE_API_KEY=test-key

call .\.pyenv\Scripts\activate.bat
python test_api_integration.py
```

## Common Development Patterns

### Error Handling Strategy
```typescript
// Injector: Graceful degradation without target process crashes
try {
    const result = riskyWindowsAPIOperation();
    this.eventSender.sendFileOperation('ReadFile', result);
} catch (error) {
    this.logger.error(`Operation failed: ${error}`);
    // Continue execution - don't crash target process
}
```

```python
# Controller: Comprehensive error reporting with API failover
try:
    success = await self.api_client.send_event(event)
    if not success:
        self.logger.warning("API send failed, event queued for retry")
except Exception as e:
    self.logger.error(f"API client error: {e}")
    # Event still displayed in console, API failure doesn't block monitoring
```

### Memory Safety Patterns
```typescript
// Always check for null pointers with enhanced validation
if (!pointer.isNull() && this.isValidMemoryRange(pointer, size)) {
    try {
        const content = buffer.readUtf8String(size);
        // Process content with configurable limits
        const truncatedContent = this.truncateContent(content, this.config.maxContentLength);
    } catch (error) {
        this.logger.error(`Memory read failed: ${error}`);
    }
}
```

### Simple Integration Patterns
```python
# Immediate API sending using requests in background thread
def _send_to_api(self, event_type: str, data: Dict[str, Any]):
    """Send event to API immediately using requests (simple approach)"""
    if not self.api_enabled or not self.session:
        return
        
    # Fire and forget - run in background thread
    def send_in_thread():
        try:
            self._send_api_event(event_type, data)
        except Exception as e:
            print(f"{Fore.YELLOW}[API] Send failed: {e}")
    
    # Start background thread for immediate sending
    thread = threading.Thread(target=send_in_thread, daemon=True)
    thread.start()

def _send_api_event(self, event_type: str, data: Dict[str, Any]):
    """Send single event to API immediately using requests"""
    try:
        # Prepare event payload
        payload = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': 'os-pulse-controller',
            'data': data
        }
        
        # Send POST request
        response = self.session.post(
            f"{self.api_endpoint}/events",
            json=payload,
            timeout=config.api_timeout
        )
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}[API] Sent {event_type} event successfully")
    except requests.exceptions.ConnectionError:
        print(f"{Fore.YELLOW}[API] Connection failed - dropping {event_type} event")
    except Exception as e:
        print(f"{Fore.YELLOW}[API] Failed to send {event_type}: {e}")
```

### Configuration Management Patterns
```python
# Environment-based configuration with sensible defaults
class Config:
    def __init__(self):
        self.api_enabled = self._get_bool_env('OSPULSE_API_ENABLED', False)
        self.api_endpoint = os.getenv('OSPULSE_API_ENDPOINT', '')
        self.api_key = os.getenv('OSPULSE_API_KEY', '')
        self.api_batch_size = self._get_int_env('OSPULSE_API_BATCH_SIZE', 10)
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        return os.getenv(key, str(default)).lower() in ('true', '1', 'yes')
    
    def _get_int_env(self, key: str, default: int) -> int:
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
```

## Performance Considerations

### Injector Performance
- **Low Overhead**: API hooks add ~1-5μs per call (measured)
- **Memory Efficient**: Configurable content limits prevent exhaustion
- **Selective Monitoring**: Disable unused monitors for optimal performance
- **Smart Content Extraction**: Only capture content when needed, skip binary when configured

### Controller Performance
- **Real-time Processing**: Minimal latency event display (<1ms per event)
- **Memory Usage**: ~5-10MB for controller process, ~2-5MB for API client buffers
- **Async Operations**: Non-blocking API calls don't impact console responsiveness
- **Batch Optimization**: Configurable batching reduces HTTP overhead

### API Integration Performance
- **Batch Processing**: 10-100 events per HTTP request (configurable)
- **Connection Pooling**: Reuses HTTP connections for efficiency
- **Retry Logic**: Exponential backoff prevents API server overload
- **Health Monitoring**: Automatic connection testing and recovery

## Security and Deployment

### Security Considerations
- **Elevated Privileges**: May require Administrator rights for system processes
- **Data Sensitivity**: File content monitoring may capture sensitive information
- **Process Injection**: Inherently requires code injection capabilities
- **Antivirus Compatibility**: May trigger security software alerts
- **🆕 API Security**: HTTPS endpoints, secure API key management, network security

### Deployment Patterns
- **Development**: Watch mode with continuous rebuilding and local API server
- **Testing**: Isolated virtual environments with mock API endpoints
- **Production**: Compiled agents with minimal logging, HTTPS APIs, and monitoring dashboards

### 🆕 API Security Best Practices
```powershell
# Use HTTPS in production
$env:OSPULSE_API_ENDPOINT="https://secure-api.company.com/events"

# Secure API key management
$env:OSPULSE_API_KEY="your-secure-random-key"

# Network security considerations
# - Firewall rules for API endpoints
# - VPN connections for sensitive environments
# - Rate limiting on API servers
# - Authentication and authorization
```

## Future Architecture Extensions

### Planned Enhancements
- **🆕 Database Integration**: SQLite/PostgreSQL for historical event analysis
- **🆕 Web Dashboard**: React-based real-time event visualization
- **🆕 Alert System**: Rule-based suspicious activity detection with API notifications
- **Multi-Process**: Simultaneous monitoring of multiple target processes
- **🆕 Plugin Architecture**: Dynamic loading of custom API integrations
- **🆕 Stream Processing**: Real-time event analysis with Apache Kafka integration

### 🆕 Advanced API Integration Patterns
```python
# Future: Multiple API destinations with routing
class ApiRouter:
    def __init__(self):
        self.siem_client = ApiClient("https://siem.company.com/events")
        self.analytics_client = ApiClient("https://analytics.company.com/events")
        self.threat_intel_client = ApiClient("https://threatintel.company.com/iocs")
    
    async def route_event(self, event: Dict[str, Any]) -> None:
        # Route different event types to different systems
        if event['type'] == 'file_operation':
            await self.siem_client.send_event(event)
        elif event['type'] == 'process_creation':
            await self.analytics_client.send_event(event)
        
        # Send all events to analytics
        await self.analytics_client.send_event(event)

# Future: Real-time threat detection
class ThreatDetector:
    async def analyze_event(self, event: Dict[str, Any]) -> Optional[ThreatAlert]:
        if self.is_suspicious_file_access(event):
            return ThreatAlert(
                severity='high',
                description='Suspicious file access detected',
                event=event,
                recommendations=['Isolate process', 'Collect memory dump']
            )
```

### Additional Monitoring Capabilities
- **🆕 Network Operations**: WinSock API monitoring for network I/O with packet analysis
- **🆕 Registry Operations**: RegCreateKey, RegSetValue, RegDeleteKey tracking with change detection
- **🆕 Memory Operations**: VirtualAlloc, HeapAlloc, memory protection changes with injection detection
- **🆕 Thread Operations**: CreateThread, SetThreadContext, thread manipulation with injection analysis
- **🆕 Service Operations**: Service creation, modification, and control with persistence detection
- **🆕 Driver Operations**: Driver loading and system call monitoring with rootkit detection

## AI Assistant Guidelines

### When Working with This Codebase
1. **Understand the Dual Architecture**: Always consider both injector (TypeScript/Frida) and controller (Python) components
2. **🆕 Consider API Integration**: New features should integrate with the async API client when applicable
3. **Respect Performance**: API hooking has performance implications - optimize carefully
4. **Handle Errors Gracefully**: Failed hooks shouldn't crash target processes, failed API calls shouldn't block monitoring
5. **Maintain Type Safety**: Use TypeScript features to prevent runtime errors in injector
6. **🆕 Follow Async Patterns**: Use proper async/await patterns for API operations
7. **Consider Security**: Changes affect running processes and may handle sensitive data

### Code Style Preferences
- **Explicit Types**: Prefer explicit type annotations for clarity in TypeScript and Python
- **Comprehensive Error Handling**: Always wrap risky operations in try-catch
- **🆕 Async Best Practices**: Use proper async/await patterns, avoid blocking operations
- **Consistent Naming**: Use descriptive names following established conventions
- **Modular Design**: Keep classes focused on single responsibilities
- **Documentation**: Comment complex Windows API interactions and memory operations

### File Modification Guidelines
- **Build Process**: Remember TypeScript compiles to `_agent.js` - test the compiled output
- **🆕 API Integration**: New event types should be forwarded to the API client when applicable
- **Configuration**: Interface changes may require updates in multiple files
- **Dependencies**: Be cautious with new dependencies, especially in Frida context
- **Cross-Component**: Changes in injector events may require controller updates

### Testing Requirements
- **Injector**: Always test with actual Windows processes after compilation
- **Controller**: Use the test suite and manual validation with real processes
- **🆕 API Integration**: Test with mock API server and validate event forwarding
- **Integration**: Verify end-to-end message flow between components
- **Performance**: Monitor for performance regressions in API hooking and HTTP operations

### 🆕 API Integration Development Guidelines
- **Environment Configuration**: Use environment variables for API settings
- **Non-blocking Operations**: API calls should never block console output or monitoring
- **Error Resilience**: API failures should not stop monitoring or crash the application
- **No Queuing/Buffering**: Events are sent immediately using fire-and-forget pattern
- **Security**: Always use HTTPS in production and secure API key management
- **Testing**: Use the provided mock API server for development and testing

### 🚧 Go Controller Development Guidelines
- **Future Implementation**: The Go controller in `controller-go/` is a future alternative
- **Frida Go Bindings**: Requires stable Frida Go bindings for completion
- **CLI Compatibility**: Should maintain identical CLI interface to Python controller
- **Performance Focus**: Emphasize single executable and performance benefits
- **API Integration**: Maintains same immediate-sending pattern as simplified Python controller

---

This comprehensive context enables AI assistants to understand the complete OS-Pulse architecture including the simplified API integration approach and future Go controller implementation, providing accurate assistance for development, debugging, and enhancement tasks across both current and future components.

## Development Workflows

### Injector Development
```bash
cd injector
npm install              # Install dependencies
npm run build           # Build _agent.js
npm run watch           # Development mode with auto-rebuild
```

### Controller Development
```bash
cd controller
setup.bat               # One-time setup (creates .venv, installs deps)
.venv\Scripts\activate.bat
python test_controller.py  # Validate setup
python main.py --help   # Explore CLI options
```

### Integration Testing
```bash
# Terminal 1: Build injector
cd injector && npm run watch

# Terminal 2: Run controller
cd controller
python main.py spawn --executable "C:\Windows\System32\notepad.exe"
```

## Configuration Management

### Injector Configuration
```typescript
// injector/src/index.ts
const config: Partial<HookConfiguration> = {
    enableFileOperations: true,     // Monitor file I/O
    enableProcessCreation: true,    // Monitor process creation
    maxContentLength: 512,          // Bytes limit for content extraction
    logBinaryData: false           // Whether to log binary data as hex
};
```

### Controller Configuration
```python
# Environment variables
OSPULSE_LOG_LEVEL=DEBUG
OSPULSE_API_ENDPOINT=http://localhost:8080/api/events
OSPULSE_API_KEY=your-api-key
```

## Message Flow and Communication

### Event Communication Pattern
1. **Injector** hooks Windows APIs using Frida interceptors
2. **Event Data** is structured and sent via `send()` to host
3. **Controller** receives events through Frida message handlers
4. **Message Handler** processes and displays events with color coding
5. **Future API** integration will forward events to external systems

### Event Structure
```typescript
// File operation event
{
  type: 'file_operation',
  operation: 'WriteFile',
  data: {
    handle: '0x12345678',
    filePath: 'C:\\Users\\user\\document.txt',
    bytesTransferred: 256,
    content: 'Hello, World!',
    timestamp: '2025-09-09T12:00:01.000Z'
  },
  metadata: {
    sessionId: 'session-123',
    processName: 'notepad.exe',
    processId: 1234
  }
}
```

### Bidirectional Communication
```typescript
// Controller → Injector
recv('ping', (message) => {
    send({ type: 'pong', timestamp: new Date().toISOString() });
});

recv('config_update', (message) => {
    // Handle configuration updates
});
```

## Common Development Patterns

### Error Handling Strategy
```typescript
// Injector: Graceful degradation
try {
    const result = riskyWindowsAPIOperation();
    this.eventSender.sendFileOperation('ReadFile', result);
} catch (error) {
    this.logger.error(`Operation failed: ${error}`);
    // Continue execution - don't crash target process
}
```

```python
# Controller: Comprehensive error reporting
try:
    self.session = frida.attach(process_name)
except frida.ProcessNotFoundError:
    print(f"{Fore.RED}Process not found: {process_name}")
    return False
except Exception as e:
    print(f"{Fore.RED}Failed to attach: {e}")
    return False
```

### Memory Safety Patterns
```typescript
// Always check for null pointers
if (!pointer.isNull()) {
    const value = pointer.readU32();
}

// Use try-catch for memory operations
try {
    const content = buffer.readUtf8String(size);
} catch (error) {
    this.logger.error(`Memory read failed: ${error}`);
}
```

### TypeScript Best Practices
- **Strict null checks**: All pointers and optional values properly typed
- **Interface segregation**: Small, focused interfaces for specific purposes
- **Dependency injection**: Logger, configuration, and event sender injected into monitors
- **Path aliases**: Clean imports using `@/core`, `@/monitors`, etc.

## Testing and Validation

### Injector Testing
```bash
# Type checking without compilation
npm run type-check

# Manual testing with specific targets
frida -n notepad.exe -l _agent.js --no-pause
```

### Controller Testing
```bash
# Comprehensive test suite
python test_controller.py

# Manual testing with debug output
set OSPULSE_LOG_LEVEL=DEBUG
python main.py spawn --executable "C:\Windows\System32\notepad.exe"
```

### Integration Validation
1. Build injector and verify `_agent.js` exists
2. Run controller test suite
3. Spawn notepad and perform file operations
4. Verify events appear in controller console
5. Test interactive mode with ping/status commands

## Performance Considerations

### Injector Performance
- **Low Overhead**: API hooks add ~1-5μs per call
- **Memory Efficient**: Configurable content limits prevent exhaustion
- **Selective Monitoring**: Disable unused monitors for optimal performance
- **Smart Content Extraction**: Only capture content when needed

### Controller Performance
- **Real-time Processing**: Minimal latency event display
- **Memory Usage**: ~5-10MB for controller process
- **Scalability**: Designed for multiple simultaneous process monitoring

## Security and Deployment

### Security Considerations
- **Elevated Privileges**: May require Administrator rights for system processes
- **Data Sensitivity**: File content monitoring may capture sensitive information
- **Process Injection**: Inherently requires code injection capabilities
- **Antivirus Compatibility**: May trigger security software alerts

### Deployment Patterns
- **Development**: Watch mode with continuous rebuilding
- **Testing**: Isolated virtual environments with specific target processes
- **Production**: Compiled agents with minimal logging for performance

## Future Architecture Extensions

### Planned Enhancements
- **REST API Server**: Built-in web server in controller for external integration
- **Database Storage**: SQLite/PostgreSQL for historical event analysis
- **Web Dashboard**: React-based real-time event visualization
- **Alert System**: Rule-based suspicious activity detection
- **Multi-Process**: Simultaneous monitoring of multiple target processes

### API Integration Design
```python
# Future: REST API endpoints
@app.route('/api/events', methods=['POST'])
async def receive_events():
    event = await request.get_json()
    await process_monitoring_event(event)
    return {'status': 'received'}

@app.route('/api/processes', methods=['GET'])
async def list_monitored_processes():
    return {'processes': active_sessions}
```

### Additional Monitoring Capabilities
- **Network Operations**: WinSock API monitoring for network I/O
- **Registry Operations**: RegCreateKey, RegSetValue, RegDeleteKey tracking
- **Memory Operations**: VirtualAlloc, HeapAlloc, memory protection changes
- **Thread Operations**: CreateThread, SetThreadContext, thread manipulation

## AI Assistant Guidelines

### When Working with This Codebase
1. **Understand the Dual Architecture**: Always consider both injector (TypeScript/Frida) and controller (Python) components
2. **Respect Performance**: API hooking has performance implications - optimize carefully
3. **Handle Errors Gracefully**: Failed hooks shouldn't crash target processes
4. **Maintain Type Safety**: Use TypeScript features to prevent runtime errors in injector
5. **Consider Security**: Changes affect running processes and may handle sensitive data

### Code Style Preferences
- **Explicit Types**: Prefer explicit type annotations for clarity in TypeScript
- **Comprehensive Error Handling**: Always wrap risky operations in try-catch
- **Consistent Naming**: Use descriptive names following established conventions
- **Modular Design**: Keep classes focused on single responsibilities
- **Documentation**: Comment complex Windows API interactions and memory operations

### File Modification Guidelines
- **Build Process**: Remember TypeScript compiles to `_agent.js` - test the compiled output
- **Configuration**: Interface changes may require updates in multiple files
- **Dependencies**: Be cautious with new dependencies, especially in Frida context
- **Cross-Component**: Changes in injector events may require controller updates

### Testing Requirements
- **Injector**: Always test with actual Windows processes after compilation
- **Controller**: Use the test suite and manual validation with real processes
- **Integration**: Verify end-to-end message flow between components
- **Performance**: Monitor for performance regressions in API hooking

---

This comprehensive context should enable any AI assistant to understand the OS-Pulse architecture and provide accurate assistance for development, debugging, and enhancement tasks across both the injector and controller components.

### Key Interfaces

#### HookConfiguration
```typescript
interface HookConfiguration {
    enableFileOperations: boolean;    // Toggle file I/O monitoring
    enableProcessCreation: boolean;   // Toggle process creation monitoring
    maxContentLength: number;         // Bytes limit for content extraction
    logBinaryData: boolean;          // Whether to log binary data as hex
}
```

#### Logger Interface
```typescript
interface Logger {
    info(message: string): void;
    error(message: string): void;
    debug(message: string): void;
    logFileOperation(operation: string, info: FileOperationInfo): void;
    logProcessCreation(operation: string, info: ProcessCreationInfo): void;
}
```

## Windows API Monitoring

### File Operations (kernel32.dll)
- **ReadFile**: Monitors file read operations with content extraction
- **WriteFile**: Monitors file write operations with content extraction
- **Features**: Handle-to-path resolution, binary data handling, configurable content limits

### Process Creation (ntdll.dll)
- **NtCreateUserProcess**: Modern Windows process creation (Windows Vista+)
- **NtCreateProcess**: Legacy process creation
- **NtCreateProcessEx**: Extended process creation with additional flags
- **Features**: Command line extraction, process parameters, parent-child relationships

### API Hooking Strategy
```typescript
// Example hook pattern used throughout the codebase
Interceptor.attach(apiAddress, {
    onEnter: function(args) {
        // Capture input parameters
        this.param1 = args[0];
        this.param2 = args[1];
    },
    onLeave: function(retval) {
        // Process results and log
        monitor.handleApiResult(this, retval);
    }
});
```

## Development Environment

### Prerequisites Setup
```powershell
# Python virtual environment
python -m venv .pyenv
& .\.pyenv\Scripts\Activate.ps1
pip install -r requirements.txt

# Node.js dependencies
npm install
npm run build
```

### Development Workflow
1. **Watch Mode**: `npm run watch` for continuous TypeScript compilation
2. **Quick Testing**: `.\run-frida.ps1` for immediate testing
3. **VS Code Integration**: Debug configurations and tasks available
4. **Target Flexibility**: Attach to existing processes or spawn new ones

### Build System
- **TypeScript Config**: ES2022 target, strict mode, path aliases
- **Compilation**: `frida-compile` generates single `_agent.js` file
- **Watch Mode**: Automatic recompilation on file changes
- **VS Code Tasks**: Integrated build and run tasks

## Code Patterns and Conventions

### Error Handling
```typescript
try {
    // Risky operation
    const result = dangerousOperation();
    this.logger.info(`Success: ${result}`);
} catch (error) {
    this.logger.error(`Failed operation: ${error}`);
    // Graceful degradation - don't crash the entire agent
}
```

### Memory Safety
```typescript
// Always check for null pointers before dereferencing
if (!pointer.isNull()) {
    const value = pointer.readU32();
}

// Use try-catch for memory operations
try {
    const content = buffer.readUtf8String(size);
} catch (error) {
    // Handle invalid memory access
}
```

### TypeScript Patterns
- **Strict null checks**: All pointers and optional values properly typed
- **Path aliases**: `@/core`, `@/monitors`, etc. for clean imports
- **Interface segregation**: Small, focused interfaces
- **Readonly where appropriate**: Immutable data structures

## Configuration Management

### Default Configuration
```typescript
const defaultConfig: HookConfiguration = {
    enableFileOperations: true,
    enableProcessCreation: true,
    maxContentLength: 256,
    logBinaryData: false
};
```

### Runtime Configuration Updates
```typescript
monitor.updateConfig({
    maxContentLength: 1024,
    logBinaryData: true
});
```

### Performance Tuning
- **Low overhead**: `maxContentLength: 64, logBinaryData: false`
- **Full analysis**: `maxContentLength: 4096, logBinaryData: true`
- **Selective monitoring**: Disable unused monitors

## Execution Models

### Attach Mode (Default)
```powershell
frida -n notepad.exe -l _agent.js
```
- Attaches to existing running process
- Less intrusive, good for production monitoring

### Spawn Mode
```powershell
frida -f "C:\Windows\System32\notepad.exe" -l _agent.js
```
- Starts new process under monitoring
- Captures initialization behavior

## Common Development Tasks

### Adding New API Monitors
1. Create new monitor class in `src/monitors/`
2. Implement required interfaces (`Logger`, `HookConfiguration`)
3. Add Frida interceptors for target APIs
4. Export from `src/monitors/index.ts`
5. Initialize in `SystemMonitor` constructor
6. Add configuration options if needed

### Custom Logger Implementation
1. Implement `Logger` interface
2. Add to `src/logging/` directory
3. Export from `src/logging/index.ts`
4. Configure in `SystemMonitor` constructor

### Configuration Extensions
1. Extend `HookConfiguration` interface in `src/types/index.ts`
2. Update default configuration in `SystemMonitor`
3. Add validation logic if needed
4. Update documentation

## Testing and Debugging

### VS Code Integration
- **Launch Configurations**: Attach/spawn with different targets
- **Task Definitions**: Build, run, and test tasks
- **Debug Support**: Breakpoints work in TypeScript source

### Manual Testing
```powershell
# Test file operations
.\run-frida.ps1 -Target "notepad.exe"
# Open/save files in notepad to see monitoring

# Test process creation
.\run-frida.ps1 -Target "explorer.exe"
# Launch applications from Explorer
```

### Common Issues
- **Python Environment**: Ensure `.pyenv` is activated
- **Process Permissions**: Run as Administrator for system processes
- **Target Process**: Verify target process is running (attach mode)
- **Frida Version**: Match versions between Python and Node.js

## Performance Considerations

### Memory Usage
- **Smart Content Extraction**: Configurable limits prevent memory exhaustion
- **Lazy Evaluation**: Only resolve file paths when needed
- **Efficient String Handling**: UTF-16/UTF-8 conversion optimizations

### CPU Overhead
- **Selective Monitoring**: Disable unused monitors
- **Optimized Hooks**: Minimal work in `onEnter`, heavy lifting in `onLeave`
- **Error Resilience**: Failures don't cascade

### I/O Performance
- **Non-blocking Logging**: Console output doesn't block API calls
- **Structured Output**: Consistent format for parsing
- **Minimal File System Operations**: Direct memory access where possible

## Security Considerations

### Data Sensitivity
- **Content Extraction**: May capture sensitive data from file operations
- **Command Lines**: Process creation captures full command lines
- **Binary Data**: Optional hex logging may expose encrypted content

### Privilege Requirements
- **Process Attachment**: May require elevated privileges
- **System Processes**: Administrator rights needed for system process monitoring
- **API Hooking**: Inherently requires code injection capabilities

## Extension Points

### Future Monitor Types
- **Network Operations**: WinSock API monitoring
- **Registry Operations**: RegCreateKey, RegSetValue, etc.
- **Memory Operations**: VirtualAlloc, HeapAlloc tracking
- **Thread Operations**: CreateThread, SetThreadContext monitoring

### Advanced Features
- **Remote Logging**: Network-based log aggregation
- **Plugin System**: Dynamic monitor loading
- **Configuration Hot-reload**: Runtime configuration updates
- **Multi-process Coordination**: Cross-process event correlation

## Dependencies and Versions

### Python Dependencies (requirements.txt)
- `frida==17.2.17`: Core instrumentation framework
- `frida-tools==14.4.5`: Command-line interface tools
- `colorama==0.4.6`: Cross-platform colored terminal output
- Supporting libraries for CLI and WebSocket communication

### Node.js Dependencies (package.json)
- `frida-compile`: TypeScript to Frida JavaScript compiler
- `@types/frida-gum`: TypeScript definitions for Frida APIs
- Development and build toolchain dependencies

### Version Compatibility
- **Frida**: Maintain version consistency between Python and Node.js
- **TypeScript**: ES2022 features, strict mode
- **Node.js**: Version 16+ for modern JavaScript features
- **Windows**: Compatible with Windows 7+ (both 32-bit and 64-bit)

## Common AI Assistant Guidelines

### When Working with This Codebase
1. **Understand the Context**: This is a security/monitoring tool using dynamic instrumentation
2. **Respect the Architecture**: Follow the modular design patterns established
3. **Consider Performance**: API hooking has performance implications
4. **Handle Errors Gracefully**: Failed hooks shouldn't crash the entire agent
5. **Maintain Type Safety**: Use TypeScript features to prevent runtime errors
6. **Test Thoroughly**: Changes affect running processes, test carefully

### Code Style Preferences
- **Explicit Types**: Prefer explicit type annotations for clarity
- **Error Boundaries**: Always wrap risky operations in try-catch
- **Consistent Naming**: Use descriptive names for variables and functions
- **Documentation**: Comment complex Windows API interactions
- **Modularity**: Keep classes focused on single responsibilities

### File Modification Guidelines
- **Build Process**: Remember that TypeScript compiles to `_agent.js`
- **Configuration**: Changes to interfaces may require updates in multiple places
- **Dependencies**: Be cautious with new dependencies, especially in Frida context
- **Testing**: Always test changes with actual Windows processes

---

This documentation should enable any AI assistant to quickly understand the OS-Pulse Agent codebase and provide accurate, contextual assistance for development, debugging, and enhancement tasks.
