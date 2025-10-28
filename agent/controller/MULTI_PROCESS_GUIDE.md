# Multi-Process Monitoring Guide

This guide explains how to use the enhanced controller to monitor single or multiple processes.

## New Features

- ✅ Attach to a single process (by PID or name)
- ✅ Attach to multiple processes (by multiple PIDs)
- ✅ Attach to all running processes (with optional filter)

## Usage Examples

### 1. Attach to Single Process (Existing Feature)

**By PID:**
```bash
python main.py attach --pid 1234
```

**By Process Name:**
```bash
python main.py attach --process-name "notepad.exe"
```

### 2. Attach to Multiple Specific PIDs (NEW)

```bash
python main.py attach --pids 1234 5678 9012
```

This will attach to all three processes with PIDs 1234, 5678, and 9012.

### 3. Attach to All Processes (NEW)

**All processes:**
```bash
python main.py attach --all
```

**With filter (recommended):**
```bash
python main.py attach --all --filter notepad
```

This will attach to all processes with "notepad" in their name.

## Safety Features

### System Process Protection
When using `--all`, the controller automatically excludes:
- System critical processes (System, csrss.exe, smss.exe, wininit.exe, services.exe)
- The controller itself (to prevent self-monitoring)

### Confirmation Delay
When attaching to all processes, you get a 5-second countdown to cancel:
```
[ATTACH] Found 47 processes to attach to
[WARNING] Attaching to many processes may impact system performance
Press Ctrl+C within 5 seconds to cancel...
```

Press `Ctrl+C` during this time to abort.

## Output and Monitoring

### Attachment Summary
After attempting to attach, you'll see a summary:
```
[SUMMARY] Attached to 45/47 processes
[SUMMARY] Failed PIDs: [1234, 5678]
```

### Active Monitoring
Once attached:
```
[MONITOR] Starting monitoring...
[MONITOR] Attached to 45 session(s)
Press Ctrl+C to stop monitoring
```

### Statistics on Exit
When you stop monitoring (Ctrl+C):
```
[SCRIPT] Agent scripts unloaded
[SESSION] Detached from 45 process(es)

[STATISTICS]
Events processed: 12847
Session: session-123-456
API Events - Sent: 12800, Failed: 0
```

## Performance Considerations

### Memory Usage
Each attached process requires:
- ~2-5 MB for Frida session
- ~1-3 MB for agent script
- Event buffer memory

**Example:** 50 processes ≈ 150-400 MB total memory

### CPU Usage
- Minimal when processes are idle
- Increases with active API calls being monitored
- Agent hooks add ~5-10% overhead per process

### Recommendations
1. **Filter processes:** Use `--filter` to limit scope
2. **Monitor specific processes:** Use `--pids` for known targets
3. **Test incrementally:** Start with few processes, scale up
4. **Watch system resources:** Monitor RAM and CPU usage

## Common Use Cases

### Monitoring All Browser Instances
```bash
python main.py attach --all --filter chrome
```

### Monitoring Specific Critical Processes
```bash
python main.py attach --pids 1234 5678 9012 4567
```

### Development/Testing Multiple Apps
```bash
python main.py attach --all --filter myapp
```

## Troubleshooting

### "Failed to attach to process"
- **Permission denied:** Run as Administrator
- **Process not found:** PID may have changed, use `list-processes`
- **Process protected:** Some system processes cannot be monitored

### High Memory Usage
- Reduce number of attached processes
- Use `--filter` to be more specific
- Monitor fewer API calls in agent script

### Missing Events
- Check if process is actually performing operations
- Verify agent script is loaded (`[SCRIPT] Agent script loaded successfully`)
- Check API statistics for failed sends

## Advanced Examples

### Monitor All Office Applications
```bash
python main.py attach --all --filter "WINWORD\|EXCEL\|POWERPNT"
```

### Monitor Specific Security Tools
```bash
# First, list processes to get PIDs
python main.py list-processes --filter defender

# Then attach to specific ones
python main.py attach --pids 1234 5678
```

### Development Workflow
```bash
# List processes
python main.py list-processes --filter myapp

# Attach to all instances
python main.py attach --all --filter myapp

# Or attach to specific PIDs
python main.py attach --pids 1234 5678
```

## Implementation Details

### Multiple Sessions
The controller now maintains:
- `self.sessions: List[frida.Session]` - All active Frida sessions
- `self.scripts: List[frida.Script]` - All loaded agent scripts

### Message Handling
All messages from all processes are handled by a single `MessageHandler`, which:
- Batches events from all processes
- Sends to backend with appropriate session ID
- Provides aggregate statistics

### Cleanup
On exit (`Ctrl+C`), all sessions and scripts are properly cleaned up to prevent:
- Memory leaks
- Orphaned Frida sessions
- Locked processes
