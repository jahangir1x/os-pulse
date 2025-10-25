# OS-Pulse Frontend 🔍

**Real-time Windows System Monitoring Dashboard**

A sophisticated React-based frontend for the OS-Pulse Windows system monitoring framework. This dashboard provides real-time visualization of file operations, process creation, and API events with comprehensive malware analysis capabilities.

[![React](https://img.shields.io/badge/React-19-blue?logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue?logo=typescript)](https://typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-7.1-purple?logo=vite)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.1-blue?logo=tailwindcss)](https://tailwindcss.com)

## 🎯 Features

### 🖥️ **Real-Time Dashboard**
- **VNC Integration**: Live view of monitored virtual environments via noVNC
- **Process Monitoring**: Real-time process list with PID tracking
- **Event Analysis**: Tabbed interface for HTTP, connections, and file operations
- **Live Updates**: WebSocket integration for real-time event streaming

### 📊 **Analysis Capabilities**
- **File Operations**: ReadFile/WriteFile monitoring with content extraction
- **Network Activity**: HTTP requests and raw connection tracking
- **Process Creation**: NtCreateUserProcess and legacy API monitoring
- **Behavioral Analysis**: Process relationship tracking and timeline visualization

### 🏗️ **Modern Architecture**
- **React 19**: Latest React with TypeScript for type safety
- **Shadcn/UI**: Accessible component library with Radix UI primitives
- **Tailwind CSS**: Utility-first styling with responsive design
- **Vite**: Fast development and optimized builds

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │  OS-Pulse Agent │
│   (React/TS)    │    │   (Node.js)     │    │ (Frida/Python)  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Dashboard     │    │ • Session Mgmt  │    │ • API Hooking   │
│ • VNC Viewer    │◄──►│ • Event Storage │◄──►│ • File Monitor  │
│ • Event Tables  │    │ • WebSocket     │    │ • Process Track │
│ • Process List  │    │ • File Upload   │    │ • Event Stream  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** with npm
- **Backend API** running on port 3003
- **OS-Pulse Agent** for data collection

### Development Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Configuration

The frontend expects the backend API to be running on `http://localhost:3003` with the following endpoints:
- `POST /api/create-session` - File upload and session creation
- `GET /api/events/:sessionId` - Event data retrieval
- WebSocket connection for real-time updates

## 📱 Component Structure

### Core Components

#### App.tsx
Main application router managing state between:
- **FileUpload**: Initial malware upload interface
- **AnalysisDashboard**: Main monitoring dashboard

#### AnalysisDashboard.tsx
Primary dashboard layout with:
- **VNC Display**: noVNC integration for live environment view
- **Process Sidebar**: Real-time process monitoring
- **Event Tables**: Comprehensive event analysis tabs

#### EventTables.tsx
Tabbed interface displaying:
- **HTTP Requests**: Method, URL, bytes, originating process
- **Connections**: Raw network operations with protocol/host details  
- **File Operations**: Read/write operations with file paths and content

#### ProcessList.tsx
Process monitoring sidebar showing:
- Unique processes extracted from monitoring events
- Process names, PIDs, and timestamps
- Process relationship tracking

### UI Components (shadcn/ui)
- **Tabs**: Event categorization and navigation
- **Tables**: Structured data display with sorting
- **Cards**: Information grouping and layout
- **Buttons**: Action triggers and navigation
- **Upload**: File selection and progress indication

## 🔄 Data Flow

### Event Processing Pipeline
```
OS-Pulse Agent → Backend API → WebSocket → Frontend Dashboard
     ↓              ↓            ↓              ↓
File/Process → Event Storage → Real-time → React State
  Events                      Updates      Management
```

### Session Management
1. **File Upload**: User uploads malware sample
2. **Session Creation**: Backend creates isolated analysis session
3. **VNC Connection**: noVNC connects to virtual environment
4. **Event Streaming**: Real-time event data via WebSocket
5. **Analysis Display**: Dashboard updates with live monitoring data

## 🎨 Styling & Theming

### Design System
- **Tailwind CSS 4.1**: Utility-first styling with custom configuration
- **Dark/Light Themes**: Automatic theme switching with next-themes
- **Responsive Design**: Mobile-first approach with breakpoint optimization
- **Accessibility**: WCAG 2.1 compliance through Radix UI primitives

### Color Scheme
- **Primary**: Security-focused blue tones
- **Accent**: Warning oranges and error reds
- **Neutral**: Professional grays for data display
- **Success**: Process completion and health indicators

## 🧪 Testing & Quality

### Code Quality
```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

### Development Tools
- **ESLint**: Code quality and consistency
- **TypeScript**: Static type checking
- **Prettier**: Code formatting
- **React DevTools**: Component debugging

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
