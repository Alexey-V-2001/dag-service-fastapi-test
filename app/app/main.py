import os
import uvicorn

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import create_tables
# from app.api import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield
    ...

app = FastAPI(
    title="DAG Service API",
    description="API",
    version="0.0.2",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# app.include_router(router, prefix="/api/graph")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": f"Internal Server Error: {str(exc)}"
        }
    )

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("FASTAPI_PORT")),
        reload=True
    )