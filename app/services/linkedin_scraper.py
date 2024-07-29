from services.base_scraper import BaseScraper
from typing import List, Dict
from fastapi import HTTPException

class LinkedInScraper(BaseScraper):
    def scrape_jobs(self, job_title: str, country: str, pages: int) -> List[Dict]:
        raise HTTPException(status_code=501, detail="LinkedIn scraper not implemented yet")
