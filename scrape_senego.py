# scrape_senego.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

def scrappe_senego(max_pages=1):
    BASE_URL = "https://senego.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    def get_soup(url):
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return BeautifulSoup(res.content, 'html.parser')

    try:
        soup = get_soup(BASE_URL)
        menu_items = soup.select("header nav.nav .top-menu-content-wrapper .menuItemWrapper a.navItem")
        navigation = [{'theme': a.text.strip(), 'url': BASE_URL + a['href'] if a['href'].startswith('/') else a['href']}
                      for a in menu_items]
        themes_dict = {item['theme'].lower(): item['url'] for item in navigation if '/rubrique/' in item['url']}
        if themes_dict:
            first_key = next(iter(themes_dict))
            themes_dict.pop(first_key)
    except Exception as e:
        print("❌ Erreur menu :", e)
        return pd.DataFrame()

    articles_data = []

    for theme, base_link in themes_dict.items():
        print(f"📚 Thème : {theme}")
        for page_num in range(1, max_pages + 1):
            url = f"{base_link}/page/{page_num}" if page_num > 1 else base_link
            print(f"🔍 Page {page_num}...")

            try:
                soup = get_soup(url)
                articles = soup.select("section.sectionWithSidebar section.postsSectionCenter article")

                if not articles:
                    break

                for article in articles:
                    try:
                        title_tag = article.select_one("h2.archive-post-title a")
                        titre = title_tag.get_text(strip=True)
                        article_url = title_tag['href']
                        auteur = article.select_one("span.archive-post-author")
                        date = article.select_one("span.archive-post-date")
                        auteur = auteur.get_text(strip=True) if auteur else "Auteur inconnu"
                        date = date.get_text(strip=True) if date else "Date inconnue"
                        article_soup = get_soup(article_url)
                        content_tag = article_soup.select_one("div.articleLeftContainer article div.article-detail-content123")
                        contenu = content_tag.get_text(separator="\n", strip=True) if content_tag else "Contenu vide"

                        articles_data.append({
                            "theme": theme,
                            "titre": titre,
                            "date": date,
                            "auteur": auteur,
                            "contenu": contenu
                        })

                    except Exception as e:
                        print(f"⚠ Erreur article : {e}")

            except Exception as e:
                print(f"❌ Erreur page {page_num} : {e}")
                break

    df = pd.DataFrame(articles_data)
    print("✅ Scraping terminé :", len(df), "articles")

    os.makedirs("output", exist_ok=True)
    filename = f"output/senego_articles_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
    df.to_csv(filename, index=False)
    print(f"📁 Données sauvegardées dans {filename}")

if __name__ == "__main__":
    scrappe_senego(max_pages=1)
