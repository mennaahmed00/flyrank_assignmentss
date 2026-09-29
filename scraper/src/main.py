import os
import requests


URL = "https://books.toscrape.com/catalogue/category/books/science_22/index.html"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")

HEADERS = {"User_Agent": "Menna-Scraper/1.0 https://github.com/mennaahmed00/flyrank_assignmentss"}

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
            raise Exception(f"Failed to fetch page. HTTP Status Code: {response.status_code}")[cite: 2]
        html_content = response.text

        os.makedirs(CACHE_DIR, exist_ok=True)

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)

    print(f"Response size: {len (html_content)} bytes")
    return html_content
if __name__ == "__main__":
    get_page_html()