# API Integration Usage Guide

## Overview

The OS-Pulse agent now supports sending monitoring events to external APIs for analysis and storage. This enables integration with log aggregation systems, SIEM platforms, and custom analytics pipelines.

## Quick Start

### 1. Enable API Integration

Set environment variables:
```powershell
$env:OSPULSE_API_ENABLED="true"
$env:OSPULSE_API_ENDPOINT="http://your-api-server.com/api/events"
$env:OSPULSE_API_KEY="your-api-key"
```

### 2. Start the OS-Pulse Controller

```powershell
cd controller
python main.py spawn --executable "C:\Windows\System32\notepad.exe"
```

The controller will automatically send file operations and process creation events to your API endpoint.

## Configuration Options

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OSPULSE_API_ENABLED` | Enable API integration | `false` | `true` |
| `OSPULSE_API_ENDPOINT` | API endpoint URL | `None` | `http://localhost:8080/api/events` |
| `OSPULSE_API_KEY` | API authentication key | `None` | `your-secret-key` |
| `OSPULSE_API_TIMEOUT` | Request timeout in seconds | `10` | `30` |
| `OSPULSE_API_RETRY_COUNT` | Number of retry attempts | `3` | `5` |
| `OSPULSE_API_RETRY_DELAY` | Delay between retries (seconds) | `1` | `2` |
| `OSPULSE_API_BATCH_SIZE` | Events per batch request | `10` | `50` |
| `OSPULSE_API_BATCH_TIMEOUT` | Batch timeout (seconds) | `5` | `10` |

### Programmatic Configuration

```python
from message_handler import MessageHandler
import asyncio

async def configure_api():
    handler = MessageHandler()
    
    # Enable API with custom settings
    await handler.enable_api(
        endpoint="http://localhost:8080/api/events",
        api_key="your-api-key"
    )
    
    # Your monitoring code here...
    
    # Cleanup
    await handler.shutdown()

asyncio.run(configure_api())
```

## API Event Format

### File Operation Events

```json
{
  "type": "file_operation",
  "operation": "WriteFile",
  "data": {
    "handle": "0x12345678",
    "filePath": "C:\\Users\\user\\document.txt",
    "bytesTransferred": 256,
    "content": "File content here...",
    "timestamp": "2025-01-09T12:00:01.000Z"
  },
  "metadata": {
    "sessionId": "session-123",
    "processName": "notepad.exe",
    "processId": 1234
  }
}
```

### Process Creation Events

```json
{
  "type": "process_creation",
  "operation": "NtCreateUserProcess",
  "data": {
    "commandLine": "C:\\Windows\\System32\\calc.exe",
    "processId": 5678,
    "parentProcessId": 1234,
    "timestamp": "2025-01-09T12:00:02.000Z"
  },
  "metadata": {
    "sessionId": "session-123",
    "processName": "explorer.exe",
    "processId": 1234
  }
}
```

## Testing Your API Integration

### 1. Start the Test API Server

```powershell
cd controller
python test_api_server.py
```

This starts a Flask server on `http://localhost:8080` that receives and displays events.

### 2. Configure OS-Pulse to Use Test Server

```powershell
$env:OSPULSE_API_ENABLED="true"
$env:OSPULSE_API_ENDPOINT="http://localhost:8080/api/events"
$env:OSPULSE_API_KEY="test-key"
```

### 3. Run API Integration Test

```powershell
python test_api_integration.py
```

This test validates:
- ✅ Basic API client functionality
- ✅ File operation event sending
- ✅ Process creation event sending
- ✅ Message handler integration
- ✅ Error handling and recovery

### 4. Live Testing with Real Process

```powershell
# Terminal 1: Start test API server
python test_api_server.py

# Terminal 2: Start OS-Pulse with API integration
python main.py spawn --executable "C:\Windows\System32\notepad.exe"

# Terminal 3: Create file operations in notepad
# - Open notepad
# - Type some text
# - Save file
# - Open another file
# Watch events appear in both terminals!
```

## Advanced Usage

### Custom API Client

```python
from api_client import ApiClient
import asyncio

async def custom_monitoring():
    # Create API client
    client = ApiClient("http://your-api.com/events", "your-key")
    
    # Send custom event
    await client.send_event({
        'type': 'custom_event',
        'data': {'key': 'value'},
        'timestamp': '2025-01-09T12:00:00.000Z'
    })
    
    # Send file operation
    await client.send_file_operation(
        operation='ReadFile',
        file_path='C:\\important\\file.txt',
        content='sensitive data',
        bytes_transferred=100,
        process_name='myapp.exe',
        process_id=1234
    )
    
    # Get statistics
    stats = await client.get_stats()
    print(f"Sent {stats['events_sent']} events")
    
    # Cleanup
    await client.disconnect()

asyncio.run(custom_monitoring())
```

### Batch Event Processing

```python
# Configure larger batches for high-volume scenarios
import config

config.api_batch_size = 100        # 100 events per batch
config.api_batch_timeout = 10      # 10 second timeout
config.api_retry_count = 5         # 5 retry attempts
```

### API Error Handling

The API client includes comprehensive error handling:

- **Network Errors**: Automatic retry with exponential backoff
- **HTTP Errors**: Logging and graceful degradation
- **Timeout Errors**: Configurable timeouts and retries
- **Batch Failures**: Failed events are re-queued for retry

## Integration Examples

### Elasticsearch Integration

```python
# Your API server receives OS-Pulse events
@app.route('/api/events', methods=['POST'])
def receive_events():
    events = request.get_json()
    
    # Index events in Elasticsearch
    for event in events:
        es.index(
            index=f"ospulse-{datetime.now().strftime('%Y-%m')}",
            document=event
        )
    
    return {'status': 'indexed'}
```

### Splunk Integration

```python
# Forward events to Splunk HEC
import requests

def forward_to_splunk(events):
    splunk_data = []
    for event in events:
        splunk_data.append({
            "time": event.get('timestamp'),
            "source": "ospulse",
            "sourcetype": f"ospulse:{event['type']}",
            "event": event
        })
    
    requests.post(
        "https://splunk.company.com:8088/services/collector",
        headers={"Authorization": f"Splunk {HEC_TOKEN}"},
        json={"events": splunk_data}
    )
```

### Custom Analytics Pipeline

```python
# Process events for behavioral analysis
def analyze_file_operations(events):
    suspicious_patterns = []
    
    for event in events:
        if event['type'] == 'file_operation':
            file_path = event['data']['filePath']
            
            # Detect suspicious file access patterns
            if any(suspicious in file_path.lower() for suspicious in 
                   ['system32', 'windows', 'programdata']):
                suspicious_patterns.append(event)
    
    return suspicious_patterns
```

## Performance Considerations

### Optimizing for High Volume

1. **Increase Batch Size**: Larger batches reduce HTTP overhead
   ```python
   config.api_batch_size = 100
   ```

2. **Adjust Timeouts**: Balance responsiveness vs reliability
   ```python
   config.api_timeout = 30
   config.api_batch_timeout = 15
   ```

3. **Configure Retries**: Appropriate retry settings for your network
   ```python
   config.api_retry_count = 3
   config.api_retry_delay = 2
   ```

### Resource Usage

- **Memory**: ~5-10MB additional for API client buffering
- **CPU**: <1% overhead for API operations
- **Network**: Configurable based on batch size and frequency

## Troubleshooting

### Common Issues

1. **API Not Receiving Events**
   - Check `OSPULSE_API_ENABLED=true`
   - Verify `OSPULSE_API_ENDPOINT` URL
   - Confirm API server is running and accessible

2. **HTTP Errors**
   - Check API server logs
   - Verify authentication (API key)
   - Test endpoint with curl

3. **Performance Issues**
   - Reduce batch size
   - Increase timeouts
   - Check network latency

### Debug Mode

Enable detailed logging:
```powershell
$env:OSPULSE_LOG_LEVEL="DEBUG"
python main.py spawn --executable "notepad.exe"
```

### API Health Check

```python
from message_handler import MessageHandler
import asyncio

async def check_api_health():
    handler = MessageHandler()
    
    if await handler.test_api_connection():
        print("✅ API connection is healthy")
    else:
        print("❌ API connection failed")
    
    await handler.shutdown()

asyncio.run(check_api_health())
```

## Security Considerations

1. **HTTPS**: Always use HTTPS in production
   ```
   OSPULSE_API_ENDPOINT=https://secure-api.company.com/events
   ```

2. **Authentication**: Protect your API keys
   ```
   OSPULSE_API_KEY=your-secure-random-key
   ```

3. **Network Security**: Consider firewalls and VPNs
4. **Data Sensitivity**: Monitor events may contain sensitive file content
5. **Rate Limiting**: Implement rate limiting on your API server

## Next Steps

1. **Set up your API endpoint** to receive OS-Pulse events
2. **Configure authentication** and security measures
3. **Test the integration** using the provided test tools
4. **Monitor performance** and adjust batch/timeout settings
5. **Build analytics** on top of the received event data

For more advanced usage patterns and examples, see the `test_api_integration.py` and `test_api_server.py` files.
