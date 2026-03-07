import io
import mimetypes
import os
import uuid

import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

STORAGE_BASE = os.getenv('STORAGE_BASE', '/tmp/md2gost/sessions')
STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 's3').lower()
S3_ENDPOINT = os.getenv('S3_ENDPOINT', 'http://minio:9000')
S3_REGION = os.getenv('S3_REGION', 'us-east-1')
S3_BUCKET = os.getenv('S3_BUCKET', 'md2gost-sessions')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', 'minioadmin')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', 'minioadmin')
S3_USE_SSL = os.getenv('S3_USE_SSL', '0') == '1'

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}


def allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        region_name=S3_REGION,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        use_ssl=S3_USE_SSL
    )


def ensure_bucket_exists():
    if STORAGE_BACKEND != 's3':
        return

    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
    except ClientError as exc:
        status_code = exc.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if status_code not in (404, 400):
            raise
        if S3_REGION == 'us-east-1':
            s3.create_bucket(Bucket=S3_BUCKET)
        else:
            s3.create_bucket(
                Bucket=S3_BUCKET,
                CreateBucketConfiguration={'LocationConstraint': S3_REGION}
            )


def build_object_key(session_id, filename):
    return f"{session_id}/images/{filename}"


@app.route('/health', methods=['GET'])
def health():
    try:
        if STORAGE_BACKEND == 's3':
            ensure_bucket_exists()
        return jsonify({
            'status': 'healthy',
            'service': 'file-service',
            'storage_backend': STORAGE_BACKEND
        }), 200
    except Exception as exc:
        return jsonify({
            'status': 'unhealthy',
            'service': 'file-service',
            'storage_backend': STORAGE_BACKEND,
            'error': str(exc)
        }), 500


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

    if STORAGE_BACKEND == 's3':
        s3 = get_s3_client()
        ensure_bucket_exists()
        key = build_object_key(session_id, filename)
        content_type = file.content_type or mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        s3.upload_fileobj(
            file.stream,
            S3_BUCKET,
            key,
            ExtraArgs={'ContentType': content_type}
        )
    else:
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

    if STORAGE_BACKEND == 's3':
        s3 = get_s3_client()
        key = build_object_key(session_id, filename)
        try:
            obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        except ClientError:
            return jsonify({'error': 'Image not found'}), 404

        file_content = obj['Body'].read()
        mimetype = obj.get('ContentType') or mimetypes.guess_type(filename)[0] or 'image/png'
        return send_file(io.BytesIO(file_content), mimetype=mimetype)

    filepath = os.path.join(STORAGE_BASE, session_id, 'images', filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Image not found'}), 404

    mimetype, _ = mimetypes.guess_type(filepath)
    if not mimetype:
        mimetype = 'image/png'

    return send_file(filepath, mimetype=mimetype)


@app.route('/api/session/<session_id>/images', methods=['GET'])
def list_images(session_id):
    if STORAGE_BACKEND == 's3':
        s3 = get_s3_client()
        prefix = f"{session_id}/images/"
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        images = []
        for obj in response.get('Contents', []):
            key = obj.get('Key', '')
            filename = key.split('/')[-1]
            if filename:
                images.append({
                    'filename': filename,
                    'url': f'/api/images/{session_id}/{filename}'
                })
        return jsonify({'images': images}), 200

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
    if STORAGE_BACKEND == 's3':
        ensure_bucket_exists()
    else:
        os.makedirs(STORAGE_BASE, exist_ok=True)
    app.run(host='0.0.0.0', port=5002, debug=False)

