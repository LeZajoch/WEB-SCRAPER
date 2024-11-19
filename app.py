import requests
from bs4 import BeautifulSoup
import pandas as pd


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
        images = len(soup.find_all('img'))  # Počet obrázků na stránce
        content = soup.find('div', class_='article-body').text.strip() if soup.find('div',
                                                                                    class_='article-body') else "N/A"

        return {"Title": title, "Category": category, "Comments": comments, "Images": images, "Content": content}
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


# Hlavní funkce pro procházení více článků
def scrape_website(base_url, article_selector):
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

        # Uložíme výsledky
        df = pd.DataFrame(articles)
        df.to_csv("articles.csv", index=False, encoding="utf-8")
        print("Data saved to articles.csv")
    except Exception as e:
        print(f"Error accessing {base_url}: {e}")


# Spuštění crawleru pro konkrétní web
if __name__ == "__main__":
    # Příklad pro novinky.cz (vyměňte za jiné weby dle potřeby)
    scrape_website("https://www.novinky.cz", "a.teaser-title")
