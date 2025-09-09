#!/usr/bin/env python3
"""
Test script for API integration functionality
Tests the API client and message handler integration without requiring Frida
"""

import sys
import json
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama for Windows
init(autoreset=True)

# Add controller directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api_client import APIClient, initialize_api_client
from message_handler import MessageHandler
from config import Config


def test_api_client():
    """Test API client functionality"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}TESTING API CLIENT")
    print(f"{Fore.CYAN}{'=' * 60}")
    
    # Initialize with test endpoint
    config = Config()
    test_endpoint = "https://httpbin.org/post"  # Test endpoint that echoes data
    
    print(f"{Fore.YELLOW}Testing with endpoint: {test_endpoint}")
    
    # Test initialization
    client = initialize_api_client(test_endpoint, "test-key")
    if not client:
        print(f"{Fore.RED}❌ Failed to initialize API client")
        return False
    
    print(f"{Fore.GREEN}✅ API client initialized")
    
    # Test connection
    print(f"{Fore.YELLOW}Testing connection...")
    if client.test_connection():
        print(f"{Fore.GREEN}✅ Connection test passed")
    else:
        print(f"{Fore.RED}❌ Connection test failed")
        return False
    
    # Test adding events to batch
    print(f"{Fore.YELLOW}Testing event batching...")
    
    # Add file operation event
    file_event = {
        "operation": "WriteFile",
        "file_path": "C:\\test\\document.txt",
        "bytes_transferred": 256,
        "content": "Test file content",
        "timestamp": "2024-01-15T12:00:00.000Z",
        "process_info": {
            "name": "notepad.exe",
            "pid": 1234,
            "session_id": "test-session"
        }
    }
    
    client.add_to_batch(
        event_type="file_operation",
        event_data=file_event,
        metadata={
            "operation": "WriteFile",
            "source": "os-pulse-test",
            "handler": "file_operation"
        }
    )
    
    # Add process creation event
    process_event = {
        "operation": "NtCreateUserProcess",
        "status": 0,
        "image_path": "C:\\Windows\\System32\\calc.exe",
        "command_line": "calc.exe",
        "timestamp": "2024-01-15T12:01:00.000Z",
        "process_info": {
            "name": "explorer.exe",
            "pid": 5678,
            "session_id": "test-session"
        }
    }
    
    client.add_to_batch(
        event_type="process_creation", 
        event_data=process_event,
        metadata={
            "operation": "NtCreateUserProcess",
            "source": "os-pulse-test",
            "handler": "process_creation"
        }
    )
    
    print(f"{Fore.GREEN}✅ Added 2 events to batch")
    
    # Test statistics
    stats = client.get_statistics()
    print(f"\n{Fore.CYAN}Current Statistics:")
    print(f"{Fore.CYAN}  Events Sent: {stats['events_sent']}")
    print(f"{Fore.CYAN}  Events Failed: {stats['events_failed']}")
    print(f"{Fore.CYAN}  Events Pending: {stats['events_pending']}")
    print(f"{Fore.CYAN}  Endpoint: {stats['endpoint']}")
    
    # Test batch flush
    print(f"\n{Fore.YELLOW}Testing batch flush...")
    if client.flush_batch():
        print(f"{Fore.GREEN}✅ Batch flush successful")
    else:
        print(f"{Fore.RED}❌ Batch flush failed")
    
    # Final statistics
    stats = client.get_statistics()
    print(f"\n{Fore.CYAN}Final Statistics:")
    print(f"{Fore.CYAN}  Events Sent: {stats['events_sent']}")
    print(f"{Fore.CYAN}  Events Failed: {stats['events_failed']}")
    print(f"{Fore.CYAN}  Events Pending: {stats['events_pending']}")
    
    if stats['last_error']:
        print(f"{Fore.RED}  Last Error: {stats['last_error']}")
    
    client.shutdown()
    return True


def test_message_handler():
    """Test message handler with API integration"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}TESTING MESSAGE HANDLER")
    print(f"{Fore.CYAN}{'=' * 60}")
    
    # Initialize message handler
    handler = MessageHandler()
    
    # Test API connection status
    print(f"{Fore.YELLOW}Testing API connection status...")
    if handler.test_api_connection():
        print(f"{Fore.GREEN}✅ API connection available")
    else:
        print(f"{Fore.YELLOW}ℹ️  API not configured (expected for test)")
    
    # Test statistics
    stats = handler.get_statistics()
    print(f"\n{Fore.CYAN}Handler Statistics:")
    print(f"{Fore.CYAN}  Events Processed: {stats['events_processed']}")
    print(f"{Fore.CYAN}  API Enabled: {stats['api_enabled']}")
    
    # Test with simulated file operation message
    print(f"\n{Fore.YELLOW}Testing with simulated file operation...")
    
    file_message = {
        'type': 'file_operation',
        'operation': 'ReadFile',
        'data': {
            'filePath': 'C:\\Users\\test\\document.txt',
            'bytesTransferred': 1024,
            'content': 'This is test file content for API testing',
            'timestamp': '2024-01-15T12:00:00.000Z'
        },
        'metadata': {
            'processName': 'notepad.exe',
            'processId': 1234,
            'sessionId': 'test-session-123'
        }
    }
    
    handler.handle_message(file_message)
    
    # Test with simulated process creation message
    print(f"\n{Fore.YELLOW}Testing with simulated process creation...")
    
    process_message = {
        'type': 'process_creation',
        'operation': 'NtCreateUserProcess',
        'data': {
            'status': 0,
            'imagePath': 'C:\\Windows\\System32\\notepad.exe',
            'commandLine': 'notepad.exe C:\\test.txt',
            'currentDirectory': 'C:\\Users\\test',
            'processHandle': '0x12345678',
            'timestamp': '2024-01-15T12:01:00.000Z'
        },
        'metadata': {
            'processName': 'explorer.exe',
            'processId': 5678,
            'sessionId': 'test-session-123'
        }
    }
    
    handler.handle_message(process_message)
    
    # Final statistics
    stats = handler.get_statistics()
    print(f"\n{Fore.CYAN}Final Handler Statistics:")
    print(f"{Fore.CYAN}  Events Processed: {stats['events_processed']}")
    print(f"{Fore.CYAN}  API Enabled: {stats['api_enabled']}")
    
    handler.shutdown()
    return True


def main():
    """Main test function"""
    print(f"{Fore.GREEN}{'=' * 60}")
    print(f"{Fore.GREEN}OS-PULSE API INTEGRATION TEST")
    print(f"{Fore.GREEN}{'=' * 60}")
    
    success_count = 0
    total_tests = 2
    
    try:
        # Test API client
        if test_api_client():
            success_count += 1
        
        # Test message handler
        if test_message_handler():
            success_count += 1
        
    except Exception as e:
        print(f"{Fore.RED}❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}TEST SUMMARY")
    print(f"{Fore.CYAN}{'=' * 60}")
    
    if success_count == total_tests:
        print(f"{Fore.GREEN}✅ All tests passed ({success_count}/{total_tests})")
        print(f"{Fore.GREEN}🎉 API integration is working correctly!")
    else:
        print(f"{Fore.RED}❌ Some tests failed ({success_count}/{total_tests})")
        print(f"{Fore.YELLOW}💡 Check network connectivity and API configuration")
    
    print(f"\n{Fore.CYAN}Next steps:")
    print(f"{Fore.CYAN}1. Configure OSPULSE_API_ENDPOINT in environment")
    print(f"{Fore.CYAN}2. Test with real Frida monitoring")
    print(f"{Fore.CYAN}3. Use interactive commands: api-test, api-stats, api-flush")


if __name__ == "__main__":
    main()
