import { Logger, FileOperationInfo, HookConfiguration } from '../types';
import { getFilePath, bytesToHex } from '../utils/windows-api';
import { EventSender } from '../messaging';

/**
 * Monitors file operations (ReadFile, WriteFile) using Frida interceptors
 */
export class FileOperationsMonitor {
    private logger: Logger;
    private config: HookConfiguration;
    private eventSender: EventSender;

    constructor(logger: Logger, config: HookConfiguration, eventSender: EventSender) {
        this.logger = logger;
        this.config = config;
        this.eventSender = eventSender;
    }

    /**
     * Initialize file operation monitoring hooks
     */
    initialize(): void {
        if (!this.config.enableFileOperations) {
            this.logger.debug("File operations monitoring disabled");
            return;
        }

        this.hookWriteFile();
        this.hookReadFile();
    }

    private hookWriteFile(): void {
        const WriteFile = Process.getModuleByName("kernel32.dll").findExportByName("WriteFile");
        
        if (!WriteFile) {
            this.logger.error("WriteFile export not found!");
            return;
        }

        const monitor = this;
        Interceptor.attach(WriteFile, {
            onEnter: function (args) {
                // WriteFile parameters:
                // BOOL WriteFile(
                //   [in]  HANDLE hFile,
                //   [in]  LPCVOID lpBuffer,
                //   [in]  DWORD nNumberOfBytesToWrite,
                //   [out] LPDWORD lpNumberOfBytesWritten,
                //   [in]  LPOVERLAPPED lpOverlapped
                // );
                
                this.handle = args[0];
                this.buffer = args[1];
                this.bytesToWrite = args[2].toInt32();
            },
            onLeave: function (retval) {
                if (retval.toInt32() !== 0) { // Write succeeded
                    monitor.handleWriteFileSuccess(this);
                }
            }
        });

        this.logger.info("Hooked WriteFile");
    }

    private handleWriteFileSuccess(interceptorContext: any): void {
        try {
            const filePath = getFilePath(interceptorContext.handle);
            let content: string | undefined;

            if (interceptorContext.bytesToWrite <= this.config.maxContentLength) {
                // Always encode as hex regardless of content type
                content = bytesToHex(interceptorContext.buffer, interceptorContext.bytesToWrite);
            } else {
                content = `<data too large: ${interceptorContext.bytesToWrite} bytes>`;
            }

            const info: FileOperationInfo = {
                handle: interceptorContext.handle,
                filePath,
                bytesTransferred: interceptorContext.bytesToWrite,
                content,
                timestamp: new Date().toISOString()
            };

            this.logger.logFileOperation("WriteFile", info);
            
            // Send event to host via Frida messaging
            this.eventSender.sendFileOperation("WriteFile", info);
        } catch (error) {
            this.logger.error(`Error processing WriteFile: ${error}`);
        }
    }

    private hookReadFile(): void {
        const ReadFile = Process.getModuleByName("kernel32.dll").findExportByName("ReadFile");
        
        if (!ReadFile) {
            this.logger.error("ReadFile export not found!");
            return;
        }

        const monitor = this;
        Interceptor.attach(ReadFile, {
            onEnter: function (args) {
                // ReadFile parameters:
                // BOOL ReadFile(
                //   [in]  HANDLE hFile,
                //   [out] LPVOID lpBuffer,
                //   [in]  DWORD nNumberOfBytesToRead,
                //   [out] LPDWORD lpNumberOfBytesRead,
                //   [in]  LPOVERLAPPED lpOverlapped
                // );
                
                this.handle = args[0];
                this.buffer = args[1];
                this.bytesToRead = args[2].toInt32();
                this.lpNumberOfBytesRead = args[3];
            },
            onLeave: function (retval) {
                if (retval.toInt32() !== 0) { // Read succeeded
                    monitor.handleReadFileSuccess(this);
                }
            }
        });

        this.logger.info("Hooked ReadFile");
    }

    private handleReadFileSuccess(interceptorContext: any): void {
        try {
            const filePath = getFilePath(interceptorContext.handle);
            
            // Get actual bytes read
            let bytesRead = 0;
            if (!interceptorContext.lpNumberOfBytesRead.isNull()) {
                bytesRead = interceptorContext.lpNumberOfBytesRead.readU32();
            }

            let content: string | undefined;
            if (bytesRead > 0 && bytesRead <= this.config.maxContentLength) {
                // Always encode as hex regardless of content type
                content = bytesToHex(interceptorContext.buffer, bytesRead);
            } else if (bytesRead > this.config.maxContentLength) {
                content = `<data too large: ${bytesRead} bytes>`;
            }

            const info: FileOperationInfo = {
                handle: interceptorContext.handle,
                filePath,
                bytesTransferred: bytesRead,
                content,
                timestamp: new Date().toISOString()
            };

            this.logger.logFileOperation("ReadFile", info);
            
            // Send event to host via Frida messaging
            this.eventSender.sendFileOperation("ReadFile", info);
        } catch (error) {
            this.logger.error(`Error processing ReadFile: ${error}`);
        }
    }
}
