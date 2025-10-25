import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import type { Process } from '../types/analysis';

interface ProcessListProps {
  processes: Process[];
}

export function ProcessList({ processes }: ProcessListProps) {
  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Processes ({processes.length})</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 overflow-y-auto max-h-96">
        {processes.length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            No processes detected yet
          </div>
        ) : (
          processes.map((process, index) => (
            <div
              key={`${process.processId}-${index}`}
              className="flex items-center justify-between p-3 bg-muted/50 rounded-md hover:bg-muted/70 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">
                  {process.processName}
                </div>
                <div className="text-sm text-muted-foreground">
                  PID: {process.processId}
                </div>
              </div>
              <div className="flex flex-col items-end">
                <Badge variant="outline" className="text-xs">
                  {process.processId}
                </Badge>
                <div className="text-xs text-muted-foreground mt-1">
                  {new Date(process.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}