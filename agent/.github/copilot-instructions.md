# GitHub Copilot Instructions for OS-Pulse Agent

## Project Overview

This is **OS-Pulse Agent**, a sophisticated Windows system monitoring tool built with **Frida** (dynamic instrumentation framework) and **TypeScript**. The agent performs real-time monitoring of Windows API calls to track file operations and process creation activities.

### Key Characteristics
- **Runtime**: Frida JavaScript engine injected into Windows processes
- **Language**: TypeScript compiled to JavaScript via `frida-compile`
- **Platform**: Windows (32-bit and 64-bit processes)
- **Architecture**: Modular, enterprise-ready design with clean separation of concerns
- **Purpose**: Security monitoring, system analysis, debugging, and behavior tracking

## Technology Stack

### Core Technologies
- **Frida 17.2.17**: Dynamic instrumentation framework for Windows API hooking
- **TypeScript**: Type-safe development with modern ES2022 features
- **Node.js**: Build toolchain and dependency management
- **Python 3.8+**: Frida runtime and command-line tools
- **PowerShell**: Automation and execution scripts

### Build Pipeline
```
TypeScript (src/) → frida-compile → JavaScript (_agent.js) → Frida injection
```

## Architecture Deep Dive

### Core Design Patterns
1. **Dependency Injection**: Logger and configuration injected into monitors
2. **Strategy Pattern**: Different monitors implement similar interfaces
3. **Observer Pattern**: Frida interceptors observe API calls
4. **Factory Pattern**: SystemMonitor orchestrates component creation
5. **SOLID Principles**: Single responsibility, open/closed, dependency inversion

### Module Structure
```
src/
├── index.ts                 # Entry point - configuration and initialization
├── core/
│   └── system-monitor.ts    # Main orchestrator - coordinates all monitors
├── monitors/               # API hooking implementations
│   ├── file-operations.ts  # ReadFile/WriteFile hooks
│   └── process-creation.ts # NtCreateUserProcess/NtCreateProcess hooks
├── logging/
│   └── console-logger.ts   # Structured console output with timestamps
├── utils/
│   └── windows-api.ts      # Windows API utilities and memory operations
└── types/
    └── index.ts           # TypeScript interfaces and type definitions
```

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
