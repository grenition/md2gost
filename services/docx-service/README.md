# DOCX Service

Python Flask service for converting Markdown to DOCX and DOCX to HTML.

## Description

This service handles the core conversion functionality:
- Converts Markdown content to DOCX format (GOST compliant)
- Converts DOCX to HTML for preview purposes
- Uses the md2gost library for conversion

## API Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "docx-service"
}
```

### POST /api/convert

Converts Markdown content to DOCX file.

**Request Body:**
```json
{
  "markdown": "# Example\n\nThis is markdown content.",
  "syntax_highlighting": true
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

Converts Markdown content to HTML preview.

**Request Body:**
```json
{
  "markdown": "# Example\n\nThis is markdown content.",
  "syntax_highlighting": true
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
  "error": "Error message",
  "traceback": "..."
}
```

## Environment Variables

- `TEMPLATE_PATH` - Path to Template.docx file (default: `/app/md2gost/Template.docx`)
- `WORKING_DIR` - Working directory for temporary files (default: `/tmp/md2gost`)

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

## Building Docker Image

```bash
docker build -t docx-service .
```

## Running in Docker

```bash
docker run -p 5000:5000 docx-service
```

