# OS-Pulse

**A sophisticated cross-platform system monitoring monorepo for real-time process and file operation analysis.**

OS-Pulse is a comprehensive system monitoring solution designed for security research, system analysis, and behavior tracking. It provides real-time monitoring capabilities across different platforms with a focus on Windows API instrumentation and native system utilities.

## 🚀 Features

- **Real-time Windows API Monitoring**: Track file operations, process creation, and system calls
- **Dynamic Instrumentation**: Built with Frida framework for runtime process injection
- **Cross-platform Utilities**: Native C++ utilities for system operations
- **TypeScript Development**: Modern, type-safe codebase with enterprise-ready architecture
- **Modular Design**: Clean separation of concerns with plugin-style monitors
- **Performance Optimized**: Low-overhead monitoring with configurable data extraction limits

## 📁 Project Structure

```
os-pulse/
├── agent/                    # Frida-based Windows API monitoring agent
│   ├── src/                  # TypeScript source code
│   │   ├── core/             # Core system monitoring logic
│   │   ├── monitors/         # API hook implementations
│   │   ├── logging/          # Structured logging system
│   │   ├── utils/            # Windows API utilities
│   │   └── types/            # TypeScript interfaces
│   ├── _agent.js             # Compiled Frida agent
│   └── run-frida.ps1         # PowerShell execution script
└── utils/                    # Native C++ system utilities
    ├── build/                # Compiled binaries
    ├── command_exec.cpp      # Command execution utilities
    ├── file_read.cpp         # File reading operations
    ├── file_write.cpp        # File writing operations
    └── Procmon.exe           # Process Monitor tool
```

## 🛠 Components

### Agent (Frida-based Monitoring)

The **agent** directory contains a sophisticated Windows system monitoring tool built with Frida and TypeScript. It performs real-time monitoring of Windows API calls to track:

- **File Operations**: ReadFile/WriteFile with content extraction
- **Process Creation**: NtCreateUserProcess, NtCreateProcess, NtCreateProcessEx
- **System Behavior**: Runtime analysis with configurable monitoring depth

**Key Features:**
- Dynamic instrumentation without process restart
- Configurable content extraction limits
- Binary data handling with hex logging
- Handle-to-path resolution
- Parent-child process relationship tracking

### Utils (Native Utilities)

The **utils** directory provides native C++ utilities for direct system operations and includes Process Monitor (Procmon) for advanced system monitoring.

## 🔧 Prerequisites

### For Agent Development
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **PowerShell** (Windows)
- **Administrator privileges** (for system process monitoring)

### For Utils Development
- **Visual Studio 2019+** or compatible C++ compiler
- **Windows SDK**

## 🚀 Quick Start

### Agent Setup

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/jahangir1x/os-pulse.git
   cd os-pulse/agent
   ```

2. **Set up Python environment:**
   ```powershell
   python -m venv .pyenv
   .\.pyenv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**
   ```powershell
   npm install
   ```

4. **Build the agent:**
   ```powershell
   npm run build
   ```

5. **Run monitoring:**
   ```powershell
   # Attach to existing process
   .\run-frida.ps1 -Target "notepad.exe"
   
   # Or spawn new process
   frida -f "C:\Windows\System32\notepad.exe" -l _agent.js
   ```

### Utils Setup

1. **Navigate to utils directory:**
   ```powershell
   cd os-pulse/utils
   ```

2. **Compile utilities:**
   ```powershell
   # Example compilation (adjust for your compiler)
   g++ -o build/command_exec.exe command_exec.cpp
   g++ -o build/file_read.exe file_read.cpp
   g++ -o build/file_write.exe file_write.cpp
   ```

## 📊 Usage Examples

### Real-time File Operation Monitoring
```powershell
# Monitor file operations in notepad
.\run-frida.ps1 -Target "notepad.exe"
# Open, edit, and save files to see detailed operation logs
```

### Process Creation Tracking
```powershell
# Monitor process creation in explorer
.\run-frida.ps1 -Target "explorer.exe"
# Launch applications to see process creation details
```

### Configuration Options
The agent supports runtime configuration for different monitoring scenarios:

- **Low overhead**: `maxContentLength: 64, logBinaryData: false`
- **Full analysis**: `maxContentLength: 4096, logBinaryData: true`
- **Selective monitoring**: Enable/disable specific monitor types

## 🏗 Architecture

### Agent Architecture
- **Dependency Injection**: Clean separation with injected dependencies
- **Strategy Pattern**: Pluggable monitor implementations
- **Observer Pattern**: Frida interceptors for API observation
- **Factory Pattern**: Centralized component orchestration
- **SOLID Principles**: Maintainable, extensible design

### Technology Stack
- **Frida 17.2.17**: Dynamic instrumentation framework
- **TypeScript**: Type-safe development with ES2022 features
- **Node.js**: Build toolchain and dependency management
- **Python**: Frida runtime and CLI tools
- **C++**: Native system utilities

## 🔍 Monitoring Capabilities

### Windows API Coverage
- **kernel32.dll**: File operations (ReadFile, WriteFile)
- **ntdll.dll**: Process creation APIs
- **Handle Resolution**: Automatic file path resolution
- **Memory Safety**: Protected memory access with error handling

### Data Extraction
- **Content Analysis**: Configurable content extraction from file operations
- **Binary Data**: Optional hex logging for binary content
- **Process Parameters**: Command line and environment capture
- **Relationship Tracking**: Parent-child process relationships

## 🚧 Development

### Development Workflow
```powershell
# Watch mode for continuous compilation
npm run watch

# Quick testing
.\run-frida.ps1

# VS Code integration available
```

### Adding New Monitors
1. Create monitor class in `src/monitors/`
2. Implement required interfaces
3. Add Frida interceptors
4. Export from `src/monitors/index.ts`
5. Initialize in `SystemMonitor`

### Testing
- **VS Code Integration**: Debug configurations and tasks
- **Manual Testing**: Multiple target processes supported
- **Error Resilience**: Graceful degradation on failures

## 📈 Performance Considerations

- **Memory Efficient**: Configurable content limits prevent exhaustion
- **CPU Optimized**: Minimal overhead in critical paths
- **Selective Monitoring**: Disable unused features
- **Non-blocking I/O**: Asynchronous logging operations

## 🔒 Security & Privacy

⚠️ **Important Security Considerations:**
- This tool captures sensitive data from monitored processes
- File operation content and process command lines are logged
- Requires code injection capabilities and elevated privileges
- Use responsibly and in compliance with applicable laws and policies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is proprietary. See the license file for details.

## 🔗 Related Projects

- [Frida](https://frida.re/) - Dynamic instrumentation framework
- [Process Monitor](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon) - Advanced monitoring for Windows

## 📞 Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

**OS-Pulse** - Real-time system monitoring for security research and system analysis.
