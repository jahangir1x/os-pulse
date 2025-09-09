/**
 * Windows System Monitor - Frida Agent
 * 
 * A professional, modular system monitoring agent for Windows that tracks:
 * - File operations (ReadFile, WriteFile)
 * - Process creation (NtCreateUserProcess, NtCreateProcess, NtCreateProcessEx)
 * 
 * @author System Monitor Team
 * @version 1.0.0
 */

import { SystemMonitor } from './core';
import { HookConfiguration } from './types';

// Configuration - customize as needed
const config: Partial<HookConfiguration> = {
    enableFileOperations: true,
    enableProcessCreation: true,
    maxContentLength: 512,      // Maximum content length to log
    logBinaryData: false        // Whether to log binary data as hex
};

// Initialize and start the monitoring system
const monitor = new SystemMonitor(config);

try {
    monitor.start();
} catch (error) {
    console.error(`Failed to start system monitor: ${error}`);
}
