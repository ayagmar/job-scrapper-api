from abc import ABC, abstractmethod
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self):
        self.driver = self._get_driver()

    def _get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={UserAgent().random}")
        return webdriver.Chrome(options=chrome_options)

    def _wait_and_get_element(self, by, value, timeout=20):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def _wait_and_get_elements(self, by, value, timeout=20):
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

    @abstractmethod
    def scrape_jobs(self, job_title: str, country: str, pages: int) -> List[Dict]:
        pass
