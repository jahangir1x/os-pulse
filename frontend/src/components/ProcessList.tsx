import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import type { Process, Event } from '../types/analysis';
import { useState, useEffect } from 'react';

interface ProcessListProps {
  processes: Process[];
  selectedEvent?: Event | null;
  onEventSelect?: (event: Event | null) => void;
  onEventDeselect?: () => void;
}

export function ProcessList({ processes, selectedEvent, onEventSelect, onEventDeselect }: ProcessListProps) {
  const [activeTab, setActiveTab] = useState<string>("processes");

  // Auto-switch to details when an event is selected
  useEffect(() => {
    if (selectedEvent) {
      setActiveTab("details");
    }
  }, [selectedEvent]);

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    // If switching back to processes tab and there's a selected event, deselect it
    if (value === "processes" && selectedEvent && onEventDeselect) {
      onEventDeselect();
    }
  };
  const formatTimestamp = (timestamp: string): string => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatBytes = (bytes?: number): string => {
    return bytes ? `${bytes} B` : 'N/A';
  };

  const renderEventDetails = () => {
    if (!selectedEvent) {
      return (
        <div className="text-center text-muted-foreground py-8">
          Click on an event from the tables below to view details
        </div>
      );
    }

    const { event_type, data } = selectedEvent;

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="text-sm">
            {event_type.replace(/_/g, ' ').toUpperCase()}
          </Badge>
          <button
            onClick={() => onEventSelect?.(null)}
            className="text-xs text-muted-foreground hover:text-foreground"
          >
            Clear
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-muted-foreground">Timestamp</label>
            <p className="text-sm font-mono">{formatTimestamp(data.timestamp)}</p>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground">Process</label>
            <p className="text-sm">{data.metadata?.processName} (PID: {data.metadata?.processId})</p>
          </div>

          {event_type === 'file_operation' && (
            <>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Operation</label>
                <p className="text-sm">{data.operation}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">File Path</label>
                <p className="text-sm break-all">{data.filePath}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Content (Hex)</label>
                <p className="text-xs font-mono bg-muted p-2 rounded break-all">{data.content}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Bytes Transferred</label>
                <p className="text-sm">{formatBytes(data.bytesTransferred)}</p>
              </div>
            </>
          )}

          {event_type === 'http_network_operation' && (
            <>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Method</label>
                <p className="text-sm">{data.method?.toUpperCase()}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">URL</label>
                <p className="text-sm break-all">{data.url}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Request Body (Base64)</label>
                <p className="text-xs font-mono bg-muted p-2 rounded break-all max-h-20 overflow-y-auto">
                  {data.base64RequestBody || 'Empty'}
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Response (Base64)</label>
                <p className="text-xs font-mono bg-muted p-2 rounded break-all max-h-20 overflow-y-auto">
                  {data.base64Response || 'Empty'}
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Bytes Transferred</label>
                <p className="text-sm">{formatBytes(data.bytesTransferred)}</p>
              </div>
            </>
          )}

          {event_type === 'raw_network_operation' && (
            <>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Protocol</label>
                <p className="text-sm">{data.protocol?.toUpperCase()}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Host</label>
                <p className="text-sm">{data.host}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Request (Hex)</label>
                <p className="text-xs font-mono bg-muted p-2 rounded break-all">{data.request}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Response (Hex)</label>
                <p className="text-xs font-mono bg-muted p-2 rounded break-all">{data.response}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Bytes Transferred</label>
                <p className="text-sm">{formatBytes(data.bytesTransferred)}</p>
              </div>
            </>
          )}

          {event_type === 'process_creation_operation' && (
            <>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Executable Path</label>
                <p className="text-sm break-all">{data.filePath}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Arguments</label>
                <p className="text-sm break-all">{data.args || 'None'}</p>
              </div>
            </>
          )}
        </div>
      </div>
    );
  };

  return (
    <Card className="h-full flex flex-col">
      <CardContent className="flex-1 overflow-hidden p-0">
        <Tabs value={activeTab} onValueChange={handleTabChange} className="h-full flex flex-col">
          <div className="px-6 pt-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="processes">
                Processes ({processes.length})
              </TabsTrigger>
              <TabsTrigger value="details">
                Details
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="processes" className="flex-1 overflow-hidden px-6 pb-6">
            <div className="h-full overflow-y-auto pr-2">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Process</TableHead>
                    <TableHead>PID</TableHead>
                    <TableHead>First Seen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {processes.map((process, index) => (
                    <TableRow key={`${process.processId}-${index}`}>
                      <TableCell className="font-medium">
                        {process.processName}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs">
                          {process.processId}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {formatTimestamp(process.timestamp)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {processes.length === 0 && (
                <div className="text-center text-muted-foreground py-8">
                  No processes detected yet
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="details" className="flex-1 overflow-hidden px-6 pb-6">
            <div className="h-full overflow-y-auto pr-2">
              {renderEventDetails()}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}