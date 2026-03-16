# Async Production-Ready API (FastAPI + pgvector)

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-316192?style=flat-square&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

## Deskripsi Singkat
Proyek ini adalah REST API *production-ready* berarsitektur *fully asynchronous* yang dirancang untuk skalabilitas dan keamanan tinggi. API ini mendukung kemampuan penyimpanan memori AI tingkat lanjut menggunakan PostgreSQL dan ekstensi pgvector. 

Fitur utama meliputi:
- **Vector semantic search**: Pencarian nalar semantik (optimal untuk AI/RAG dengan penyimpanan *embedding* 768 dimensi).
- **General purpose CRUD**: Skema operasional dinamis dengan *payload* JSONB yang terindeksasi.
- **Fully async architecture**: Dibangun di atas fondasi non-blocking murni menggunakan SQLAlchemy 2.0 Async, framework FastAPI, dan driver spesifik `asyncpg` untuk asinkronisasi tingkat tinggi.
- **Secure by default**: Proteksi ketat meliputi lapisan otentikasi API Key, pembatasan dinamis *rate limiting*, keamanan CORS terotonomisasi, filter IP berlapis, serta sanitasi *stack trace* internal agar tidak membocorkan logika program di ranah publik.

## Tech Stack

| Technology | Version | Keterangan |
|---|---|---|
| **Python** | 3.12+ | Ekosistem sistem komputasi dan manajemen fungsional *backend*. |
| **FastAPI** | Latest | Basis integrasi asinkron server modern. |
| **PostgreSQL** | 16 | Lapisan utama database berformat Object-Relational ACID. |
| **pgvector** | Latest | Komputasi ekstensi native untuk kapabilitas kalkulasi *cosine similarity*. |
| **SQLAlchemy** | 2.0 | Pengendalian query-builders deklaratif. |
| **asyncpg** | Latest | Implementasi spesifik driver PostgreSQL tercepat tanpa C-bindings I/O blok. |
| **Alembic** | Latest | Sistem engine integrasi versi skema database (Migrations). |
| **Pydantic** | V2 | Deklarasi validasi asertif struktur *request/response* tipe statik. |
| **slowapi** | Latest | Penjaga gerbang penolakan laju trafik berbahaya berbasis IP client. |
| **Docker** | Latest | Standardisasi multi-stage microservices yang aman lintas sistem operasi lintas kluster. |
| **Pytest** | Latest | Automasi instrumentasi QA fungsionalitas (*Pytest-asyncio*). |

## Arsitektur Proyek

Berikut adalah hierarki aplikasi utama dalam ekosistem *backend*:

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

## Cara Instalasi & Menjalankan (Docker — Recommended)

Sistem telah dilengkapi dengan integrasi Docker otomatisasi *healthcheck* database serta proteksi container.

```bash
# 1. Clone repo
git clone <repo-url>
cd pgvector

# 2. Setup environment
cp .env.example .env
# Edit .env sesuai kebutuhan

# 3. Build dan jalankan
make build
make up

# 4. Jalankan migrasi database
make migrate

# 5. Cek status
docker ps
```

## Cara Menjalankan Tanpa Docker (Local Development)

Bila Anda ingin mengembangkan aplikasi ini tanpa *container* pada ekosistem *host* secara langsung:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Pastikan PostgreSQL + pgvector sudah running
alembic upgrade head
uvicorn app.main:app --reload
```

## Environment Variables

Salin `.env.example` ke `.env` dan perbarui parameter kredensial Anda.

| Variable | Contoh | Keterangan |
|---|---|---|
| DB_HOST | db | Nama service docker-compose. |
| DB_PORT | 5432 | Port PostgreSQL database default. |
| DB_NAME | pgvector_db | Terminologi basis data. |
| DB_USER | postgres | Akses super-otoritatif user instance. |
| DB_PASSWORD | your_secure_password_here | Rahasia kunci proteksi utama akses skema. |
| API_KEY | your_api_key_here | Kunci token perlindungan akses endpoint WRITE. |
| ALLOWED_ORIGINS | https://yourdomain.com | Daftar domain putih (*whitelist*) koneksi lintas-*origin* (*CORS*). |

> **Catatan Penting**: DB_HOST harus diisi `db` saat menggunakan Docker, dan `localhost` saat development lokal.

## API Documentation

Dokumentasi parameter API interaktif standar otomatis (Swagger UI) dapat disimulasi melalui:  
**http://localhost:8000/docs**

### Endpoint Summary

| Method | Endpoint | Auth | Rate Limit | Deskripsi |
|---|---|---|---|---|
| POST | /api/v1/memories/ | ✅ API Key | 30/min | Ingest vector memory |
| POST | /api/v1/memories/search | ❌ Public | 60/min | Semantic search |
| POST | /api/v1/data/ | ✅ API Key | 30/min | Create data |
| GET | /api/v1/data/ | ❌ Public | - | List data (pagination) |
| GET | /api/v1/data/{id} | ❌ Public | - | Get single data |
| PUT | /api/v1/data/{id} | ✅ API Key | 30/min | Update data |
| DELETE | /api/v1/data/{id} | ✅ API Key | 30/min | Delete data |

### Contoh Request

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

Manajemen kluster telah diabstraksi menggunakan perintah pintasan *Make*.

| Command | Deskripsi |
|---|---|
| make build | Build Docker image |
| make up | Jalankan semua container |
| make down | Hentikan semua container |
| make logs | Lihat log API container |
| make migrate | Jalankan Alembic migration |
| make test | Jalankan test suite |

## Testing

Arsitektur aplikasi tercover oleh utilitas integrasi QA mendalam. 

```bash
# Jalankan semua tests
.venv/bin/pytest tests/ -v

# Hasil: 48 passed, 0 warnings
```

Distribusi spesifikasi testing secara konseptual (100% test coverage operasional):
- test_data.py — 15 tests (CRUD endpoints)
- test_vector.py — 8 tests (vector ingest & search)
- test_security.py — 4 tests (API Key & stack trace)
- test_database.py — 21 tests (koneksi, schema, transaksi, concurrency)

## Security Features

Tingkat keamanan diisolasi secara sistematis:
- API Key authentication (proteksi mutlak modifikasi POST, PUT, DELETE).
- Rate limiting per IP (mitigasi abuse *compute* mesin algoritma pencarian & kluster query SQL).
- CORS restricted via env var (keamanan identitas domain).
- No stack trace exposure (intercept Exception lokal HTTP 500 error sanitization).
- Non-root Docker user (restriksi keamanan sistem virtualisasi UID host OS).
- Environment variables (tidak ada hardcoded credentials).

## Troubleshooting

Panduan cepat meresolusikan tantangan pengembangan maupun produksi operasional saat server online:

| Error | Penyebab | Solusi |
|---|---|---|
| `failed to resolve host 'db'` | DB_HOST salah | Pastikan DB_HOST=db di .env |
| `address already in use :5432` | PostgreSQL lokal jalan | `sudo systemctl stop postgresql` |
| `address already in use :8000` | uvicorn dev server jalan | `pkill -f uvicorn` |
| `permission denied docker.sock` | User belum di group docker | `sudo usermod -aG docker $USER && newgrp docker` |
