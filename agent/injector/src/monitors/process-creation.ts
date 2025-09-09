import { Logger, ProcessCreationInfo, HookConfiguration } from '../types';
import { readProcessParameters, isNtSuccess } from '../utils/windows-api';
import { EventSender } from '../messaging';

/**
 * Monitors process creation using NT APIs
 */
export class ProcessCreationMonitor {
    private logger: Logger;
    private config: HookConfiguration;
    private eventSender: EventSender;

    constructor(logger: Logger, config: HookConfiguration, eventSender: EventSender) {
        this.logger = logger;
        this.config = config;
        this.eventSender = eventSender;
    }

    /**
     * Initialize process creation monitoring hooks
     */
    initialize(): void {
        if (!this.config.enableProcessCreation) {
            this.logger.debug("Process creation monitoring disabled");
            return;
        }

        this.hookNtCreateUserProcess();
        this.hookNtCreateProcess();
        this.hookNtCreateProcessEx();
    }

    private hookNtCreateUserProcess(): void {
        const NtCreateUserProcess = Process.getModuleByName("ntdll.dll").findExportByName("NtCreateUserProcess");
        
        if (!NtCreateUserProcess) {
            this.logger.error("NtCreateUserProcess export not found!");
            return;
        }

        const monitor = this;
        Interceptor.attach(NtCreateUserProcess, {
            onEnter: function (args) {
                // NtCreateUserProcess parameters:
                // NTSTATUS NtCreateUserProcess(
                //   [out] PHANDLE ProcessHandle,
                //   [out] PHANDLE ThreadHandle,
                //   [in]  ACCESS_MASK ProcessDesiredAccess,
                //   [in]  ACCESS_MASK ThreadDesiredAccess,
                //   [in]  POBJECT_ATTRIBUTES ProcessObjectAttributes,
                //   [in]  POBJECT_ATTRIBUTES ThreadObjectAttributes,
                //   [in]  ULONG ProcessFlags,
                //   [in]  ULONG ThreadFlags,
                //   [in]  PRTL_USER_PROCESS_PARAMETERS ProcessParameters,
                //   [in]  PPS_CREATE_INFO CreateInfo,
                //   [in]  PPS_ATTRIBUTE_LIST AttributeList
                // );
                
                this.processHandle = args[0];
                this.threadHandle = args[1];
                this.processParameters = args[8];
                
                // Try to read process parameters
                if (!this.processParameters.isNull()) {
                    const params = readProcessParameters(this.processParameters);
                    this.imagePath = params.imagePath;
                    this.commandLine = params.commandLine;
                    this.currentDirectory = params.currentDirectory;
                }
            },
            onLeave: function (retval) {
                monitor.handleNtCreateUserProcessResult(this, retval);
            }
        });

        this.logger.info("Hooked NtCreateUserProcess");
    }

    private handleNtCreateUserProcessResult(interceptorContext: any, retval: InvocationReturnValue): void {
        try {
            const status = retval.toInt32();
            
            let processHandle: NativePointer | undefined;
            let threadHandle: NativePointer | undefined;
            
            if (isNtSuccess(status)) {
                try {
                    if (!interceptorContext.processHandle.isNull()) {
                        processHandle = interceptorContext.processHandle.readPointer();
                    }
                    if (!interceptorContext.threadHandle.isNull()) {
                        threadHandle = interceptorContext.threadHandle.readPointer();
                    }
                } catch (error) {
                    this.logger.error(`Error reading handles: ${error}`);
                }
            }

            const info: ProcessCreationInfo = {
                processHandle,
                threadHandle,
                imagePath: interceptorContext.imagePath,
                commandLine: interceptorContext.commandLine,
                currentDirectory: interceptorContext.currentDirectory,
                status,
                timestamp: new Date().toISOString()
            };

            this.logger.logProcessCreation("NtCreateUserProcess", info);
            
            // Send event to host via Frida messaging
            this.eventSender.sendProcessCreation("NtCreateUserProcess", info);
        } catch (error) {
            this.logger.error(`Error processing NtCreateUserProcess: ${error}`);
        }
    }

    private hookNtCreateProcess(): void {
        const NtCreateProcess = Process.getModuleByName("ntdll.dll").findExportByName("NtCreateProcess");
        
        if (!NtCreateProcess) {
            this.logger.error("NtCreateProcess export not found!");
            return;
        }

        const monitor = this;
        Interceptor.attach(NtCreateProcess, {
            onEnter: function (args) {
                // NtCreateProcess parameters:
                // NTSTATUS NtCreateProcess(
                //   [out] PHANDLE ProcessHandle,
                //   [in]  ACCESS_MASK DesiredAccess,
                //   [in]  POBJECT_ATTRIBUTES ObjectAttributes,
                //   [in]  HANDLE ParentProcess,
                //   [in]  BOOLEAN InheritObjectTable,
                //   [in]  HANDLE SectionHandle,
                //   [in]  HANDLE DebugPort,
                //   [in]  HANDLE ExceptionPort
                // );
                
                this.processHandle = args[0];
                this.parentProcess = args[3];
                this.sectionHandle = args[5];
            },
            onLeave: function (retval) {
                monitor.handleNtCreateProcessResult(this, retval);
            }
        });

        this.logger.info("Hooked NtCreateProcess");
    }

    private handleNtCreateProcessResult(interceptorContext: any, retval: InvocationReturnValue): void {
        try {
            const status = retval.toInt32();
            
            let processHandle: NativePointer | undefined;
            
            if (isNtSuccess(status)) {
                try {
                    if (!interceptorContext.processHandle.isNull()) {
                        processHandle = interceptorContext.processHandle.readPointer();
                    }
                } catch (error) {
                    this.logger.error(`Error reading process handle: ${error}`);
                }
            }

            const info: ProcessCreationInfo = {
                processHandle,
                parentProcess: interceptorContext.parentProcess,
                sectionHandle: interceptorContext.sectionHandle,
                status,
                timestamp: new Date().toISOString()
            };

            this.logger.logProcessCreation("NtCreateProcess", info);
            
            // Send event to host via Frida messaging
            this.eventSender.sendProcessCreation("NtCreateProcess", info);
        } catch (error) {
            this.logger.error(`Error processing NtCreateProcess: ${error}`);
        }
    }

    private hookNtCreateProcessEx(): void {
        const NtCreateProcessEx = Process.getModuleByName("ntdll.dll").findExportByName("NtCreateProcessEx");
        
        if (!NtCreateProcessEx) {
            this.logger.error("NtCreateProcessEx export not found!");
            return;
        }

        const monitor = this;
        Interceptor.attach(NtCreateProcessEx, {
            onEnter: function (args) {
                // NtCreateProcessEx parameters:
                // NTSTATUS NtCreateProcessEx(
                //   [out] PHANDLE ProcessHandle,
                //   [in]  ACCESS_MASK DesiredAccess,
                //   [in]  POBJECT_ATTRIBUTES ObjectAttributes,
                //   [in]  HANDLE ParentProcess,
                //   [in]  ULONG Flags,
                //   [in]  HANDLE SectionHandle,
                //   [in]  HANDLE DebugPort,
                //   [in]  HANDLE ExceptionPort,
                //   [in]  ULONG JobMemberLevel
                // );
                
                this.processHandle = args[0];
                this.parentProcess = args[3];
                this.flags = args[4].toInt32();
                this.sectionHandle = args[5];
            },
            onLeave: function (retval) {
                monitor.handleNtCreateProcessExResult(this, retval);
            }
        });

        this.logger.info("Hooked NtCreateProcessEx");
    }

    private handleNtCreateProcessExResult(interceptorContext: any, retval: InvocationReturnValue): void {
        try {
            const status = retval.toInt32();
            
            let processHandle: NativePointer | undefined;
            
            if (isNtSuccess(status)) {
                try {
                    if (!interceptorContext.processHandle.isNull()) {
                        processHandle = interceptorContext.processHandle.readPointer();
                    }
                } catch (error) {
                    this.logger.error(`Error reading process handle: ${error}`);
                }
            }

            const info: ProcessCreationInfo = {
                processHandle,
                parentProcess: interceptorContext.parentProcess,
                flags: interceptorContext.flags,
                sectionHandle: interceptorContext.sectionHandle,
                status,
                timestamp: new Date().toISOString()
            };

            this.logger.logProcessCreation("NtCreateProcessEx", info);
            
            // Send event to host via Frida messaging
            this.eventSender.sendProcessCreation("NtCreateProcessEx", info);
        } catch (error) {
            this.logger.error(`Error processing NtCreateProcessEx: ${error}`);
        }
    }
}
