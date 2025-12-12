# API Service (Python)

Flask service for orchestrating requests to internal services.

## Description

This service acts as an orchestration layer that:
- Validates sessions before processing requests
- Routes requests to appropriate internal services (docx-service, file-service)
- Provides a unified API interface for the frontend

## Architecture

- **Internal Services** (not exposed via gateway):
  - `docx-service`: DOCX conversion
  - `file-service`: File storage
  
- **External Services** (exposed via gateway):
  - `session-service`: Session management
  - `api-service`: This service (orchestration)

## API Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "api-service"
}
```

### POST /api/convert

Convert Markdown to DOCX.

**Request:**
```json
{
  "markdown": "# Hello World",
  "syntax_highlighting": true,
  "session_id": "session_20231211_123456_abc123"
}
```

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Binary DOCX file

### POST /api/preview

Generate PDF preview of Markdown.

**Request:**
```json
{
  "markdown": "# Hello World",
  "syntax_highlighting": true,
  "session_id": "session_20231211_123456_abc123"
}
```

**Response:**
```json
{
  "pdf": "base64_encoded_pdf_data"
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

### GET /api/images/{session_id}/{filename}

Retrieve an image file.

**Response:**
- Content-Type: `image/*`
- Binary image data

### POST /api/session/create

Create a new session (proxies to session-service).

**Response:**
```json
{
  "session_id": "session_20231211_123456_abc123"
}
```

## Configuration

The service is configured via environment variables:

- `DOCX_SERVICE_URL`: URL of the docx-service (default: `http://docx-service:5000`)
- `FILE_SERVICE_URL`: URL of the file-service (default: `http://file-service:5002`)
- `SESSION_SERVICE_URL`: URL of the session-service (default: `http://session-service:5003`)

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

## Building Docker Image

```bash
docker build -t api-service .
```

## Running in Docker

```bash
docker run -p 5001:5001 api-service
```

