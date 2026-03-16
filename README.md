🌐 **Language:** English | [Indonesia](README.id.md)

# Async Production-Ready API (FastAPI + pgvector)

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-316192?style=flat-square&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

## Short Description
This project is a production-ready REST API with a fully asynchronous architecture designed for high scalability and security. This API supports advanced AI memory storage capabilities using PostgreSQL and the pgvector extension.

Main features include:
- **Vector semantic search**: Semantic reasoning search (optimized for AI/RAG with 768-dimension embedding storage).
- **General purpose CRUD**: Dynamic operational schema with indexed JSONB payload.
- **Fully async architecture**: Built on a pure non-blocking foundation using SQLAlchemy 2.0 Async, the FastAPI framework, and the specific `asyncpg` driver for high-level synchronization.
- **Secure by default**: Strict protection including an API Key authentication layer, dynamic rate limiting, autonomous CORS security, layered IP filtering, and internal stack trace sanitization to avoid leaking program logic to the public domain.

## Tech Stack

| Technology | Version | Description |
|---|---|---|
| **Python** | 3.12+ | Ecosystem for backend computing and functional management. |
| **FastAPI** | Latest | Foundation for modern asynchronous server integration. |
| **PostgreSQL** | 16 | Primary database layer in Object-Relational ACID format. |
| **pgvector** | Latest | Native extension computation for cosine similarity calculation capabilities. |
| **SQLAlchemy** | 2.0 | Declarative query-builders controller. |
| **asyncpg** | Latest | Specific implementation of the fastest PostgreSQL driver without blocking I/O C-bindings. |
| **Alembic** | Latest | Database schema engine integration system (Migrations). |
| **Pydantic** | V2 | Assertive validation declarations for statically typed request/response structures. |
| **slowapi** | Latest | Gatekeeper for rejecting malicious traffic rates based on client IP. |
| **Docker** | Latest | Multi-stage microservices standardization that is secure across operating systems and clusters. |
| **Pytest** | Latest | Automation of QA functionality instrumentation (*Pytest-asyncio*). |

## Project Architecture

Below is the main application hierarchy within the backend ecosystem:

```
pgvector/
├── app/
│   ├── main.py          # Entry point, CORS, lifespan
│   ├── config.py        # Pydantic settings, env vars
│   ├── database.py      # Async engine, init_db, get_db
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic V2 schemas
│   ├── dependencies.py  # API Key, rate limiter
│   └── routers/
│       ├── vector.py    # /api/v1/memories endpoints
│       └── data.py      # /api/v1/data endpoints
├── alembic/             # Database migrations
├── tests/               # 48 tests, 0 warnings
├── Dockerfile           # Multi-stage build
├── docker-compose.yml   # API + pgvector DB
├── Makefile             # Shortcuts
└── .env.example         # Template environment
```

## Prerequisites
- **Docker** & **docker-compose**
- **Git**

## Installation & Running (Docker — Recommended)

The system is equipped with Docker integration, including automated database health checks and container protection.

```bash
# 1. Clone repo
git clone <repo-url>
cd pgvector

# 2. Setup environment
cp .env.example .env
# Edit .env according to your needs

# 3. Build and run
make build
make up

# 4. Run database migrations
make migrate

# 5. Check status
docker ps
```

## Running Without Docker (Local Development)

If you prefer to develop this application without containers on the host ecosystem directly:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Ensure PostgreSQL + pgvector is already running
alembic upgrade head
uvicorn app.main:app --reload
```

## Environment Variables

Copy `.env.example` to `.env` and update your credential parameters.

| Variable | Example | Description |
|---|---|---|
| DB_HOST | db | docker-compose service name. |
| DB_PORT | 5432 | Default PostgreSQL database port. |
| DB_NAME | pgvector_db | Database terminology. |
| DB_USER | postgres | Super-authoritative user instance access. |
| DB_PASSWORD | your_secure_password_here | Main protection secret key for schema access. |
| API_KEY | your_api_key_here | Token key for WRITE endpoint access protection. |
| ALLOWED_ORIGINS | https://yourdomain.com | Whitelist of domains for cross-origin connections (CORS). |

> **Important Note**: DB_HOST must be filled with `db` when using Docker, and `localhost` during local development.

## API Documentation

Interactive, auto-generated standard API parameter documentation (Swagger UI) can be simulated via:  
**http://localhost:8000/docs**

### Endpoint Summary

| Method | Endpoint | Auth | Rate Limit | Description |
|---|---|---|---|---|
| POST | /api/v1/memories/ | ✅ API Key | 30/min | Ingest vector memory |
| POST | /api/v1/memories/search | ❌ Public | 60/min | Semantic search |
| POST | /api/v1/data/ | ✅ API Key | 30/min | Create data |
| GET | /api/v1/data/ | ❌ Public | - | List data (pagination) |
| GET | /api/v1/data/{id} | ❌ Public | - | Get single data |
| PUT | /api/v1/data/{id} | ✅ API Key | 30/min | Update data |
| DELETE | /api/v1/data/{id} | ✅ API Key | 30/min | Delete data |

### Example Requests

- POST `/api/v1/memories/` (Create Memory)
  ```bash
  curl -X POST "http://localhost:8000/api/v1/memories/" \
       -H "x-api-key: your_api_key_here" \
       -H "Content-Type: application/json" \
       -d '{
         "persona_id": "ai_assistant_01",
         "content": "This is a memory about how to build a FastAPI app.",
         "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8] # <-- 768-D array length limit actual
       }'
  ```

- POST `/api/v1/memories/search` (Semantic Search Query)
  ```bash
  curl -X POST "http://localhost:8000/api/v1/memories/search" \
       -H "Content-Type: application/json" \
       -d '{
         "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
         "persona_id": "ai_assistant_01",
         "limit": 5
       }'
  ```

- POST `/api/v1/data/` (Insert JSONB Metadata)
  ```bash
  curl -X POST "http://localhost:8000/api/v1/data/" \
       -H "x-api-key: your_api_key_here" \
       -H "Content-Type: application/json" \
       -d '{
         "title": "Application Configuration",
         "description": "General settings payload",
         "payload": {"theme": "dark", "notifications": true}
       }'
  ```

- GET `/api/v1/data/` (Retrieve Pagination Records)
  ```bash
  curl -X GET "http://localhost:8000/api/v1/data/?skip=0&limit=10" \
       -H "accept: application/json"
  ```

## Makefile Commands

Cluster management has been abstracted using Make shortcut commands.

| Command | Description |
|---|---|
| make build | Build Docker image |
| make up | Run all containers |
| make down | Stop all containers |
| make logs | View API container logs |
| make migrate | Run Alembic migration |
| make test | Run test suite |

## Testing

The application architecture is covered by an in-depth QA integration utility. 

```bash
# Run all tests
.venv/bin/pytest tests/ -v

# Results: 48 passed, 0 warnings
```

Conceptual distribution of testing specifications (100% operational test coverage):
- test_data.py — 15 tests (CRUD endpoints)
- test_vector.py — 8 tests (vector ingest & search)
- test_security.py — 4 tests (API Key & stack trace)
- test_database.py — 21 tests (connection, schema, transaction, concurrency)

## Security Features

Security levels are systematically isolated:
- API Key authentication (absolute protection for POST, PUT, DELETE modifications).
- Rate limiting per IP (mitigates compute abuse of the search algorithm & SQL query cluster).
- CORS restricted via env var (domain identity security).
- No stack trace exposure (intercepts local Exceptions with HTTP 500 error sanitization).
- Non-root Docker user (OS host UID virtualization security restriction).
- Environment variables (no hardcoded credentials).

## Troubleshooting

A quick guide to resolving operational or development challenges when the server is online:

| Error | Cause | Solution |
|---|---|---|
| `failed to resolve host 'db'` | Incorrect DB_HOST | Ensure DB_HOST=db in .env |
| `address already in use :5432` | Local PostgreSQL is running | `sudo systemctl stop postgresql` |
| `address already in use :8000` | uvicorn dev server is running | `pkill -f uvicorn` |
| `permission denied docker.sock` | User not in docker group | `sudo usermod -aG docker $USER && newgrp docker` |
