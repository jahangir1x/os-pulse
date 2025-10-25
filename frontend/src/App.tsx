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

  return (
    <>
      {sessionData ? (
        <AnalysisDashboard sessionData={sessionData} />
      ) : (
        <FileUpload onSessionCreated={handleSessionCreated} />
      )}
    </>
  )
}

export default App
