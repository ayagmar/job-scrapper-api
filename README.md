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

This script utilizes the FastAPI framework to create a RESTful API for scraping job listings from Indeed. The API
provides two endpoints: `/scrape_jobs` and `/jobs`. The former endpoint allows users to scrape jobs based on their
title, country, and number of pages to crawl.


**Features**
------------

*   Scrapes job listings from Indeed
*   Supports multiple countries (using IETF language tags)
*   Handles pagination for efficient job crawling
*   Provides a simple RESTful API using FastAPI
*   Includes basic logging and error handling


**Requirements**
---------------

*   Python 3.8+
*   FastAPI framework (`pip install fastapi`)
*   Selenium WebDriver for browser automation (`pip install selenium`)


**Usage**
---------

1.  Clone the repository using `git clone https://github.com/ayagmar/job-scrapper-api`
2.  Install required dependencies by running `pip install -r requirements.txt`
3.  Run the script using `python .\app.py`


**Endpoints**
------------

### `/scrape_jobs`

*   **Method:** GET
*   **Parameters:**

    *   `job_title`: Job title to scrape (string)
    *   `country`: Country code for job listings (default: "us")
    *   `pages`: Number of pages to crawl (default: 1, range: 1-10)

### `/jobs`

*   **Method:** GET
*   **Parameters:** None

**Example Use Cases**
-------------------

To scrape jobs using the `/scrape_jobs` endpoint, send a GET request with the following parameters:

```bash
curl -X GET \
  http://localhost:8000/scrape_jobs?job_title=python+developer&country=fr&page=5 \
  -H 'accept: application/json'
```

This will return a list of scraped job listings in JSON format.