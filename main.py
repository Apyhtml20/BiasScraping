from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.audit_router import router


app = FastAPI(
    title="AI for Inclusion API",
    description=(
        "Web scraping and AI-powered inclusion "
        "and bias detection auditor."
    ),
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    router,
    prefix="/api"
)


@app.get("/")
async def root():
    return {
        "message": "AI for Inclusion API is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }