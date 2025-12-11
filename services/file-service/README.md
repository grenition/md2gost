# File Service

Flask service for handling image uploads and storage with session-based organization.

## Description

This service handles:
- Image uploads with session-based storage
- Image retrieval by session ID and filename
- Session image listing

## API Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "file-service"
}
```

### POST /api/images/upload

Upload an image file.

**Headers:**
- `X-Session-Id`: Session identifier (required)

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response:**
```json
{
  "filename": "a1b2c3d4.png",
  "url": "/api/images/{session_id}/a1b2c3d4.png"
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

### GET /api/images/{session_id}/{filename}

Retrieve an image file.

**Response:**
- Content-Type: `image/*`
- Binary image data

**Error Response:**
```json
{
  "error": "Image not found"
}
```

### GET /api/session/{session_id}/images

List all images for a session.

**Response:**
```json
{
  "images": [
    {
      "filename": "a1b2c3d4.png",
      "url": "/api/images/{session_id}/a1b2c3d4.png"
    }
  ]
}
```

## Configuration

The service is configured via environment variables:

- `STORAGE_BASE`: Base directory for session storage (default: `/tmp/md2gost/sessions`)

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

## Building Docker Image

```bash
docker build -t file-service .
```

## Running in Docker

```bash
docker run -p 5002:5002 file-service
```

