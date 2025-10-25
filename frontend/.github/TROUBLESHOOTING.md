# Troubleshooting Guide

## 🚨 Common Issues & Solutions

### 1. Events Not Appearing in UI

**Symptoms:**
- API calls are being made (visible in Network tab)
- No events showing in tables
- Console shows "Events state updated, count: 0"

**Debug Steps:**
1. Check browser console for error messages
2. Verify API response format in Network tab
3. Ensure response is valid JSON array
4. Check if events match expected type structure

**Solution:**
```typescript
// Verify API response structure matches:
[
  {
    "event_type": "file_operation" | "http_network_operation" | "raw_network_operation" | "process_creation_operation",
    "data": {
      "timestamp": "2025-10-22T16:03:11.372Z",
      "metadata": {
        "processName": "notepad.exe",
        "processId": 800
      },
      // ... other event-specific fields
    }
  }
]
```

### 2. CORS Errors

**Symptoms:**
- Network requests failing with CORS error
- "Access to fetch at '...' has been blocked by CORS policy"

**Solutions:**
```bash
# Backend needs to allow frontend origin
# Add to backend CORS config:
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

### 3. TypeScript Compilation Errors

**Common Issues:**
```typescript
// ❌ Wrong: Runtime error risk
import { Event } from '../types/analysis';

// ✅ Correct: Type-only import
import type { Event } from '../types/analysis';

// ❌ Wrong: Accessing nested property without checking
event.data.metadata.processId

// ✅ Correct: Safe property access
event.data?.metadata?.processId
```

### 4. Performance Issues

**Symptoms:**
- UI becomes sluggish
- High memory usage
- Browser freezing

**Solutions:**
```typescript
// ❌ Wrong: Memory leak
useEffect(() => {
  setInterval(fetchEvents, 1000); // No cleanup!
}, []);

// ✅ Correct: Proper cleanup
useEffect(() => {
  const interval = setInterval(fetchEvents, 1000);
  return () => clearInterval(interval);
}, [sessionId]);
```

### 5. File Upload Not Working

**Debug Checklist:**
- [ ] File is selected (check file input state)
- [ ] FormData is constructed correctly
- [ ] Backend endpoint is available
- [ ] File size is within limits
- [ ] Content-Type is not manually set (let browser set it)

**Correct Upload Pattern:**
```typescript
const formData = new FormData();
formData.append('file', file);

fetch('http://localhost:3003/api/create-session', {
  method: 'POST',
  body: formData, // Don't set Content-Type header manually
});
```

### 6. noVNC Integration Issues

**When implementing noVNC:**
- Use sessionData.vncServerHost and vncServerPort
- Embed within the existing card structure
- Maintain responsive design
- Handle connection errors gracefully

```typescript
// VNC URL construction
const vncUrl = `ws://${sessionData.vncServerHost}:${sessionData.vncServerPort}`;
```

## 🔍 Debugging Tools

### Browser DevTools
```javascript
// Inspect current component state (in React DevTools)
$r.state

// Check API response manually
fetch('http://localhost:3003/api/events/test-session-id')
  .then(r => r.json())
  .then(console.log);

// Monitor event state changes
window.addEventListener('storage', (e) => {
  console.log('Storage changed:', e.key, e.newValue);
});
```

### Console Logging Strategy
```typescript
// Temporary debugging (remove before production)
console.log('🔍 Debug - Events received:', events.length);
console.log('📊 Debug - Process count:', processes.length);
console.log('🚀 Debug - API call to:', url);

// Permanent logging for errors
console.error('❌ Failed to fetch events:', error);
console.warn('⚠️ Invalid event format:', event);
```

## 🔧 Development Environment Issues

### 1. Development Server Won't Start
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version compatibility
node --version  # Should be >= 18
```

### 2. Hot Reload Not Working
- Check if files are saved
- Restart dev server: `Ctrl+C` then `npm run dev`
- Clear browser cache
- Check for TypeScript errors that might block HMR

### 3. Build Failures
```bash
# Check for TypeScript errors
npx tsc --noEmit

# Check for linting issues
npm run lint

# Clean build
rm -rf dist
npm run build
```

## 📞 Getting Help

### Before Asking for Help:
1. Check browser console for errors
2. Verify API endpoints are responding
3. Test with sample data
4. Check this troubleshooting guide
5. Review component source code

### Information to Provide:
- Browser and version
- Node.js version
- Exact error messages
- Steps to reproduce
- Expected vs actual behavior
- Relevant console logs