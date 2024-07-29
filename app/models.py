from sqlalchemy import Column, String, Text, DateTime
from database import Base
import uuid
from datetime import datetime

class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True, nullable=True)
    company = Column(String, index=True, nullable=True)
    location = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    url = Column(String, unique=True, nullable=True)
    full_job_description = Column(Text, nullable=True)
    company_details_url = Column(String, nullable=True)
    company_url = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    date_scraped = Column(DateTime, default=datetime.utcnow)
    source = Column(String, nullable=False)