import os
import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json

BASE_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"

HEADERS = {
    "User-Agent": "Menna-Scraper/1.0 (+https://github.com/mennaahmed00/flyrank_assignmentss)"
}

def fetch_or_cache(url, page_number):
    cache_file = os.path.join(CACHE_DIR, f"catalogue-page-{page_number}.html")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read(), True
            
    time.sleep(0.5)
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code} for {url}")
        
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(response.text)

    return response.text, False

def fetch_or_cache_detail(url, cache_filename):
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
            
    time.sleep(0.5)
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}, status code {response.status_code}")
        
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    return response.text

def parse_book_detail(html_content, product_url, source_page):
    soup = BeautifulSoup(html_content, "html.parser")
    
    main_div = soup.select_one("div.product_main")
    
    # Title
    title = main_div.select_one("h1").get_text(strip=True) if main_div and main_div.select_one("h1") else None
    
    # Price
    price_tag = main_div.select_one("p.price_color") if main_div else None
    price_text = price_tag.get_text(strip=True) if price_tag else None
    
    # Availability
    avail_tag = main_div.select_one("p.instock.availability") if main_div else None
    availability_text = avail_tag.get_text(strip=True) if avail_tag else None
    
    # Rating
    rating_tag = main_div.select_one("p.star-rating") if main_div else None
    rating_text = None
    if rating_tag:
        classes = rating_tag.get("class", [])
        rating_classes = [c for c in classes if c != "star-rating"]
        if rating_classes:
            rating_text = rating_classes[0]
            
    # Description
    desc_header = soup.select_one("#product_description")
    description = None
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        if desc_p:
            description = desc_p.get_text(strip=True)
            
    # Timestamp
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }

def run_scraper():
    current_url = BASE_URL
    page_count = 0
    discovered_items = []  # Stores (book_url, source_page) tuples
    
    # Stage 2: Crawl Catalogue Pages
    while current_url and page_count < 3:
        page_count += 1
        source_page = current_url
        
        html, is_cached = fetch_or_cache(current_url, page_count)
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

    # Deduplicate items based on book URL
    seen_urls = set()
    unique_items = []
    for item in discovered_items:
        url, src = item
        if url not in seen_urls:
            seen_urls.add(url)
            unique_items.append(item)

    print(f"catalogue_pages={page_count}, discovered={len(discovered_items)}, unique_urls={len(unique_items)}")

    # Stage 3: Extract Book Details
    records = []
    for book_url, source_page in unique_items:
        slug = book_url.rstrip("/").split("/")[-2]
        cache_filename = f"detail-{slug}.html"
        
        html = fetch_or_cache_detail(book_url, cache_filename)
        record = parse_book_detail(html, book_url, source_page)
        records.append(record)

    # Checkpoint output
    print("\n--- Sample Record ---")
    print(json.dumps(records[0], indent=2))
    print(f"detail_pages={len(records)}")

if __name__ == "__main__":
    run_scraper()