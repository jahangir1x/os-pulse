import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import type { Event, FileOperationEvent, HttpNetworkEvent, RawNetworkEvent } from '../types/analysis';

interface EventTablesProps {
  events: Event[];
}

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString();
}

function formatBytes(bytes: number): string {
  return `${bytes} B`;
}

export function EventTables({ events }: EventTablesProps) {
  // Filter events by type, maintain the order from the API response
  const httpEvents = events.filter((e): e is HttpNetworkEvent => e.event_type === 'http_network_operation');
  const rawNetworkEvents = events.filter((e): e is RawNetworkEvent => e.event_type === 'raw_network_operation');
  const fileEvents = events.filter((e): e is FileOperationEvent => e.event_type === 'file_operation');

  console.log('EventTables - Total events:', events.length);
  console.log('EventTables - HTTP events:', httpEvents.length);
  console.log('EventTables - Network events:', rawNetworkEvents.length);
  console.log('EventTables - File events:', fileEvents.length);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3 flex-shrink-0">
        <CardTitle className="text-lg">Event Analysis</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden">
        <Tabs defaultValue="http" className="h-full flex flex-col">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="http">
              HTTP Requests ({httpEvents.length})
            </TabsTrigger>
            <TabsTrigger value="connections">
              Connections ({rawNetworkEvents.length})
            </TabsTrigger>
            <TabsTrigger value="files">
              File Operations ({fileEvents.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="http" className="flex-1 overflow-hidden">
            <div className="h-full overflow-y-auto pr-2">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Method</TableHead>
                    <TableHead>URL</TableHead>
                    <TableHead>Bytes</TableHead>
                    <TableHead>Process</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {httpEvents.map((event, index) => (
                    <TableRow key={`http-${event.data.timestamp}-${index}`}>
                      <TableCell className="font-mono text-xs">
                        {formatTimestamp(event.data.timestamp)}
                      </TableCell>
                      <TableCell>
                        <Badge variant={event.data.method.toUpperCase() === 'POST' ? 'default' : 'secondary'}>
                          {event.data.method.toUpperCase()}
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
                          <span className="text-xs">{event.data.metadata.processName}</span>
                          <span className="text-xs text-muted-foreground">PID: {event.data.metadata.processId}</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {httpEvents.length === 0 && (
                <div className="text-center text-muted-foreground py-8">
                  No HTTP requests detected yet
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="connections" className="flex-1 overflow-hidden">
            <div className="h-full overflow-y-auto pr-2">
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
                    <TableRow key={`network-${event.data.timestamp}-${index}`}>
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
                    <TableRow key={`file-${event.data.timestamp}-${index}`}>
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