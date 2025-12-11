# Frontend

Modern, minimalistic React frontend for MD2GOST Markdown to DOCX converter.

## Description

This is a React application that provides:
- CodeMirror-based Markdown editor
- Real-time DOCX preview (debounced)
- Download DOCX functionality
- Syntax highlighting toggle
- Minimalistic, modern design
- Responsive layout

## Features

- **Markdown Editor**: CodeMirror editor with syntax highlighting
- **Live Preview**: Real-time preview of generated DOCX (converted to HTML)
- **Download**: Download generated DOCX files
- **Syntax Highlighting**: Toggle syntax highlighting for code blocks

## Running Locally

```bash
npm install
npm start
```

The app will be available at `http://localhost:3000`.

## Building for Production

```bash
npm run build
```

## Building Docker Image

```bash
docker build -t frontend .
```

## Running in Docker

```bash
docker run -p 3000:3000 frontend
```

## API Integration

The frontend communicates with the API service through:
- `/api/preview` - Get HTML preview
- `/api/convert` - Download DOCX file

These endpoints are proxied through Nginx to the ASP.NET API service.

