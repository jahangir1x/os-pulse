# OS-Pulse Controller Usage Guide

## Quick Start

1. **Setup the environment:**
   ```bash
   # Run the setup script
   setup.bat
   ```

2. **Test the installation:**
   ```bash
   # Activate environment
   .venv\Scripts\activate.bat
   
   # Run tests
   python test_controller.py
   ```

3. **List running processes:**
   ```bash
   python main.py list-processes
   python main.py list-processes --filter notepad
   ```

4. **Spawn a new process with monitoring:**
   ```bash
   python main.py spawn --executable "C:\Windows\System32\notepad.exe"
   
   # With interactive mode
   python main.py spawn --executable "C:\Windows\System32\notepad.exe" --interactive
   ```

5. **Attach to existing process:**
   ```bash
   python main.py attach --process-name "notepad.exe"
   python main.py attach --pid 1234
   ```

## Quick Launch Scripts

- `spawn-notepad.bat` - Quickly spawn notepad with monitoring
- `attach-notepad.bat` - Quickly attach to existing notepad process

## Interactive Mode Commands

When in interactive mode, you can use these commands:
- `ping` - Send ping to the agent
- `status` - Request status from the agent  
- `help` - Show available commands
- `quit` - Exit interactive mode

## Expected Output

### Session Start
When the agent connects, you'll see:
```
[SESSION START] Frida Agent Connected
Session ID: 1725872400000-abc123
Process: notepad.exe (PID: 1234)
Platform: windows (x64)
Timestamp: 2025-09-09T12:00:00.000Z
```

### File Operations
When files are read/written:
```
[FILE OPERATION #1] ReadFile
Path: C:\Users\user\test.txt
Bytes: 256
Content: "Hello, World!..."
Time: 2025-09-09T12:00:01.000Z
Process: notepad.exe (PID: 1234)
```

### Process Creation
When new processes are created:
```
[PROCESS CREATION #1] NtCreateUserProcess
Status: SUCCESS (0x00000000)
Image: C:\Windows\System32\calc.exe
Command: calc.exe
Process Handle: 0x12345678
Thread Handle: 0x87654321
Time: 2025-09-09T12:00:02.000Z
Source Process: notepad.exe (PID: 1234)
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Controller    │    │    Injector     │    │ Target Process  │
│   (Python)      │    │ (TypeScript/JS) │    │   (notepad.exe) │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Frida Control │    │ • File Hooks    │    │ • ReadFile()    │
│ • Message Handler│◄──►│ • Process Hooks │    │ • WriteFile()   │
│ • Display       │    │ • Event Sender  │    │ • NtCreateProc()│
│ • Future API    │    │ • send() msgs   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Troubleshooting

### Common Issues

1. **"Agent script not found"**
   - Make sure the injector folder has `_agent.js` file
   - Run `npm run build` in the injector folder

2. **"Process not found"**
   - Use `list-processes` to find the correct process name
   - Make sure the process is running

3. **"Failed to attach"**
   - Try running as Administrator
   - Check if the process is a system process

4. **No events showing**
   - Make sure to perform file operations in the target process
   - Try opening/saving files in notepad

### Debug Mode

Set environment variable for more verbose output:
```bash
set OSPULSE_LOG_LEVEL=DEBUG
python main.py spawn --executable "C:\Windows\System32\notepad.exe"
```

## Future Enhancements

The controller is designed to support:
- External API integration (REST endpoints)
- Event batching and buffering
- Real-time dashboards
- Alert systems
- Historical analysis
