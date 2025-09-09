#!/usr/bin/env python3
"""
Simple test API server to receive OS-Pulse monitoring events
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Store received events
received_events = []
stats = {
    'total_events': 0,
    'file_operations': 0,
    'process_creations': 0,
    'errors': 0,
    'start_time': datetime.now()
}

@app.route('/api/events', methods=['POST'])
def receive_events():
    """Receive monitoring events from OS-Pulse"""
    try:
        data = request.get_json()
        
        if not data:
            stats['errors'] += 1
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Process single event or batch
        events = data if isinstance(data, list) else [data]
        
        for event in events:
            # Validate required fields
            if 'type' not in event:
                stats['errors'] += 1
                continue
            
            # Add timestamp if not present
            if 'timestamp' not in event:
                event['timestamp'] = datetime.now().isoformat()
            
            # Update stats
            stats['total_events'] += 1
            if event['type'] == 'file_operation':
                stats['file_operations'] += 1
            elif event['type'] == 'process_creation':
                stats['process_creations'] += 1
            
            # Store event
            received_events.append(event)
            
            # Print event (colorful output)
            print_event(event)
        
        return jsonify({
            'status': 'success',
            'received': len(events),
            'total_events': stats['total_events']
        })
    
    except Exception as e:
        stats['errors'] += 1
        print(f"❌ Error processing events: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    uptime = datetime.now() - stats['start_time']
    return jsonify({
        'status': 'healthy',
        'uptime_seconds': int(uptime.total_seconds()),
        'stats': stats
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all received events"""
    return jsonify({
        'events': received_events[-100:],  # Last 100 events
        'total_count': len(received_events),
        'stats': stats
    })

@app.route('/api/events/clear', methods=['POST'])
def clear_events():
    """Clear all received events"""
    global received_events
    count = len(received_events)
    received_events = []
    stats['total_events'] = 0
    stats['file_operations'] = 0
    stats['process_creations'] = 0
    stats['errors'] = 0
    stats['start_time'] = datetime.now()
    
    return jsonify({
        'status': 'cleared',
        'cleared_count': count
    })

def print_event(event):
    """Print event with color coding"""
    event_type = event.get('type', 'unknown')
    timestamp = event.get('timestamp', 'N/A')
    
    if event_type == 'file_operation':
        operation = event.get('operation', 'Unknown')
        data = event.get('data', {})
        file_path = data.get('filePath', 'Unknown')
        bytes_transferred = data.get('bytesTransferred', 0)
        
        print(f"🗂️  [{timestamp}] FILE: {operation} - {file_path} ({bytes_transferred} bytes)")
        
        # Show content preview if available
        content = data.get('content', '')
        if content and len(content) > 0:
            preview = content[:50] + '...' if len(content) > 50 else content
            print(f"   📄 Content: {repr(preview)}")
    
    elif event_type == 'process_creation':
        operation = event.get('operation', 'Unknown')
        data = event.get('data', {})
        command_line = data.get('commandLine', 'Unknown')
        process_id = data.get('processId', 'Unknown')
        
        print(f"⚙️  [{timestamp}] PROCESS: {operation} - PID {process_id}")
        print(f"   💻 Command: {command_line}")
    
    else:
        print(f"❓ [{timestamp}] UNKNOWN: {event_type} - {json.dumps(event, indent=2)}")

def print_stats():
    """Print periodic statistics"""
    while True:
        time.sleep(30)  # Every 30 seconds
        uptime = datetime.now() - stats['start_time']
        print(f"\n📊 API Server Stats (Uptime: {int(uptime.total_seconds())}s)")
        print(f"   📈 Total Events: {stats['total_events']}")
        print(f"   🗂️  File Operations: {stats['file_operations']}")
        print(f"   ⚙️  Process Creations: {stats['process_creations']}")
        print(f"   ❌ Errors: {stats['errors']}")
        print()

if __name__ == '__main__':
    print("🚀 Starting OS-Pulse API Test Server")
    print("📡 Listening for monitoring events on http://localhost:8080")
    print("🔗 Endpoints:")
    print("   POST /api/events    - Receive monitoring events")
    print("   GET  /api/events    - View received events")
    print("   GET  /api/health    - Health check")
    print("   POST /api/events/clear - Clear all events")
    print()
    
    # Start stats thread
    stats_thread = threading.Thread(target=print_stats, daemon=True)
    stats_thread.start()
    
    # Start Flask app
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Shutting down API server...")
