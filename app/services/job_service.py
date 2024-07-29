from typing import List
from models import JobListing
from database import SessionLocal
from services.base_scraper import BaseScraper

class JobService:
    def __init__(self, scraper: BaseScraper):
        self.scraper = scraper

    def scrape_and_store_jobs(self, job_title: str, country: str, pages: int) -> List[JobListing]:
        job_listings = self.scraper.scrape_jobs(job_title, country, pages)
        db = SessionLocal()
        try:
            for job in job_listings:
                db_job = JobListing(**job)
                db.add(db_job)
            db.commit()
            return job_listings
        finally:
            db.close()

    @staticmethod
    def get_all_jobs() -> List[JobListing]:
        db = SessionLocal()
        try:
            return db.query(JobListing).all()
        finally:
            db.close()
