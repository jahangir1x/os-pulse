"""
Message handlers for processing events from the Frida injector
"""
import asyncio
import json
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
        self.api_client = None  # Will be initialized asynchronously
        
        if self.api_enabled:
            print(f"{Fore.CYAN}[HANDLER] API integration enabled - Endpoint: {config.api_endpoint}")
            # Initialize API client asynchronously
            asyncio.create_task(self._init_api_client())
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
    
    def _send_to_api_async(self, event_type: str, data: Dict[str, Any]):
        """Send event to API asynchronously (non-blocking)"""
        if self.api_client:
            try:
                if event_type == 'file_operation':
                    asyncio.create_task(self.api_client.send_file_operation(
                        data.get('operation', 'unknown'),
                        data
                    ))
                elif event_type == 'process_creation':
                    asyncio.create_task(self.api_client.send_process_creation(
                        data.get('operation', 'unknown'),
                        data
                    ))
                else:
                    asyncio.create_task(self.api_client.send_event(event_type, data))
            except Exception as e:
                print(f"{Fore.RED}[API] Error sending {event_type}: {e}")
        
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
        
        # Send to API
        self._send_to_api_async('session_start', data)
    
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
        
        # Send to API
        combined_data = {**data, 'operation': operation, 'metadata': metadata}
        self._send_to_api_async('file_operation', combined_data)
    
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
        
        # Send to API
        combined_data = {**data, 'operation': operation, 'metadata': metadata}
        self._send_to_api_async('process_creation', combined_data)
    
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
        
        if self.api_client:
            try:
                # Use asyncio to run the async method
                import asyncio
                loop = asyncio.get_event_loop()
                api_stats = loop.run_until_complete(self.api_client.get_stats())
                stats['api_stats'] = api_stats
            except Exception as e:
                stats['api_stats'] = {'error': str(e)}
        
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
        if self.api_client:
            print(f"{Fore.CYAN}[HANDLER] Shutting down API client...")
            await self.api_client.disconnect()
    
    async def flush_api_events(self) -> int:
        """Flush any pending API events"""
        if self.api_client:
            return await self.api_client.flush_events()
        return 0
    
    async def test_api_connection(self) -> bool:
        """Test API connection"""
        if self.api_client:
            try:
                return await self.api_client.test_connection()
            except Exception:
                return False
        return False
