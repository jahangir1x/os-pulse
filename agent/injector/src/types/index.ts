/**
 * Type definitions for Windows API structures and common interfaces
 */

export interface FileOperationInfo {
    handle: NativePointer;
    filePath: string | null;
    bytesTransferred: number;
    content?: string;
    timestamp: string;
}

export interface ProcessCreationInfo {
    processHandle?: NativePointer;
    threadHandle?: NativePointer;
    imagePath?: string | null;
    commandLine?: string | null;
    currentDirectory?: string | null;
    parentProcess?: NativePointer;
    flags?: number;
    sectionHandle?: NativePointer;
    status: number;
    timestamp: string;
}

export interface HookConfiguration {
    enableFileOperations: boolean;
    enableProcessCreation: boolean;
    maxContentLength: number;
    logBinaryData: boolean;
}

export interface Logger {
    info(message: string): void;
    error(message: string): void;
    debug(message: string): void;
    logFileOperation(operation: string, info: FileOperationInfo): void;
    logProcessCreation(operation: string, info: ProcessCreationInfo): void;
}
