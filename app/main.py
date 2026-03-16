import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.routers import vector, data
from app.config import settings
from app.database import init_db
from app.dependencies import limiter

# 1. Setup Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("fastapi_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application and initializing database...")
    await init_db()
    yield
    logger.info("Application shutdown complete.")

app = FastAPI(
    title="Async Production-Ready API (FastAPI + pgvector)",
    description="A highly scalable, fully asynchronous REST API handling General CRUD and Vector Database (RAG) operations natively, protected by API Keys and Rate Limiting.",
    version="2.0.0",
    lifespan=lifespan
)

# 2. CORS Configuration mapping to allowed origins from .env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. SlowAPI Rate Limiting Setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 4. Global Exception Handler (To prevent raw stack traces from leaking)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

# 5. Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Completed request: {request.method} {request.url.path} with status {response.status_code}")
    return response

# 6. Include versioned routers
app.include_router(vector.router)
app.include_router(data.router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Async Production-Ready API.",
        "version": "v1",
        "documentation": "/docs"
    }
