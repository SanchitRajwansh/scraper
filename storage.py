import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

class Storage(ABC):
    @abstractmethod
    def save(self, data):
        pass

class JSONStorage(Storage):
    def __init__(self, file_path):
        self.file_path = file_path

    def save(self, data):
        existing_data = self.fetch()

        if isinstance(data, list):
            existing_data.extend(data)
        else:
            existing_data.append(data)

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

class PostgresStorage(Storage):
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)

    def save(self, data):
        cur = self.conn.cursor()
        for product in data:
            cur.execute(
                """
                INSERT INTO products (product_title, product_price, path_to_image)
                VALUES (%s, %s, %s)
                ON CONFLICT (product_title) DO UPDATE
                SET product_price = EXCLUDED.product_price, path_to_image = EXCLUDED.path_to_image;
                """,
                (product['product_title'], product['product_price'], product['path_to_image'])
            )
        self.conn.commit()
        cur.close()

