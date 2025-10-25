# OS Pulse - Malware Analysis Platform Frontend

## 📋 Project Overview

OS Pulse is a real-time malware analysis platform that provides a comprehensive dashboard for monitoring file operations, network activities, and process creation during malware execution in a controlled virtual environment.

## 🏗️ Architecture

### Frontend Stack
- **React 19** with TypeScript
- **Vite** for development and build tooling
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **Radix UI** for accessible component primitives

### Key Components

#### 1. App.tsx
Main application router that switches between:
- `FileUpload` component (initial upload screen)
- `AnalysisDashboard` component (main analysis interface)

#### 2. FileUpload.tsx
- Handles file selection and upload
- Posts to `http://localhost:3003/api/create-session`
- Receives session data: `{ sessionId, vncServerHost, vncServerPort }`
- Transitions to analysis dashboard upon successful upload

#### 3. AnalysisDashboard.tsx
Main dashboard with three sections:
- **Top Left**: VNC display area (placeholder for noVNC integration)
- **Right Sidebar**: Process list showing detected processes
- **Bottom**: Tabbed event tables (HTTP, Connections, File Operations)

#### 4. EventTables.tsx
Tabbed interface displaying:
- **HTTP Requests**: Method, URL, bytes, originating process
- **Connections**: Raw network operations with protocol/host
- **File Operations**: Read/write operations with file paths

#### 5. ProcessList.tsx
Sidebar component showing:
- Unique processes extracted from events
- Process names and PIDs
- Timestamps of first detection

## 🔄 Data Flow

### Event Fetching Logic
```
Every 1 second:
GET /api/events/:sessionId
↓
Parse JSON array response
↓
Replace entire events state
↓
Auto-extract processes from events
↓
Update UI tables (latest events first)
```

### Event Types Supported
```typescript
// File operations
{
  "event_type": "file_operation",
  "data": {
    "filePath": "\\\\?\\C:\\Windows\\System32\\file.dll",
    "operation": "ReadFile" | "WriteFile",
    "content": "AB 02 01 30", // hex data
    "bytesTransferred": 4,
    "timestamp": "2025-10-22T16:03:11.372Z",
    "metadata": { "processName": "notepad.exe", "processId": 800 }
  }
}

// HTTP network operations
{
  "event_type": "http_network_operation", 
  "data": {
    "url": "example.com/endpoint",
    "method": "POST",
    "base64RequestBody": "...",
    "base64Response": "...",
    "bytesTransferred": 20,
    "timestamp": "2025-10-22T16:03:11.372Z",
    "metadata": { "processName": "browser.exe", "processId": 1234 }
  }
}

// Raw network operations
{
  "event_type": "raw_network_operation",
  "data": {
    "host": "192.168.100.100", 
    "protocol": "tcp" | "udp" | "dns",
    "request": "AB CD 02 30", // hex
    "response": "02 AB CD EF", // hex
    "bytesTransferred": 20,
    "timestamp": "2025-10-22T16:03:11.372Z",
    "metadata": { "processName": "malware.exe", "processId": 5678 }
  }
}

// Process creation
{
  "event_type": "process_creation_operation",
  "data": {
    "filePath": "\\\\?\\C:\\Windows\\System32\\paint.exe",
    "args": "--some --arg1 --arg2",
    "timestamp": "2025-10-22T16:03:11.372Z", 
    "metadata": { "processName": "explorer.exe", "processId": 100 }
  }
}
```

## 🎨 UI Design

### Layout Structure
```
┌─────────────────────────────────────┬─────────────┐
│                                     │   Process   │
│         VNC Display Area            │    List     │
│        (noVNC Integration)          │  (Sidebar)  │  
│                                     │             │
├─────────────────────────────────────┤             │
│                                     │             │
│  ┌─────┬─────────┬──────────────┐   │             │
│  │HTTP │Connections│File Operations│   │             │
│  └─────┴─────────┴──────────────┘   │             │
│        Event Tables (Tabbed)        │             │
└─────────────────────────────────────┴─────────────┘
```

### Color Scheme & Styling
- Dark theme with professional blue/gray palette
- Consistent with security analysis tools aesthetic
- Real-time indicators (pulsing dots, live timestamps)
- Responsive design with proper spacing

## 🚀 Development

### Setup
```bash
npm install
npm run dev
```

### Key Dependencies
```json
{
  "@radix-ui/react-tabs": "^1.x.x",
  "@radix-ui/react-slot": "^1.x.x", 
  "tailwindcss": "^4.x.x",
  "lucide-react": "^0.x.x",
  "class-variance-authority": "^0.x.x"
}
```

### Environment
- Development server: `http://localhost:5173`
- Backend API: `http://localhost:3003`
- noVNC integration: TBD

## 🔧 Backend Integration

### Required Endpoints
- `POST /api/create-session` - File upload, returns session data
- `GET /api/events/:sessionId` - Fetch all events (polled every 1s)

### noVNC Integration
The VNC display area is currently a placeholder. Future integration should:
1. Use the `vncServerHost` and `vncServerPort` from session data
2. Embed noVNC client in the top-left card
3. Maintain responsive layout within the card boundaries

## 🐛 Debugging

### Console Logs Available
- Event fetching: `"Fetching events for session: [sessionId]"`
- API responses: `"Received events: [array]"`
- State updates: `"Events state updated, count: X"`
- Table filtering: Event counts per table type

### Common Issues
1. **Events not appearing**: Check browser console for API errors
2. **CORS issues**: Ensure backend allows frontend origin
3. **State not updating**: Verify JSON response format matches types
4. **Performance**: Monitor console for excessive re-renders

## 📁 File Structure
```
src/
├── components/
│   ├── ui/                    # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── table.tsx
│   │   ├── tabs.tsx
│   │   ├── input.tsx
│   │   └── badge.tsx
│   ├── FileUpload.tsx         # Initial upload screen
│   ├── AnalysisDashboard.tsx  # Main dashboard
│   ├── EventTables.tsx        # Tabbed event display
│   └── ProcessList.tsx        # Process sidebar
├── types/
│   └── analysis.ts            # Shared TypeScript types
├── lib/
│   └── utils.ts               # Utility functions
├── App.tsx                    # Main app component
└── main.tsx                   # React entry point
```

## 🔜 Future Enhancements

### Planned Features
1. **noVNC Integration**: Real VM display in dashboard
2. **Event Filtering**: Search and filter capabilities
3. **Export Functionality**: Download analysis reports
4. **Real-time Alerts**: Notifications for suspicious activities
5. **Timeline View**: Chronological event visualization
6. **Process Tree**: Hierarchical process relationships

### Technical Improvements
1. **WebSocket Integration**: Replace polling with real-time events
2. **Virtual Scrolling**: Handle large event datasets
3. **Event Persistence**: Local storage for session data
4. **Error Boundaries**: Better error handling and recovery
5. **Performance Optimization**: Memoization and lazy loading

## 📞 Support

For technical issues or questions about the frontend implementation, check:
1. Browser developer console for errors
2. Network tab for API communication issues
3. This documentation for architecture guidance
4. Component source code for implementation details