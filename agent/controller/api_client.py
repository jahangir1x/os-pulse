"""
API client for sending monitoring events to external services
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

import aiohttp
import requests
from colorama import Fore

from config import config


class ApiClient:
    """Handles communication with external API endpoints"""
    
    def __init__(self, endpoint: str = None, api_key: str = None, timeout: int = None):
        """
        Initialize API client
        
        Args:
            endpoint: API endpoint URL (defaults to config)
            api_key: API authentication key (defaults to config)  
            timeout: Request timeout in seconds (defaults to config)
        """
        self.endpoint = endpoint or config.api_endpoint
        self.api_key = api_key or config.api_key
        self.timeout = timeout or config.api_timeout
        self.batch_size = config.api_batch_size
        
        # Event batching
        self.event_batch: List[Dict[str, Any]] = []
        self.batch_lock = threading.Lock()
        self.last_flush = time.time()
        self.flush_interval = 10  # seconds
        
        # Statistics
        self.events_sent = 0
        self.events_failed = 0
        self.last_error = None
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.running = True
        
        # Start background flush timer
        self._start_flush_timer()
        
        print(f"{Fore.CYAN}[API] Initialized - Endpoint: {self.endpoint}")
    
    def send_event_sync(self, event_type: str, event_data: Dict[str, Any], 
                       metadata: Dict[str, Any] = None) -> bool:
        """
        Send event synchronously (blocking)
        
        Args:
            event_type: Type of event (file_operation, process_creation, etc.)
            event_data: Event data payload
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not config.api_enabled:
            return True  # Skip if API is disabled
        
        try:
            # Prepare event payload
            payload = self._prepare_event_payload(event_type, event_data, metadata)
            
            # Send immediately via requests (synchronous)
            headers = self._get_headers()
            
            response = requests.post(
                f"{self.endpoint}/events",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201, 202]:
                self.events_sent += 1
                return True
            else:
                self.events_failed += 1
                self.last_error = f"HTTP {response.status_code}: {response.text}"
                print(f"{Fore.RED}[API] Failed to send event: {self.last_error}")
                return False
                
        except Exception as e:
            self.events_failed += 1
            self.last_error = str(e)
            print(f"{Fore.RED}[API] Exception sending event: {e}")
            return False
    
    def send_event_async(self, event_type: str, event_data: Dict[str, Any],
                        metadata: Dict[str, Any] = None) -> None:
        """
        Send event asynchronously (non-blocking via thread pool)
        
        Args:
            event_type: Type of event
            event_data: Event data payload
            metadata: Additional metadata
        """
        if not config.api_enabled:
            return
        
        # Submit to thread pool for async execution
        self.executor.submit(self.send_event_sync, event_type, event_data, metadata)
    
    def add_to_batch(self, event_type: str, event_data: Dict[str, Any],
                    metadata: Dict[str, Any] = None) -> None:
        """
        Add event to batch for bulk sending
        
        Args:
            event_type: Type of event
            event_data: Event data payload
            metadata: Additional metadata
        """
        if not config.api_enabled:
            return
        
        with self.batch_lock:
            payload = self._prepare_event_payload(event_type, event_data, metadata)
            self.event_batch.append(payload)
            
            # Flush if batch is full
            if len(self.event_batch) >= self.batch_size:
                self._flush_batch_async()
    
    def flush_batch(self) -> bool:
        """
        Flush current batch synchronously
        
        Returns:
            True if successful, False otherwise
        """
        if not config.api_enabled:
            return True
        
        with self.batch_lock:
            if not self.event_batch:
                return True
            
            batch_to_send = self.event_batch.copy()
            self.event_batch.clear()
        
        try:
            headers = self._get_headers()
            
            response = requests.post(
                f"{self.endpoint}/events/batch",
                json={"events": batch_to_send},
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201, 202]:
                self.events_sent += len(batch_to_send)
                print(f"{Fore.GREEN}[API] Sent batch of {len(batch_to_send)} events")
                return True
            else:
                self.events_failed += len(batch_to_send)
                self.last_error = f"HTTP {response.status_code}: {response.text}"
                print(f"{Fore.RED}[API] Failed to send batch: {self.last_error}")
                return False
                
        except Exception as e:
            self.events_failed += len(batch_to_send)
            self.last_error = str(e)
            print(f"{Fore.RED}[API] Exception sending batch: {e}")
            
            # Put events back in batch for retry
            with self.batch_lock:
                self.event_batch = batch_to_send + self.event_batch
            
            return False
    
    def _flush_batch_async(self) -> None:
        """Flush batch asynchronously via thread pool"""
        self.executor.submit(self.flush_batch)
    
    def _prepare_event_payload(self, event_type: str, event_data: Dict[str, Any],
                              metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepare event payload for API"""
        return {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": event_data,
            "metadata": metadata or {},
            "source": "os-pulse-controller",
            "version": "1.0.0"
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "OS-Pulse-Controller/1.0.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            # Alternative: headers["X-API-Key"] = self.api_key
        
        return headers
    
    def _start_flush_timer(self) -> None:
        """Start background timer to flush batches periodically"""
        def flush_timer():
            while self.running:
                time.sleep(self.flush_interval)
                if time.time() - self.last_flush > self.flush_interval:
                    if self.event_batch:
                        self._flush_batch_async()
                    self.last_flush = time.time()
        
        timer_thread = threading.Thread(target=flush_timer, daemon=True)
        timer_thread.start()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API client statistics"""
        return {
            "events_sent": self.events_sent,
            "events_failed": self.events_failed,
            "events_pending": len(self.event_batch),
            "last_error": self.last_error,
            "endpoint": self.endpoint,
            "api_enabled": config.api_enabled
        }
    
    def test_connection(self) -> bool:
        """
        Test API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        if not config.api_enabled:
            print(f"{Fore.YELLOW}[API] API is disabled")
            return False
        
        try:
            headers = self._get_headers()
            
            # Send test event
            test_payload = {
                "event_type": "connection_test",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {"test": True},
                "source": "os-pulse-controller"
            }
            
            response = requests.post(
                f"{self.endpoint}/test",
                json=test_payload,
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 201, 202, 404]:  # 404 might be OK if test endpoint doesn't exist
                print(f"{Fore.GREEN}[API] Connection test successful")
                return True
            else:
                print(f"{Fore.RED}[API] Connection test failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[API] Connection test failed: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown API client and flush remaining events"""
        print(f"{Fore.YELLOW}[API] Shutting down...")
        self.running = False
        
        # Flush remaining events
        if self.event_batch:
            print(f"{Fore.CYAN}[API] Flushing {len(self.event_batch)} remaining events...")
            self.flush_batch()
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        # Print final statistics
        stats = self.get_statistics()
        print(f"{Fore.CYAN}[API] Final stats - Sent: {stats['events_sent']}, Failed: {stats['events_failed']}")


# Global API client instance
api_client = None

def get_api_client() -> Optional[ApiClient]:
    """Get or create global API client instance"""
    global api_client
    
    if api_client is None and config.api_enabled:
        api_client = ApiClient()
    
    return api_client

def initialize_api_client(endpoint: str = None, api_key: str = None) -> ApiClient:
    """Initialize API client with custom parameters"""
    global api_client
    api_client = ApiClient(endpoint, api_key)
    return api_client
