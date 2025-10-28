# OS-Pulse Network Monitor 🌐

**Network traffic interception and analysis component for the OS-Pulse monitoring system**

The Network Monitor provides comprehensive HTTP/HTTPS traffic interception and analysis capabilities, integrating seamlessly with the OS-Pulse backend to deliver complete network visibility for monitored systems.

## 🎯 Core Capabilities

### 🕸️ **Traffic Interception**
- **HTTP/HTTPS Monitoring**: Complete request/response capture using mitmproxy
- **SSL/TLS Analysis**: Certificate inspection and encrypted traffic analysis
- **Real-time Processing**: Live traffic monitoring with immediate event forwarding
- **Protocol Support**: HTTP/1.1, HTTP/2, and WebSocket traffic analysis

### 📊 **Event Processing**
- **Structured Events**: JSON-formatted network events with rich metadata
- **Backend Integration**: Direct communication with OS-Pulse backend
- **Request/Response Capture**: Complete HTTP transaction recording
- **Content Analysis**: Payload inspection and categorization

### 🔍 **Advanced Analysis**
- **DNS Resolution**: Domain name resolution tracking
- **Connection Analysis**: TCP connection lifecycle monitoring
- **Performance Metrics**: Latency and throughput measurements
- **Security Detection**: Suspicious traffic pattern identification

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Target System     │    │  Network Monitor    │    │  OS-Pulse Backend   │
│   (Applications)    │    │   (mitmproxy)       │    │  (Go + PostgreSQL)  │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • Web Browsers      │    │ • HTTP Interceptor  │    │ • Event Storage     │
│ • HTTP Clients      │◄──►│ • SSL/TLS Handler   │◄──►│ • Network Analysis  │
│ • API Calls         │    │ • Event Processor   │    │ • Web Dashboard     │
│ • Background Apps   │    │ • Backend Client    │    │ • Real-time UI      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Requirements

```bash
pip install -r requirements.txt
# Installs: mitmproxy, requests, flask, colorama
```

## Setup and Usage

### 1. Backend Integration

Ensure the OS-Pulse backend is running:

```bash
# Backend should be running on http://localhost:3003
cd ../../backend
go run main.go
```

### 2. Start Network Monitor

```bash
cd agent/network-monitor

# HTTP traffic interception
python http_interceptor.py

# Or use the batch script
.\start-http-interceptor.bat

# Advanced options with mitmproxy
mitmdump -s http_interceptor.py --set confdir=~/.mitmproxy -p 8080 -v
```

### 3. Configure System Proxy

Configure applications to use the network monitor as a proxy:

- **Proxy Host**: `127.0.0.1`
- **Proxy Port**: `8080` (default)

#### Option A: Application-specific Configuration
Configure individual applications (browsers, HTTP clients) to use the proxy.

#### Option B: System-wide Proxy (Windows)
```powershell
# Set system proxy (requires admin)
netsh winhttp set proxy proxy-server="127.0.0.1:8080"

# Remove system proxy
netsh winhttp reset proxy
```

#### Option B: System-wide Proxy (Windows)
```powershell
# Set system proxy
netsh winhttp set proxy 127.0.0.1:8080

# Remove system proxy when done
netsh winhttp reset proxy
```

#### Option C: Environment Variables
```bash
export HTTP_PROXY=http://127.0.0.1:8080
export HTTPS_PROXY=http://127.0.0.1:8080
```

### 4. HTTPS Certificate Installation (for HTTPS interception)

For HTTPS traffic interception, you need to install mitmproxy's certificate:

1. Start mitmproxy: `mitmdump -s http_interceptor.py`
2. Configure your browser to use the proxy
3. Visit `http://mitm.it` in your browser
4. Download and install the certificate for your platform

## Configuration

Edit `http_interceptor.py` to configure:

```python
# API endpoint
API_URL = "http://127.0.0.1:3003/network-monitor/events"

# Maximum body size to capture
MAX_BODY_BYTES = 100 * 1024  # 100 KB
```

## Event Structure

The interceptor sends events with this structure:

```json
{
  "timestamp_ms": 1698000000000,
  "kind": "request",  // or "response"
  "client": {
    "ip": "192.168.1.100",
    "port": 12345
  },
  "server": {
    "ip": "93.184.216.34"
  },
  "request": {
    "method": "GET",
    "scheme": "https",
    "host": "example.com",
    "port": 443,
    "path": "/api/data",
    "url": "https://example.com/api/data",
    "http_version": "HTTP/2.0",
    "headers": {
      "user-agent": "Mozilla/5.0...",
      "accept": "application/json"
    },
    "body": {
      "type": "text",  // or "binary"
      "content": "request data",
      "size": 12,
      "truncated": false
    }
  },
  "response": {  // Only present in response events
    "status_code": 200,
    "reason": "OK",
    "http_version": "HTTP/2.0",
    "headers": {
      "content-type": "application/json"
    },
    "body": {
      "type": "text",
      "content": "{\"result\": \"success\"}",
      "size": 20,
      "truncated": false
    }
  },
  "timings": {
    "request_timestamp": 1698000000.123,
    "response_timestamp": 1698000000.456
  }
}
```

## Integration with OS-Pulse Controller

To integrate with the OS-Pulse controller, update the API endpoint:

```python
# In http_interceptor.py
API_URL = "http://localhost:8080/api/events"  # Controller API endpoint
```

The controller's message handler can be extended to process network events alongside file and process events.

## Troubleshooting

### Common Issues

1. **Certificate Errors**: Install mitmproxy certificate for HTTPS interception
2. **Proxy Detection**: Some applications detect and block proxy usage
3. **Network Loops**: Ensure the interceptor's API requests don't go through the proxy

### Avoiding Request Loops

If mitmproxy is set as a system proxy, its own API requests might be intercepted. To avoid this:

```bash
# Set NO_PROXY environment variable
export NO_PROXY=127.0.0.1,localhost

# Or run mitmproxy with trust_env=False in requests
```

### Performance Considerations

- **Body Size Limit**: Adjust `MAX_BODY_BYTES` based on your needs
- **Thread Pool**: Adjust `ThreadPoolExecutor(max_workers=4)` for your workload
- **API Timeout**: Adjust timeout in `_post_event()` function

## Testing

### Quick Test

1. Start test server: `python test_http_server.py`
2. Start mitmproxy: `mitmdump -s http_interceptor.py`
3. Make HTTP requests through the proxy:

```bash
# Using curl with proxy
curl -x http://127.0.0.1:8080 http://example.com

# Using Python requests
import requests
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
requests.get("http://example.com", proxies=proxies)
```

### Browser Testing

1. Configure browser proxy settings to use `127.0.0.1:8080`
2. Install mitmproxy certificate (for HTTPS)
3. Browse websites and observe events in the test server

## Security Considerations

- **Certificate Installation**: mitmproxy certificate allows intercepting HTTPS traffic
- **Data Sensitivity**: HTTP/HTTPS content may contain sensitive information
- **Network Security**: Proxy interception can expose credentials and private data
- **Production Use**: Consider data privacy and compliance requirements

## Future Enhancements

- **Filtering**: Add URL/host filtering to focus on specific traffic
- **Encryption**: Encrypt sensitive data before forwarding to API
- **Buffering**: Add event buffering for high-traffic scenarios
- **Metrics**: Add performance and traffic metrics
- **WebSocket Support**: Extend to support WebSocket traffic interception