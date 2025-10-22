"""
Frida controller for managing process injection and message handling
"""
import os
import sys
import time
import signal
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any

import frida
import psutil
from colorama import Fore, Style, init

from message_handler import MessageHandler

# Initialize colorama
init(autoreset=True)


class FridaController:
    """Controls Frida injection and manages agent communication"""
    
    def __init__(self, agent_script_path: Optional[str] = None):
        """
        Initialize the Frida controller
        
        Args:
            agent_script_path: Path to the compiled agent script (_agent.js)
        """
        self.agent_script_path = agent_script_path or self._find_agent_script()
        self.session: Optional[frida.Session] = None
        self.script: Optional[frida.Script] = None
        self.message_handler = MessageHandler()
        self.running = False
        
        # Load agent script
        self.agent_code = self._load_agent_script()
        
        print(f"{Fore.GREEN}[CONTROLLER] Initialized with agent script: {self.agent_script_path}")
    
    def _find_agent_script(self) -> str:
        """Find the compiled agent script"""
        # Look for _agent.js in the injector folder
        script_path = Path(__file__).parent.parent / "injector" / "_agent.js"
        
        if not script_path.exists():
            raise FileNotFoundError(f"Agent script not found at {script_path}")
        
        return str(script_path)
    
    def _load_agent_script(self) -> str:
        """Load the agent script content"""
        try:
            with open(self.agent_script_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to load agent script: {e}")
    
    def list_processes(self, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List running processes"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_info = proc.info
                    if filter_name is None or filter_name.lower() in proc_info['name'].lower():
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'exe': proc_info['exe'],
                            'cmdline': ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to list processes: {e}")
        
        return processes
    
    def spawn_process(self, executable: str, args: Optional[List[str]] = None) -> bool:
        """
        Spawn a new process with Frida injection
        
        Args:
            executable: Path to executable
            args: Optional command line arguments
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"{Fore.YELLOW}[SPAWN] Starting process: {executable}")
            
            # Build command line
            cmdline = [executable]
            if args:
                cmdline.extend(args)
            
            # Spawn process with Frida
            pid = frida.spawn(cmdline)
            print(f"{Fore.GREEN}[SPAWN] Process spawned with PID: {pid}")
            
            # Attach to the spawned process
            self.session = frida.attach(pid)
            print(f"{Fore.GREEN}[ATTACH] Attached to PID: {pid}")
            
            # Create and load script
            self._create_and_load_script()
            
            # Resume the process
            frida.resume(pid)
            print(f"{Fore.GREEN}[RESUME] Process resumed")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to spawn process: {e}")
            return False
    
    def attach_to_process(self, process_name: Optional[str] = None, pid: Optional[int] = None) -> bool:
        """
        Attach to an existing process
        
        Args:
            process_name: Name of the process to attach to
            pid: PID of the process to attach to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if pid:
                print(f"{Fore.YELLOW}[ATTACH] Attaching to PID: {pid}")
                self.session = frida.attach(pid)
            elif process_name:
                print(f"{Fore.YELLOW}[ATTACH] Attaching to process: {process_name}")
                self.session = frida.attach(process_name)
            else:
                print(f"{Fore.RED}[ERROR] Must specify either process_name or pid")
                return False
            
            print(f"{Fore.GREEN}[ATTACH] Successfully attached")
            
            # Create and load script
            self._create_and_load_script()
            
            return True
            
        except frida.ProcessNotFoundError:
            print(f"{Fore.RED}[ERROR] Process not found: {process_name or pid}")
            return False
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to attach to process: {e}")
            return False
    
    def _create_and_load_script(self) -> None:
        """Create and load the agent script"""
        try:
            # Create script
            self.script = self.session.create_script(self.agent_code)
            
            # Set up message handler
            self.script.on('message', self._on_message)
            
            # Load script
            self.script.load()
            print(f"{Fore.GREEN}[SCRIPT] Agent script loaded successfully")
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to load script: {e}")
            raise
    
    def _on_message(self, message: Dict[str, Any], data: bytes = None) -> None:
        """Handle messages from the Frida script"""
        try:
            if message['type'] == 'send':
                # Handle messages sent from the agent via send()
                payload = message['payload']
                self.message_handler.handle_message(payload, data)
            elif message['type'] == 'error':
                print(f"{Fore.RED}[SCRIPT ERROR] {message['description']}")
                if 'stack' in message:
                    print(f"{Fore.RED}Stack trace: {message['stack']}")
            else:
                print(f"{Fore.YELLOW}[MESSAGE] Type: {message['type']}, Content: {message}")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to process message: {e}")
    
    def start_monitoring(self) -> None:
        """Start the monitoring loop"""
        self.running = True
        print(f"\n{Fore.GREEN}[MONITOR] Starting monitoring...")
        print(f"{Fore.GREEN}Press Ctrl+C to stop monitoring\n")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[MONITOR] Stopping monitoring...")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop monitoring and cleanup"""
        self.running = False
        
        try:
            if self.script:
                self.script.unload()
                print(f"{Fore.YELLOW}[SCRIPT] Agent script unloaded")
            
            if self.session:
                self.session.detach()
                print(f"{Fore.YELLOW}[SESSION] Detached from process")
                
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Error during cleanup: {e}")
        
        # Shutdown message handler
        try:
            self.message_handler.shutdown()
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Error shutting down message handler: {e}")
        
        # Print statistics
        stats = self.message_handler.get_statistics()
        print(f"\n{Fore.CYAN}[STATISTICS]")
        print(f"{Fore.CYAN}Events processed: {stats['event_count']}")
        if stats['session_info']:
            print(f"{Fore.CYAN}Session: {stats['session_info'].get('sessionId', 'Unknown')}")
        
        if stats.get('api_stats'):
            api_stats = stats['api_stats']
            print(f"{Fore.CYAN}API Events - Sent: {api_stats['events_sent']}, Failed: {api_stats['events_failed']}")
            if api_stats['events_pending'] > 0:
                print(f"{Fore.YELLOW}API Events - Pending: {api_stats['events_pending']}")


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print(f"\n{Fore.YELLOW}[SIGNAL] Received signal {signum}, shutting down...")
    sys.exit(0)


# Set up signal handler
signal.signal(signal.SIGINT, signal_handler)
