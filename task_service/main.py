from fastapi import FastAPI
from app.api.routes import router as task_router

app = FastAPI(title="Chronos Task Service")
app.include_router(task_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
