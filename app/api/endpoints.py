from fastapi import APIRouter, HTTPException, Query
from typing import List
from schemas import JobListingResponse
from services.job_service import JobService
from services.indeed_scraper import IndeedScraper
from services.linkedin_scraper import LinkedInScraper
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/scrape_jobs", response_model=List[JobListingResponse])
async def scrape_jobs(
    job_title: str,
    country: str = Query("us", description="Country code (e.g., 'us' for the United States, 'fr' for France)"),
    pages: int = Query(1, ge=1, le=10, description="Number of pages to scrape"),
    source: str = Query("indeed", description="Job source to scrape (e.g., 'indeed', 'linkedin')")
):
    scraper = None
    if source == "indeed":
        scraper = IndeedScraper()
    elif source == "linkedin":
        scraper = LinkedInScraper()
    else:
        raise HTTPException(status_code=400, detail="Invalid source parameter. Valid options are 'indeed' or 'linkedin'.")
    
    job_service = JobService(scraper)
    try:
        job_listings = job_service.scrape_and_store_jobs(job_title, country, pages)
        
        return [JobListingResponse(**job) for job in job_listings]
    except Exception as e:
        logger.error(f"Failed to scrape jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to scrape jobs")

@router.get("/jobs", response_model=List[JobListingResponse])
async def get_jobs():
    """
    Retrieve job listings from the database.
    """
    try:
        # Retrieve all job listings from the database
        jobs = JobService.get_all_jobs()
        
        # Convert JobListing instances to JobListingResponse
        return [JobListingResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            summary=job.summary,
            url=job.url,
            full_job_description=job.full_job_description,
            company_url=job.company_url,
            company_details_url=job.company_details_url,
            industry=job.industry,
            date_scraped=job.date_scraped,
            source=job.source
        ) for job in jobs]
    except Exception as e:
        logger.error(f"Failed to retrieve jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs")
