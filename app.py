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
def scrape_website(base_url, article_selector, output_file, seen_articles):
    try:
        print(f"Fetching: {base_url}")
        response = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Najdeme odkazy na články
        links = [a['href'] for a in soup.select(article_selector) if a['href'].startswith('http')]
        print(f"Found {len(links)} articles on {base_url}.")

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
    BASE_URLS = [
        "https://www.idnes.cz/",  # Hlavní stránka
        "https://www.idnes.cz/zpravy/domaci",  # Kategorie: Domácí
        "https://www.idnes.cz/sport/formule",  # Kategorie: F1
        "https://www.idnes.cz/ekonomika"  # Kategorie: Ekonomika
    ]
    ARTICLE_SELECTOR = "a.art-link"  # Aktualizovaný CSS selektor
    OUTPUT_FILE = "articles.json"
    SEEN_ARTICLES = set()

    # Vytvoření prázdného výstupního souboru
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("")

    print("Starting scraping...")
    for base_url in BASE_URLS:
        print(f"Scraping URL: {base_url}")
        scrape_website(base_url, ARTICLE_SELECTOR, OUTPUT_FILE, SEEN_ARTICLES)
        print(f"Completed scraping for {base_url}")

    print("Scraping completed.")

if __name__ == "__main__":
    main()
