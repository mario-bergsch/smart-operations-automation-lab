#!/usr/bin/env python3
"""
Hermes API — FastAPI backend for vault operations
Provides: health checks, vault file search, chat logging, git status
"""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from pythonjsonlogger import jsonlogger

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Configuration from environment
VAULT_PATH = Path(os.getenv("VAULT_PATH", "/vault"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
API_KEY = os.getenv("API_KEY", None)  # Optional: None means no auth required
REQUIRE_AUTH = API_KEY is not None

# Prometheus metrics
request_count = Counter('hermes_api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('hermes_api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
vault_operations = Counter('hermes_vault_operations_total', 'Vault operations', ['operation', 'status'])

# Health state
health_status = {
    "status": "initializing",
    "vault_accessible": False,
    "git_accessible": False,
    "last_sync": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info(f"🚀 Hermes API starting. Vault path: {VAULT_PATH}")
    
    # Verify vault accessibility
    if VAULT_PATH.exists():
        health_status["vault_accessible"] = True
        logger.info(f"✅ Vault directory accessible: {VAULT_PATH}")
    else:
        health_status["vault_accessible"] = False
        logger.error(f"❌ Vault directory not found: {VAULT_PATH}")
    
    health_status["status"] = "ready"
    yield
    
    logger.info("🛑 Hermes API shutting down")

# Create FastAPI app
app = FastAPI(
    title="Hermes API",
    description="Backend API for Hermes Vault multi-device access",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key authentication dependency
async def verify_api_key(x_api_key: str = Header(None)):
    """
    Verify API key from X-API-KEY header.
    If REQUIRE_AUTH=False, authentication is optional (dev mode).
    """
    if not REQUIRE_AUTH:
        return None  # Auth disabled

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-KEY header")

    if x_api_key != API_KEY:
        request_count.labels(method="GET", endpoint="/api/*", status=401).inc()
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid API key")

    return x_api_key

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    request_count.labels(method="GET", endpoint="/api/health", status=200).inc()
    return {
        "status": health_status["status"],
        "vault_accessible": health_status["vault_accessible"],
        "git_accessible": health_status["git_accessible"],
        "vault_path": str(VAULT_PATH),
    }

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Vault operations endpoints
@app.get("/api/vault/files")
async def list_vault_files(path: str = "", _: str = Depends(verify_api_key)):
    """List files in vault"""
    try:
        target_path = VAULT_PATH / path if path else VAULT_PATH
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not target_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        files = []
        for item in sorted(target_path.iterdir()):
            if item.is_file() and item.suffix == ".md":
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(VAULT_PATH)),
                    "size": item.stat().st_size,
                    "modified": item.stat().st_mtime,
                })
        
        vault_operations.labels(operation="list_files", status="success").inc()
        request_count.labels(method="GET", endpoint="/api/vault/files", status=200).inc()
        
        return {"path": path, "files": files, "count": len(files)}
    
    except Exception as e:
        vault_operations.labels(operation="list_files", status="error").inc()
        logger.error(f"Error listing vault files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vault/search")
async def search_vault(query: str, _: str = Depends(verify_api_key)):
    """Full-text search in vault"""
    if not query or len(query) < 2:
        raise HTTPException(status_code=400, detail="Query too short (min 2 chars)")
    
    try:
        results = []
        query_lower = query.lower()
        
        for md_file in VAULT_PATH.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                    if query_lower in content.lower():
                        # Find line numbers
                        lines = content.split("\n")
                        matches = [i+1 for i, line in enumerate(lines) if query_lower in line.lower()]
                        
                        results.append({
                            "file": str(md_file.relative_to(VAULT_PATH)),
                            "matches": len(matches),
                            "lines": matches[:5],  # First 5 matches
                            "size": md_file.stat().st_size,
                        })
            except Exception as e:
                logger.warning(f"Error reading file {md_file}: {e}")
        
        vault_operations.labels(operation="search", status="success").inc()
        request_count.labels(method="GET", endpoint="/api/vault/search", status=200).inc()
        
        return {"query": query, "results": results, "count": len(results)}
    
    except Exception as e:
        vault_operations.labels(operation="search", status="error").inc()
        logger.error(f"Error searching vault: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vault/file")
async def read_vault_file(path: str, _: str = Depends(verify_api_key)):
    """Read specific vault file"""
    try:
        file_path = VAULT_PATH / path
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        vault_operations.labels(operation="read_file", status="success").inc()
        request_count.labels(method="GET", endpoint="/api/vault/file", status=200).inc()
        
        return {
            "path": path,
            "size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime,
            "content": content,
        }
    
    except Exception as e:
        vault_operations.labels(operation="read_file", status="error").inc()
        logger.error(f"Error reading vault file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Status endpoint
@app.get("/api/status")
async def vault_status(_: str = Depends(verify_api_key)):
    """Get vault status (git info, sync status)"""
    try:
        import subprocess
        
        # Get git status
        git_status = "unknown"
        git_branch = "unknown"
        git_commit = "unknown"
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=VAULT_PATH,
                capture_output=True,
                text=True,
                timeout=5
            )
            git_status = "clean" if result.returncode == 0 and not result.stdout.strip() else "modified"
            
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=VAULT_PATH,
                capture_output=True,
                text=True,
                timeout=5
            )
            git_branch = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=VAULT_PATH,
                capture_output=True,
                text=True,
                timeout=5
            )
            git_commit = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            health_status["git_accessible"] = True
        except Exception as e:
            logger.warning(f"Could not get git status: {e}")
            health_status["git_accessible"] = False
        
        # Count files
        md_count = len(list(VAULT_PATH.rglob("*.md")))
        total_size = sum(f.stat().st_size for f in VAULT_PATH.rglob("*") if f.is_file())
        
        request_count.labels(method="GET", endpoint="/api/status", status=200).inc()
        
        return {
            "vault_path": str(VAULT_PATH),
            "vault_accessible": health_status["vault_accessible"],
            "git_status": git_status,
            "git_branch": git_branch,
            "git_commit": git_commit,
            "git_accessible": health_status["git_accessible"],
            "file_count": md_count,
            "total_size_bytes": total_size,
        }
    
    except Exception as e:
        logger.error(f"Error getting vault status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    request_count.labels(method="GET", endpoint="/", status=200).inc()
    return {
        "name": "Hermes API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=LOG_LEVEL.lower())
