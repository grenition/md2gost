# API Service

ASP.NET Core orchestration service that coordinates between the frontend and the Python DOCX service.

## Description

This service acts as an API gateway/orchestrator:
- Receives requests from the frontend
- Proxies requests to the Python DOCX service
- Handles errors and timeouts
- Returns appropriate HTTP responses

## API Endpoints

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "api-service"
}
```

### POST /api/convert

Converts Markdown content to DOCX file. Proxies to Python DOCX service.

**Request Body:**
```json
{
  "markdown": "# Example\n\nThis is markdown content.",
  "syntaxHighlighting": true
}
```

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Binary DOCX file

**Error Response:**
```json
{
  "error": "Error message"
}
```

### POST /api/preview

Converts Markdown content to HTML preview. Proxies to Python DOCX service.

**Request Body:**
```json
{
  "markdown": "# Example\n\nThis is markdown content.",
  "syntaxHighlighting": true
}
```

**Response:**
```json
{
  "html": "<html>...</html>"
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

## Configuration

The service is configured via `appsettings.json`:

```json
{
  "DocxService": {
    "Url": "http://docx-service:5000"
  }
}
```

## Running Locally

```bash
dotnet restore
dotnet run
```

## Building Docker Image

```bash
docker build -t api-service .
```

## Running in Docker

```bash
docker run -p 5001:5001 api-service
```

