from fastapi import FastAPI
from api.endpoints import router as api_router
from database import engine, Base
from config import settings
import logging

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Job Scraper API", version="1.0.0")

# Create tables
if settings.DROP_AND_CREATE_SCHEMA:
    Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Include the API router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)