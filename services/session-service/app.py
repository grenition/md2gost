import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

SESSIONS = {}
SESSION_TIMEOUT = timedelta(hours=24)
SESSION_DATA = {}
SHORT_ID_TO_SESSION = {}
SESSION_TO_SHORT_ID = {}


def generate_session_id():
    return 'session_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:12]


def generate_short_id():
    import random
    import string
    chars = string.ascii_lowercase + string.digits
    while True:
        short_id = ''.join(random.choices(chars, k=8))
        if short_id not in SHORT_ID_TO_SESSION:
            return short_id


def is_session_valid(session_id):
    if not session_id or session_id not in SESSIONS:
        return False
    
    session = SESSIONS[session_id]
    if datetime.now() - session['created_at'] > SESSION_TIMEOUT:
        # Clean up expired session
        del SESSIONS[session_id]
        if session_id in SESSION_TO_SHORT_ID:
            short_id = SESSION_TO_SHORT_ID[session_id]
            del SESSION_TO_SHORT_ID[session_id]
            if short_id in SHORT_ID_TO_SESSION:
                del SHORT_ID_TO_SESSION[short_id]
        if session_id in SESSION_DATA:
            del SESSION_DATA[session_id]
        return False
    
    return True


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'session-service'}), 200


@app.route('/api/session/create', methods=['POST'])
def create_session():
    session_id = generate_session_id()
    short_id = generate_short_id()
    
    SESSIONS[session_id] = {
        'id': session_id,
        'created_at': datetime.now(),
        'last_activity': datetime.now()
    }
    SHORT_ID_TO_SESSION[short_id] = session_id
    SESSION_TO_SHORT_ID[session_id] = short_id
    
    app.logger.info(f"Session created: {session_id}, short_id: {short_id}, total sessions: {len(SESSIONS)}")
    return jsonify({'session_id': session_id, 'short_id': short_id}), 200


@app.route('/api/session/short/<short_id>', methods=['GET'])
def get_session_by_short_id(short_id):
    if short_id not in SHORT_ID_TO_SESSION:
        return jsonify({'error': 'Short ID not found'}), 404
    
    session_id = SHORT_ID_TO_SESSION[short_id]
    if not is_session_valid(session_id):
        # Clean up invalid mappings
        del SHORT_ID_TO_SESSION[short_id]
        if session_id in SESSION_TO_SHORT_ID:
            del SESSION_TO_SHORT_ID[session_id]
        return jsonify({'error': 'Session expired'}), 404
    
    return jsonify({'session_id': session_id, 'short_id': short_id}), 200


@app.route('/api/session/validate', methods=['POST'])
def validate_session():
    data = request.get_json()
    session_id = data.get('session_id') if data else None
    
    if not session_id:
        app.logger.warning("Session validation: no session_id provided")
        return jsonify({'valid': False, 'error': 'Session ID required'}), 400
    
    app.logger.info(f"Validating session: {session_id}, exists: {session_id in SESSIONS}, total sessions: {len(SESSIONS)}")
    
    if is_session_valid(session_id):
        SESSIONS[session_id]['last_activity'] = datetime.now()
        app.logger.info(f"Session validated successfully: {session_id}")
        return jsonify({'valid': True}), 200
    else:
        app.logger.warning(f"Session validation failed: {session_id}")
        return jsonify({'valid': False, 'error': 'Invalid or expired session'}), 200


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    if is_session_valid(session_id):
        session = SESSIONS[session_id]
        return jsonify({
            'session_id': session['id'],
            'created_at': session['created_at'].isoformat(),
            'last_activity': session['last_activity'].isoformat()
        }), 200
    else:
        return jsonify({'error': 'Session not found or expired'}), 404


@app.route('/api/session/<session_id>/data', methods=['GET'])
def get_session_data(session_id):
    if not is_session_valid(session_id):
        return jsonify({'error': 'Session not found or expired'}), 404
    
    data = SESSION_DATA.get(session_id, {})
    return jsonify({'data': data}), 200


@app.route('/api/session/<session_id>/data', methods=['POST'])
def save_session_data(session_id):
    if not is_session_valid(session_id):
        return jsonify({'error': 'Session not found or expired'}), 404
    
    data = request.get_json()
    if 'data' not in data:
        return jsonify({'error': 'Data field required'}), 400
    
    SESSION_DATA[session_id] = data['data']
    SESSIONS[session_id]['last_activity'] = datetime.now()
    return jsonify({'success': True}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)

