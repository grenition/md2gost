import os
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

DOCX_SERVICE_URL = os.getenv('DOCX_SERVICE_URL', 'http://docx-service:5000')
FILE_SERVICE_URL = os.getenv('FILE_SERVICE_URL', 'http://file-service:5002')
SESSION_SERVICE_URL = os.getenv('SESSION_SERVICE_URL', 'http://session-service:5003')


def validate_session(session_id):
    if not session_id:
        app.logger.warning("Session validation: no session_id provided")
        return False
    try:
        response = requests.post(
            f'{SESSION_SERVICE_URL}/api/session/validate',
            json={'session_id': session_id},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            is_valid = result.get('valid', False)
            if not is_valid:
                app.logger.warning(f"Session validation failed for session_id: {session_id}, response: {result}")
            return is_valid
        else:
            app.logger.error(f"Session validation returned status {response.status_code}: {response.text}")
    except Exception as e:
        app.logger.error(f"Session validation error: {e}")
    return False


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'api-service'}), 200


@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        markdown_content = data.get('markdown', '')
        syntax_highlighting = data.get('syntax_highlighting', True)
        session_id = data.get('session_id')
        
        app.logger.warning(f"Convert request: session_id={session_id}, markdown_length={len(markdown_content)}")
        
        if not markdown_content:
            return jsonify({'error': 'Markdown content is required'}), 400
        
        if session_id and not validate_session(session_id):
            return jsonify({'error': 'Invalid session'}), 401
        
        request_data = {
            'markdown': markdown_content,
            'syntax_highlighting': syntax_highlighting,
            'session_id': session_id
        }
        app.logger.warning(f"Sending to docx-service: session_id={session_id}, data_keys={list(request_data.keys())}")
        
        response = requests.post(
            f'{DOCX_SERVICE_URL}/api/convert',
            json=request_data,
            timeout=300
        )
        response.raise_for_status()
        
        return send_file(
            io.BytesIO(response.content),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name='document.docx'
        )
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling docx-service: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Error converting markdown: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview', methods=['POST'])
def preview():
    try:
        data = request.get_json()
        markdown_content = data.get('markdown', '')
        syntax_highlighting = data.get('syntax_highlighting', True)
        session_id = data.get('session_id')
        
        app.logger.warning(f"Preview request: session_id={session_id}, markdown_length={len(markdown_content)}")
        
        if not markdown_content:
            return jsonify({'error': 'Markdown content is required'}), 400
        
        if session_id and not validate_session(session_id):
            return jsonify({'error': 'Invalid session'}), 401
        
        request_data = {
            'markdown': markdown_content,
            'syntax_highlighting': syntax_highlighting,
            'session_id': session_id
        }
        app.logger.warning(f"Sending to docx-service: session_id={session_id}, data_keys={list(request_data.keys())}")
        
        response = requests.post(
            f'{DOCX_SERVICE_URL}/api/preview',
            json=request_data,
            timeout=300
        )
        response.raise_for_status()
        
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling docx-service: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Error generating preview: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/images/upload', methods=['POST'])
def upload_image():
    try:
        session_id = request.headers.get('X-Session-Id')
        app.logger.info(f"Image upload request, session_id: {session_id}")
        
        if not session_id:
            app.logger.warning("Image upload: no session_id in headers")
            return jsonify({'error': 'Session ID required'}), 400
        
        if not validate_session(session_id):
            app.logger.warning(f"Image upload: invalid session {session_id}")
            return jsonify({'error': 'Invalid session'}), 401
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        files = {'file': (file.filename, file.stream, file.content_type)}
        headers = {'X-Session-Id': session_id}
        
        response = requests.post(
            f'{FILE_SERVICE_URL}/api/images/upload',
            files=files,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling file-service: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Error uploading image: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/images/<session_id>/<filename>', methods=['GET'])
def get_image(session_id, filename):
    try:
        if not validate_session(session_id):
            return jsonify({'error': 'Invalid session'}), 401
        
        response = requests.get(
            f'{FILE_SERVICE_URL}/api/images/{session_id}/{filename}',
            timeout=30
        )
        response.raise_for_status()
        
        return send_file(
            io.BytesIO(response.content),
            mimetype=response.headers.get('Content-Type', 'image/png')
        )
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling file-service: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Error retrieving image: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/create', methods=['POST'])
def create_session():
    try:
        response = requests.post(
            f'{SESSION_SERVICE_URL}/api/session/create',
            timeout=5
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling session-service: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>/data', methods=['GET'])
def get_session_data(session_id):
    try:
        response = requests.get(
            f'{SESSION_SERVICE_URL}/api/session/{session_id}/data',
            timeout=5
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling session-service: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>/data', methods=['POST'])
def save_session_data(session_id):
    try:
        data = request.get_json()
        response = requests.post(
            f'{SESSION_SERVICE_URL}/api/session/{session_id}/data',
            json=data,
            timeout=5
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling session-service: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/short/<short_id>', methods=['GET'])
def get_session_by_short_id(short_id):
    try:
        response = requests.get(
            f'{SESSION_SERVICE_URL}/api/session/short/{short_id}',
            timeout=5
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling session-service: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)

