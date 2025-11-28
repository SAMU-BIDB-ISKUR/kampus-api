from fastapi import FastAPI
from app.config.database import create_tables
from app.campus.controller.campus_controller import router as campus_router

app = FastAPI(
    title="Üniversite Kampüs API",
    description="Üniversite kampüslerini yönetmek için REST API",
    version="1.0.0"
)

app.include_router(campus_router, prefix="/api", tags=["Campuses"])

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {
        "message": "Üniversite Kampüs API'ye hoş geldiniz",
        "docs": "/docs",
        "version": "1.0.0"
    }
