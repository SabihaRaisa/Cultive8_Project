
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.upload import router as upload_router
from app.routes.reports import router as reports_router


app = FastAPI(
    title="Local AI Security Log Analyzer",
    description="Analyze server logs using a local AI model",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload_router)
app.include_router(reports_router)


@app.get("/")
def home():
    return {
        "message": "Local AI Security Log Analyzer is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
