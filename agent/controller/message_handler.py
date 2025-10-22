"""
Message handlers for processing events from the Frida injector
"""
import json
import threading
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from colorama import Fore, Style, init

from config import config

# Initialize colorama for colored output
init(autoreset=True)


class MessageHandler:
    """Handles and displays messages from the Frida injector"""
    
    def __init__(self, enable_api: bool = None):
        self.session_info = {}
        self.event_count = 0
        self.api_enabled = enable_api if enable_api is not None else config.api_enabled
        self.api_endpoint = config.api_endpoint
        self.api_key = config.api_key
        self.session = requests.Session() if self.api_enabled else None
        
        if self.api_enabled:
            print(f"{Fore.CYAN}[HANDLER] API integration enabled - Endpoint: {config.api_endpoint}")
            # Set up session headers
            if self.session:
                self.session.headers.update({
                    'Content-Type': 'application/json',
                    'User-Agent': 'OS-Pulse-Controller/1.0'
                })
                if self.api_key:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.api_key}',
                        'X-API-Key': self.api_key
                    })
        else:
            print(f"{Fore.YELLOW}[HANDLER] API integration disabled")
    
    def _send_to_api(self, event_type: str, data: Dict[str, Any]):
        """Send event to API immediately using requests (simple approach)"""
        if not self.api_enabled or not self.session:
            return
            
        # Fire and forget - run in background thread
        def send_in_thread():
            try:
                self._send_api_event(event_type, data)
            except Exception as e:
                print(f"{Fore.YELLOW}[API] Send failed: {e}")
        
        # Start background thread for immediate sending
        thread = threading.Thread(target=send_in_thread, daemon=True)
        thread.start()
    
    def _send_api_event(self, event_type: str, data: Dict[str, Any]):
        """Send single event to API immediately using requests"""
        try:
            # Prepare event payload
            payload = {
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'source': 'os-pulse-controller',
                'data': data
            }
            
            # Send POST request
            response = self.session.post(
                f"{self.api_endpoint}/events",
                json=payload,
                timeout=config.api_timeout
            )
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}[API] Sent {event_type} event successfully")
            elif response.status_code == 401:
                print(f"{Fore.RED}[API] Authentication failed (401)")
            elif response.status_code == 429:
                print(f"{Fore.YELLOW}[API] Rate limited (429) - dropping event")
            else:
                print(f"{Fore.YELLOW}[API] Unexpected status {response.status_code} - dropping event")
                
        except requests.exceptions.ConnectionError:
            print(f"{Fore.YELLOW}[API] Connection failed - dropping {event_type} event")
        except requests.exceptions.Timeout:
            print(f"{Fore.YELLOW}[API] Request timeout - dropping {event_type} event")
        except Exception as e:
            print(f"{Fore.YELLOW}[API] Failed to send {event_type}: {e}")
        
    def handle_message(self, message: Dict[str, Any], data: bytes = None) -> None:
        """Process incoming message from Frida injector"""
        try:
            if isinstance(message, dict):
                message_type = message.get('type', 'unknown')
                
                # Route message to appropriate handler
                if message_type == 'session_start':
                    self._handle_session_start(message)
                elif message_type == 'file_operation':
                    self._handle_file_operation(message)
                elif message_type == 'process_creation':
                    self._handle_process_creation(message)
                elif message_type == 'pong':
                    self._handle_pong(message)
                elif message_type == 'status_response':
                    self._handle_status_response(message)
                else:
                    self._handle_unknown_message(message)
            else:
                print(f"{Fore.YELLOW}[WARNING] Received non-dict message: {message}")
                
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to handle message: {e}")
            print(f"{Fore.RED}Message content: {message}")
    
    def _handle_session_start(self, message: Dict[str, Any]) -> None:
        """Handle session initialization message"""
        data = message.get('data', {})
        self.session_info = data
        
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}[SESSION START] Frida Agent Connected")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}Session ID: {data.get('sessionId', 'Unknown')}")
        print(f"{Fore.CYAN}Process: {data.get('processName', 'Unknown')} (PID: {data.get('processId', 'Unknown')})")
        print(f"{Fore.CYAN}Platform: {data.get('platform', 'Unknown')} ({data.get('arch', 'Unknown')})")
        print(f"{Fore.CYAN}Timestamp: {data.get('timestamp', 'Unknown')}")
        print(f"{Fore.GREEN}{'='*60}\n")
        
        # Send to API immediately
        self._send_to_api('session_start', data)
    
    def _handle_file_operation(self, message: Dict[str, Any]) -> None:
        """Handle file operation events"""
        self.event_count += 1
        data = message.get('data', {})
        operation = message.get('operation', 'Unknown')
        metadata = message.get('metadata', {})
        
        print(f"\n{Fore.BLUE}[FILE OPERATION #{self.event_count}] {operation}")
        print(f"{Fore.WHITE}{'─' * 50}")
        print(f"{Fore.YELLOW}Path: {data.get('filePath', 'Unknown')}")
        print(f"{Fore.YELLOW}Bytes: {data.get('bytesTransferred', 0)}")
        
        if data.get('content'):
            content = data['content']
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"{Fore.YELLOW}Content: {repr(content)}")
        
        print(f"{Fore.YELLOW}Time: {data.get('timestamp', 'Unknown')}")
        
        # Show metadata
        print(f"{Fore.MAGENTA}Process: {metadata.get('processName', 'Unknown')} (PID: {metadata.get('processId', 'Unknown')})")
        
        # Send to API immediately
        combined_data = {**data, 'operation': operation, 'metadata': metadata}
        self._send_to_api('file_operation', combined_data)
    
    def _handle_process_creation(self, message: Dict[str, Any]) -> None:
        """Handle process creation events"""
        self.event_count += 1
        data = message.get('data', {})
        operation = message.get('operation', 'Unknown')
        metadata = message.get('metadata', {})
        
        print(f"\n{Fore.RED}[PROCESS CREATION #{self.event_count}] {operation}")
        print(f"{Fore.WHITE}{'─' * 50}")
        
        status = data.get('status', 0)
        status_text = "SUCCESS" if status >= 0 else "FAILED"
        status_color = Fore.GREEN if status >= 0 else Fore.RED
        print(f"{status_color}Status: {status_text} (0x{status:08x})")
        
        if data.get('imagePath'):
            print(f"{Fore.YELLOW}Image: {data['imagePath']}")
        
        if data.get('commandLine'):
            print(f"{Fore.YELLOW}Command: {data['commandLine']}")
        
        if data.get('currentDirectory'):
            print(f"{Fore.YELLOW}Directory: {data['currentDirectory']}")
        
        if data.get('processHandle'):
            print(f"{Fore.YELLOW}Process Handle: {data['processHandle']}")
        
        if data.get('threadHandle'):
            print(f"{Fore.YELLOW}Thread Handle: {data['threadHandle']}")
        
        print(f"{Fore.YELLOW}Time: {data.get('timestamp', 'Unknown')}")
        
        # Show metadata
        print(f"{Fore.MAGENTA}Source Process: {metadata.get('processName', 'Unknown')} (PID: {metadata.get('processId', 'Unknown')})")
        
        # Send to API immediately
        combined_data = {**data, 'operation': operation, 'metadata': metadata}
        self._send_to_api('process_creation', combined_data)
    
    def _handle_pong(self, message: Dict[str, Any]) -> None:
        """Handle pong response"""
        print(f"{Fore.GREEN}[PONG] Agent is alive - {message.get('timestamp', 'Unknown')}")
    
    def _handle_status_response(self, message: Dict[str, Any]) -> None:
        """Handle status response"""
        data = message.get('data', {})
        print(f"\n{Fore.CYAN}[STATUS RESPONSE]")
        print(f"{Fore.CYAN}Session: {data.get('sessionId', 'Unknown')}")
        print(f"{Fore.CYAN}Process: {data.get('processName', 'Unknown')} (PID: {data.get('processId', 'Unknown')})")
        print(f"{Fore.CYAN}Status: {data.get('status', 'Unknown')}")
        print(f"{Fore.CYAN}Time: {data.get('timestamp', 'Unknown')}")
    
    def _handle_unknown_message(self, message: Dict[str, Any]) -> None:
        """Handle unknown message types"""
        message_type = message.get('type', 'unknown')
        print(f"{Fore.YELLOW}[UNKNOWN MESSAGE] Type: {message_type}")
        print(f"{Fore.YELLOW}Content: {json.dumps(message, indent=2)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics"""
        stats = {
            'session_info': self.session_info,
            'event_count': self.event_count,
            'api_enabled': self.api_enabled
        }
        
        # For now, skip API stats to avoid event loop issues
        # In a production environment, we'd want to implement proper async context management
        if self.api_client:
            stats['api_stats'] = {
                'status': 'initialized',
                'note': 'Detailed stats require async context'
            }
        else:
            stats['api_stats'] = {
                'status': 'not_initialized'
            }
        
        return stats
    
    def shutdown(self) -> None:
        """Shutdown message handler and close session"""
        print(f"{Fore.CYAN}[HANDLER] Shutting down...")
        
        # Close HTTP session
        if self.session:
            self.session.close()
            self.session = None
    
    def flush_api_events(self) -> int:
        """No buffering - events are sent immediately"""
        return 0  # No events to flush since we send immediately
