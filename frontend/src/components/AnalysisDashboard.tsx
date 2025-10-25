import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ProcessList } from './ProcessList';
import { EventTables } from './EventTables';
import { ThemeToggle } from './theme-toggle';
import { MonitoringControls } from './MonitoringControls';
import type { Event, Process, SessionData } from '../types/analysis';

interface AnalysisDashboardProps {
  sessionData: SessionData;
}

export function AnalysisDashboard({ sessionData }: AnalysisDashboardProps) {
  const [events, setEvents] = useState<Event[]>([]);
  const [processes, setProcesses] = useState<Process[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(0.8); // Start zoomed out to remove scrollbars

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

  // Fetch events every 5 seconds and append new ones
  useEffect(() => {
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
  }, [sessionData.sessionId]);

  return (
    <div className="h-screen flex flex-col p-4 gap-4 bg-background overflow-hidden">
      {/* Header */}
      <div className="flex flex-col gap-3 shrink-0">
        {/* Main row - Title, monitoring controls, and status */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">OS-Pulse Dashboard</h1>
            <p className="text-muted-foreground">
              Session: {sessionData.sessionId}
            </p>
          </div>
          
          {/* Center - Monitoring controls */}
          <div className="flex-1 flex justify-center px-8">
            <MonitoringControls sessionData={sessionData} />
          </div>
          
          {/* Right - Status indicators */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              {isLoading ? 'Loading...' : `${events.length} events`}
            </div>
            <div className="text-xs text-muted-foreground">
              Last update: {lastUpdate.toLocaleTimeString()}
            </div>
            <ThemeToggle />
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 p-3 rounded-md">
          {error}
        </div>
      )}

      {/* Main content grid */}
      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        {/* Left side - VNC area (top) and Event tables (bottom) */}
        <div className="col-span-9 flex flex-col gap-4">
          {/* VNC Area with zoom controls */}
          <div className="flex-1">
            <Card className="h-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle>Virtual Machine Display</CardTitle>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">
                    {Math.round(zoomLevel * 100)}%
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={handleZoomOut}
                      className="p-1 rounded hover:bg-muted transition-colors"
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
                      className="px-2 py-1 text-xs rounded hover:bg-muted transition-colors"
                      title="Reset Zoom"
                    >
                      1:1
                    </button>
                    <button
                      onClick={handleZoomIn}
                      className="p-1 rounded hover:bg-muted transition-colors"
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
                  className="border-0 w-full h-full"
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

          {/* Event Tables */}
          <div className="h-70">
            <EventTables events={events} onEventSelect={setSelectedEvent} />
          </div>
        </div>

        {/* Right sidebar - Process list */}
        <div className="col-span-3">
          <ProcessList 
            processes={processes} 
            selectedEvent={selectedEvent}
            onEventSelect={setSelectedEvent}
            onEventDeselect={() => setSelectedEvent(null)}
          />
        </div>
      </div>
    </div>
  );
}