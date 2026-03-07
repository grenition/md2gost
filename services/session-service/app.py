import os
import uuid
import time
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://md2gost:md2gost@postgres:5432/md2gost'
)
DB_INIT_MAX_RETRIES = int(os.getenv('DB_INIT_MAX_RETRIES', '20'))
DB_INIT_RETRY_DELAY_SEC = float(os.getenv('DB_INIT_RETRY_DELAY_SEC', '1'))
DB_INITIALIZED = False


def get_connection():
    return psycopg2.connect(DATABASE_URL, connect_timeout=5)


def init_db():
    global DB_INITIALIZED
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    short_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    last_activity TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    data JSONB NOT NULL DEFAULT '{}'::jsonb
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_short_id ON sessions(short_id)"
            )
    DB_INITIALIZED = True


def ensure_db_initialized():
    if DB_INITIALIZED:
        return

    last_error = None
    for _ in range(DB_INIT_MAX_RETRIES):
        try:
            init_db()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(DB_INIT_RETRY_DELAY_SEC)
    raise last_error


def short_exists(short_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM sessions WHERE short_id = %s", (short_id,))
            return cursor.fetchone() is not None


def create_session_record(session_id, short_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sessions (id, short_id, created_at, last_activity, data)
                VALUES (%s, %s, NOW(), NOW(), '{}'::jsonb)
                """,
                (session_id, short_id),
            )


def is_session_valid(session_id):
    if not session_id:
        return False
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM sessions WHERE id = %s", (session_id,))
            return cursor.fetchone() is not None


def touch_session(session_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE sessions SET last_activity = NOW() WHERE id = %s",
                (session_id,),
            )


def get_session_row(session_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, short_id, created_at, last_activity
                FROM sessions
                WHERE id = %s
                """,
                (session_id,),
            )
            return cursor.fetchone()


def get_session_id_by_short(short_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM sessions WHERE short_id = %s", (short_id,))
            row = cursor.fetchone()
            return row[0] if row else None


def get_session_data_row(session_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT data FROM sessions WHERE id = %s", (session_id,))
            row = cursor.fetchone()
            return row['data'] if row else {}


def save_session_data_row(session_id, data):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE sessions
                SET data = %s, last_activity = NOW()
                WHERE id = %s
                """,
                (Json(data), session_id),
            )


def generate_session_id():
    return 'session_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:12]


def generate_short_id():
    import random
    import string
    chars = string.ascii_lowercase + string.digits
    while True:
        short_id = ''.join(random.choices(chars, k=8))
        if not short_exists(short_id):
            return short_id


@app.route('/health', methods=['GET'])
def health():
    try:
        ensure_db_initialized()
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        return jsonify({
            'status': 'healthy',
            'service': 'session-service',
            'store_backend': 'postgres'
        }), 200
    except Exception as exc:
        return jsonify({
            'status': 'unhealthy',
            'service': 'session-service',
            'store_backend': 'postgres',
            'error': str(exc)
        }), 500


@app.route('/api/session/create', methods=['POST'])
def create_session():
    ensure_db_initialized()
    session_id = generate_session_id()
    short_id = generate_short_id()

    create_session_record(session_id, short_id)
    app.logger.info(f"Session created: {session_id}, short_id: {short_id}")
    return jsonify({'session_id': session_id, 'short_id': short_id}), 200


@app.route('/api/session/short/<short_id>', methods=['GET'])
def get_session_by_short_id(short_id):
    ensure_db_initialized()
    session_id = get_session_id_by_short(short_id)
    if not session_id:
        return jsonify({'error': 'Short ID not found'}), 404

    if not is_session_valid(session_id):
        return jsonify({'error': 'Session not found'}), 404

    return jsonify({'session_id': session_id, 'short_id': short_id}), 200


@app.route('/api/session/validate', methods=['POST'])
def validate_session():
    ensure_db_initialized()
    data = request.get_json()
    session_id = data.get('session_id') if data else None
    
    if not session_id:
        app.logger.warning("Session validation: no session_id provided")
        return jsonify({'valid': False, 'error': 'Session ID required'}), 400

    if is_session_valid(session_id):
        touch_session(session_id)
        return jsonify({'valid': True}), 200

    app.logger.warning(f"Session validation failed: {session_id}")
    return jsonify({'valid': False, 'error': 'Invalid or expired session'}), 200


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    ensure_db_initialized()
    if is_session_valid(session_id):
        touch_session(session_id)
        session = get_session_row(session_id)
        return jsonify({
            'session_id': session['id'],
            'created_at': session['created_at'].isoformat(),
            'last_activity': session['last_activity'].isoformat()
        }), 200
    return jsonify({'error': 'Session not found or expired'}), 404


@app.route('/api/session/<session_id>/data', methods=['GET'])
def get_session_data(session_id):
    ensure_db_initialized()
    if not is_session_valid(session_id):
        return jsonify({'error': 'Session not found or expired'}), 404
    
    data = get_session_data_row(session_id)
    return jsonify({'data': data}), 200


@app.route('/api/session/<session_id>/data', methods=['POST'])
def save_session_data(session_id):
    ensure_db_initialized()
    if not is_session_valid(session_id):
        return jsonify({'error': 'Session not found or expired'}), 404
    
    data = request.get_json()
    if 'data' not in data:
        return jsonify({'error': 'Data field required'}), 400

    save_session_data_row(session_id, data['data'])
    return jsonify({'success': True}), 200


if __name__ == '__main__':
    ensure_db_initialized()
    app.run(host='0.0.0.0', port=5003, debug=False)

