# Copilot Instructions for OS Pulse Frontend

## 🎯 Project Context
This is a **malware analysis platform frontend** built with React + TypeScript. The application provides a dashboard for monitoring malware behavior in real-time through file operations, network activities, and process monitoring.

## 🏗️ Architecture Guidelines

### Component Structure
- **Atomic Design**: Use shadcn/ui components as building blocks
- **Type Safety**: All components use TypeScript with shared types from `src/types/analysis.ts`
- **Separation of Concerns**: Each component has a single responsibility
- **Real-time Updates**: Components handle live data updates via polling

### Key Design Patterns
```typescript
// 1. Use shared types for consistency
import type { Event, SessionData, Process } from '../types/analysis';

// 2. Handle async operations with proper error states
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

// 3. Use useEffect for data fetching with cleanup
useEffect(() => {
  const interval = setInterval(fetchData, 1000);
  return () => clearInterval(interval);
}, [dependencies]);
```

## 🔄 Data Flow Principles

### Event Handling
- **Replace, Don't Append**: Each API response completely replaces previous events
- **No Client-Side Filtering**: Display events exactly as received from API
- **Timestamp Ordering**: API provides events in correct order (latest first)
- **Process Extraction**: Dynamically build process list from current events

### API Integration
```typescript
// Standard fetch pattern for this project
const fetchEvents = async () => {
  try {
    const response = await fetch(`http://localhost:3003/api/events/${sessionId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const events = await response.json();
    setEvents(events); // Direct replacement, no transformation
  } catch (err) {
    setError(err.message);
  }
};
```

## 🎨 UI/UX Guidelines

### Visual Design
- **Dark Theme**: Professional security tool aesthetic
- **Consistent Spacing**: Use Tailwind classes for uniform layout
- **Real-time Indicators**: Pulsing dots, live timestamps, loading states
- **Responsive Layout**: Grid-based layout that adapts to screen size

### Component Patterns
```typescript
// Card wrapper for major sections
<Card className="h-full">
  <CardHeader>
    <CardTitle>Section Title ({count})</CardTitle>
  </CardHeader>
  <CardContent>
    {/* Content with overflow handling */}
  </CardContent>
</Card>

// Table with proper key handling
{events.map((event, index) => (
  <TableRow key={`${event.event_type}-${event.data.timestamp}-${index}`}>
    {/* Row content */}
  </TableRow>
))}
```

## 🔧 Development Workflows

### Adding New Event Types
1. Update `src/types/analysis.ts` with new event interface
2. Add filtering logic in `EventTables.tsx`
3. Create new tab or modify existing table structure
4. Update process extraction logic if needed

### Adding New UI Components
1. Use shadcn/ui CLI: `npx shadcn-ui@latest add [component]`
2. Import with type-only imports: `import type { ... } from '...'`
3. Follow existing patterns for styling and accessibility

### Debugging Guidelines
```typescript
// Add console logs for debugging (remove before production)
console.log('Events state updated:', events.length, events);
console.log('API response:', response);

// Use descriptive error messages
throw new Error(`Failed to fetch events: ${response.statusText}`);

// Visual debug indicators in UI
<div className="text-xs text-muted-foreground">
  Last update: {lastUpdate.toLocaleTimeString()}
</div>
```

## 🚨 Common Pitfalls to Avoid

### Performance Issues
- ❌ Don't add unnecessary sorting/filtering client-side
- ❌ Don't accumulate events without cleanup
- ❌ Don't use object/array indexes as React keys for dynamic data
- ✅ Trust API ordering and display directly
- ✅ Use proper React keys with unique identifiers
- ✅ Implement proper cleanup in useEffect

### Type Safety Issues
- ❌ Don't use `any` types
- ❌ Don't access nested properties without optional chaining
- ✅ Use type-only imports for interfaces
- ✅ Use proper type guards for event filtering
- ✅ Define shared types in `src/types/analysis.ts`

### State Management
- ❌ Don't mutate state directly
- ❌ Don't mix different data sources in one state
- ✅ Replace entire state for real-time data
- ✅ Use separate states for different concerns
- ✅ Handle loading and error states explicitly

## 🔗 Integration Points

### Backend API Contract
```typescript
// Session creation
POST /api/create-session
FormData: { file: File }
Response: { sessionId: string, vncServerHost: string, vncServerPort: string }

// Event fetching  
GET /api/events/:sessionId
Response: Event[] // Array of events, latest first
```

### noVNC Integration (Future)
- Placeholder area: Top-left card in dashboard
- Integration points: Use sessionData.vncServerHost:vncServerPort
- Maintain responsive layout within card boundaries

## 📝 Code Review Checklist

### Before Submitting Code
- [ ] All TypeScript errors resolved
- [ ] Components use shared types from `src/types/analysis.ts`
- [ ] Proper error handling with user-friendly messages
- [ ] Console logs removed (except for debugging)
- [ ] Responsive design tested
- [ ] Real-time updates working correctly
- [ ] Performance impact considered (especially for polling)

### Architecture Compliance
- [ ] Components follow single responsibility principle
- [ ] State management is appropriate for component scope
- [ ] API integration follows established patterns
- [ ] UI/UX matches existing design system
- [ ] Accessibility considerations included

## 🎯 Context for AI Assistants

### Project Goals
This is a **security analysis tool** for malware research. The UI should be:
- Professional and technical (not consumer-facing)
- Real-time and responsive to live data
- Comprehensive in displaying security events
- Intuitive for security analysts

### Technical Priorities
1. **Real-time Performance**: Handle continuous data updates smoothly
2. **Type Safety**: Prevent runtime errors in security-critical application
3. **Maintainability**: Clear, documented code for team collaboration
4. **Extensibility**: Easy to add new event types and features

### User Context
Primary users are security analysts who need:
- Quick identification of malicious behavior
- Detailed event information for investigation
- Reliable, always-updated information
- Professional tool interface they can trust