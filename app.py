import logging
from datetime import datetime
import time
import random
import uuid
from urllib.parse import quote_plus
import re
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Job Scraper API", version="1.0.0")

# Database configuration
DATABASE_URL = "postgresql://jobuser:jobpassword@localhost/jobscraper"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True, nullable=True)
    company = Column(String, index=True, nullable=True)
    location = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    url = Column(String, unique=True, nullable=True)
    full_job_description = Column(Text, nullable=True)
    indeed_company_url = Column(String, nullable=True)
    company_url = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    date_scraped = Column(DateTime, default=datetime.utcnow)

Base.metadata.drop_all(bind=engine)  # Drop existing tables
Base.metadata.create_all(bind=engine)

class JobListingResponse(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    full_job_description: Optional[str] = None
    indeed_company_url: Optional[str] = None
    company_url: Optional[str] = None
    industry: Optional[str] = None
    date_scraped: Optional[datetime] = None

    class Config:
        orm_mode = True

class JobScraper:
    def __init__(self):
        self.driver = self._get_driver()

    def _get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={UserAgent().random}")
        return webdriver.Chrome(options=chrome_options)

    def _wait_and_get_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def _wait_and_get_elements(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

    def _extract_element_text(self, element, xpaths):
        for xpath in xpaths:
            try:
                return element.find_element(By.XPATH, xpath).text.strip()
            except NoSuchElementException:
                continue
        logger.error(f"Error extracting text with XPaths '{xpaths}'")
        return None

    def _extract_element_attribute(self, element, xpaths, attribute):
        for xpath in xpaths:
            try:
                return element.find_element(By.XPATH, xpath).get_attribute(attribute)
            except NoSuchElementException:
                continue
        logger.error(f"Error extracting attribute '{attribute}' with XPaths '{xpaths}'")
        return None

    def _clean_job_link(self, link):
        match = re.search(r'jk=([a-f0-9]+)', link)
        return f"https://www.indeed.com/viewjob?jk={match.group(1)}" if match else link

    def _scrape_page(self, url):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                job_cards = self._wait_and_get_elements(By.XPATH, "//div[@class='job_seen_beacon']")
                logger.info(f"Found {len(job_cards)} job cards on page")
                return [self._parse_job_card(card) for card in job_cards if self._parse_job_card(card)]
            except TimeoutException:
                if attempt < max_retries - 1:
                    logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                    time.sleep(random.uniform(2, 5))
                else:
                    logger.error("Max retries reached, unable to scrape page")
                    return []

    def _parse_job_card(self, card):
        job = {
            'title': self._extract_element_text(card, [
                ".//h2[contains(@class, 'jobTitle')]//span",
                ".//a[contains(@class, 'jcs-JobTitle')]"
            ]),
            'company': self._extract_element_text(card, [
                ".//span[@data-testid='company-name']",
                ".//span[contains(@class, 'companyName')]"
            ]),
            'location': self._extract_element_text(card, [
                ".//div[@data-testid='text-location']",
                ".//div[contains(@class, 'companyLocation')]"
            ]),
            'summary': self._extract_element_text(card, [
                ".//div[contains(@class, 'css-9446fg')]",
                ".//div[contains(@class, 'job-snippet')]"
            ]),
            'url': self._clean_job_link(self._extract_element_attribute(card, [
                ".//a[contains(@href, '/rc/clk')]",
                ".//a[contains(@href, '/company')]"
            ], 'href')),
            'date_scraped': datetime.utcnow()
        }

        logger.info(f"Parsed job: {job['title']} at {job['company']}")
        return job

    def _fetch_company_details(self, company_url):
        self.driver.get(company_url)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'css-hbpv4x')]"))
        )
        company_info = self.driver.find_element(By.XPATH, "//ul[contains(@class, 'css-hbpv4x')]").get_attribute('outerHTML')
        soup = BeautifulSoup(company_info, 'html.parser')
        company_industry = None
        real_company_url = None
        for li in soup.find_all('li'):
            if li.get('data-testid') == 'companyInfo-industry':
                company_industry = li.find('a').text if li.find('a') else None
            elif li.get('data-testid') == 'companyInfo-companyWebsite':
                real_company_url = li.find('a')['href'] if li.find('a') else None
        return {
            'company_url': real_company_url,
            'industry': company_industry
        }

    def _fetch_job_details(self, job_url):
        self.driver.get(job_url)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='jobDescriptionText']"))
        )

        job_description = self._extract_element_text(self.driver, [
            "//div[@id='jobDescriptionText']",
            "//div[@class='jobsearch-JobComponent-description']"
        ])
        indeed_company_url = self._extract_element_attribute(self.driver, [
            "//div[@data-testid='jobsearch-CompanyInfoContainer']//a",
            "//a[@data-tn-element='companyName']"
        ], 'href')

        company_details = {'company_url': None, 'industry': None}
        if indeed_company_url:
            try:
                company_details = self._fetch_company_details(indeed_company_url)
            except Exception as e:
                logger.error(f"Error fetching company details: {e}")

        return {
            'full_job_description': job_description,
            'indeed_company_url': indeed_company_url,
            'company_url': company_details['company_url'],
            'industry': company_details['industry']
        }

    def scrape_jobs(self, job_title: str, country: str, pages: int) -> List[dict]:
        base_url = f"https://{country}.indeed.com/jobs"
        all_job_listings = []

        try:
            for page in range(pages):
                url = f'{base_url}?q={quote_plus(job_title)}&start={page * 10}'
                logger.info(f"Scraping page {page + 1}: {url}")
                page_listings = self._scrape_page(url)
                all_job_listings.extend(page_listings)
                logger.info(f"Scraped {len(page_listings)} jobs from page {page + 1}")
                time.sleep(random.uniform(2, 5))  # Random delay between pages

            for job in all_job_listings:
                try:
                    job_details = self._fetch_job_details(job['url'])
                    job.update(job_details)
                    logger.info(f"Fetched details for job: {job['title']}")
                except Exception as e:
                    logger.error(f"Error fetching details for job {job['title']}: {e}")
                time.sleep(random.uniform(1, 3))  # Random delay between job detail requests

            return all_job_listings
        except Exception as e:
            logger.error(f"Failed to scrape jobs: {e}")
            raise
        finally:
            self.driver.quit()

@app.get("/scrape_jobs", response_model=List[JobListingResponse])
async def scrape_jobs(
    job_title: str,
    country: str = Query("us", description="Country code (e.g., 'us' for the United States, 'fr' for France)"),
    pages: int = Query(1, ge=1, le=10, description="Number of pages to scrape")
):
    """
    Scrape jobs from Indeed and store them in the database.
    """
    scraper = JobScraper()
    try:
        job_listings = scraper.scrape_jobs(job_title, country, pages)
        db = SessionLocal()
        for job in job_listings:
            db_job = JobListing(**job)
            db.add(db_job)
        db.commit()
        db.close()
        return job_listings
    except Exception as e:
        logger.error(f"Failed to scrape jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to scrape jobs")

@app.get("/jobs", response_model=List[JobListingResponse])
async def get_jobs():
    """
    Retrieve job listings from the database.
    """
    db = SessionLocal()
    try:
        jobs = db.query(JobListing).all()
        return [JobListingResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            summary=job.summary,
            url=job.url,
            full_job_description=job.full_job_description,
            company_url=job.company_url,
            indeed_company_url=job.indeed_company_url,
            industry=job.industry,
            date_scraped=job.date_scraped
        ) for job in jobs]
    except Exception as e:
        logger.error(f"Failed to retrieve jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)