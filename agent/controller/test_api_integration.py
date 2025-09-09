#!/usr/bin/env python3
"""
Test script for API integration functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import ApiClient
from message_handler import MessageHandler
import config

async def test_api_client():
    """Test basic API client functionality"""
    print("Testing API Client...")
    
    # Test with mock endpoint
    client = ApiClient("http://httpbin.org/post", "test-key")
    
    # Test event sending
    test_event = {
        'type': 'file_operation',
        'operation': 'WriteFile',
        'data': {
            'filePath': 'C:\\test\\file.txt',
            'content': 'Hello, World!',
            'bytesTransferred': 13
        },
        'metadata': {
            'processName': 'test.exe',
            'processId': 1234,
            'timestamp': '2025-01-09T12:00:00.000Z'
        }
    }
    
    try:
        # Test basic event sending
        success = await client.send_event(test_event)
        print(f"✓ Basic event sending: {'SUCCESS' if success else 'FAILED'}")
        
        # Test file operation sending
        success = await client.send_file_operation(
            operation='ReadFile',
            file_path='C:\\test\\read.txt',
            content='Read content',
            bytes_transferred=12,
            process_name='reader.exe',
            process_id=5678
        )
        print(f"✓ File operation sending: {'SUCCESS' if success else 'FAILED'}")
        
        # Test process creation sending
        success = await client.send_process_creation(
            operation='NtCreateUserProcess',
            command_line='notepad.exe test.txt',
            process_name='notepad.exe',
            process_id=9999,
            parent_process_id=1111
        )
        print(f"✓ Process creation sending: {'SUCCESS' if success else 'FAILED'}")
        
        # Test stats
        stats = await client.get_stats()
        print(f"✓ API Stats: {stats}")
        
        # Test flush
        flushed = await client.flush_events()
        print(f"✓ Flushed events: {flushed}")
        
    except Exception as e:
        print(f"✗ API Client test failed: {e}")
    finally:
        await client.disconnect()

async def test_message_handler():
    """Test message handler with API integration"""
    print("\nTesting Message Handler with API...")
    
    # Temporarily enable API for testing
    original_enabled = config.api_enabled
    original_endpoint = config.api_endpoint
    
    config.api_enabled = True
    config.api_endpoint = "http://httpbin.org/post"
    config.api_key = "test-key"
    
    handler = MessageHandler()
    
    try:
        # Test file operation message
        file_message = {
            'type': 'file_operation',
            'operation': 'WriteFile',
            'data': {
                'handle': '0x12345678',
                'filePath': 'C:\\Users\\test\\document.txt',
                'bytesTransferred': 256,
                'content': 'Test file content',
                'timestamp': '2025-01-09T12:00:01.000Z'
            },
            'metadata': {
                'sessionId': 'test-session-123',
                'processName': 'notepad.exe',
                'processId': 1234
            }
        }
        
        print("Processing file operation message...")
        handler.handle_message(file_message, None)
        
        # Test process creation message
        process_message = {
            'type': 'process_creation',
            'operation': 'NtCreateUserProcess',
            'data': {
                'commandLine': 'C:\\Windows\\System32\\calc.exe',
                'processId': 5678,
                'parentProcessId': 1234,
                'timestamp': '2025-01-09T12:00:02.000Z'
            },
            'metadata': {
                'sessionId': 'test-session-123',
                'processName': 'explorer.exe',
                'processId': 1234
            }
        }
        
        print("Processing process creation message...")
        handler.handle_message(process_message, None)
        
        # Test statistics
        stats = handler.get_statistics()
        print(f"✓ Handler Stats: {stats}")
        
        # Test API management
        await handler.flush_api_events()
        print("✓ Flushed API events")
        
        # Test API connection
        connection_ok = await handler.test_api_connection()
        print(f"✓ API connection test: {'SUCCESS' if connection_ok else 'FAILED'}")
        
    except Exception as e:
        print(f"✗ Message Handler test failed: {e}")
    finally:
        # Restore original config
        config.api_enabled = original_enabled
        config.api_endpoint = original_endpoint
        
        # Shutdown handler
        await handler.shutdown()

async def main():
    """Run all tests"""
    print("🚀 Starting API Integration Tests\n")
    
    try:
        await test_api_client()
        await test_message_handler()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
