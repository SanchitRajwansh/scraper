from fastapi import FastAPI, Header, HTTPException, Depends
from typing import Optional
import requests
from bs4 import BeautifulSoup
import json
import os
from pydantic import BaseModel, field_validator
from storage import JSONStorage, PostgresStorage
from notifier import ConsoleNotifier, EmailNotifier
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import redis
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

access_token = os.getenv('STATIC_TOKEN', 'some-token')
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
redis_index = os.getenv('REDIS_INDEX', 0)

redis_object = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_index)

class ScrapingSettings(BaseModel):
    page_limit: Optional[int] = None
    proxy: Optional[str] = None
    email: Optional[str] = None

    @field_validator('page_limit')
    def validate_page_limit(cls, v):
        if v is not None and v < 1:
            raise ValueError("page_limit must be greater than 0")
        return v

class Product(BaseModel):
    product_title: str
    product_price: float
    path_to_image: str

    @field_validator('product_price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("product_price must be non-negative")
        return v

class Scraper:
    def __init__(self, settings: ScrapingSettings):
        self.page_limit = settings.page_limit
        self.proxy = settings.proxy
        self.session = requests.Session()
        self.email_id = settings.email

        # Add retry mechanism
        retries = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        if self.proxy:
            self.session.proxies.update({
                'http': self.proxy,
                'https': self.proxy,
            })

        self.products = []
        storage_type = os.getenv('STORAGE_TYPE')
        if storage_type == 'postgres':
            self.storage = PostgresStorage(os.getenv('DATABASE_URL'))
        else:
            self.storage = JSONStorage(os.getenv('JSON_FILE_PATH'))

        if self.email_id:
            self.notifier = EmailNotifier()
        else:
            self.notifier = ConsoleNotifier()

    def save_data(self):
        for product in self.products:
            # Check cache if price has changed
            cached_price = redis_object.get(product.product_title)
            if cached_price is None or float(cached_price) != product.product_price:
                self.storage.save([product.dict()])
                redis_object.set(product.product_title, product.product_price)

    def fetch_page(self, url):
        response = self.session.get(url)
        response.raise_for_status()
        return response.text

    def parse_products(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        product_divs = soup.find_all('div', class_=['product-inner', 'clearfix'])

        if product_divs:
            for div in product_divs:
                image_tag = div.find('div', class_='mf-product-thumbnail').find('img')
                image_url = image_tag['data-lazy-src']
                product_title = image_tag['alt'].replace(" - Dentalstall India", "")
                price_span = div.find('div', class_='mf-product-price-box').find('span', class_='price')
                current_price = None
                if price_span.find('ins'):
                    current_price = price_span.find('ins').find('span', class_='woocommerce-Price-amount amount').text.strip("₹")
                else:
                    current_price = price_span.find('span', class_='woocommerce-Price-amount amount').text.strip("₹")
                
                image_path = self.download_image(image_url)
                product = Product(product_title=product_title, product_price=current_price, path_to_image=image_path)
                self.products.append(product)
        else:
            print("An exception occured")

    def download_image(self, image_url):
        img_response = self.session.get(image_url)
        img_path = os.path.join("images", os.path.basename(image_url))
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        with open(img_path, 'wb') as f:
            f.write(img_response.content)
        return img_path

    def scrape(self):
        base_url = "https://dentalstall.com/shop/page/{}/"
        page = 1
        while not self.page_limit or page <= self.page_limit:
            page_url = base_url.format(page) if page > 1 else "https://dentalstall.com/shop"
            try:
                html_content = self.fetch_page(page_url)
                self.parse_products(html_content)
            except requests.HTTPError as e:
                print(f"Failed to retrieve page {page}: {e}")
            page += 1

    def notify(self):
        self.notifier.notify(len(self.products), self.email_id)

def authenticate(token: str = Header(...)):
    if token != access_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/scrape")
def scrape(settings: ScrapingSettings, token: str = Depends(authenticate)):
    scraper = Scraper(settings)
    scraper.scrape()
    scraper.save_data()
    scraper.notify()
    return {"status": "success", "scraped_products": len(scraper.products)}
