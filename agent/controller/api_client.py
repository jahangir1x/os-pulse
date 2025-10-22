"""
API client for sending monitoring events to external services
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import aiohttp
from colorama import Fore, Style
from config import config


class ApiClient:
    """Asynchronous HTTP client for sending events to external API"""
    
    def __init__(self, endpoint: str, api_key: Optional[str] = None):
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=config.api_timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_connected = False
        
        # Statistics tracking
        self.events_sent = 0
        self.events_failed = 0
        
        print(f"{Fore.GREEN}[API] Client initialized - Endpoint: {self.endpoint}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Initialize HTTP session"""
        if not self.session:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'OS-Pulse-Controller/1.0'
            }
            
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                headers['X-API-Key'] = self.api_key
            
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=headers
            )
            
            # Test connectivity
            await self.test_connection()
    
    async def disconnect(self):
        """Close HTTP session and flush remaining events"""
        try:
            # Flush any remaining events
            await self.flush_events()
            
            if self.session:
                await self.session.close()
                self.session = None
                print(f"{Fore.YELLOW}[API] Client disconnected")
        except Exception as e:
            print(f"{Fore.RED}[API] Error during disconnect: {e}")
    
    async def test_connection(self) -> bool:
        """Test API connectivity"""
        try:
            if not self.session:
                return False
            
            # Try a simple GET to test endpoint
            test_url = f"{self.endpoint}/health" if not self.endpoint.endswith('/') else f"{self.endpoint}health"
            
            async with self.session.get(test_url) as response:
                if response.status in [200, 404]:  # 404 is OK if health endpoint doesn't exist
                    self.is_connected = True
                    print(f"{Fore.GREEN}[API] Connection test successful")
                    return True
                else:
                    print(f"{Fore.YELLOW}[API] Connection test returned status {response.status}")
                    return False
                    
        except aiohttp.ClientConnectorError:
            print(f"{Fore.YELLOW}[API] Connection test failed - endpoint may be unreachable")
            return False
        except Exception as e:
            print(f"{Fore.YELLOW}[API] Connection test failed: {e}")
            return False
    
    async def send_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Send a single event to the API
        
        Args:
            event_type: Type of event ('file_operation', 'process_creation', etc.)
            event_data: Event data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.session:
                await self.connect()
            
            # Prepare event payload
            payload = {
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'source': 'os-pulse-controller',
                'data': event_data
            }
            
            # Send immediately - no buffering or queuing
            return await self._send_payload(payload)
            
        except Exception as e:
            print(f"{Fore.RED}[API] Failed to send event: {e}")
            return False
    
    async def send_file_operation(self, operation: str, data: Dict[str, Any]) -> bool:
        """Send file operation event"""
        event_data = {
            'operation': operation,
            'file_path': data.get('filePath'),
            'bytes_transferred': data.get('bytesTransferred', 0),
            'content_preview': data.get('content', '')[:100] if data.get('content') else None,
            'process_info': data.get('metadata', {}),
            'timestamp': data.get('timestamp')
        }
        
        return await self.send_event('file_operation', event_data)
    
    async def send_process_creation(self, operation: str, data: Dict[str, Any]) -> bool:
        """Send process creation event"""
        event_data = {
            'operation': operation,
            'image_path': data.get('imagePath'),
            'command_line': data.get('commandLine'),
            'current_directory': data.get('currentDirectory'),
            'process_handle': data.get('processHandle'),
            'thread_handle': data.get('threadHandle'),
            'status': data.get('status', 0),
            'process_info': data.get('metadata', {}),
            'timestamp': data.get('timestamp')
        }
        
        return await self.send_event('process_creation', event_data)
    
    async def _send_payload(self, payload: Dict[str, Any]) -> bool:
        """Internal method to send payload immediately"""
        try:
            if not self.session:
                await self.connect()
                
            if not self.is_connected:
                await self.test_connection()
            
            if self.is_connected and self.session:
                async with self.session.post(
                    f"{self.endpoint}/events",
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        self.events_sent += 1
                        print(f"{Fore.GREEN}[API] Event sent successfully")
                        return True
                    elif response.status == 401:
                        self.events_failed += 1
                        print(f"{Fore.RED}[API] Authentication failed (401)")
                        return False
                    elif response.status == 429:
                        self.events_failed += 1
                        print(f"{Fore.YELLOW}[API] Rate limited (429) - dropping event")
                        return False
                    else:
                        self.events_failed += 1
                        print(f"{Fore.YELLOW}[API] Unexpected status {response.status} - dropping event")
                        return False
            else:
                # Drop event if connection is down
                self.events_failed += 1
                print(f"{Fore.YELLOW}[API] Connection down - dropping event")
                return False
                
        except aiohttp.ClientConnectorError:
            self.events_failed += 1
            print(f"{Fore.YELLOW}[API] Connection failed - dropping event")
            return False
        except asyncio.TimeoutError:
            self.events_failed += 1
            print(f"{Fore.YELLOW}[API] Request timeout - dropping event")
            return False
        except Exception as e:
            self.events_failed += 1
            print(f"{Fore.RED}[API] Send error: {e}")
            return False
    
    async def flush_events(self) -> int:
        """
        No-op method for compatibility - no buffering used
        
        Returns:
            Always returns 0 since no events are buffered
        """
        return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get API client statistics"""
        return {
            'endpoint': self.endpoint,
            'connected': self.is_connected,
            'timeout': self.timeout.total,
            'has_auth': bool(self.api_key),
            'events_sent': self.events_sent,
            'events_failed': self.events_failed
        }


class ApiClientManager:
    """Manager for API client lifecycle"""
    
    def __init__(self):
        self.client: Optional[ApiClient] = None
        self._lock = asyncio.Lock()
    
    async def get_client(self) -> Optional[ApiClient]:
        """Get or create API client"""
        async with self._lock:
            if not self.client and config.api_enabled:
                if config.api_endpoint:
                    try:
                        self.client = ApiClient(config.api_endpoint, config.api_key)
                        await self.client.connect()
                        return self.client
                    except Exception as e:
                        print(f"{Fore.RED}[API] Failed to create client: {e}")
                        return None
            return self.client
    
    async def shutdown(self):
        """Shutdown API client"""
        async with self._lock:
            if self.client:
                await self.client.disconnect()
                self.client = None


# Global API client manager
api_manager = ApiClientManager()


async def get_api_client() -> Optional[ApiClient]:
    """Get the global API client instance"""
    return await api_manager.get_client()


async def shutdown_api():
    """Shutdown the global API client"""
    await api_manager.shutdown()
