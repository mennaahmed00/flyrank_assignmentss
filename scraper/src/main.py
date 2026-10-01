import os
import re
import json
import time
from datetime import datetime, timezone
from urllib.parse import urljoin
from typing import Optional
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError

BASE_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"

HEADERS = {
    "User-Agent": "Menna-Scraper/1.0 (+https://github.com/mennaahmed00/flyrank_assignmentss)"
}


class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str] = None
    description: Optional[str] = None
    source_page: HttpUrl
    fetched_at: str


def fetch_or_cache(url, page_number, report_stats):
    cache_file = os.path.join(CACHE_DIR, f"catalogue-page-{page_number}.html")
    
    if os.path.exists(cache_file):
        report_stats["cache_hits"] += 1
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read(), True

    report_stats["pages_fetched"] += 1
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            time.sleep(0.5)
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code in (404, 403):
                raise Exception(f"HTTP {response.status_code} Permanent Failure")
                
            if response.status_code != 200:
                raise requests.RequestException(f"HTTP Error {response.status_code}")

            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(response.text)
                
            return response.text, False
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1.5)


def fetch_or_cache_detail(url, cache_filename, report_stats):
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    if os.path.exists(cache_path):
        report_stats["cache_hits"] += 1
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    report_stats["pages_fetched"] += 1
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            time.sleep(0.5)
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code in (404, 403):
                raise Exception(f"HTTP {response.status_code} Permanent Failure")
                
            if response.status_code != 200:
                raise requests.RequestException(f"HTTP Error {response.status_code}")

            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(response.text)
                
            return response.text
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1.5)


def parse_book_detail(html_content, product_url, source_page):
    soup = BeautifulSoup(html_content, "html.parser")
    main_div = soup.select_one("div.product_main")

    title = main_div.select_one("h1").get_text(strip=True) if main_div and main_div.select_one("h1") else None

    price_tag = main_div.select_one("p.price_color") if main_div else None
    price_text = price_tag.get_text(strip=True) if price_tag else None

    avail_tag = main_div.select_one("p.instock.availability") if main_div else None
    availability_text = avail_tag.get_text(strip=True) if avail_tag else None

    rating_tag = main_div.select_one("p.star-rating") if main_div else None
    rating_text = None
    if rating_tag:
        classes = rating_tag.get("class", [])
        rating_classes = [c for c in classes if c != "star-rating"]
        if rating_classes:
            rating_text = rating_classes[0]

    desc_header = soup.select_one("#product_description")
    description = None
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        if desc_p:
            description = desc_p.get_text(strip=True)

    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    match = re.search(r"[\d.]+", price_text) if price_text else None
    price_gbp = float(match.group()) if match else 0.0

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }


def run_scraper():
    start_time = datetime.now(timezone.utc)

    report_stats = {
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_seconds": 0.0,
        "pages_fetched": 0,
        "cache_hits": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "failed_pages": 0,
    }

    current_url = BASE_URL
    page_count = 0
    discovered_items = []

    valid_books = []
    errors = []

    # Stage 2: Crawl Catalogue Pages
    while current_url and page_count < 3:
        page_count += 1
        source_page = current_url

        try:
            html, is_cached = fetch_or_cache(current_url, page_count, report_stats)
            soup = BeautifulSoup(html, "html.parser")

            book_tags = soup.select("article.product_pod h3 a")
            for a_tag in book_tags:
                href = a_tag.get("href")
                if href:
                    full_url = urljoin(current_url, href)
                    discovered_items.append((full_url, source_page))

            next_tag = soup.select_one("ul.pager li.next a")
            if next_tag and next_tag.get("href"):
                current_url = urljoin(current_url, next_tag.get("href"))
            else:
                current_url = None

        except Exception:
            report_stats["failed_pages"] += 1

    # Deduplicate items
    seen_urls = set()
    unique_items = []
    for item in discovered_items:
        url, src = item
        if url not in seen_urls:
            seen_urls.add(url)
            unique_items.append(item)

    print(f"catalogue_pages={page_count}, discovered={len(discovered_items)}, unique_urls={len(unique_items)}")

    # Stage 5 requirement: Add fake URL to test failure handling
    unique_items.append((
        "https://books.toscrape.com/catalogue/fake-non-existent-book_9999/index.html",
        BASE_URL
    ))

    # Stage 3, 4 & 5: Detail Fetching, Validation & Failure Isolation
    for book_url, source_page in unique_items:
        slug = book_url.rstrip("/").split("/")[-2]
        cache_filename = f"detail-{slug}.html"

        try:
            html = fetch_or_cache_detail(book_url, cache_filename, report_stats)
            raw_data = parse_book_detail(html, book_url, source_page)

            record = BookRecord(**raw_data)
            valid_books.append(record.model_dump(mode="json"))

        except ValidationError as ve:
            report_stats["invalid_records"] += 1
            errors.append({"url": book_url, "reason": str(ve)})

        except Exception as e:
            report_stats["failed_pages"] += 1
            errors.append({"url": book_url, "reason": str(e)})

    # Finalize report metrics
    report_stats["valid_records"] = len(valid_books)
    end_time = datetime.now(timezone.utc)
    report_stats["duration_seconds"] = round((end_time - start_time).total_seconds(), 2)

    # Save outputs
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "books.json"), "w", encoding="utf-8") as f:
        json.dump(valid_books, f, indent=2)

    with open(os.path.join(output_dir, "errors.json"), "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2)

    with open(os.path.join(output_dir, "run-report.json"), "w", encoding="utf-8") as f:
        json.dump(report_stats, f, indent=2)

    print("\n--- Stage 5 Run Summary ---")
    print(f"Valid books: {len(valid_books)}")
    print(f"Failed pages logged: {report_stats['failed_pages']}")


if __name__ == "__main__":
    run_scraper()