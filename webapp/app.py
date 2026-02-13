from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import os
import sys
import threading
import json
import time
from datetime import datetime
from io import StringIO

app = Flask(__name__)

# Track script execution status
script_running = False
script_status = "idle"
script_logs = []
log_file_path = None

def capture_script_output():
    """Run the script and capture output"""
    global script_running, script_status, script_logs, log_file_path
    try:
        script_running = True
        script_status = "running"
        script_logs = []
        
        # Get the parent directory (where script.py is located)
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(parent_dir, 'script.py')
        log_file_path = os.path.join(parent_dir, 'scrape_log.json')
        
        # Run the script with output capture
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=parent_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Read output line by line
        for line in process.stdout:
            line = line.rstrip('\n')
            if line:
                timestamp = datetime.now().strftime("%H:%M:%S")
                script_logs.append(f"[{timestamp}] {line}")
                print(f"[LOG] {line}")
        
        process.wait()
        script_status = "completed"
        script_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Script completed successfully!")
    except Exception as e:
        script_status = f"error: {str(e)}"
        script_logs.append(f"ERROR: {str(e)}")
    finally:
        script_running = False

@app.route('/', methods=['GET', 'POST'])
def index():
    global script_running, script_logs
    if request.method == 'POST':
        if script_running:
            return jsonify({"status": "error", "message": "Script is already running"}), 400
        
        # Clear previous logs
        script_logs = []
        
        # Run script in background thread
        thread = threading.Thread(target=capture_script_output)
        thread.daemon = True
        thread.start()
        
        return jsonify({"status": "success", "message": "Script started!"})
    
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    """Check the status of the script"""
    return jsonify({
        "running": script_running,
        "status": script_status,
        "logs": script_logs,
        "log_count": len(script_logs)
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get all logs"""
    return jsonify({"logs": script_logs})

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Show dashboard with stats and search"""
    return render_template('dashboard.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics from the latest log file"""
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_file = os.path.join(parent_dir, 'scrape_log.json')
        
        if not os.path.exists(log_file):
            # Return a default empty response instead of 404
            return jsonify({
                'session_start': 'No data yet',
                'search_term': 'N/A',
                'total_categories': 0,
                'total_offers_scanned': 0,
                'matches_found': 0,
                'categories': [],
                'matches': []
            })
        
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        results = data.get('results', {})
        offers = results.get('offers_scanned', [])
        categories = results.get('categories_found', [])
        
        stats = {
            'session_start': data.get('session_start'),
            'search_term': data.get('search_term'),
            'total_categories': len(categories),
            'total_offers_scanned': len(offers),
            'matches_found': sum(1 for o in offers if o.get('match', False)),
            'categories': categories[:20],  # First 20 categories
            'matches': [o for o in offers if o.get('match', False)]
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'session_start': 'Error loading',
            'search_term': 'N/A',
            'total_categories': 0,
            'total_offers_scanned': 0,
            'matches_found': 0,
            'categories': [],
            'matches': []
        })

@app.route('/api/search', methods=['GET'])
def search_offers():
    """Search through offers"""
    try:
        query = request.args.get('q', '').lower()
        match_only = request.args.get('match_only', 'false').lower() == 'true'
        
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_file = os.path.join(parent_dir, 'scrape_log.json')
        
        if not os.path.exists(log_file):
            # Return empty results instead of error
            return jsonify({
                'total': 0,
                'results': []
            })
        
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        offers = data.get('results', {}).get('offers_scanned', [])
        results = []
        
        for offer in offers:
            if match_only and not offer.get('match', False):
                continue
            
            if query:
                url = offer.get('url', '').lower()
                desc = offer.get('raw_description', '').lower()
                if query not in url and query not in desc:
                    continue
            
            results.append({
                'url': offer.get('url'),
                'match': offer.get('match'),
                'description': offer.get('raw_description', '')[:500]  # First 500 chars
            })
        
        return jsonify({
            'total': len(results),
            'results': results[:100]  # Limit to 100 results
        })
    except Exception as e:
        return jsonify({
            'total': 0,
            'results': [],
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 7001)))