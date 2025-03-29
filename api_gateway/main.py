import uvicorn
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.config import settings
from app.db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Task Management - API Gateway",
    description="API Gateway for Smart Task Management System",
    version="1.0.0",
    root_path="",
)

# Include API router
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)