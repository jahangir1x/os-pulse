# OS-Pulse Agent

A Windows system monitoring agent built with Frida for real-time file I/O and process creation tracking.

## 🎯 Purpose

Monitor Windows system activities in real-time:
- **File Operations**: Track ReadFile/WriteFile API calls with content extraction
- **Process Creation**: Monitor NtCreateUserProcess and related APIs
- **Extensible Architecture**: Easy to add new monitoring capabilities

## 🚀 Quick Start

### Prerequisites
- Node.js and npm
- Python 3.8+ for Frida
- Windows target application

### Installation & Usage

#### 1. Setup Python Environment
```powershell
# Create virtual environment
python -m venv .pyenv

# Activate environment (PowerShell)
& .\.pyenv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

#### 2. Setup Node.js Dependencies
```powershell
# Install Node.js dependencies
npm install

# Build the agent
npm run build
```

#### 3. Run the Agent
```powershell
# Run with PowerShell script (recommended)
.\run-frida.ps1

# Or run manually
frida -n notepad.exe -l .\_agent.js --no-pause
```

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
