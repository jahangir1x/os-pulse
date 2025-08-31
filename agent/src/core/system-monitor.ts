import { Logger, HookConfiguration } from '../types';
import { ConsoleLogger } from '../logging';
import { FileOperationsMonitor, ProcessCreationMonitor } from '../monitors';

/**
 * Main orchestrator for the Windows system monitoring agent
 */
export class SystemMonitor {
    private logger: Logger;
    private config: HookConfiguration;
    private fileMonitor: FileOperationsMonitor;
    private processMonitor: ProcessCreationMonitor;

    constructor(config?: Partial<HookConfiguration>, logger?: Logger) {
        // Default configuration
        this.config = {
            enableFileOperations: true,
            enableProcessCreation: true,
            maxContentLength: 256,
            logBinaryData: false,
            ...config
        };

        this.logger = logger || new ConsoleLogger();
        this.fileMonitor = new FileOperationsMonitor(this.logger, this.config);
        this.processMonitor = new ProcessCreationMonitor(this.logger, this.config);
    }

    /**
     * Start monitoring system calls
     */
    start(): void {
        this.logger.info("Starting Windows System Monitor");
        this.logger.info(`Configuration: ${JSON.stringify(this.config, null, 2)}`);

        try {
            this.fileMonitor.initialize();
            this.processMonitor.initialize();
            
            this.logger.info("System monitoring initialized successfully");
        } catch (error) {
            this.logger.error(`Failed to initialize monitoring: ${error}`);
            throw error;
        }
    }

    /**
     * Update configuration at runtime
     */
    updateConfig(newConfig: Partial<HookConfiguration>): void {
        this.config = { ...this.config, ...newConfig };
        this.logger.info(`Configuration updated: ${JSON.stringify(this.config, null, 2)}`);
    }

    /**
     * Get current configuration
     */
    getConfig(): HookConfiguration {
        return { ...this.config };
    }
}
