# OS-Pulse Controller

The **Python process management** component of the OS-Pulse system. The controller manages Frida injection, handles process spawning/attachment, and processes monitoring events from the injector in real-time.

## 🎯 Purpose

The controller serves as the orchestration layer that:
- **Process Management**: Spawns new processes or attaches to existing ones
- **Frida Control**: Manages Frida sessions and script injection
- **Event Processing**: Receives and displays monitoring events from the injector
- **API Gateway**: Prepared for future external API integration

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│     Controller      │    │     Injector        │
│     (Python)        │    │   (Frida Agent)     │
├─────────────────────┤    ├─────────────────────┤
│ • FridaController   │    │ • File Monitors     │
│ • MessageHandler    │◄──►│ • Process Monitors  │
│ • ProcessSpawner    │    │ • EventSender       │
│ • EventProcessor    │    │ • send() messages   │
│ • CLI Interface     │    │                     │
└─────────────────────┘    └─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Target Process    │
│   (notepad.exe)     │
│ • ReadFile calls    │
│ • WriteFile calls   │
│ • Process creation  │
└─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Windows** operating system
- **Frida** libraries
- **Administrator privileges** (for some processes)

### Setup

1. **One-time setup:**
   ```bash
   setup.bat
   ```
   This creates a virtual environment and installs all dependencies.

2. **Test the installation:**
   ```bash
   .venv\Scripts\activate.bat
   python test_controller.py
   ```

### Basic Usage

1. **Spawn a new process:**
   ```bash
   python main.py spawn --executable "C:\Windows\System32\notepad.exe"
   ```

2. **Attach to existing process:**
   ```bash
   python main.py attach --process-name "notepad.exe"
   ```

3. **List running processes:**
   ```bash
   python main.py list-processes
   python main.py list-processes --filter notepad
   ```

### Quick Launchers

For convenience, use the batch files:
```bash
spawn-notepad.bat    # Spawn notepad with monitoring
attach-notepad.bat   # Attach to existing notepad
```

## 📁 Project Structure

```
controller/
├── main.py              # CLI entry point with argparse
├── frida_controller.py  # Core Frida management logic
├── message_handler.py   # Event processing and display
├── config.py           # Configuration management
├── test_controller.py  # Test suite for validation
├── requirements.txt    # Python dependencies
├── setup.bat          # Automated setup script
├── spawn-notepad.bat  # Quick spawn launcher
├── attach-notepad.bat # Quick attach launcher
├── README.md          # This file
└── USAGE.md           # Detailed usage guide
```

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
- `help` - Show available commands
- `quit` - Exit interactive mode

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
