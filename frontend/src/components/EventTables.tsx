import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Card, CardContent } from './ui/card';
// import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import type { Event, FileOperationEvent, HttpNetworkEvent, RawNetworkEvent } from '../types/analysis';

interface EventTablesProps {
  events: Event[];
  onEventSelect?: (event: Event) => void;
}

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString();
}

function formatBytes(bytes: number): string {
  return `${bytes} B`;
}

export function EventTables({ events, onEventSelect }: EventTablesProps) {
  // Filter events by type, maintain the order from the API response
  const httpEvents = events.filter((e): e is HttpNetworkEvent => e.event_type === 'http_network_operation');
  const rawNetworkEvents = events.filter((e): e is RawNetworkEvent => e.event_type === 'raw_network_operation');
  const fileEvents = events.filter((e): e is FileOperationEvent => e.event_type === 'file_operation');

  console.log('EventTables - Total events:', events.length);
  console.log('EventTables - HTTP events:', httpEvents.length);
  console.log('EventTables - Network events:', rawNetworkEvents.length);
  console.log('EventTables - File events:', fileEvents.length);

  return (
    <Card className="h-full flex flex-col hover-lift">
      <CardContent className="flex-1 overflow-hidden p-4">
        <Tabs defaultValue="http" className="h-full flex flex-col">
          <TabsList className="grid w-full grid-cols-3 animate-fade-in">
            <TabsTrigger value="http" className="transition-all hover-scale relative">
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
                HTTP 
                {httpEvents.length > 0 && (
                  <Badge variant="secondary" className="ml-1 animate-scale-in event-badge-pulse">
                    {httpEvents.length}
                  </Badge>
                )}
              </span>
            </TabsTrigger>
            <TabsTrigger value="connections" className="transition-all hover-scale">
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Connections
                {rawNetworkEvents.length > 0 && (
                  <Badge variant="secondary" className="ml-1 animate-scale-in event-badge-pulse">
                    {rawNetworkEvents.length}
                  </Badge>
                )}
              </span>
            </TabsTrigger>
            <TabsTrigger value="files" className="transition-all hover-scale">
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                File Ops
                {fileEvents.length > 0 && (
                  <Badge variant="secondary" className="ml-1 animate-scale-in event-badge-pulse">
                    {fileEvents.length}
                  </Badge>
                )}
              </span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="http" className="flex-1 overflow-hidden animate-fade-in">
            <div className="h-full overflow-y-auto pr-2 scroll-container">
              <Table>
                <TableHeader className="sticky top-0 bg-background z-10">
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Method</TableHead>
                    <TableHead>URL</TableHead>
                    <TableHead>Bytes</TableHead>
                    <TableHead>Process</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody className="animate-stagger">
                  {httpEvents.map((event, index) => (
                    <TableRow 
                      key={`http-${event.data.timestamp}-${index}`}
                      className="cursor-pointer hover:bg-muted/70 transition-colors new-event-row"
                      onClick={() => onEventSelect?.(event)}
                    >
                      <TableCell className="font-mono text-xs">
                        {formatTimestamp(event.data.timestamp)}
                      </TableCell>
                      <TableCell>
                        <Badge variant={event.data?.method?.toUpperCase() === 'POST' ? 'default' : 'secondary'} className="hover-scale">
                          {event.data?.method?.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="max-w-xs truncate" title={event.data.url}>
                        {event.data.url}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatBytes(event.data.bytesTransferred)}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="text-xs">{event.data?.metadata?.processName ? event.data.metadata.processName : 'Unknown'}</span>
                          <span className="text-xs text-muted-foreground">PID: {event.data?.metadata?.processId ? event.data.metadata.processId : 'Unknown'}</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {httpEvents.length === 0 && (
                <div className="text-center text-muted-foreground py-12 animate-fade-in flex flex-col items-center gap-3">
                  <svg className="w-12 h-12 opacity-50 animate-bounce-slow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                  </svg>
                  <p>No HTTP requests detected yet</p>
                  <p className="text-xs">Waiting for network activity...</p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="connections" className="flex-1 overflow-hidden animate-fade-in">
            <div className="h-full overflow-y-auto pr-2 scroll-container">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Protocol</TableHead>
                    <TableHead>Host</TableHead>
                    <TableHead>Bytes</TableHead>
                    <TableHead>Process</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rawNetworkEvents.map((event, index) => (
                    <TableRow 
                      key={`network-${event.data.timestamp}-${index}`}
                      className="cursor-pointer hover:bg-muted/70"
                      onClick={() => onEventSelect?.(event)}
                    >
                      <TableCell className="font-mono text-xs">
                        {formatTimestamp(event.data.timestamp)}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {event.data.protocol.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>{event.data.host}</TableCell>
                      <TableCell className="text-right">
                        {formatBytes(event.data.bytesTransferred)}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="text-xs">{event.data.metadata.processName}</span>
                          <span className="text-xs text-muted-foreground">PID: {event.data.metadata.processId}</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {rawNetworkEvents.length === 0 && (
                <div className="text-center text-muted-foreground py-8">
                  No network connections detected yet
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="files" className="flex-1 overflow-hidden">
            <div className="h-full overflow-y-auto pr-2">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Operation</TableHead>
                    <TableHead>File Path</TableHead>
                    <TableHead>Bytes</TableHead>
                    <TableHead>Process</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {fileEvents.map((event, index) => (
                    <TableRow 
                      key={`file-${event.data.timestamp}-${index}`}
                      className="cursor-pointer hover:bg-muted/70"
                      onClick={() => onEventSelect?.(event)}
                    >
                      <TableCell className="font-mono text-xs">
                        {formatTimestamp(event.data.timestamp)}
                      </TableCell>
                      <TableCell>
                        <Badge variant={event.data.operation === 'WriteFile' ? 'destructive' : 'secondary'}>
                          {event.data.operation}
                        </Badge>
                      </TableCell>
                      <TableCell className="max-w-xs truncate" title={event.data.filePath}>
                        {event.data.filePath}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatBytes(event.data.bytesTransferred)}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="text-xs">{event.data.metadata.processName}</span>
                          <span className="text-xs text-muted-foreground">PID: {event.data.metadata.processId}</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {fileEvents.length === 0 && (
                <div className="text-center text-muted-foreground py-8">
                  No file operations detected yet
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}