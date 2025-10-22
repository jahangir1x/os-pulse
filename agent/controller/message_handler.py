"""
Message handlers for processing events from the Frida injector
"""
import asyncio
import json
import threading
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
        self.api_client = None  # Will be initialized on first use
        self._api_init_attempted = False
        
        if self.api_enabled:
            print(f"{Fore.CYAN}[HANDLER] API integration enabled - Endpoint: {config.api_endpoint}")
        else:
            print(f"{Fore.YELLOW}[HANDLER] API integration disabled")
    
    async def _init_api_client(self):
        """Initialize API client asynchronously"""
        try:
            from api_client import get_api_client
            self.api_client = await get_api_client()
            if self.api_client:
                print(f"{Fore.GREEN}[HANDLER] API client initialized successfully")
            else:
                print(f"{Fore.YELLOW}[HANDLER] API client initialization failed")
        except Exception as e:
            print(f"{Fore.RED}[HANDLER] Error initializing API client: {e}")
    
    def _send_to_api(self, event_type: str, data: Dict[str, Any]):
        """Send event to API immediately (simple approach)"""
        if not self.api_enabled:
            return
            
        # Fire and forget - run in background thread
        def send_in_thread():
            try:
                asyncio.run(self._send_api_event(event_type, data))
            except Exception as e:
                print(f"{Fore.YELLOW}[API] Send failed: {e}")
        
        # Start background thread for immediate sending
        thread = threading.Thread(target=send_in_thread, daemon=True)
        thread.start()
    
    async def _send_api_event(self, event_type: str, data: Dict[str, Any]):
        """Send single event to API immediately"""
        try:
            # Initialize API client if needed
            if self.api_client is None and not self._api_init_attempted:
                self._api_init_attempted = True
                await self._init_api_client()
            
            if self.api_client:
                if event_type == 'session_start':
                    await self.api_client.send_event(event_type, data)
                elif event_type == 'file_operation':
                    await self.api_client.send_file_operation(
                        data.get('operation', 'unknown'),
                        data
                    )
                elif event_type == 'process_creation':
                    await self.api_client.send_process_creation(
                        data.get('operation', 'unknown'),
                        data
                    )
                else:
                    await self.api_client.send_event(event_type, data)
                    
                print(f"{Fore.GREEN}[API] Sent {event_type} event")
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
    
    async def enable_api(self, endpoint: str = None, api_key: str = None) -> None:
        """Enable API integration"""
        self.api_enabled = True
        await self._init_api_client()
        print(f"{Fore.GREEN}[HANDLER] API integration enabled")
    
    async def disable_api(self) -> None:
        """Disable API integration"""
        if self.api_client:
            await self.api_client.disconnect()
        
        self.api_enabled = False
        self.api_client = None
        print(f"{Fore.YELLOW}[HANDLER] API integration disabled")
    
    async def shutdown(self) -> None:
        """Shutdown message handler and API client"""
        print(f"{Fore.CYAN}[HANDLER] Shutting down...")
        
        # Shutdown API client
        if self.api_client:
            print(f"{Fore.CYAN}[HANDLER] Shutting down API client...")
            await self.api_client.disconnect()
    
    async def flush_api_events(self) -> int:
        """No buffering - events are sent immediately"""
        return 0  # No events to flush since we send immediately
    
    async def test_api_connection(self) -> bool:
        """Test API connection"""
        if self.api_client:
            try:
                return await self.api_client.test_connection()
            except Exception:
                return False
        return False
