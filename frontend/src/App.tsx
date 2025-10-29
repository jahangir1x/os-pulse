/**
 * OS-Pulse Frontend - Main Application Component
 * 
 * A sophisticated React-based dashboard for real-time Windows system monitoring
 * and malware analysis. Provides comprehensive visualization of file operations,
 * process creation, and API events through dynamic instrumentation.
 * 
 * @author OS-Pulse Team
 * @version 1.0.0
 */
import './App.css'
import { useState } from 'react'
import { FileUpload } from './components/FileUpload'
import { AnalysisDashboard } from './components/AnalysisDashboard'
import type { SessionData } from './types/analysis'

function App() {
  const [sessionData, setSessionData] = useState<SessionData | null>(null)

  const handleSessionCreated = (data: SessionData) => {
    setSessionData(data)
  }

  const handleBackToUpload = () => {
    setSessionData(null)
  }

  return (
    <>
      {sessionData ? (
        <AnalysisDashboard sessionData={sessionData} onBackToUpload={handleBackToUpload} />
      ) : (
        <FileUpload onSessionCreated={handleSessionCreated} />
      )}
    </>
  )
}

export default App
