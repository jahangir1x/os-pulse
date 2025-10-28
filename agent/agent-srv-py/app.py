"""
Flask-based Agent Server for OS-Pulse
Handles file uploads, process listing, and monitoring control
"""
import os
import subprocess
import csv
import io
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = Path.home() / "Desktop"
CONTROLLER_PATH = Path(__file__).parent.parent / "controller" / "main.py"
ALLOWED_EXTENSIONS = {'exe', 'dll', 'bat', 'ps1', 'py'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max file size

# Store active monitoring processes
monitoring_processes = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads and save them to Desktop"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(str(filepath))
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'path': str(filepath)
        }), 200


@app.route('/api/processes', methods=['GET'])
def list_processes():
    """List running processes using tasklist"""
    try:
        # Run tasklist with CSV format
        result = subprocess.run(
            ['tasklist', '/FO', 'CSV', '/NH'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse CSV output
        processes = []
        csv_reader = csv.reader(io.StringIO(result.stdout))
        
        for row in csv_reader:
            if len(row) >= 2:
                try:
                    processes.append({
                        'name': row[0].strip('"'),
                        'pid': int(row[1].strip('"'))
                    })
                except (ValueError, IndexError):
                    continue
        
        return jsonify({
            'processes': processes,
            'count': len(processes)
        }), 200
        
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to list processes: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/start', methods=['POST'])
def start_monitor():
    """Start monitoring based on mode"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    session_id = data.get('sessionId')
    mode = data.get('mode')
    
    if not session_id:
        return jsonify({'error': 'sessionId is required'}), 400
    
    if mode not in [1, 2, 3]:
        return jsonify({'error': 'Invalid monitoring mode'}), 400
    
    # Build command based on mode
    python_path = "python"
    cmd = [python_path, str(CONTROLLER_PATH)]
    
    if mode == 1:  # All Processes
        file_name = data.get('fileName')
        if file_name:
            # Attach to all processes with filter
            cmd.extend(['attach', '--all', '--filter', file_name])
        else:
            cmd.extend(['attach', '--all'])
    
    elif mode == 2:  # Specific Processes
        processes = data.get('processes', [])
        if not processes:
            return jsonify({'error': 'Mode 2 requires process list'}), 400
        
        # Attach to specific PIDs
        cmd.extend(['attach', '--pids'])
        cmd.extend([str(pid) for pid in processes])
    
    elif mode == 3:  # Spawn Uploaded
        file_name = data.get('fileName')
        if not file_name:
            return jsonify({'error': 'Mode 3 requires fileName'}), 400
        
        # For now, spawn notepad for testing
        exec_path = app.config['UPLOAD_FOLDER'] / file_name
        # exec_path = r"C:\Windows\System32\Notepad.exe"
        cmd.extend(['spawn', '--executable', exec_path])
    
    try:
        # Set environment variable for session ID
        env = os.environ.copy()
        env['SESSION_ID'] = session_id
        
        # Start the monitoring process
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Store the process
        monitoring_processes[session_id] = process
        
        return jsonify({
            'message': 'Monitoring started successfully',
            'sessionId': session_id,
            'monitoringPid': process.pid,
            'mode': mode
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to start monitoring: {str(e)}'}), 500


@app.route('/monitor/stop', methods=['POST'])
def stop_monitor():
    """Stop monitoring for a session"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    session_id = data.get('sessionId')
    
    if not session_id:
        return jsonify({'error': 'sessionId is required'}), 400
    
    # Get the process for this session
    process = monitoring_processes.get(session_id)
    
    if not process:
        return jsonify({'error': 'No active monitoring session found'}), 404
    
    try:
        # Terminate the process
        process.terminate()
        
        # Wait for process to terminate (with timeout)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't terminate gracefully
            process.kill()
            process.wait()
        
        # Remove from active processes
        del monitoring_processes[session_id]
        
        return jsonify({
            'message': 'Monitoring stopped successfully',
            'sessionId': session_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to stop monitoring: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'agent-srv-py',
        'active_sessions': len(monitoring_processes)
    }), 200


if __name__ == '__main__':
    # Ensure upload folder exists
    app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
    
    # Run the server
    port = int(os.environ.get('PORT', 7000))
    app.run(host='0.0.0.0', port=port, debug=True)
