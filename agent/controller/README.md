# OS-Pulse Controller 🎛️

**Python-based process management and API integration hub for the OS-Pulse monitoring system**

The controller serves as the orchestration layer that manages Frida injection, processes monitoring events in real-time, and forwards data to external APIs for advanced analysis and threat detection.

## 🎯 Core Capabilities

### 🔧 **Process Management**
- **Spawn Mode**: Launch new processes under monitoring
- **Attach Mode**: Connect to existing running processes
- **Multi-Target**: Support for any Windows executable
- **Session Management**: Robust Frida session handling with cleanup

### 📊 **Event Processing**
- **Real-Time Display**: Color-coded console output with timestamps
- **Event Statistics**: Track file operations and process creations
- **Interactive Mode**: Send commands to injected agents
- **Structured Logging**: Configurable log levels and formatting

### 🌐 **API Integration** ✨ *SIMPLIFIED*
- **Simple HTTP Client**: Immediate event transmission using requests library
- **Fire-and-Forget**: No buffering or queuing - events sent immediately
- **Background Threads**: Non-blocking event sending via daemon threads
- **Error Resilience**: Graceful handling of connection failures
- **Multiple Destinations**: Support for SIEM, log aggregation, and analytics platforms

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│     Controller      │    │     Injector        │    │   External APIs     │
│     (Python)        │    │   (Frida Agent)     │    │ (SIEM/Analytics)    │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • FridaController   │    │ • File Monitors     │    │ • Elasticsearch     │
│ • MessageHandler    │◄──►│ • Process Monitors  │    │ • Splunk            │
│ • ApiClient         │    │ • EventSender       │    │ • Custom Analytics  │
│ • ConfigManager     │    │ • Frida send()      │    │ • Threat Intel      │
│ • CLI Interface     │    │                     │    │ • Dashboards        │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
          │                                                        ▲
          ▼                                                        │
┌─────────────────────┐                              ┌─────────────────────┐
│   Target Process    │                              │    API Events       │
│   (notepad.exe)     │                              │                     │
│ • ReadFile calls    │                              │ • File Operations   │
│ • WriteFile calls   │──────────────────────────────┤ • Process Creation  │
│ • Process creation  │                              │ • Metadata          │
└─────────────────────┘                              └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Windows 7/10/11** (x86/x64)
- **Frida 17.2.17+** (automatically installed)
- **Administrator privileges** (for system process monitoring)

### 1. Environment Setup

```powershell
# One-time setup (creates .pyenv virtual environment)
setup.bat

# Activate environment
.\.pyenv\Scripts\activate.bat

# Verify installation
python test_controller.py
```

### 2. Basic Monitoring

```powershell
# Spawn new process with monitoring
python main.py spawn --executable "C:\Windows\System32\notepad.exe"

# Attach to existing process
python main.py attach --process-name "notepad.exe"

# List available processes
python main.py list-processes --filter notepad
```

### 3. API Integration Setup ✨

```powershell
# Configure API integration
$env:OSPULSE_API_ENABLED="true"
$env:OSPULSE_API_ENDPOINT="http://your-api-server.com/api/events"
$env:OSPULSE_API_KEY="your-api-key"

# Start monitoring with API forwarding
python main.py spawn --executable "C:\Windows\System32\notepad.exe"
```

### 4. Quick Testing

```powershell
# Use convenience scripts
spawn-notepad.bat      # Quick spawn
attach-notepad.bat     # Quick attach
.\test-api.bat         # Test API integration
```

## 📁 Project Structure

```
controller/
├── 🐍 Core Components
│   ├── main.py                    # CLI entry point with argparse
│   ├── frida_controller.py        # Frida session management
│   ├── message_handler.py         # Event processing & display
│   └── config.py                  # Configuration management
├── 🌐 API Integration
│   ├── api_client.py              # Async HTTP client for external APIs
│   ├── test_api_integration.py    # API integration test suite
│   ├── test_api_server.py         # Mock API server for testing
│   └── API_INTEGRATION.md         # Comprehensive API guide
├── 🧪 Testing & Validation
│   ├── test_controller.py         # Core functionality tests
│   └── test-api.bat              # Quick API test script
├── 🚀 Quick Launchers
│   ├── setup.bat                  # Environment setup
│   ├── spawn-notepad.bat         # Quick spawn launcher
│   └── attach-notepad.bat        # Quick attach launcher
├── 📦 Dependencies
│   ├── requirements.txt           # Python dependencies
│   └── .pyenv/                   # Virtual environment (created by setup.bat)
└── 📚 Documentation
    ├── README.md                  # This file
    ├── USAGE.md                   # Detailed usage guide
    └── API_INTEGRATION.md         # API integration documentation
```

## 🔧 Core Components

### 1. FridaController (`frida_controller.py`)

**Purpose**: Manages Frida sessions and agent injection

**Key Features:**
- **Process Spawning**: Launch new processes with monitoring
- **Process Attachment**: Connect to existing processes
- **Script Injection**: Load and manage the TypeScript agent
- **Session Lifecycle**: Handle connection, disconnection, and cleanup
- **Error Recovery**: Graceful handling of target process crashes

**Example Usage:**
```python
from frida_controller import FridaController

controller = FridaController()

# Spawn new process
success = controller.spawn_and_attach("C:\\Windows\\System32\\notepad.exe")

# Start monitoring
controller.start_monitoring()

# Cleanup when done
controller.stop()
```

### 2. MessageHandler (`message_handler.py`)

**Purpose**: Processes events from the injector and manages API forwarding

**Key Features:**
- **Event Processing**: Handle file operations and process creation events
- **Color-Coded Display**: Rich console output with timestamps
- **API Integration**: Forward events to external APIs asynchronously
- **Statistics Tracking**: Monitor event counts and performance metrics
- **Interactive Commands**: Send ping/status commands to agents

**Event Types Handled:**
```python
# File operation events
{
  'type': 'file_operation',
  'operation': 'WriteFile',
  'data': {...},
  'metadata': {...}
}

# Process creation events
{
  'type': 'process_creation',
  'operation': 'NtCreateUserProcess',
  'data': {...},
  'metadata': {...}
}
```

### 3. ApiClient (`api_client.py`) ✨ *NEW*

**Purpose**: Async HTTP client for external API integration

**Key Features:**
- **Async Operations**: Non-blocking HTTP requests using aiohttp
- **Batch Processing**: Group events for efficient transmission
- **Retry Logic**: Automatic retry with exponential backoff
- **Health Monitoring**: Connection testing and performance stats
- **Error Handling**: Graceful degradation on API failures

**Configuration:**
```python
from api_client import ApiClient

client = ApiClient(
    endpoint="http://your-api.com/events",
    api_key="your-key",
    batch_size=20,
    timeout=10
)

# Send single event
await client.send_event(event_data)

# Send file operation
await client.send_file_operation(
    operation='ReadFile',
    file_path='C:\\important\\file.txt',
    content='data',
    bytes_transferred=100,
    process_name='app.exe',
    process_id=1234
)
```

### 4. Configuration Management (`config.py`)

**Purpose**: Centralized configuration using environment variables

**Available Settings:**
```python
# Logging
OSPULSE_LOG_LEVEL = "INFO"         # DEBUG, INFO, WARNING, ERROR

# API Integration
OSPULSE_API_ENABLED = "false"      # Enable API forwarding
OSPULSE_API_ENDPOINT = ""          # API endpoint URL
OSPULSE_API_KEY = ""               # Authentication key
OSPULSE_API_TIMEOUT = "10"         # Request timeout (seconds)
OSPULSE_API_RETRY_COUNT = "3"      # Number of retry attempts
OSPULSE_API_RETRY_DELAY = "1"      # Delay between retries (seconds)
OSPULSE_API_BATCH_SIZE = "10"      # Events per batch
OSPULSE_API_BATCH_TIMEOUT = "5"    # Batch timeout (seconds)
```

## 🌐 API Integration

### Configuration Options

**Environment Variables:**
```powershell
# Basic API setup
$env:OSPULSE_API_ENABLED="true"
$env:OSPULSE_API_ENDPOINT="http://localhost:8080/api/events"
$env:OSPULSE_API_KEY="your-secret-key"

# Performance tuning
$env:OSPULSE_API_BATCH_SIZE="50"      # Larger batches for high volume
$env:OSPULSE_API_TIMEOUT="30"         # Longer timeout for slow networks
$env:OSPULSE_API_RETRY_COUNT="5"      # More retries for unreliable networks
```

**Programmatic Configuration:**
```python
import asyncio
from message_handler import MessageHandler

async def setup_api():
    handler = MessageHandler()
    
    # Enable API with custom settings
    await handler.enable_api(
        endpoint="http://api.company.com/events",
        api_key="secure-api-key"
    )
    
    # Test connection
    if await handler.test_api_connection():
        print("✅ API connection successful")
    
    # Get statistics
    stats = await handler.get_api_stats()
    print(f"API Stats: {stats}")
    
    # Cleanup
    await handler.shutdown()

asyncio.run(setup_api())
```

### Event Format

**File Operation Events:**
```json
{
  "type": "file_operation",
  "operation": "WriteFile",
  "data": {
    "handle": "0x12345678",
    "filePath": "C:\\Users\\user\\document.txt",
    "bytesTransferred": 256,
    "content": "File content here...",
    "timestamp": "2025-09-11T12:00:01.000Z"
  },
  "metadata": {
    "sessionId": "session-abc123",
    "processName": "notepad.exe",
    "processId": 1234
  }
}
```

**Process Creation Events:**
```json
{
  "type": "process_creation",
  "operation": "NtCreateUserProcess",
  "data": {
    "commandLine": "C:\\Windows\\System32\\calc.exe",
    "processId": 5678,
    "parentProcessId": 1234,
    "timestamp": "2025-09-11T12:00:02.000Z"
  },
  "metadata": {
    "sessionId": "session-abc123",
    "processName": "explorer.exe",
    "processId": 1234
  }
}
```

## 🧪 Testing & Validation

### Unit Tests

```powershell
# Test core controller functionality
python test_controller.py

# Test API integration
python test_api_integration.py

# Quick API test with mock server
.\test-api.bat
```

### Integration Testing

```powershell
# Terminal 1: Start mock API server
python test_api_server.py

# Terminal 2: Configure and run OS-Pulse
$env:OSPULSE_API_ENABLED="true"
$env:OSPULSE_API_ENDPOINT="http://localhost:8080/api/events"
python main.py spawn --executable "C:\Windows\System32\notepad.exe"

# Terminal 3: Generate events
# - Open notepad (if not already open)
# - Type some text
# - Save file (Ctrl+S)
# - Open another file (Ctrl+O)
# Watch events appear in both terminals!
```

### Performance Testing

```powershell
# Test with high-volume events
$env:OSPULSE_API_BATCH_SIZE="100"
$env:OSPULSE_API_BATCH_TIMEOUT="2"
python main.py spawn --executable "C:\Windows\System32\cmd.exe"

# Run commands that generate many file operations
# Monitor performance in task manager
```

## 🔧 CLI Commands

### Process Management

```powershell
# Spawn new process
python main.py spawn --executable "C:\Windows\System32\notepad.exe"
python main.py spawn --executable "C:\Program Files\MyApp\app.exe"

# Attach to existing process
python main.py attach --process-name "notepad.exe"
python main.py attach --pid 1234
python main.py attach --process-name "chrome.exe" --pid 5678

# List processes
python main.py list-processes
python main.py list-processes --filter notepad
python main.py list-processes --filter chrome --detailed
```

### Interactive Commands

```powershell
# While monitoring is active, use these commands:
ping        # Test agent connectivity
status      # Get agent status
config      # Show current configuration
stats       # Display statistics
api-status  # Check API connection health
flush       # Flush pending API events
help        # Show available commands
quit        # Stop monitoring and exit
```

### Debug Mode

```powershell
# Enable detailed logging
$env:OSPULSE_LOG_LEVEL="DEBUG"
python main.py spawn --executable "notepad.exe"

# This will show:
# - Detailed Frida session information
# - HTTP request/response details
# - Event processing timings
# - API client statistics
```

## 🔧 Development Workflows

### Setting Up Development Environment

```powershell
# Clone and setup
git clone https://github.com/jahangir1x/os-pulse.git
cd os-pulse/agent/controller

# Create development environment
setup.bat

# Activate environment
.\.pyenv\Scripts\activate.bat

# Install additional dev dependencies (optional)
pip install pytest pytest-asyncio black flake8

# Run tests
python test_controller.py
python test_api_integration.py
```

### Adding New Event Types

1. **Update MessageHandler**: Add new event processing method
2. **Update ApiClient**: Add specific sending method if needed
3. **Update Tests**: Add test cases for new event type
4. **Update Documentation**: Document the new event format

Example:
```python
# In message_handler.py
def _handle_registry_operation(self, message: Dict[str, Any]) -> None:
    """Handle registry operation events"""
    data = message.get('data', {})
    operation = message.get('operation', 'Unknown')
    
    # Display event
    print(f"🗂️  [REGISTRY OPERATION] {operation}")
    print(f"📁 Key: {data.get('keyPath', 'Unknown')}")
    
    # Forward to API
    self._send_to_api_async('registry_operation', message)
```

### Custom API Integrations

```python
# Custom API client example
from api_client import ApiClient
import asyncio

async def custom_integration():
    # Create client with custom settings
    client = ApiClient(
        endpoint="https://your-api.company.com/events",
        api_key="your-api-key",
        timeout=30,
        batch_size=50
    )
    
    # Custom event processing
    async def process_event(event):
        # Add custom metadata
        event['metadata']['environment'] = 'production'
        event['metadata']['datacenter'] = 'dc1'
        
        # Send to API
        await client.send_event(event)
    
    # Use in your monitoring loop
    # ...
    
    # Cleanup
    await client.disconnect()
```

## 🛡️ Security Considerations

### 🔒 **Data Protection**
- **Sensitive Content**: File operations may capture sensitive data
- **API Security**: Use HTTPS and secure API keys
- **Network Security**: Consider VPNs and firewalls
- **Access Control**: Limit who can run monitoring tools

### ⚡ **Performance Impact**
- **CPU Usage**: <1% additional overhead per monitored process
- **Memory Usage**: ~5-10MB for controller process
- **Network Usage**: Configurable via batch settings
- **Storage**: Log files and event data accumulation

### 🚨 **Operational Security**
- **Administrator Rights**: Required for system process monitoring
- **Process Injection**: Inherently requires code injection capabilities
- **Antivirus Compatibility**: May trigger security software alerts
- **Audit Trail**: All monitoring activities are logged

## 🔮 Future Enhancements

### Planned Features
- [ ] **Database Integration**: SQLite/PostgreSQL for event storage
- [ ] **Web Dashboard**: Real-time monitoring interface
- [ ] **Alert System**: Rule-based threat detection
- [ ] **Multi-Process**: Simultaneous monitoring of multiple processes
- [ ] **Plugin System**: Dynamic loading of custom processors
- [ ] **Performance Analytics**: Advanced metrics and optimization

### API Enhancements
- [ ] **GraphQL Support**: Advanced query capabilities
- [ ] **Webhook Support**: Push notifications for critical events
- [ ] **Stream Processing**: Real-time event streaming
- [ ] **Data Transformation**: Custom event formatting and filtering
- [ ] **Rate Limiting**: Built-in rate limiting and backpressure handling

## 📞 Support & Resources

### 📚 **Documentation**
- **Main README**: `../README.md` - Project overview
- **API Integration**: `API_INTEGRATION.md` - Comprehensive API guide
- **Usage Guide**: `USAGE.md` - Detailed usage instructions
- **AI Context**: `../.github/copilot-instructions.md` - AI assistant context

### 🐛 **Troubleshooting**

**Common Issues:**
1. **"Process not found"** - Ensure target process is running
2. **"Permission denied"** - Run as Administrator
3. **"API connection failed"** - Check endpoint URL and network
4. **"Virtual environment not found"** - Run `setup.bat` first

**Debug Steps:**
```powershell
# Enable debug logging
$env:OSPULSE_LOG_LEVEL="DEBUG"

# Test basic functionality
python test_controller.py

# Test API integration
python test_api_integration.py

# Check environment
python -c "import frida; print(f'Frida version: {frida.__version__}')"
```

### 💬 **Getting Help**
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check all README and guide files
- **Tests**: Run test suites to validate functionality
- **Community**: Share your use cases and integration patterns

---

**OS-Pulse Controller** - *Your gateway to comprehensive Windows system monitoring with enterprise-grade API integration*

## 🎛️ Command Line Interface

### Main Commands

```bash
python main.py <command> [options]
```

#### Spawn Process
```bash
python main.py spawn --executable "C:\Windows\System32\notepad.exe"
python main.py spawn --executable "C:\Windows\System32\cmd.exe" --args "/c" "dir"
python main.py spawn --executable "notepad.exe" --interactive
```

#### Attach to Process
```bash
python main.py attach --process-name "notepad.exe"
python main.py attach --pid 1234
python main.py attach --process-name "notepad.exe" --interactive
```

#### List Processes
```bash
python main.py list-processes
python main.py list-processes --filter explorer
python main.py list-processes --filter "Visual Studio"
```

### Interactive Mode

When using `--interactive`, you can send commands to the agent:
- `ping` - Test agent connectivity
- `status` - Request agent status
- `api-test` - Test API connection
- `api-stats` - Show API statistics  
- `api-flush` - Flush pending API events
- `help` - Show available commands
- `quit` - Exit interactive mode

### API Integration Commands

The controller supports forwarding events to external APIs for analysis:

```bash
# Test API connectivity
> api-test

# View API statistics  
> api-stats

# Force flush pending events
> api-flush
```

## 🌐 API Integration

OS-Pulse can forward monitoring events to external APIs for centralized analysis and storage.

### Configuration

Set these environment variables or create a `.env` file:

```bash
# Enable API forwarding
OSPULSE_API_ENABLED=true

# API endpoint for events
OSPULSE_API_ENDPOINT=https://your-analysis-service.com/api/events

# API authentication (optional)
OSPULSE_API_KEY=your-api-key

# Batch configuration
OSPULSE_API_BATCH_SIZE=10
OSPULSE_API_BATCH_TIMEOUT=5.0
```

### Event Format

Events are sent as JSON with this structure:

```json
{
  "event_type": "file_operation",
  "event_data": {
    "operation": "WriteFile",
    "file_path": "C:\\Users\\user\\document.txt", 
    "bytes_transferred": 256,
    "content": "File content...",
    "timestamp": "2024-01-15T12:00:00.000Z",
    "process_info": {
      "name": "notepad.exe",
      "pid": 1234,
      "session_id": "session-123"
    }
  },
  "metadata": {
    "operation": "WriteFile",
    "source": "os-pulse-injector",
    "handler": "file_operation",
    "timestamp": "2024-01-15T12:00:00.000Z"
  }
}
```

### Testing API Integration

Use the test script to validate API functionality:

```bash
# Run API integration tests
python test_api.py
```

This tests:
- API client initialization
- Connection testing
- Event batching
- Batch flushing
- Message handler integration

## 📊 Event Display

The controller provides colorful, structured output for monitoring events:

### Session Start
```
╔═══════════════════════════════════════════════════════════╗
║                     OS-Pulse Controller                   ║
║              Windows System Monitor v1.0                 ║
╚═══════════════════════════════════════════════════════════╝

[SESSION START] Frida Agent Connected
Session ID: 1725872400000-abc123
Process: notepad.exe (PID: 1234)
Platform: windows (x64)
Timestamp: 2025-09-09T12:00:00.000Z
```

### File Operations
```
[FILE OPERATION #1] WriteFile
──────────────────────────────────────────────────
Path: C:\Users\user\document.txt
Bytes: 256
Content: "Hello, World! This is a test document..."
Time: 2025-09-09T12:00:01.000Z
Process: notepad.exe (PID: 1234)
```

### Process Creation
```
[PROCESS CREATION #1] NtCreateUserProcess
──────────────────────────────────────────────────
Status: SUCCESS (0x00000000)
Image: C:\Windows\System32\calc.exe
Command: calc.exe
Process Handle: 0x12345678
Thread Handle: 0x87654321
Time: 2025-09-09T12:00:02.000Z
Source Process: notepad.exe (PID: 1234)
```

## ⚙️ Configuration

### Environment Variables

```bash
# Logging configuration
set OSPULSE_LOG_LEVEL=DEBUG
set OSPULSE_LOG_FILE=ospulse.log

# Future API integration
set OSPULSE_API_ENDPOINT=http://localhost:8080/api/events
set OSPULSE_API_KEY=your-api-key
set OSPULSE_API_TIMEOUT=30
set OSPULSE_API_BATCH_SIZE=10
```

### Configuration File

The `config.py` file contains settings for:
- Agent script path resolution
- Display preferences
- API integration settings (for future use)
- Logging configuration

## 🔧 Development

### Testing

Run the comprehensive test suite:
```bash
python test_controller.py
```

The test suite validates:
- Configuration loading
- Message handler functionality
- Controller initialization
- Process listing capabilities

### Adding Custom Message Handlers

Extend the `MessageHandler` class in `message_handler.py`:

```python
def _handle_custom_event(self, message: Dict[str, Any]) -> None:
    """Handle custom event type"""
    data = message.get('data', {})
    print(f"{Fore.CYAN}[CUSTOM EVENT] {data}")
    
    # Add your custom processing logic here
```

### API Integration (Future)

The controller is designed for easy API integration:

```python
# In message_handler.py
async def send_to_api(self, event_data: Dict[str, Any]) -> None:
    """Send event to external API"""
    if config.api_enabled:
        async with aiohttp.ClientSession() as session:
            await session.post(
                config.api_endpoint,
                json=event_data,
                headers={'Authorization': f'Bearer {config.api_key}'}
            )
```

## 🐛 Troubleshooting

### Common Issues

1. **"Agent script not found"**
   ```bash
   # Ensure injector is built
   cd ../injector
   npm run build
   ```

2. **"Process not found"**
   ```bash
   # List processes to find correct name
   python main.py list-processes --filter notepad
   ```

3. **"Failed to attach"**
   ```bash
   # Try running as Administrator
   # Right-click PowerShell -> "Run as Administrator"
   ```

4. **No events appearing**
   - Perform file operations in the target process
   - Try opening/saving files in notepad
   - Create new processes from the target

### Debug Mode

Enable verbose logging:
```bash
set OSPULSE_LOG_LEVEL=DEBUG
python main.py spawn --executable "C:\Windows\System32\notepad.exe"
```

### Process Discovery

Find the correct process name:
```bash
# List all processes
python main.py list-processes

# Filter by name
python main.py list-processes --filter notepad
python main.py list-processes --filter "Visual Studio"
```

## 📈 Performance Notes

- **Memory Usage**: ~5-10MB for the controller
- **Event Processing**: Real-time with minimal latency
- **Process Impact**: No impact on target process performance
- **Scalability**: Can monitor multiple processes simultaneously

## 🛡️ Security Considerations

- **Elevated Privileges**: Required for system process attachment
- **Process Injection**: May trigger security software alerts
- **Data Exposure**: Events may contain sensitive file content
- **Network Security**: Future API integration requires secure endpoints

## 🔮 Future Enhancements

The controller architecture supports:

### Planned Features
- **REST API Server**: Built-in web API for external integration
- **Web Dashboard**: Real-time event visualization
- **Database Storage**: SQLite/PostgreSQL for historical analysis
- **Alert System**: Rule-based suspicious activity detection
- **Event Filtering**: Advanced filtering and search capabilities
- **Multi-Process**: Simultaneous monitoring of multiple processes

### API Integration Example
```python
# Future: REST API endpoint
@app.route('/api/events', methods=['POST'])
async def receive_events():
    event = await request.get_json()
    await process_monitoring_event(event)
    return {'status': 'received'}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests in `test_controller.py`
5. Update documentation
6. Submit a pull request

## 📞 Support

For issues and questions:
- Check `USAGE.md` for detailed examples
- Run `python test_controller.py` to validate setup
- Review logs with `OSPULSE_LOG_LEVEL=DEBUG`
- Create GitHub issues for bugs or feature requests
