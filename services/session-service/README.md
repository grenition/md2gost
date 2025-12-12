# Session Service

Flask service for managing user sessions.

## Description

This service handles:
- Session creation
- Session validation
- Session information retrieval

## API Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "session-service"
}
```

### POST /api/session/create

Create a new session.

**Response:**
```json
{
  "session_id": "session_20231211_123456_abc123def456"
}
```

### POST /api/session/validate

Validate a session.

**Request:**
```json
{
  "session_id": "session_20231211_123456_abc123def456"
}
```

**Response:**
```json
{
  "valid": true
}
```

**Error Response:**
```json
{
  "valid": false,
  "error": "Invalid or expired session"
}
```

### GET /api/session/{session_id}

Get session information.

**Response:**
```json
{
  "session_id": "session_20231211_123456_abc123def456",
  "created_at": "2023-12-11T12:34:56",
  "last_activity": "2023-12-11T13:45:00"
}
```

**Error Response:**
```json
{
  "error": "Session not found or expired"
}
```

## Configuration

Sessions expire after 24 hours of inactivity.

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

## Building Docker Image

```bash
docker build -t session-service .
```

## Running in Docker

```bash
docker run -p 5003:5003 session-service
```

