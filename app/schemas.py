from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobListingResponse(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    full_job_description: Optional[str] = None
    company_details_url: Optional[str] = None
    company_url: Optional[str] = None
    industry: Optional[str] = None
    date_scraped: Optional[datetime] = None
    source: str

    class Config:
        from_attributes = True 