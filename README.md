# FastAPI - pgvector (Multi-Purpose API)

Ini adalah sebuah REST API serbaguna yang dibangun menggunakan **FastAPI**. Aplikasi ini berfungsi sebagai backend terpusat untuk database **PostgreSQL**, yang menangani:
1. **General Relational Database** (CRUD data pengguna/sensor biasa).
2. **Vector Database / RAG System** (Semantic Search menggunakan `pgvector`).

## Struktur Folder

```text
pgvector/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── data.py        # Endpoint /api/data (Relasional CRUD)
│   │   └── vector.py      # Endpoint /api/vector (Vector & AI)
│   ├── __init__.py
│   ├── config.py          # Validasi .env dan konfigurasi database
│   ├── database.py        # Setup koneksi SQLAlchemy dan inisialiasi DB
│   ├── main.py            # Entry point FastAPI, CORS, dan register routers
│   ├── models.py          # Skema tabel database SQLAlchemy
│   └── schemas.py         # Skema referensi Pydantic V2
├── .env                   # Kredensial Database
├── requirements.txt       # Dependencies Python
└── README.md              # File instruksi ini
```

## Persyaratan
- Python 3.9+
- PostgreSQL dengan ekstensi `pgvector` terinstal. 

## Cara Menjalankan Aplikasi

1. **Aktifkan Virtual Environment** (Jika belum):
   ```bash
   source .venv/bin/activate
   ```

2. **Instal Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi Database**:
   Buka file `.env` di root project dan sesuaikan dengan kredensial PostgreSQL Anda:
   ```env
   DB_USER=postgres
   DB_PASS=secretpassword
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=postgredb_name
   ```
   > **Penting**: Pastikan user PostgreSQL Anda merupakan *superuser* atau minimal memiliki hak akses untuk menjalankan `CREATE EXTENSION vector`.

4. **Jalankan Uvicorn Server**:
   Jalankan perintah berikut di root folder `pgvector`:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Akses Dokumentasi API**:
   Buka browser dan akses Swagger UI API Anda:
   - [http://localhost:8000/docs](http://localhost:8000/docs)

## Fitur dan Endpoint:

- **Router Vector (`/api/vector`)**
  - `POST /api/vector/tambah`: Menambahkan rekaman vektor baru (dimensi: 768).
  - `POST /api/vector/cari`: Mencari teks/vektor terdekat menggunakan operator *L2 distance* (`<->`).
  
- **Router General (`/api/data`)**
  - `GET /api/data/`: Mengambil data list (mendukung pagination).
  - `GET /api/data/{id}`: Mengambil data tunggal.
  - `POST /api/data/`: Membuat data baru.
  - `PUT /api/data/{id}`: Memperbarui data yang ada.
  - `DELETE /api/data/{id}`: Menghapus data dengan ID.

Aplikasi telah terkonfigurasi untuk membolehkan akses CORS penuh (`allow_origins=["*"]`) dari *tunneling services*.
