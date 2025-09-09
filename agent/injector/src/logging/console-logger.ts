import { Logger, FileOperationInfo, ProcessCreationInfo } from '../types';

/**
 * Console logger implementation with structured output
 */
export class ConsoleLogger implements Logger {
    
    info(message: string): void {
        console.log(`[INFO] ${message}`);
    }

    error(message: string): void {
        console.log(`[ERROR] ${message}`);
    }

    debug(message: string): void {
        console.log(`[DEBUG] ${message}`);
    }

    logFileOperation(operation: string, info: FileOperationInfo): void {
        console.log(`\n[${operation}]`);
        console.log(`Path: ${info.filePath || "Unknown"}`);
        console.log(`Bytes: ${info.bytesTransferred}`);
        
        if (info.content) {
            console.log(`Content: ${info.content}`);
        }
        
        console.log(`Timestamp: ${info.timestamp}`);
    }

    logProcessCreation(operation: string, info: ProcessCreationInfo): void {
        console.log(`\n[${operation}]`);
        console.log(`Status: ${info.status >= 0 ? 'SUCCESS' : 'FAILED'} (0x${info.status.toString(16).padStart(8, '0')})`);
        
        if (info.processHandle) {
            console.log(`Process Handle: 0x${info.processHandle.toString(16)}`);
        }
        
        if (info.threadHandle) {
            console.log(`Thread Handle: 0x${info.threadHandle.toString(16)}`);
        }
        
        if (info.imagePath) {
            console.log(`Image Path: ${info.imagePath}`);
        }
        
        if (info.commandLine) {
            console.log(`Command Line: ${info.commandLine}`);
        }
        
        if (info.currentDirectory) {
            console.log(`Current Directory: ${info.currentDirectory}`);
        }
        
        if (info.parentProcess) {
            console.log(`Parent Process: 0x${info.parentProcess.toString(16)}`);
        }
        
        if (info.flags !== undefined) {
            console.log(`Flags: 0x${info.flags.toString(16)}`);
        }
        
        if (info.sectionHandle) {
            console.log(`Section Handle: 0x${info.sectionHandle.toString(16)}`);
        }
        
        console.log(`Timestamp: ${info.timestamp}`);
    }
}

// Legacy function for backward compatibility
export function log(message: string): void {
    console.log(message);
}
