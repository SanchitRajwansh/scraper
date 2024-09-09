# Python Scraper Project

This is a Python-based web scraping project built using the FastAPI framework. The scraper collects product data (title, price, image) from a specified e-commerce website, stores it in a JSON file or PostgreSQL database, and provides flexible notification mechanisms upon scraping completion. It uses Redis to cache the data and check for price updation and update in the storage only if the price is updated.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Running the Project](#running-the-project)
- [Notification Strategy](#notification-strategy)
- [Results](#results)

## Features
- Scrape product titles, prices, and images from e-commerce pages.
- Supports configurable page limits and proxy settings.
- Stores scraped data in either a JSON file or PostgreSQL database(environment configurable setting).
- Sends notifications when scraping is completed (e.g., via console).
- Caching with Redis to avoid updating products with unchanged prices.

## Tech Stack
- **Python**: Core language.
- **FastAPI**: Web framework.
- **BeautifulSoup**: HTML parsing library.
- **PostgreSQL**: (Optional) Database for storing scraped data.
- **Redis**: In-memory database for caching.



 ### Prerequisites
Make sure you have the following installed on your system:
- Python 3.8+
- PostgreSQL (if using as a storage option)
- Redis (optional for caching)
- Virtualenv (for creating isolated Python environments)



## Setup
 ### Step 1: Clone the Repository
```bash
git clone https://github.com/SanchitRajwansh/scraper.git
cd scraper
```

 ### Step 2: Create a virual environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
```

 ### Step 3: Install the Required Packages
```bash
pip install -r requirements.txt
```

 ### Step 4: Set up the Environment Variables
```bash
# .env file

# STORAGE_TYPE can be 'json' or 'postgres'
STORAGE_TYPE=json

# If using JSON storage
JSON_FILE_PATH=/scraped_data.json

# If using PostgreSQL storage
# make dbname as 'scraper'
# add your local postgres settings here if different
DATABASE_URL=postgresql://username:password@localhost:5432/scraper

# Redis configuration
REDIS_HOST=localhost  # add your local redis settings here if different
REDIS_PORT=6379
REDIS_INDEX=0

# Add your token here for authentication
STATIC_TOKEN=some-token  # Token for protected API access
```

 ### Step 5: Create Database (if using PostgreSQL)
```bash
# Access psql shell
psql -U postgres

# In psql shell, create a new database
CREATE DATABASE scraper;
```

 ### Step 6: Run Database Migrations (if using PostgreSQL)
```bash
# Access psql shell
psql -U postgres

# Use the scraper database
\c scraper

# Create table products
CREATE TABLE IF NOT EXISTS products (
    product_title VARCHAR(255) PRIMARY KEY,
    product_price DOUBLE PRECISION,
    path_to_image TEXT
);
```

 ### Step 7: Create an images folder at the root level of your project
```bash
cd scraper
mkdir images
```


## Running the Project

 ### Step 1: Start the FastAPI Server
```bash
uvicorn main:app --reload
#FastApi Server starts running at `http://127.0.0.1:8000/`
```

 ### Step 2: Test the scraper
```bash

# Use this when basic functionality listed below needed:
# 1. Token Authentication
# 2. Page Limit

curl -X POST "http://127.0.0.1:8000/scrape" \
-H "Content-Type: application/json" \
-H "token: some-token" \
-d '{"page_limit": 2}'

```

```bash

# Use this when below listed functionality needed:
# 1. Token Authentication
# 2. Page Limit
# 3. Proxy Server 
# 4. Email Notification

# NOTE: Email notification logic is not done, placeholder for email notification is done. It can be implemented later.
# This CURL request will work as well.

curl -X POST "http://127.0.0.1:8000/scrape" \
-H "Content-Type: application/json" \
-H "token: some-token" \
-d '{"page_limit": 2,
   "email": "sanchit.rajwansh@gmail.com",
   "proxy" : your proxy server connection string
}'

```

## Notification Strategy
- if email is not provided in the params in the curl request or via postman, console notification will be provided by default.
- if email is provided in the params, then email notifier will work. For now a different result than console notifier will be shown, we can add the logic for email notification in the email notifier class.


## Results
### JSON Based Results
- Check the scraped_data.json file to see data scraped from the site.

### Postgres Based Results
- Check the products table in scraper database to see the scraped results.
