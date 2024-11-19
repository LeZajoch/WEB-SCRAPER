from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


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
        return {"error": str(e)}


# Endpoint pro získání dat z článku
@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    data = scrape_article(url)
    return jsonify(data)


# Endpoint pro procházení více článků z hlavní stránky
@app.route('/scrape-website', methods=['GET'])
def scrape_website():
    base_url = request.args.get('base_url')
    article_selector = request.args.get('selector')

    if not base_url or not article_selector:
        return jsonify({"error": "Missing 'base_url' or 'selector' parameters"}), 400

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

        return jsonify(articles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
