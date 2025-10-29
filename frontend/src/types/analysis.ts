// Shared types for the analysis platform

export interface FileOperationEvent {
  event_type: 'file_operation';
  data: {
    filePath: string;
    bytesTransferred: number;
    content: string;
    timestamp: string;
    operation: string;
    metadata: {
      processName: string;
      processId: number;
    };
  };
}

export interface HttpNetworkEvent {
  event_type: 'http_network_operation';
  data: {
      metadata: {
      processName: string;
      processId: number;
    };
    kind: string;
    client: any;
    server: {
      ip: string | null;
    };
    request: {
      method: string;
      url: string;
      scheme: string;
      host: string;
      port: number;
      path: string;
      http_version: string;
      headers: Record<string, string>;
      body: {
        type: string;
        size: number;
        truncated: boolean;
      };
    };
    response: any;
    timestamp_ms: number;
    timestamp: string;
  };
}

export interface RawNetworkEvent {
  event_type: 'raw_network_operation';
  data: {
    request: string;
    bytesTransferred: number;
    response: string;
    timestamp: string;
    host: string;
    protocol: string;
    metadata: {
      processName: string;
      processId: number;
    };
  };
}

export interface ProcessCreationEvent {
  event_type: 'process_creation_operation';
  data: {
    filePath: string;
    args: string;
    timestamp: string;
    metadata: {
      processName: string;
      processId: number;
    };
  };
}

export type Event = FileOperationEvent | HttpNetworkEvent | RawNetworkEvent | ProcessCreationEvent;

export interface Process {
  processName: string;
  processId: number;
  timestamp: string;
}

export interface SessionData {
  sessionId: string;
}

export interface MonitorMode {
  id: number;
  mode: string;
}

export interface RunningProcess {
  name: string;
  pid: number;
}