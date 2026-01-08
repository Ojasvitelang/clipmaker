import os
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import zipfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload

# Paths
BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
CLIP_MAKER_SCRIPT = BASE_DIR / "clip_maker.py"
CONVERT_SCRIPT = BASE_DIR / "convert.py"

# Ensure sessions directory exists
SESSIONS_DIR.mkdir(exist_ok=True)

# Store processing status
processing_status = {}

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_session_directory(session_id):
    """Create isolated directory structure for a session"""
    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    # Create required subdirectories
    (session_dir / "input").mkdir(exist_ok=True)
    (session_dir / "output").mkdir(exist_ok=True)
    (session_dir / "temp").mkdir(exist_ok=True)

    # Copy scripts to session directory
    shutil.copy2(CLIP_MAKER_SCRIPT, session_dir / "clip_maker.py")
    shutil.copy2(CONVERT_SCRIPT, session_dir / "convert.py")

    return session_dir


def process_video(session_id, session_dir):
    """Run both scripts in sequence - DO NOT modify script logic"""
    try:
        processing_status[session_id] = {
            'status': 'processing',
            'step': 'Creating clips...',
            'progress': 10
        }

        # Step 1: Run clip_maker.py (treats it as a black box)
        print(f"[{session_id}] Running clip_maker.py...")
        result = subprocess.run(
            ['python3', 'clip_maker.py'],
            cwd=session_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"clip_maker.py failed: {result.stderr}")

        processing_status[session_id].update({
            'step': 'Creating GIFs...',
            'progress': 50
        })

        # Step 2: Run convert.py (treats it as a black box)
        print(f"[{session_id}] Running convert.py...")
        result = subprocess.run(
            ['python3', 'convert.py'],
            cwd=session_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"convert.py failed: {result.stderr}")

        # Step 3: Count outputs
        output_dir = session_dir / "output"
        clips = list(output_dir.glob("*.mp4"))
        gifs = list(output_dir.glob("*.gif"))

        processing_status[session_id] = {
            'status': 'completed',
            'step': 'Done!',
            'progress': 100,
            'clips_count': len(clips),
            'gifs_count': len(gifs)
        }

        print(f"[{session_id}] Processing complete: {len(clips)} clips, {len(gifs)} GIFs")

    except Exception as e:
        print(f"[{session_id}] Error: {str(e)}")
        processing_status[session_id] = {
            'status': 'error',
            'step': f'Error: {str(e)}',
            'progress': 0
        }


def create_zip(session_dir, session_id):
    """Create a ZIP file of all outputs"""
    output_dir = session_dir / "output"
    zip_path = session_dir / f"{session_id}_outputs.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in output_dir.iterdir():
            if file.is_file():
                zipf.write(file, arcname=file.name)

    return zip_path


@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """Handle video upload and start processing"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['video']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: mp4, mov, avi, mkv, webm'}), 400

    # Create unique session
    session_id = str(uuid.uuid4())
    session_dir = create_session_directory(session_id)

    # Save uploaded file to input directory
    filename = secure_filename(file.filename)
    input_path = session_dir / "input" / filename
    file.save(input_path)

    # Start processing in background thread
    processing_status[session_id] = {
        'status': 'starting',
        'step': 'Initializing...',
        'progress': 0
    }

    thread = threading.Thread(target=process_video, args=(session_id, session_dir))
    thread.daemon = True
    thread.start()

    return jsonify({
        'session_id': session_id,
        'message': 'Processing started'
    })


@app.route('/status/<session_id>')
def status(session_id):
    """Check processing status"""
    if session_id not in processing_status:
        return jsonify({'error': 'Session not found'}), 404

    return jsonify(processing_status[session_id])


@app.route('/download/<session_id>')
def download(session_id):
    """Create and serve ZIP file of outputs"""
    if session_id not in processing_status:
        return jsonify({'error': 'Session not found'}), 404

    if processing_status[session_id]['status'] != 'completed':
        return jsonify({'error': 'Processing not complete'}), 400

    session_dir = SESSIONS_DIR / session_id

    if not session_dir.exists():
        return jsonify({'error': 'Session files not found'}), 404

    # Create ZIP file
    zip_path = create_zip(session_dir, session_id)

    # Send file and schedule cleanup
    def cleanup():
        time.sleep(5)  # Wait for download to start
        try:
            shutil.rmtree(session_dir)
            del processing_status[session_id]
            print(f"[{session_id}] Cleaned up session")
        except Exception as e:
            print(f"[{session_id}] Cleanup error: {e}")

    cleanup_thread = threading.Thread(target=cleanup)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    return send_file(
        zip_path,
        as_attachment=True,
        download_name=f'clipmaker_outputs_{session_id[:8]}.zip'
    )


if __name__ == '__main__':
    print("=" * 60)
    print("ClipMaker Web UI")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
