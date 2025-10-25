# API Integration Guide

## 🌐 Backend API Specification

### Base Configuration
- **Base URL**: `http://localhost:3003`
- **Content-Type**: `application/json` (for responses)
- **CORS**: Must allow `http://localhost:5173` origin

## 📡 Endpoint Details

### 1. Create Analysis Session
```http
POST /api/create-session
Content-Type: multipart/form-data

Form Data:
  file: [File] - The malware sample to analyze
```

**Response:**
```json
{
  "sessionId": "abcd-efgh-ijkl-mnop",
  "vncServerHost": "192.168.0.102", 
  "vncServerPort": "5900"
}
```

**Frontend Usage:**
```typescript
const formData = new FormData();
formData.append('file', selectedFile);

const response = await fetch('http://localhost:3003/api/create-session', {
  method: 'POST',
  body: formData
});

const sessionData = await response.json();
// Use sessionData.sessionId for subsequent API calls
```

### 2. Fetch Events
```http
GET /api/events/:sessionId
```

**Response:** Array of events (latest first)
```json
[
  {
    "event_type": "file_operation",
    "data": {
      "filePath": "\\\\?\\C:\\Windows\\System32\\UIAutomationCore.dll",
      "operation": "ReadFile",
      "content": "AB 02 01 30",
      "bytesTransferred": 4,
      "timestamp": "2025-10-22T16:03:11.372Z",
      "metadata": {
        "processName": "Notepad.exe",
        "processId": 800
      }
    }
  },
  {
    "event_type": "http_network_operation",
    "data": {
      "url": "example.com/endpoint",
      "method": "POST",
      "base64RequestBody": "c29tZXRoaW5n",
      "base64Response": "cmVzcG9uc2U=",
      "bytesTransferred": 20,
      "timestamp": "2025-10-22T16:03:11.372Z",
      "metadata": {
        "processName": "Notepad.exe", 
        "processId": 800
      }
    }
  },
  {
    "event_type": "raw_network_operation",
    "data": {
      "host": "192.168.100.100",
      "protocol": "tcp",
      "request": "AB CD 02 30",
      "response": "02 AB CD EF", 
      "bytesTransferred": 20,
      "timestamp": "2025-10-22T16:03:11.372Z",
      "metadata": {
        "processName": "Notepad.exe",
        "processId": 800
      }
    }
  },
  {
    "event_type": "process_creation_operation",
    "data": {
      "filePath": "\\\\?\\C:\\Windows\\System32\\paint.exe",
      "args": "--some --arg1 --arg2",
      "timestamp": "2025-10-22T16:03:11.372Z",
      "metadata": {
        "processName": "Notepad.exe",
        "processId": 800
      }
    }
  }
]
```

**Frontend Usage:**
```typescript
// Called every 1 second
const response = await fetch(`http://localhost:3003/api/events/${sessionId}`);
const events = await response.json();
setEvents(events); // Replace entire events array
```

## 🔄 Data Flow Requirements

### Event Ordering
- API must return events with **latest events first**
- Frontend displays events in the order received
- No client-side sorting performed

### Real-time Updates
- Frontend polls every **1 second**
- Each response **completely replaces** previous events
- No incremental updates or pagination

### Event Consistency
Each event must include:
- `event_type`: One of the 4 supported types
- `data.timestamp`: ISO 8601 format
- `data.metadata.processName`: String 
- `data.metadata.processId`: Numeric PID

## 🎯 Event Type Specifications

### File Operation Events
```typescript
{
  event_type: "file_operation",
  data: {
    filePath: string,        // Full file path
    operation: string,       // "ReadFile" | "WriteFile" | etc
    content: string,         // Hex representation of data
    bytesTransferred: number,
    timestamp: string,       // ISO 8601
    metadata: {
      processName: string,   // e.g., "notepad.exe"
      processId: number      // PID
    }
  }
}
```

### HTTP Network Events
```typescript
{
  event_type: "http_network_operation", 
  data: {
    url: string,                // Full URL
    method: string,             // "GET" | "POST" | etc
    base64RequestBody: string,  // Base64 encoded request
    base64Response: string,     // Base64 encoded response
    bytesTransferred: number,
    timestamp: string,
    metadata: {
      processName: string,
      processId: number
    }
  }
}
```

### Raw Network Events  
```typescript
{
  event_type: "raw_network_operation",
  data: {
    host: string,            // IP address or hostname
    protocol: string,        // "tcp" | "udp" | "dns"
    request: string,         // Hex representation
    response: string,        // Hex representation
    bytesTransferred: number,
    timestamp: string,
    metadata: {
      processName: string,
      processId: number
    }
  }
}
```

### Process Creation Events
```typescript
{
  event_type: "process_creation_operation",
  data: {
    filePath: string,        // Path to executable
    args: string,            // Command line arguments
    timestamp: string,
    metadata: {
      processName: string,   // Parent process
      processId: number      // Parent PID
    }
  }
}
```

## 🔧 Backend Implementation Notes

### CORS Configuration
```javascript
// Express.js example
app.use(cors({
  origin: 'http://localhost:5173',
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type']
}));
```

### File Upload Handling
```javascript
// Multer example for file uploads
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });

app.post('/api/create-session', upload.single('file'), (req, res) => {
  const file = req.file;
  // Process file and create analysis session
  res.json({
    sessionId: generateSessionId(),
    vncServerHost: process.env.VNC_HOST,
    vncServerPort: process.env.VNC_PORT
  });
});
```

### Event Streaming
```javascript
// Return events for a session
app.get('/api/events/:sessionId', (req, res) => {
  const { sessionId } = req.params;
  const events = getEventsForSession(sessionId);
  
  // Sort by timestamp (latest first)
  events.sort((a, b) => 
    new Date(b.data.timestamp) - new Date(a.data.timestamp)
  );
  
  res.json(events);
});
```

## 🔍 Testing & Validation

### Sample Test Data
```json
[
  {
    "event_type": "file_operation",
    "data": {
      "filePath": "C:\\test\\file.txt",
      "operation": "WriteFile", 
      "content": "48 65 6C 6C 6F",
      "bytesTransferred": 5,
      "timestamp": "2025-10-25T12:00:00.000Z",
      "metadata": {
        "processName": "test.exe",
        "processId": 1234
      }
    }
  }
]
```

### Frontend Validation
The frontend validates:
- Response is valid JSON array
- Each event has required fields
- Timestamps are valid ISO 8601
- Process metadata is present

### Error Handling
```typescript
// Frontend error handling
try {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  const data = await response.json();
  if (!Array.isArray(data)) {
    throw new Error('Invalid response format: expected array');
  }
  return data;
} catch (error) {
  console.error('API Error:', error);
  // Display user-friendly error message
}
```