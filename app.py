import requests
from bs4 import BeautifulSoup
import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask is running! Use /scrape or /scrape-website to start scraping."

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
        return {"error": str(e)}

# Endpoint pro scrapování jednoho článku
@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    result = scrape_article(url)
    return jsonify(result)

# Hlavní funkce pro procházení více článků
def scrape_website(base_url, article_selector, output_file, size_limit_gb=2):
    total_size = 0  # Velikost dat v bajtech
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

                # Aktualizace velikosti uložených dat
                total_size += len(json.dumps(article_data).encode('utf-8'))
                print(f"Current data size: {total_size / (1024 ** 3):.2f} GB")

                # Kontrola, zda jsme dosáhli limitu
                if total_size >= size_limit_gb * (1024 ** 3):  # Převod GB na bajty
                    print(f"Reached size limit of {size_limit_gb} GB. Stopping.")
                    return
    except Exception as e:
        print(f"Error accessing {base_url}: {e}")

# Endpoint pro scrapování webové stránky
@app.route('/scrape-website', methods=['GET'])
def scrape_website_endpoint():
    base_url = request.args.get('base_url')
    selector = request.args.get('selector')
    size_limit_gb = float(request.args.get('size_limit_gb', 2))  # Default 2 GB
    output_file = "articles.json"

    if not base_url or not selector:
        return jsonify({"error": "Missing 'base_url' or 'selector' parameter"}), 400

    # Smazání existujícího souboru
    if os.path.exists(output_file):
        os.remove(output_file)

    # Scrapování webu
    scrape_website(base_url, selector, output_file, size_limit_gb)

    return jsonify({"status": "Scraping completed", "output_file": output_file})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
