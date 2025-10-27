/**
 * Windows API utility functions for reading system structures
 */

/**
 * Gets the file path for a given file handle using GetFinalPathNameByHandleW
 */
export function getFilePath(handle: NativePointer): string | null {
    try {
        const kernel32 = Process.getModuleByName("kernel32.dll").findExportByName("GetFinalPathNameByHandleW");
        if (!kernel32) {
            return null;
        }

        const GetFinalPathNameByHandleW = new NativeFunction(kernel32, "uint32", ["pointer", "pointer", "uint32", "uint32"]);

        const bufferSize = 1024;
        const buffer = Memory.alloc(bufferSize * 2); // WCHAR (2 bytes per char)

        const len = GetFinalPathNameByHandleW(handle, buffer, bufferSize, 0);
        if (len > 0) {
            return buffer.readUtf16String();
        }
        return null;
    } catch (error) {
        return null;
    }
}

/**
 * Reads a Windows UNICODE_STRING structure
 */
export function readUnicodeString(ptr: NativePointer): string | null {
    if (ptr.isNull()) return null;
    
    try {
        const length = ptr.readU16();        // Length (bytes)
        const maxLength = ptr.add(2).readU16(); // MaximumLength (bytes)
        const bufferPtr = ptr.add(8).readPointer(); // Buffer pointer (on x64, offset is 8)
        
        if (bufferPtr.isNull() || length === 0) return null;
        
        return bufferPtr.readUtf16String(length / 2); // Convert bytes to chars
    } catch (error) {
        return null;
    }
}

/**
 * Reads RTL_USER_PROCESS_PARAMETERS structure
 */
export function readProcessParameters(ptr: NativePointer): {
    imagePath: string | null;
    commandLine: string | null;
    currentDirectory: string | null;
} {
    if (ptr.isNull()) {
        return {
            imagePath: null,
            commandLine: null,
            currentDirectory: null
        };
    }
    
    try {
        // RTL_USER_PROCESS_PARAMETERS structure offsets (x64)
        const imagePathName = ptr.add(0x60);      // UNICODE_STRING ImagePathName
        const commandLine = ptr.add(0x70);        // UNICODE_STRING CommandLine
        const currentDirectory = ptr.add(0x38);   // UNICODE_STRING CurrentDirectory.DosPath
        
        return {
            imagePath: readUnicodeString(imagePathName),
            commandLine: readUnicodeString(commandLine),
            currentDirectory: readUnicodeString(currentDirectory)
        };
    } catch (error) {
        return {
            imagePath: null,
            commandLine: null,
            currentDirectory: null
        };
    }
}

/**
 * Converts byte array to space-separated hex format like 'AB CD 01 29'
 */
export function bytesToHex(buffer: NativePointer, size: number): string {
    try {
        const byteArray = buffer.readByteArray(size);
        if (!byteArray) {
            return "<no data>";
        }
        
        // Convert byte array to hex string with spaces
        const bytes = new Uint8Array(byteArray);
        const hexPairs: string[] = [];
        
        for (let i = 0; i < bytes.length; i++) {
            hexPairs.push(bytes[i].toString(16).padStart(2, '0').toUpperCase());
        }
        
        return hexPairs.join(' ');
    } catch (error) {
        return "<error reading data>";
    }
}

/**
 * Safely reads buffer content as string or hex dump
 */
export function readBufferContent(buffer: NativePointer, size: number, maxSize: number = 64): {
    content: string;
    isBinary: boolean;
} {
    try {
        const content = buffer.readUtf8String(size);
        return { content: content || "<empty>", isBinary: false };
    } catch (error) {
        try {
            const hexData = buffer.readByteArray(Math.min(size, maxSize));
            if (hexData) {
                const content = hexdump(hexData, { ansi: false, header: false });
                return { content, isBinary: true };
            } else {
                return { content: "<no data>", isBinary: true };
            }
        } catch (error2) {
            return { content: "<unable to read data>", isBinary: true };
        }
    }
}

/**
 * Checks if an NT status code indicates success
 */
export function isNtSuccess(status: number): boolean {
    return status >= 0;
}

/**
 * Formats NT status code as hex string
 */
export function formatNtStatus(status: number): string {
    return "0x" + status.toString(16).padStart(8, '0');
}
