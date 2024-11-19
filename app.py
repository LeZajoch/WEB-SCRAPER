import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_article(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Ověření, že stránka byla načtena
        soup = BeautifulSoup(response.text, 'html.parser')

        # Získání požadovaných informací
        title = soup.find('h1').text.strip() if soup.find('h1') else "N/A"
        category = soup.find('meta', {'property': 'article:section'})['content'] if soup.find('meta', {
            'property': 'article:section'}) else "N/A"
        comments = soup.find('span', class_='comments-count').text.strip() if soup.find('span',
                                                                                        class_='comments-count') else "0"
        content = soup.find('div', class_='article-body').text.strip() if soup.find('div',
                                                                                    class_='article-body') else "N/A"

        return {"Title": title, "Category": category, "Comments": comments, "Content": content}
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_website(base_url, article_selector, output_file):
    articles = []
    try:
        response = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Najdeme odkazy na články
        links = [a['href'] for a in soup.select(article_selector) if a['href'].startswith('http')]

        # Pro každý odkaz získáme detaily
        for link in links:
            article_data = scrape_article(link)
            if article_data:
                articles.append(article_data)
                # Průběžně ukládáme data do souboru
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(article_data) + '\n')
                print(f"Scraped article: {article_data['Title']}")
    except Exception as e:
        print(f"Error accessing {base_url}: {e}")

def main():
    BASE_URL = "https://www.novinky.cz"  # Příklad základní URL
    ARTICLE_SELECTOR = "a.teaser-title"  # CSS selektor článků
    OUTPUT_FILE = "articles.json"        # Výstupní soubor
    SIZE_LIMIT_GB = 2  # Maximální velikost dat v GB

    # Smazání existujícího souboru, pokud už existuje
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    total_size = 0  # Aktuální velikost souboru v bajtech
    print(f"Starting scraping from {BASE_URL}...")

    while total_size < SIZE_LIMIT_GB * (1024 ** 3):  # Pokračujeme, dokud nepřesáhneme 2 GB
        scrape_website(BASE_URL, ARTICLE_SELECTOR, OUTPUT_FILE)
        # Aktualizace velikosti souboru
        total_size = os.path.getsize(OUTPUT_FILE)
        print(f"Current data size: {total_size / (1024 ** 3):.2f} GB")

    print(f"Scraping completed. Total data size: {total_size / (1024 ** 3):.2f} GB")

if __name__ == "__main__":
    main()
