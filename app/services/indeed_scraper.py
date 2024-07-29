import logging
import time
import random
from urllib.parse import quote_plus
import re
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from services.base_scraper import BaseScraper
from datetime import datetime

logger = logging.getLogger(__name__)

class IndeedScraper(BaseScraper):
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
            'date_scraped': datetime.utcnow(),
            'source':'indeed'
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
        company_details_url = self._extract_element_attribute(self.driver, [
            "//div[@data-testid='jobsearch-CompanyInfoContainer']//a",
            "//a[@data-tn-element='companyName']"
        ], 'href')

        company_details = {'company_url': None, 'industry': None}
        if company_details_url:
            try:
                company_details = self._fetch_company_details(company_details_url)
            except Exception as e:
                logger.error(f"Error fetching company details: {e}")

        return {
            'full_job_description': job_description,
            'company_details_url': company_details_url,
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
