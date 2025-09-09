import { FileOperationInfo, ProcessCreationInfo } from '../types';

/**
 * Simple event sender interface using Frida's send() and recv() functions
 * Sends monitoring events to the host in JSON format
 */
export interface EventSender {
    sendFileOperation(operation: string, info: FileOperationInfo): void;
    sendProcessCreation(operation: string, info: ProcessCreationInfo): void;
}

/**
 * Frida-based event sender implementation
 * Uses Frida's native send() function to communicate with the host
 */
export class FridaEventSender implements EventSender {
    private sessionId: string;
    private processName: string;
    private processId: number;

    constructor() {
        this.sessionId = this.generateSessionId();
        this.processName = Process.enumerateModules()[0].name;
        this.processId = Process.id;

        // Setup message handlers for host communication
        this.setupMessageHandlers();
        
        // Send initialization message
        this.sendMetadata();
    }

    /**
     * Send file operation event to host
     */
    sendFileOperation(operation: string, info: FileOperationInfo): void {
        const event = {
            type: 'file_operation',
            operation: operation,
            data: {
                handle: info.handle.toString(),
                filePath: info.filePath,
                bytesTransferred: info.bytesTransferred,
                content: info.content,
                timestamp: info.timestamp
            },
            metadata: {
                sessionId: this.sessionId,
                processName: this.processName,
                processId: this.processId
            }
        };

        try {
            send(event);
        } catch (error) {
            console.log(`[ERROR] Failed to send file operation event: ${error}`);
        }
    }

    /**
     * Send process creation event to host
     */
    sendProcessCreation(operation: string, info: ProcessCreationInfo): void {
        const event = {
            type: 'process_creation',
            operation: operation,
            data: {
                processHandle: info.processHandle?.toString(),
                threadHandle: info.threadHandle?.toString(),
                imagePath: info.imagePath,
                commandLine: info.commandLine,
                currentDirectory: info.currentDirectory,
                parentProcess: info.parentProcess?.toString(),
                flags: info.flags,
                sectionHandle: info.sectionHandle?.toString(),
                status: info.status,
                timestamp: info.timestamp
            },
            metadata: {
                sessionId: this.sessionId,
                processName: this.processName,
                processId: this.processId
            }
        };

        try {
            send(event);
        } catch (error) {
            console.log(`[ERROR] Failed to send process creation event: ${error}`);
        }
    }

    /**
     * Setup message handlers for bidirectional communication
     */
    private setupMessageHandlers(): void {
        // Handle ping requests from host
        recv('ping', (message) => {
            send({
                type: 'pong',
                timestamp: new Date().toISOString(),
                sessionId: this.sessionId
            });
        });

        // Handle configuration updates from host
        recv('config_update', (message) => {
            console.log(`[INFO] Received config update: ${JSON.stringify(message)}`);
            // Configuration updates can be handled here if needed
        });

        // Handle status requests
        recv('status', (message) => {
            send({
                type: 'status_response',
                data: {
                    sessionId: this.sessionId,
                    processName: this.processName,
                    processId: this.processId,
                    timestamp: new Date().toISOString(),
                    status: 'active'
                }
            });
        });
    }

    /**
     * Send initial metadata to host
     */
    private sendMetadata(): void {
        const metadata = {
            type: 'session_start',
            data: {
                sessionId: this.sessionId,
                processName: this.processName,
                processId: this.processId,
                timestamp: new Date().toISOString(),
                platform: Process.platform,
                arch: Process.arch
            }
        };

        try {
            send(metadata);
        } catch (error) {
            console.log(`[ERROR] Failed to send metadata: ${error}`);
        }
    }

    /**
     * Generate unique session ID
     */
    private generateSessionId(): string {
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substring(2);
        return `${timestamp}-${random}`;
    }
}

/**
 * Global event sender instance
 */
export const eventSender = new FridaEventSender();
