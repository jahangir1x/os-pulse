# GitHub Copilot Instructions for OS-Pulse

## Project Overview

**OS-Pulse** is a sophisticated Windows system monitoring framework consisting of two main components:

### 🏗️ Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Controller    │    │    Injector     │    │ Target Process  │
│   (Python)      │    │ (TypeScript/JS) │    │   (notepad.exe) │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Process Spawn │    │ • File Hooks    │    │ • ReadFile()    │
│ • Process Attach│◄──►│ • Process Hooks │    │ • WriteFile()   │
│ • Event Display │    │ • Event Sender  │    │ • NtCreateProc()│
│ • API Gateway   │    │ • Frida send()  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🎯 Core Purpose
- **Real-time Windows API monitoring** through dynamic instrumentation
- **File operation tracking** (ReadFile/WriteFile with content extraction)
- **Process creation monitoring** (NtCreateUserProcess and related APIs)
- **Event streaming** from injector to controller via Frida messaging
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

#### Module Structure
```
injector/src/
├── index.ts                 # Entry point with configuration
├── core/
│   └── system-monitor.ts    # Main orchestrator
├── monitors/               # API hooking implementations
│   ├── file-operations.ts  # ReadFile/WriteFile hooks
│   └── process-creation.ts # NtCreateUserProcess hooks
├── messaging/
│   └── event-sender.ts     # Frida send() wrapper for host communication
├── logging/
│   └── console-logger.ts   # Structured console output
├── utils/
│   └── windows-api.ts      # Windows API utilities and memory operations
└── types/
    └── index.ts           # TypeScript interfaces and type definitions
```

#### Windows API Monitoring
- **File Operations** (`kernel32.dll`):
  - `ReadFile`: File read operations with content extraction
  - `WriteFile`: File write operations with content extraction
  - Features: Handle-to-path resolution, binary data handling, configurable limits

- **Process Creation** (`ntdll.dll`):
  - `NtCreateUserProcess`: Modern Windows process creation (Vista+)
  - `NtCreateProcess`: Legacy process creation
  - `NtCreateProcessEx`: Extended process creation with flags
  - Features: Command line extraction, process parameters, parent-child relationships

#### Build System
```bash
npm run build    # TypeScript → _agent.js via frida-compile
npm run watch    # Continuous compilation for development
```

### 2. Controller (`controller/`)
**Technology**: Python 3.8+ with Frida libraries
**Purpose**: Process management, event processing, and future API gateway

#### Key Characteristics
- **CLI Interface**: Comprehensive argparse-based command system
- **Process Management**: Spawn new processes or attach to existing ones
- **Event Processing**: Real-time message handling with colorful console output
- **Future-Ready**: Prepared for REST API integration and external system connectivity

#### Module Structure
```
controller/
├── main.py              # CLI entry point with argparse
├── frida_controller.py  # Core Frida session management
├── message_handler.py   # Event processing and display formatting
├── config.py           # Configuration management and environment variables
├── test_controller.py  # Comprehensive test suite
├── setup.bat           # Automated environment setup
├── spawn-notepad.bat   # Quick spawn launcher
├── attach-notepad.bat  # Quick attach launcher
└── requirements.txt    # Python dependencies
```

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
