# OS-Pulse

A sophisticated Windows system monitoring framework built with **Frida** and **Python**. OS-Pulse provides real-time monitoring of file operations and process creation activities through dynamic instrumentation.

## 🎯 Overview

OS-Pulse consists of two main components:
- **Injector**: TypeScript-based Frida agent for Windows API hooking
- **Controller**: Python-based process manager and event processor

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites
- **Windows** (7, 10, 11)
- **Python 3.8+**
- **Node.js 16+**
- **Administrator privileges** (for some processes)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jahangir1x/os-pulse.git
   cd os-pulse/agent
   ```

2. **Setup the injector:**
   ```bash
   cd injector
   npm install
   npm run build
   cd ..
   ```

3. **Setup the controller:**
   ```bash
   cd controller
   setup.bat
   ```

### Usage

1. **Spawn a new process with monitoring:**
   ```bash
   cd controller
   python main.py spawn --executable "C:\Windows\System32\notepad.exe"
   ```

2. **Attach to existing process:**
   ```bash
   python main.py attach --process-name "notepad.exe"
   ```

3. **Quick launchers:**
   ```bash
   # Spawn notepad
   spawn-notepad.bat
   
   # Attach to notepad
   attach-notepad.bat
   ```

## 📁 Project Structure

```
agent/
├── injector/              # Frida TypeScript agent
│   ├── src/              # TypeScript source code
│   │   ├── monitors/     # API hook implementations
│   │   ├── messaging/    # Event communication
│   │   ├── logging/      # Console logging
│   │   └── utils/        # Windows API utilities
│   ├── _agent.js         # Compiled Frida script
│   └── package.json      # Node.js dependencies
├── controller/           # Python process controller
│   ├── main.py          # CLI entry point
│   ├── frida_controller.py # Frida management
│   ├── message_handler.py  # Event processing
│   └── requirements.txt    # Python dependencies
└── .github/
    └── copilot-instructions.md # AI assistant context
```

## 🔍 Monitoring Capabilities

### File Operations
- **ReadFile/WriteFile**: Captures file I/O with content extraction
- **Path Resolution**: Converts handles to file paths
- **Content Filtering**: Configurable content length and binary data handling

### Process Creation
- **NtCreateUserProcess**: Modern Windows process creation
- **NtCreateProcess/Ex**: Legacy process creation APIs
- **Parameter Extraction**: Command lines, image paths, working directories

### Event Output
```
[FILE OPERATION #1] WriteFile
Path: C:\Users\user\document.txt
Bytes: 256
Content: "Hello, World!..."
Time: 2025-09-09T12:00:01.000Z
Process: notepad.exe (PID: 1234)

[PROCESS CREATION #1] NtCreateUserProcess
Status: SUCCESS (0x00000000)
Image: C:\Windows\System32\calc.exe
Command: calc.exe
Process Handle: 0x12345678
Source Process: notepad.exe (PID: 1234)
```

## ⚙️ Configuration

### Injector Configuration
Configure monitoring behavior in `injector/src/index.ts`:
```typescript
const config: Partial<HookConfiguration> = {
    enableFileOperations: true,
    enableProcessCreation: true,
    maxContentLength: 512,
    logBinaryData: false
};
```

### Controller Configuration
Environment variables for controller behavior:
```bash
set OSPULSE_LOG_LEVEL=DEBUG
set OSPULSE_API_ENDPOINT=http://localhost:8080/api/events
```

## 🧪 Testing

### Test the injector:
```bash
cd injector
npm run build
npm test  # If test scripts are available
```

### Test the controller:
```bash
cd controller
python test_controller.py
```

## 🔧 Development

### Building the injector:
```bash
cd injector
npm run build    # One-time build
npm run watch    # Watch mode for development
```

### Running with custom targets:
```bash
# Controller examples
python main.py spawn --executable "C:\Windows\System32\cmd.exe"
python main.py attach --pid 1234
python main.py list-processes --filter explorer
```

## 🛡️ Security Considerations

- **Elevated Privileges**: Some system processes require Administrator rights
- **Data Sensitivity**: File content monitoring may capture sensitive information
- **Performance Impact**: API hooking introduces minimal overhead
- **Target Process**: Injection affects target process behavior

## 🔮 Future Enhancements

- **Web Dashboard**: Real-time event visualization
- **REST API**: External system integration
- **Database Storage**: Historical event analysis
- **Alert System**: Suspicious activity detection
- **Network Monitoring**: WinSock API hooks
- **Registry Monitoring**: Registry operation tracking

## 📝 License

This project is for educational and research purposes. Use responsibly and in accordance with applicable laws and regulations.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in each component folder
- Review the troubleshooting guides in USAGE.md files
