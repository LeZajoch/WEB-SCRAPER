import requests
from bs4 import BeautifulSoup
import json
import os

# Funkce pro získání dat z jedné stránky
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

# Funkce pro procházení a ukládání unikátních příspěvků
def scrape_website(base_url, article_selector, output_file, seen_articles):
    new_data_added = False  # Pro kontrolu, zda bylo přidáno nové data
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
                # Zkontrolujeme, zda příspěvek už existuje
                if article_data["Title"] not in seen_articles:
                    seen_articles.add(article_data["Title"])  # Přidáme do množiny unikátních
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(article_data) + '\n')
                    new_data_added = True
    except Exception as e:
        print(f"Error accessing {base_url}: {e}")

    return new_data_added

def main():
    BASE_URL = "https://www.novinky.cz"  # Příklad základní URL
    ARTICLE_SELECTOR = "a.teaser-title"  # CSS selektor článků
    OUTPUT_FILE = "articles.json"        # Výstupní soubor
    SIZE_LIMIT_GB = 2  # Maximální velikost dat v GB

    # Ověření, zda soubor existuje, a pokud ne, vytvoření prázdného souboru
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("")  # Prázdný soubor

    seen_articles = set()  # Množina unikátních článků
    total_size = os.path.getsize(OUTPUT_FILE)  # Aktuální velikost souboru v bajtech
    print(f"Starting scraping from {BASE_URL}...")

    last_logged_size = total_size  # Poslední velikost souboru, která byla zapsána do konzole

    while total_size < SIZE_LIMIT_GB * (1024 ** 3):  # Pokračujeme, dokud nepřesáhneme 2 GB
        new_data_added = scrape_website(BASE_URL, ARTICLE_SELECTOR, OUTPUT_FILE, seen_articles)
        total_size = os.path.getsize(OUTPUT_FILE)  # Aktualizujeme velikost souboru

        # Vypisujeme pouze při změně velikosti
        if new_data_added and total_size != last_logged_size:
            print(f"Current data size: {total_size / (1024 ** 3):.2f} GB")
            last_logged_size = total_size

    print(f"Scraping completed. Total data size: {total_size / (1024 ** 3):.2f} GB")

if __name__ == "__main__":
    main()
