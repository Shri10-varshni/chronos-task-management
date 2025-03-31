import sys
import os

# Did this coz the shared package was not being found
# when running the FastAPI app in a different directory
# Add shared package to Python path
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, shared_path)

import uvicorn
from dotenv import load_dotenv
load_dotenv()  # Add this line at the top
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.config import settings
from app.db.database import engine, Base, init_db

# Recreate database tables with new schema
# init_db()

app = FastAPI(
    title="Smart Task Management - Task Service",
    description="Task Service for Smart Task Management System",
    version="1.0.0",
)

# Include API router
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)

