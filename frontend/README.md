# OS-Pulse Frontend �️

**React-based real-time system monitoring dashboard for the OS-Pulse platform**

A modern, responsive web dashboard that provides comprehensive visualization and control for Windows system monitoring. Built with React 18, TypeScript, and Tailwind CSS to deliver real-time insights into system activities.

[![React](https://img.shields.io/badge/React-18-blue?logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue?logo=typescript)](https://typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-6.1-purple?logo=vite)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-blue?logo=tailwindcss)](https://tailwindcss.com)

## 🎯 Key Features

### 🖥️ **Real-Time Dashboard**
- **Live Event Display**: Real-time event tables with automatic updates
- **Process Monitoring**: Active process list with detailed information
- **Session Management**: Create and manage monitoring sessions
- **Status Monitoring**: Real-time agent and system status indicators

### 📊 **Analysis Capabilities**
- **File Operations**: ReadFile/WriteFile monitoring with content extraction
- **Process Events**: Process creation, termination, and lifecycle tracking
- **Session Analytics**: Comprehensive session-based event analysis
- **Export Functions**: Data export and reporting capabilities

### 🔧 **Monitoring Controls**
- **Start/Stop Monitoring**: Full control over monitoring activities
- **File Upload**: Target file processing and analysis
- **Conditional Event Fetching**: Optimized data loading based on monitoring state
- **Automatic UI Adjustments**: Smart zoom and layout management

### 🏗️ **Modern Architecture**
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Full type safety throughout the application
- **Shadcn/UI**: Accessible component library with Radix UI primitives
- **Tailwind CSS**: Utility-first styling with responsive design
- **Vite**: Fast development server and optimized production builds

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Go Backend    │    │  Agent Service  │
│   (React/TS)    │    │   (Echo/GORM)   │    │ (Python/Frida)  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Dashboard     │    │ • REST API      │    │ • File Monitor  │
│ • Event Tables  │◄──►│ • Event Storage │◄──►│ • Process Track │
│ • Session Mgmt  │    │ • Session Mgmt  │    │ • Network Mon   │
│ • File Upload   │    │ • Agent Coord   │    │ • Event Stream  │
│ • Monitoring UI │    │ • PostgreSQL    │    │ • HTTP Service  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** with npm
- **Go Backend** running on port 3003
- **Agent Service** running on port 7000 (for full functionality)

### 1. Installation
```bash
cd frontend
npm install
```

### 2. Development Server
```bash
npm run dev
# Dashboard available at http://localhost:5173
```

### 3. Production Build
```bash
npm run build
npm run preview
```
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
