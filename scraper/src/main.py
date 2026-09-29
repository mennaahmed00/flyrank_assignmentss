import os
import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-1.html"
URL = "https://books.toscrape.com/catalogue/category/books/science_22/index.html"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")

HEADERS = {"User-Agent": "Menna-Scraper/1.0 https://github.com/mennaahmed00/flyrank_assignmentss"}

#404 not found error
def get_page_html():
    if os.path.exists(CACHE_FILE):
        print("CACHE")

        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            html_content = f.read()
    else:
        print("FETCH")
        response = requests.get(URL, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch page. HTTP Status Code: {response.status_code}")
        html_content = response.text

        os.makedirs(CACHE_DIR, exist_ok=True)

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)

    print(f"Response size: {len (html_content)} bytes")
    return html_content

def fetch_or_cache(url, page_number):
    cache_file = os.path.join(CACHE_DIR, f"catalogue-page-{page_number}.html")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read(), True
    time.sleep(0.5)
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code} for {url}")
    os.makedirs(CACHE_DIR, exist_ok = True)
    with open(cache_file, "w", encoding = "utf-8") as f:
        f.write(response.text)

    return  response.text, False

def crawl_catalogue():
    current_url = BASE_URL
    page_count = 0
    all_discovered_links = []
    
    while current_url and page_count < 3:
        page_count += 1
        
        # 1. Retrieve page HTML
        html, is_cached = fetch_or_cache(current_url, page_count)
        
        # 2. Parse HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # 3. Extract all book item links on current page
        # Books on books.toscrape.com are typically inside <article class="product_pod"> -> <h3> -> <a href="...">
        book_tags = soup.select("article.product_pod h3 a")
        for a_tag in book_tags:
            href = a_tag.get("href")
            if href:
                full_url = urljoin(current_url, href)
                all_discovered_links.append(full_url)
                
        # 4. Find the "next" page link
        next_tag = soup.select_one("ul.pager li.next a")
        if next_tag and next_tag.get("href"):
            current_url = urljoin(current_url, next_tag.get("href"))
        else:
            current_url = None

    # 5. Deduplicate links
    unique_links = list(dict.fromkeys(all_discovered_links))

    # Print required Checkpoint metrics
    print(f"catalogue_pages={page_count}, discovered={len(all_discovered_links)}, unique_urls={len(unique_links)}")


if __name__ == "__main__":
    crawl_catalogue()
    
