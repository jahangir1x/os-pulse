"""
Test script for the OS-Pulse Controller
"""
import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from frida_controller import FridaController
from message_handler import MessageHandler
from config import config


def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    try:
        config.validate()
        print(f"✓ Agent script found: {config.agent_script_path}")
        print(f"✓ Configuration valid")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_message_handler():
    """Test message handler"""
    print("\nTesting message handler...")
    handler = MessageHandler()
    
    # Test session start message
    session_msg = {
        'type': 'session_start',
        'data': {
            'sessionId': 'test-session-123',
            'processName': 'test.exe',
            'processId': 1234,
            'platform': 'windows',
            'arch': 'x64',
            'timestamp': '2025-09-09T12:00:00.000Z'
        }
    }
    handler.handle_message(session_msg)
    
    # Test file operation message
    file_msg = {
        'type': 'file_operation',
        'operation': 'ReadFile',
        'data': {
            'handle': '0x12345678',
            'filePath': 'C:\\test\\file.txt',
            'bytesTransferred': 256,
            'content': 'Hello, World!',
            'timestamp': '2025-09-09T12:00:01.000Z'
        },
        'metadata': {
            'sessionId': 'test-session-123',
            'processName': 'test.exe',
            'processId': 1234
        }
    }
    handler.handle_message(file_msg)
    
    # Test process creation message
    process_msg = {
        'type': 'process_creation',
        'operation': 'NtCreateUserProcess',
        'data': {
            'processHandle': '0x87654321',
            'threadHandle': '0x11223344',
            'imagePath': 'C:\\Windows\\System32\\notepad.exe',
            'commandLine': 'notepad.exe test.txt',
            'currentDirectory': 'C:\\temp',
            'status': 0,
            'timestamp': '2025-09-09T12:00:02.000Z'
        },
        'metadata': {
            'sessionId': 'test-session-123',
            'processName': 'test.exe',
            'processId': 1234
        }
    }
    handler.handle_message(process_msg)
    
    stats = handler.get_statistics()
    print(f"✓ Message handler processed {stats['event_count']} events")
    return True


def test_controller_init():
    """Test controller initialization"""
    print("\nTesting controller initialization...")
    try:
        controller = FridaController()
        print(f"✓ Controller initialized successfully")
        print(f"✓ Agent script loaded: {len(controller.agent_code)} characters")
        return True
    except Exception as e:
        print(f"✗ Controller initialization failed: {e}")
        return False


def test_process_listing():
    """Test process listing"""
    print("\nTesting process listing...")
    try:
        controller = FridaController()
        processes = controller.list_processes("explorer")  # Should find explorer.exe
        
        if processes:
            print(f"✓ Found {len(processes)} processes matching 'explorer'")
            for proc in processes[:3]:  # Show first 3
                print(f"  - {proc['name']} (PID: {proc['pid']})")
        else:
            print("! No processes found (this might be normal)")
        
        return True
    except Exception as e:
        print(f"✗ Process listing failed: {e}")
        return False


def main():
    """Run all tests"""
    print("OS-Pulse Controller Test Suite")
    print("=" * 40)
    
    tests = [
        test_config,
        test_message_handler,
        test_controller_init,
        test_process_listing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Controller is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python main.py list-processes' to see running processes")
        print("2. Run 'python main.py spawn --executable \"C:\\Windows\\System32\\notepad.exe\"' to test")
    else:
        print("✗ Some tests failed. Check the errors above.")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
