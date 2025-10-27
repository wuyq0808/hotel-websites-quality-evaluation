#!/usr/bin/env python3
"""
Web Application Server for Quality Evaluation Tool
Serves the config editor UI and provides API endpoints for running evaluations
"""

import os
import sys
import subprocess
import signal
import threading
from pathlib import Path
from flask import Flask, request, jsonify, send_file, Response
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

# Global process management
evaluation_process = None
process_lock = threading.Lock()
log_file_path = None

# Paths
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / 'logs'
CONFIG_PATH = BASE_DIR / 'src' / 'config.yaml'
HTML_PATH = BASE_DIR / 'config-editor.html'

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)


@app.route('/')
def index():
    """Serve the config editor HTML"""
    return send_file(str(HTML_PATH))


@app.route('/api/save-config', methods=['POST'])
def save_config():
    """Save YAML configuration from the browser"""
    try:
        data = request.json
        yaml_content = data.get('yaml', '')

        if not yaml_content:
            return jsonify({'success': False, 'error': 'No YAML content provided'}), 400

        # Write to config.yaml
        with open(CONFIG_PATH, 'w') as f:
            f.write(yaml_content)

        return jsonify({'success': True, 'message': 'Configuration saved successfully'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/start', methods=['POST'])
def start_evaluation():
    """Start the evaluation process"""
    global evaluation_process, log_file_path

    with process_lock:
        # Check if already running
        if evaluation_process and evaluation_process.poll() is None:
            return jsonify({'success': False, 'error': 'Evaluation is already running'}), 400

        try:
            # Create timestamped log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file_path = LOGS_DIR / f'evaluation_{timestamp}.log'

            # Open log file
            log_file = open(log_file_path, 'w', buffering=1)

            # Determine Python interpreter (use venv if available)
            venv_python = BASE_DIR / 'venv' / 'bin' / 'python3'
            python_cmd = str(venv_python) if venv_python.exists() else 'python3'

            # Start subprocess
            script_path = BASE_DIR / 'src' / 'quality_evaluator_agent.py'
            evaluation_process = subprocess.Popen(
                [python_cmd, str(script_path)],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=str(BASE_DIR),
                bufsize=1,
                universal_newlines=True,
                preexec_fn=os.setsid  # Create new process group for easier termination
            )

            return jsonify({
                'success': True,
                'message': 'Evaluation started',
                'pid': evaluation_process.pid,
                'log_file': str(log_file_path)
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def stop_evaluation():
    """Stop the running evaluation process"""
    global evaluation_process

    with process_lock:
        if not evaluation_process or evaluation_process.poll() is not None:
            return jsonify({'success': False, 'error': 'No evaluation is running'}), 400

        try:
            # Send SIGTERM to process group
            os.killpg(os.getpgid(evaluation_process.pid), signal.SIGTERM)

            # Wait for graceful shutdown (max 5 seconds)
            try:
                evaluation_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                os.killpg(os.getpgid(evaluation_process.pid), signal.SIGKILL)
                evaluation_process.wait()

            evaluation_process = None

            return jsonify({'success': True, 'message': 'Evaluation stopped'})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current process status"""
    global evaluation_process, log_file_path

    with process_lock:
        if not evaluation_process:
            return jsonify({
                'running': False,
                'status': 'idle'
            })

        poll_result = evaluation_process.poll()

        if poll_result is None:
            # Still running
            return jsonify({
                'running': True,
                'status': 'running',
                'pid': evaluation_process.pid,
                'log_file': str(log_file_path) if log_file_path else None
            })
        else:
            # Finished
            status = 'completed' if poll_result == 0 else 'error'
            return jsonify({
                'running': False,
                'status': status,
                'exit_code': poll_result,
                'log_file': str(log_file_path) if log_file_path else None
            })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get current log file contents"""
    global log_file_path

    if not log_file_path or not log_file_path.exists():
        return jsonify({'content': '', 'exists': False})

    try:
        with open(log_file_path, 'r') as f:
            content = f.read()

        return jsonify({
            'content': content,
            'exists': True,
            'size': len(content)
        })

    except Exception as e:
        return jsonify({'content': '', 'exists': False, 'error': str(e)})


@app.route('/api/log-files', methods=['GET'])
def list_log_files():
    """List all available log files"""
    try:
        log_files = sorted(
            [f.name for f in LOGS_DIR.glob('evaluation_*.log')],
            reverse=True  # Most recent first
        )

        return jsonify({
            'files': log_files,
            'current': log_file_path.name if log_file_path else None
        })

    except Exception as e:
        return jsonify({'files': [], 'error': str(e)})


def cleanup():
    """Cleanup handler for graceful shutdown"""
    global evaluation_process

    if evaluation_process and evaluation_process.poll() is None:
        print("Shutting down evaluation process...")
        try:
            os.killpg(os.getpgid(evaluation_process.pid), signal.SIGTERM)
            evaluation_process.wait(timeout=5)
        except:
            pass


# Register cleanup on exit
import atexit
atexit.register(cleanup)


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Quality Evaluation Web App")
    print("=" * 80)
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"📄 Config Path: {CONFIG_PATH}")
    print(f"📋 Logs Directory: {LOGS_DIR}")
    print(f"🌐 Starting server at http://localhost:5000")
    print("=" * 80)
    print()

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Don't use debug mode with subprocess management
        threaded=True
    )
