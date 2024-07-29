**Job Scraper Script**
=====================

A simple Python script using the FastAPI framework to scrape job listings from Indeed.

**Table of Contents**
-----------------

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Usage](#usage)
5. [Endpoints](#endpoints)


**Overview**
------------

This application leverages FastAPI to provide a flexible and maintainable RESTful API for scraping job listings. The project is organized into distinct modules for configuration, database management, scraper architecture, and business logic, promoting better organization and extensibility.


**Features**
------------

*   Modular Architecture: Separated into modules for configuration, database handling, models, schemas, and scrapers.
*   Scraper Framework: Abstract BaseScraper class with specific implementations for different job boards (e.g., Indeed, LinkedIn).
*   Handles pagination for efficient job crawling
*   Provides a simple RESTful API using FastAPI
*   Error Handling and Logging: Consistent error handling and logging configured through Pydantic's BaseSettings.


**Requirements**
---------------

*   Python 3.8+
*   FastAPI framework (`pip install fastapi`)
*   Selenium WebDriver for browser automation (`pip install selenium`)
*   Pydantic for configuration management (pip install pydantic)


**Usage**
---------

1.  Clone the repository using `git clone https://github.com/ayagmar/job-scrapper-api`
2.  Install required dependencies by running `pip install -r requirements.txt`
3.  Run the script using `python .\app\main.py`


**Endpoints**
------------

### `/api/v1/scrape_jobs`

*   **Method:** GET
*   **Parameters:**

    *   `job_title`: Job title to scrape (string)
    *   `country`: Country code for job listings (default: "us")
    *   `source`: Source to scrape from (indeed,linkedin) default indeed
    *   `pages`: Number of pages to crawl (default: 1, range: 1-10)

### `/api/v1/jobs`

*   **Method:** GET
*   **Parameters:** None

**Example Use Cases**
-------------------

To scrape jobs using the `/scrape_jobs` endpoint, send a GET request with the following parameters:

```bash
curl -X GET \
  http://localhost:8000/api/v1/scrape_jobs?job_title=java+developer&country=fr&page=1&source=indeed \
  -H 'accept: application/json'
```

This will return a list of scraped job listings in JSON format.

Example : [View `response.json` on GitHub] (https://github.com/ayagmar/job-scrapper-api/blob/master/results.json)
