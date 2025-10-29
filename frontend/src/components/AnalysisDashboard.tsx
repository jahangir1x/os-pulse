import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ProcessList } from './ProcessList';
import { EventTables } from './EventTables';
import { ThemeToggle } from './theme-toggle';
import { MonitoringControls } from './MonitoringControls';
import type { Event, Process, SessionData } from '../types/analysis';

interface AnalysisDashboardProps {
  sessionData: SessionData;
  onBackToUpload: () => void;
}

export function AnalysisDashboard({ sessionData, onBackToUpload }: AnalysisDashboardProps) {
  const [events, setEvents] = useState<Event[]>([]);
  const [processes, setProcesses] = useState<Process[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(0.8); // Start zoomed out to remove scrollbars
  const [isMonitoring, setIsMonitoring] = useState<boolean>(false);

  // Zoom control functions
  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.1, 2.0)); // Max zoom 200%
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 0.1, 0.3)); // Min zoom 30%
  };

  const handleResetZoom = () => {
    setZoomLevel(1.0); // Reset to 100%
  };

  // Download report handler
  const handleDownloadReport = async () => {
    try {
      const response = await fetch('http://localhost:3003/api/events/export');
      
      if (!response.ok) {
        throw new Error(`Failed to download report: ${response.statusText}`);
      }
      
      // Get the JSON blob
      const blob = await response.blob();
      
      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `os-pulse-report-${sessionData.sessionId}-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download report:', err);
      setError(err instanceof Error ? err.message : 'Failed to download report');
    }
  };

  // Handle monitoring state changes
  const handleMonitoringStateChange = (monitoring: boolean) => {
    setIsMonitoring(monitoring);
    if (!monitoring) {
      // Clear events and processes when monitoring stops
      setEvents([]);
      setProcesses([]);
      setSelectedEvent(null);
      setIsLoading(true);
      // Reset zoom to default when monitoring stops
      setZoomLevel(0.8);
    } else {
      // Set zoom to 40% when monitoring starts
      setZoomLevel(0.4);
    }
  };

  // Debug: log events when they change
  useEffect(() => {
    console.log('Events state updated, count:', events.length, events);
  }, [events]);

  // Extract unique processes from events
  useEffect(() => {
    const processMap = new Map<number, Process>();
    
    events.forEach(event => {
      if (event.data?.metadata?.processId && event.data?.metadata?.processName) {
        const pid = event.data.metadata.processId;
        const processName = event.data.metadata.processName;
        const timestamp = event.data.timestamp;
        
        // Keep the earliest timestamp for each process (when it was first seen)
        if (!processMap.has(pid)) {
          processMap.set(pid, {
            processId: pid,
            processName,
            timestamp
          });
        } else {
          // Update with earlier timestamp if found
          const existing = processMap.get(pid)!;
          if (new Date(timestamp).getTime() < new Date(existing.timestamp).getTime()) {
            processMap.set(pid, {
              processId: pid,
              processName,
              timestamp
            });
          }
        }
      }
      
      // Also extract processes from process creation events
      if (event.event_type === 'process_creation_operation' && event.data?.filePath) {
        const processName = event.data.filePath.split('\\').pop() || event.data.filePath;
        const pid = event.data.metadata?.processId || Math.random(); // fallback for demo
        const timestamp = event.data.timestamp;
        
        if (!processMap.has(pid)) {
          processMap.set(pid, {
            processId: pid,
            processName,
            timestamp
          });
        } else {
          // Update with earlier timestamp if found
          const existing = processMap.get(pid)!;
          if (new Date(timestamp).getTime() < new Date(existing.timestamp).getTime()) {
            processMap.set(pid, {
              processId: pid,
              processName,
              timestamp
            });
          }
        }
      }
    });
    
    // Sort processes by most recently active (latest event timestamp)
    setProcesses(Array.from(processMap.values()).sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    ));
  }, [events]);

  // Fetch events every 5 seconds and append new ones - only when monitoring is active
  useEffect(() => {
    if (!isMonitoring) {
      return; // Don't fetch events if monitoring is not active
    }

    const fetchEvents = async () => {
      try {
        console.log('Fetching events for session:', sessionData.sessionId);
        const response = await fetch(
          `http://localhost:3003/api/events/${sessionData.sessionId}`
        );
        
        if (!response.ok) {
          throw new Error(`Failed to fetch events: ${response.statusText}`);
        }
        
        const newEvents = await response.json();
        console.log('Received events:', newEvents);

        if (newEvents.length === 0) {
          // return early if no new events
          console.log('No new events received');
          setIsLoading(false);
          return;
        }
        
        if (Array.isArray(newEvents)) {
          console.log('Appending new events, count:', newEvents.length);
          
          setEvents(prevEvents => {
            // Simply prepend new events to the beginning (so they appear at top)
            return [...newEvents, ...prevEvents];
          });
          
          setLastUpdate(new Date());
        } else {
          console.warn('Received non-array response:', newEvents);
        }
        
        setIsLoading(false);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch events:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch events');
        setIsLoading(false);
      }
    };

    // Initial fetch
    fetchEvents();

    // Set up interval for periodic fetching
    const interval = setInterval(fetchEvents, 5000);

    return () => clearInterval(interval);
  }, [sessionData.sessionId, isMonitoring]);

  return (
    <div className="h-screen flex flex-col p-4 gap-4 bg-background overflow-hidden">
      {/* Header */}
      <div className="flex flex-col gap-3 shrink-0 animate-slide-in-down">
        {/* Main row - Title, monitoring controls, and status */}
        <div className="flex items-center justify-between">
          <div className="animate-fade-in">
            <h1 
              className="text-2xl font-bold bg-clip-text text-transparent bg-linear-to-r from-primary to-accent cursor-pointer hover-scale transition-all"
              onClick={onBackToUpload}
              title="Back to file upload"
            >
              OS-Pulse Dashboard
            </h1>
            <p className="text-muted-foreground flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-primary/10 text-xs font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-glow-pulse"></span>
                Session: {sessionData.sessionId}
              </span>
            </p>
          </div>
          
          {/* Center - Monitoring controls */}
          <div className="flex-1 flex justify-center px-8 animate-scale-in" style={{ animationDelay: '0.2s', opacity: 0 }}>
            <MonitoringControls 
              sessionData={sessionData} 
              onMonitoringStateChange={handleMonitoringStateChange}
            />
          </div>
          
          {/* Right - Status indicators */}
          <div className="flex items-center gap-4 animate-fade-in" style={{ animationDelay: '0.3s', opacity: 0 }}>
            {isMonitoring && (
              <button
                onClick={handleDownloadReport}
                className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-all hover-scale"
                title="Download events report"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download Report
              </button>
            )}
            <div className="flex items-center gap-2 text-sm">
              <div className="relative">
                <div className={`w-2 h-2 rounded-full ${isMonitoring ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                {isMonitoring && <div className="absolute inset-0 w-2 h-2 rounded-full bg-green-500 animate-ping"></div>}
              </div>
              {isMonitoring ? (
                isLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="spinner w-3 h-3 border-2"></span>
                    Loading...
                  </span>
                ) : (
                  <span className="font-medium">
                    <span className="stat-value">{events.length}</span> events
                  </span>
                )
              ) : (
                'Ready to monitor'
              )}
            </div>
            {isMonitoring && (
              <div className="text-xs text-muted-foreground flex items-center gap-1 animate-fade-in">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {lastUpdate.toLocaleTimeString()}
              </div>
            )}
            <ThemeToggle />
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 p-3 rounded-md flex items-start gap-2 animate-shake">
          <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/* Main content grid */}
      <div className="flex-1 grid gap-4 min-h-0 animate-stagger" style={{ gridTemplateColumns: isMonitoring ? '3fr 1fr' : '1fr' }}>
        {/* Left side - VNC area (top) and Event tables (bottom) */}
        <div className="flex flex-col gap-4">
          {/* VNC Area with zoom controls */}
          <div className="flex-1">
            <Card className="h-full dashboard-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Virtual Machine Display
                </CardTitle>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground font-mono">
                    {Math.round(zoomLevel * 100)}%
                  </span>
                  <div className="flex items-center gap-1 bg-muted/50 rounded-lg p-1">
                    <button
                      onClick={handleZoomOut}
                      className="p-1.5 rounded hover:bg-background transition-all hover-scale"
                      title="Zoom Out"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="11" cy="11" r="8"/>
                        <path d="M21 21l-4.35-4.35"/>
                        <line x1="8" y1="11" x2="14" y2="11"/>
                      </svg>
                    </button>
                    <button
                      onClick={handleResetZoom}
                      className="px-2 py-1 text-xs rounded hover:bg-background transition-all hover-scale font-medium"
                      title="Reset Zoom"
                    >
                      Reset
                    </button>
                    <button
                      onClick={handleZoomIn}
                      className="p-1.5 rounded hover:bg-background transition-all hover-scale"
                      title="Zoom In"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="11" cy="11" r="8"/>
                        <path d="M21 21l-4.35-4.35"/>
                        <line x1="11" y1="8" x2="11" y2="14"/>
                        <line x1="8" y1="11" x2="14" y2="11"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="w-full h-full overflow-hidden">
                <iframe
                  src="http://127.0.0.1:6080/vnc.html"
                  className="border-0 w-full h-full rounded-lg"
                  style={{ 
                    transform: `scale(${zoomLevel})`,
                    transformOrigin: 'top left',
                    width: `${100 / zoomLevel}%`,
                    height: `${100 / zoomLevel}%`
                  }}
                  title="noVNC Viewer"
                  allow="fullscreen"
                />
              </CardContent>
            </Card>
          </div>

          {/* Event Tables - only show when monitoring is active */}
          {isMonitoring && (
            <div className="h-70 dashboard-card" style={{ animationDelay: '0.2s' }}>
              <EventTables events={events} onEventSelect={setSelectedEvent} />
            </div>
          )}
        </div>

        {/* Right sidebar - Process list - only show when monitoring is active */}
        {isMonitoring && (
          <div className="dashboard-card" style={{ animationDelay: '0.3s' }}>
            <ProcessList 
              processes={processes} 
              selectedEvent={selectedEvent}
              onEventSelect={setSelectedEvent}
              onEventDeselect={() => setSelectedEvent(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
}