# MD2GOST - Markdown to DOCX Converter

A microservices-based web application for converting Markdown files to GOST-compliant DOCX documents.

## Architecture

The application consists of four main services:

- **Gateway (Nginx)**: API Gateway routing requests (Port 80)
- **Frontend (React)**: Modern web interface for Markdown editing (Port 3000, internal)
- **API Service (ASP.NET Core)**: Orchestration service handling business logic (Port 5001, internal)
- **DOCX Service (Python Flask)**: Core conversion service (Port 5000, internal)

```
Browser → Nginx Gateway → React Frontend / ASP.NET API → Python DOCX Service
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)

### Running the Application

1. Clone the repository:
```bash
git clone <repository-url>
cd md2gost
```

2. Start all services:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend & API Gateway: http://localhost (port 80)
- Internal services (not exposed externally):
  - DOCX Service: port 5000 (internal only)
  - API Service: port 5001 (internal only)
  - Frontend: port 3000 (internal only)

### Testing Services

Run the test script to verify all services are working:
```bash
./test-services.sh
```

Or test manually:
```bash
# Test through Gateway (recommended)
curl http://localhost/api/health

# Test Frontend
curl http://localhost/
```

## Services Documentation

### DOCX Service

Python Flask service for Markdown to DOCX conversion.

- **Location**: `services/docx-service/`
- **Port**: 5000
- **Documentation**: [services/docx-service/README.md](services/docx-service/README.md)

**Endpoints**:
- `GET /health` - Health check
- `POST /api/convert` - Convert Markdown to DOCX
- `POST /api/preview` - Convert Markdown to HTML preview

### API Service

ASP.NET Core orchestration service.

- **Location**: `services/api-service/`
- **Port**: 5001
- **Documentation**: [services/api-service/README.md](services/api-service/README.md)

**Endpoints**:
- `GET /api/health` - Health check
- `POST /api/convert` - Proxy to DOCX service
- `POST /api/preview` - Proxy to DOCX service

### Frontend

React-based web interface.

- **Location**: `services/frontend/`
- **Port**: 3000 (internal)
- **Documentation**: [services/frontend/README.md](services/frontend/README.md)

**Features**:
- Markdown editor
- Real-time DOCX preview
- Download DOCX functionality
- Syntax highlighting toggle

### Gateway

Nginx API Gateway for routing.

- **Location**: `gateway/`
- **Port**: 80
- **Routing**:
  - `/api/*` → ASP.NET API Service
  - `/*` → React Frontend

## Development

### Running Services Individually

#### DOCX Service
```bash
cd services/docx-service
pip install -r requirements.txt
python app.py
```

#### API Service
```bash
cd services/api-service
dotnet restore
dotnet run
```

#### Frontend
```bash
cd services/frontend
npm install
npm start
```

## Project Structure

```
md2gost/
├── services/
│   ├── docx-service/      # Python Flask conversion service
│   ├── api-service/        # ASP.NET Core orchestration service
│   └── frontend/           # React frontend application
├── gateway/                 # Nginx API Gateway
├── md2gost/                # Core conversion library
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # This file
```

## Configuration

### Environment Variables

#### DOCX Service
- `TEMPLATE_PATH` - Path to Template.docx (default: `/app/md2gost/Template.docx`)
- `WORKING_DIR` - Working directory for temp files (default: `/tmp/md2gost`)

#### API Service
- `DocxService__Url` - URL of DOCX service (default: `http://docx-service:5000`)

## Troubleshooting

### Services not starting

1. Check Docker logs:
```bash
docker-compose logs [service-name]
```

2. Verify ports are not in use:
```bash
lsof -i :80 -i :5000 -i :5001 -i :3000
```

3. Rebuild services:
```bash
docker-compose up --build --force-recreate
```

### Preview not working

1. Check DOCX service logs:
```bash
docker-compose logs docx-service
```

2. Verify DOCX service is accessible:
```bash
curl http://localhost:5000/health
```

### Frontend not loading

1. Check frontend build:
```bash
docker-compose logs frontend
```

2. Verify gateway routing:
```bash
curl http://localhost/
```

## License

See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
