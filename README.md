# MD2GOST - Markdown to DOCX Converter

A microservices-based web application for converting Markdown files to GOST-compliant DOCX documents.

## Architecture

The application consists of multiple services:

- **Gateway (Nginx)**: API Gateway routing requests (Port 80)
- **Frontend (React)**: Modern web interface for Markdown editing (Port 3000, internal)
- **API Service (Python Flask)**: Orchestration service handling business logic (Port 5001, internal)
- **DOCX Service (Python Flask)**: Core conversion service (Port 5000, internal)
- **File Service (Python Flask)**: Image upload/retrieval (Port 5002, internal)
- **Session Service (Python Flask)**: Session lifecycle and metadata (Port 5003, internal)
- **PostgreSQL**: Persistent session storage
- **S3-compatible storage (MinIO by default)**: Persistent image/object storage

```
Browser → Nginx Gateway → Frontend / API → (DOCX, File, Session) → (PostgreSQL, S3/MinIO)
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
docker compose up --build
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

Use `.env` file in the repository root. For production deployment:

1. Copy template:
```bash
cp .env.production.example .env
```
2. Fill required values (at minimum `DATABASE_URL` and `S3_*`).
3. Start stack:
```bash
docker compose up -d --build
```
4. Check health:
```bash
curl http://<your-host>:${GATEWAY_PORT:-80}/api/health
```

Main variables:

- `GATEWAY_PORT` - external HTTP port for Nginx (default: `80`)
- `DOCX_SERVICE_URL` - URL for docx-service inside Docker network
- `FILE_SERVICE_URL` - URL for file-service inside Docker network
- `SESSION_SERVICE_URL` - URL for session-service inside Docker network
- `SESSION_STORE_BACKEND` - session store backend: `postgres` (default)
- `STORAGE_BACKEND` - file storage backend: `s3` or `local` (default: `s3`)
- `DATABASE_URL` - PostgreSQL DSN (default in compose: `postgresql://md2gost:md2gost@postgres:5432/md2gost`)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - used by bundled `postgres` container
- `TEMPLATE_PATH` - path to DOCX template in `docx-service` (default: `/app/md2gost/Template.docx`)
- `WORKING_DIR` - temporary conversion directory in `docx-service` (default: `/tmp/md2gost`)
- `SESSIONS_STORAGE_BASE` - local fallback path used when `STORAGE_BACKEND=local`

Infrastructure variables (passed to services via environment):

- `S3_ENDPOINT`, `S3_REGION`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_USE_SSL`

### Production Notes

- `docker-compose.yml` no longer depends on local bind-mounts like `./setup.py:/app/setup.py:ro`, so it can run on VPS from a clean checkout.
- Session state is persisted in PostgreSQL (no auto-expiration), and uploaded images are stored in S3-compatible object storage.
- `docx-service` downloads session images through `file-service` API, so conversion does not require shared local volumes.
- For first deployment run `docker compose up -d --build`.
- For updates run `docker compose pull` (if using prebuilt images) or `docker compose up -d --build`.

## Troubleshooting

### Services not starting

1. Check Docker logs:
```bash
docker compose logs [service-name]
```

2. Verify ports are not in use:
```bash
lsof -i :80 -i :5000 -i :5001 -i :3000
```

3. Rebuild services:
```bash
docker compose up --build --force-recreate
```

### Preview not working

1. Check DOCX service logs:
```bash
docker compose logs docx-service
```

2. Verify DOCX service is accessible:
```bash
curl http://localhost:5000/health
```

### Frontend not loading

1. Check frontend build:
```bash
docker compose logs frontend
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
