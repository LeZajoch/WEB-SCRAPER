import requests
from bs4 import BeautifulSoup
import json
import os

# Funkce pro získání dat z jedné stránky
def scrape_article(url):
    try:
        print(f"Scraping article: {url}")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Získání požadovaných informací
        title = soup.find('h1').text.strip() if soup.find('h1') else "N/A"
        category = soup.find('meta', {'property': 'article:section'})['content'] if soup.find('meta', {
            'property': 'article:section'}) else "N/A"
        comments = soup.find('span', class_='comments-count').text.strip() if soup.find('span',
                                                                                        class_='comments-count') else "0"
        content = soup.find('div', class_='article-body').text.strip() if soup.find('div',
                                                                                    class_='article-body') else "N/A"

        print(f"Scraped article successfully: {title}")
        return {"Title": title, "Category": category, "Comments": comments, "Content": content}
    except Exception as e:
        print(f"Error scraping article {url}: {e}")
        return None

# Funkce pro scrapování jedné stránky
def scrape_website(base_url, article_selector, output_file, seen_articles, page_number):
    try:
        print(f"[Page {page_number}] Fetching: {base_url}")
        response = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Najdeme odkazy na články
        links = [a['href'] for a in soup.select(article_selector) if a['href'].startswith('http')]
        print(f"[Page {page_number}] Found {len(links)} articles.")

        for link in links:
            if link not in seen_articles:
                seen_articles.add(link)
                article_data = scrape_article(link)
                if article_data:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(article_data) + '\n')
    except Exception as e:
        print(f"Error accessing {base_url}: {e}")

def main():
    BASE_URL_TEMPLATE = "https://www.novinky.cz/page={}"  # URL s číslem stránky
    ARTICLE_SELECTOR = "a.teaser-title"  # CSS selektor článků
    OUTPUT_FILE = "articles.json"        # Výstupní soubor
    SEEN_ARTICLES = set()  # Množina pro unikátní články
    MAX_PAGES = 5  # Počet stránek pro podrobné logování

    # Vytvoření (nebo přepsání) souboru na začátku
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("")  # Prázdný soubor

    print("Starting scraping...")
    for page_number in range(1, MAX_PAGES + 1):  # Scrapujeme 5 stránek s detailním logováním
        scrape_website(BASE_URL_TEMPLATE.format(page_number), ARTICLE_SELECTOR, OUTPUT_FILE, SEEN_ARTICLES, page_number)

    print("Detailed scraping of 5 pages completed. Continuing without logging every detail...")

    # Pokračujeme bez detailního logování
    page_number = MAX_PAGES + 1
    while True:
        scrape_website(BASE_URL_TEMPLATE.format(page_number), ARTICLE_SELECTOR, OUTPUT_FILE, SEEN_ARTICLES, page_number)
        page_number += 1

if __name__ == "__main__":
    main()
