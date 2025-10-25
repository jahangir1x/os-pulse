import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ProcessList } from './ProcessList';
import { EventTables } from './EventTables';
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

  // Fetch events every 1 second
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
          console.log('Setting events, count:', newEvents.length);
          // Simply set the events as received from API, no additional sorting needed
          // The API should return events in the correct order
          setEvents(newEvents);
          setLastUpdate(new Date());
        } else {
          console.warn('Received non-array response:', newEvents);
          setEvents([]);
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
    <div className="h-screen flex flex-col p-4 gap-4 bg-background">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Analysis Dashboard</h1>
          <p className="text-muted-foreground">
            Session: {sessionData.sessionId} | VNC: {sessionData.vncServerHost}:{sessionData.vncServerPort}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            {isLoading ? 'Loading...' : `${events.length} events`}
          </div>
          <div className="text-xs text-muted-foreground">
            Last update: {lastUpdate.toLocaleTimeString()}
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
          {/* VNC Area placeholder */}
          <div className="flex-1">
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Virtual Machine Display</CardTitle>
              </CardHeader>
              <CardContent className="h-full flex items-center justify-center">
                <div className="text-center text-muted-foreground">
                  <div className="w-32 h-32 mx-auto mb-4 bg-muted/50 rounded-lg flex items-center justify-center">
                    <div className="text-4xl">🖥️</div>
                  </div>
                  <p className="text-lg font-medium">noVNC Display</p>
                  <p className="text-sm">
                    VNC Server: {sessionData.vncServerHost}:{sessionData.vncServerPort}
                  </p>
                  <p className="text-xs mt-2 text-muted-foreground">
                    This area will be replaced with the noVNC client
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Event Tables */}
          <div className="h-80">
            <EventTables events={events} />
          </div>
        </div>

        {/* Right sidebar - Process list */}
        <div className="col-span-3">
          <ProcessList processes={processes} />
        </div>
      </div>
    </div>
  );
}