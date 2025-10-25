# Development Quick Reference

## 🚀 Quick Start
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🔧 Common Tasks

### Adding New shadcn/ui Components
```bash
npx shadcn-ui@latest add [component-name]
```

### Backend Connection
- API Base: `http://localhost:3003`
- Upload: `POST /api/create-session`
- Events: `GET /api/events/:sessionId`

### Key File Locations
- Types: `src/types/analysis.ts`
- Main Dashboard: `src/components/AnalysisDashboard.tsx`
- Event Tables: `src/components/EventTables.tsx`
- Upload: `src/components/FileUpload.tsx`

## 🐛 Debugging

### Browser Console Commands
```javascript
// Check current events
console.log(window.currentEvents);

// Monitor API calls
fetch('/api/events/test-session').then(r => r.json()).then(console.log);
```

### Common Issues
1. **CORS Error**: Check backend CORS settings
2. **Events Not Updating**: Verify API response format
3. **TypeScript Errors**: Check imports use `type` keyword
4. **Styling Issues**: Ensure Tailwind classes are correct

## 📋 Component Checklist

### New Component Template
```typescript
import type { ComponentProps } from '../types/analysis';

interface Props {
  // Define props
}

export function ComponentName({ prop }: Props) {
  // State management
  // Event handlers  
  // Effects
  
  return (
    // JSX with proper accessibility
  );
}
```

### Required Patterns
- [ ] TypeScript interfaces defined
- [ ] Error states handled
- [ ] Loading states implemented
- [ ] Responsive design classes
- [ ] Proper React keys for lists
- [ ] Console logs removed

## 🎨 Design System

### Colors
- Primary: Blue variants for actions
- Secondary: Gray variants for info
- Success: Green for positive states
- Warning: Yellow for caution
- Destructive: Red for danger/write operations

### Spacing
- Cards: `gap-4` between sections
- Tables: `p-2` for cells
- Forms: `space-y-4` for form elements

### Typography
- Headers: `text-lg font-semibold`
- Body: Default text size
- Captions: `text-sm text-muted-foreground`
- Code: `font-mono text-xs`