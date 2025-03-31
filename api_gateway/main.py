import sys
import os

# Add shared package to Python path
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, shared_path)

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.config import settings
from app.db.database import engine, Base

# Load environment variables from .env file
load_dotenv()

# Debug: Print Python path
print("Python path:", sys.path)

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