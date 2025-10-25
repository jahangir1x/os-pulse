import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Checkbox } from './ui/checkbox';
import type { MonitorMode, RunningProcess, SessionData } from '../types/analysis';

interface MonitoringControlsProps {
  sessionData: SessionData;
}

export function MonitoringControls({ sessionData }: MonitoringControlsProps) {
  const [monitorModes, setMonitorModes] = useState<MonitorMode[]>([]);
  const [selectedMode, setSelectedMode] = useState<string>('');
  const [isProcessDialogOpen, setIsProcessDialogOpen] = useState(false);
  const [runningProcesses, setRunningProcesses] = useState<RunningProcess[]>([]);
  const [selectedProcesses, setSelectedProcesses] = useState<Set<number>>(new Set());
  const [isLoading, setIsLoading] = useState(false);

  // Fetch monitor modes on component mount
  useEffect(() => {
    const fetchMonitorModes = async () => {
      try {
        console.log('Fetching monitor modes...');
        const response = await fetch('http://localhost:3003/api/monitor-modes');
        console.log('Monitor modes response:', response.status);
        
        if (response.ok) {
          const modes = await response.json();
          console.log('Monitor modes data:', modes);
          setMonitorModes(modes);
        } else {
          console.error('Failed to fetch monitor modes:', response.status, response.statusText);
          // For demo purposes, set some dummy data if API fails
          const dummyModes = [
            { id: 1, mode: "All Processes" },
            { id: 2, mode: "Specific Processes" },
            { id: 3, mode: "Spawn Uploaded" }
          ];
          console.log('Using dummy data:', dummyModes);
          setMonitorModes(dummyModes);
        }
      } catch (error) {
        console.error('Failed to fetch monitor modes:', error);
        // For demo purposes, set some dummy data if API fails
        const dummyModes = [
          { id: 1, mode: "All Processes" },
          { id: 2, mode: "Specific Processes" },
          { id: 3, mode: "Spawn Uploaded" }
        ];
        console.log('Using dummy data after error:', dummyModes);
        setMonitorModes(dummyModes);
      }
    };

    fetchMonitorModes();
  }, []);

  // Fetch running processes when "Specific Processes" is selected
  const fetchRunningProcesses = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:3003/api/list-processes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId: sessionData.sessionId,
        }),
      });

      if (response.ok) {
        const processes = await response.json();
        setRunningProcesses(processes);
        setIsProcessDialogOpen(true);
      }
    } catch (error) {
      console.error('Failed to fetch running processes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle mode selection
  const handleModeChange = async (modeId: string) => {
    setSelectedMode(modeId);
    
    // If "Specific Processes" is selected, fetch processes
    if (modeId === '2') {
      await fetchRunningProcesses();
    }
  };

  // Handle process selection in dialog
  const handleProcessToggle = (pid: number) => {
    const newSelected = new Set(selectedProcesses);
    if (newSelected.has(pid)) {
      newSelected.delete(pid);
    } else {
      newSelected.add(pid);
    }
    setSelectedProcesses(newSelected);
  };

  // Start monitoring
  const handleStartMonitoring = async () => {
    try {
      setIsLoading(true);
      
      const requestBody: {
        sessionId: string;
        mode: number;
        processes?: number[];
      } = {
        sessionId: sessionData.sessionId,
        mode: parseInt(selectedMode),
      };

      // Add processes for specific mode
      if (selectedMode === '2' && selectedProcesses.size > 0) {
        requestBody.processes = Array.from(selectedProcesses);
      }

      const response = await fetch('http://localhost:3003/api/start-monitor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        console.log('Monitoring started successfully');
        // Optionally show success message
      }
    } catch (error) {
      console.error('Failed to start monitoring:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Check if start button should be shown
  const shouldShowStartButton = () => {
    if (!selectedMode) return false;
    if (selectedMode === '2') {
      // For specific processes, only show button if processes are selected
      return selectedProcesses.size > 0;
    }
    // For "All Processes" (1) and "Spawn Uploaded" (3)
    return selectedMode === '1' || selectedMode === '3';
  };

  console.log('Current monitorModes state:', monitorModes);

  return (
    <div className="flex items-center gap-3">
      <Select value={selectedMode} onValueChange={handleModeChange}>
        <SelectTrigger className="w-48">
          <SelectValue placeholder="Select monitoring mode" />
        </SelectTrigger>
        <SelectContent>
          {monitorModes.length === 0 ? (
            <SelectItem value="loading" disabled>
              Loading modes...
            </SelectItem>
          ) : (
            monitorModes.map((mode) => {
              console.log('Rendering mode:', mode);
              return (
                <SelectItem key={mode.id} value={mode.id.toString()}>
                  {mode.mode}
                </SelectItem>
              );
            })
          )}
        </SelectContent>
      </Select>

      {shouldShowStartButton() && (
        <Button 
          onClick={handleStartMonitoring} 
          disabled={isLoading}
          className="shrink-0"
        >
          {isLoading ? 'Starting...' : 'Start Monitoring'}
        </Button>
      )}

      {selectedMode === '2' && selectedProcesses.size > 0 && (
        <Button 
          variant="outline" 
          onClick={() => setIsProcessDialogOpen(true)}
          className="shrink-0"
        >
          {selectedProcesses.size} processes selected
        </Button>
      )}

      {/* Process Selection Dialog */}
      <Dialog open={isProcessDialogOpen} onOpenChange={setIsProcessDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>Select Processes to Monitor</DialogTitle>
          </DialogHeader>
          
          <div className="flex-1 overflow-y-auto pr-2">
            <div className="space-y-2">
              {runningProcesses.map((process) => (
                <div
                  key={`${process.name}-${process.pid}`}
                  className="flex items-center space-x-3 p-2 rounded hover:bg-muted"
                >
                  <Checkbox
                    checked={selectedProcesses.has(process.pid)}
                    onCheckedChange={() => handleProcessToggle(process.pid)}
                  />
                  <div className="flex-1">
                    <div className="font-medium">{process.name}</div>
                    <div className="text-sm text-muted-foreground">PID: {process.pid}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsProcessDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={() => setIsProcessDialogOpen(false)}
              disabled={selectedProcesses.size === 0}
            >
              Select {selectedProcesses.size} Processes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}