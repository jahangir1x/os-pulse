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
    request: {
      method: string;
      url: string;
      body: {
        content_b64: string;
        size: number;
      }
    },
    response: {
      body: {
        content_b64: string;
        size: number;
      }
    },
    timestamp: string;
    metadata: {
      processName: string;
      processId: number;
    };
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