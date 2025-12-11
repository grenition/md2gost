import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import mimetypes

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

STORAGE_BASE = os.getenv('STORAGE_BASE', '/tmp/md2gost/sessions')

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}


def allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'file-service'}), 200


@app.route('/api/images/upload', methods=['POST'])
def upload_image():
    session_id = request.headers.get('X-Session-Id')
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File must be an image'}), 400
    
    ext = os.path.splitext(file.filename)[1] or '.png'
    filename = f"{uuid.uuid4().hex[:8]}{ext}"
    
    session_dir = os.path.join(STORAGE_BASE, session_id, 'images')
    os.makedirs(session_dir, exist_ok=True)
    filepath = os.path.join(session_dir, filename)
    file.save(filepath)
    
    return jsonify({
        'filename': filename,
        'url': f'/api/images/{session_id}/{filename}'
    }), 200


@app.route('/api/images/<session_id>/<filename>', methods=['GET'])
def get_image(session_id, filename):
    filename = secure_filename(filename)
    filepath = os.path.join(STORAGE_BASE, session_id, 'images', filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Image not found'}), 404
    
    mimetype, _ = mimetypes.guess_type(filepath)
    if not mimetype:
        mimetype = 'image/png'
    
    return send_file(filepath, mimetype=mimetype)


@app.route('/api/session/<session_id>/images', methods=['GET'])
def list_images(session_id):
    session_dir = os.path.join(STORAGE_BASE, session_id, 'images')
    
    if not os.path.exists(session_dir):
        return jsonify({'images': []}), 200
    
    images = []
    for filename in os.listdir(session_dir):
        filepath = os.path.join(session_dir, filename)
        if os.path.isfile(filepath):
            images.append({
                'filename': filename,
                'url': f'/api/images/{session_id}/{filename}'
            })
    
    return jsonify({'images': images}), 200


if __name__ == '__main__':
    os.makedirs(STORAGE_BASE, exist_ok=True)
    app.run(host='0.0.0.0', port=5002, debug=False)

