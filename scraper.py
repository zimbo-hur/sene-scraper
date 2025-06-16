#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time
import sys
import os

class UnifiedNewsScraper:
    def __init__(self, main_csv_file='articles_scraped.csv'):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.all_articles = []
        self.main_csv_file = main_csv_file
        self.existing_urls = set()
        
        # Charger les URLs existantes pour éviter les doublons
        self.load_existing_urls()
    
    def load_existing_urls(self):
        """Charge les URLs existantes pour éviter les doublons"""
        if os.path.exists(self.main_csv_file):
            try:
                existing_df = pd.read_csv(self.main_csv_file)
                if 'url' in existing_df.columns:
                    self.existing_urls = set(existing_df['url'].dropna().tolist())
                    print(f"📂 Fichier existant chargé: {len(self.existing_urls)} URLs existantes")
                else:
                    print("⚠️ Colonne 'url' introuvable dans le fichier existant")
            except Exception as e:
                print(f"⚠️ Erreur chargement fichier existant: {e}")
        else:
            print("📄 Nouveau fichier - aucune donnée existante")
    
    def is_duplicate_url(self, url):
        """Vérifie si l'URL existe déjà"""
        return url in self.existing_urls
    
    def harmonize_theme(self, original_theme):
        """Harmonise les thèmes selon les règles spécifiées"""
        if not original_theme or pd.isna(original_theme):
            return "Autre"
        
        theme = str(original_theme).strip()
        theme_lower = theme.lower()
        
        # Règles de mapping spécifiques
        theme_mapping = {
            # Politique
            'politique': 'Politique',
            
            # Economie
            'economie': 'Economie',
            'économie': 'Economie',
            'pêche': 'Economie',
            'peche': 'Economie',
            
            # Sport
            'sport': 'Sport',
            'sports': 'Sport',
            'football': 'Sport',
            'senenews sport': 'Sport',
            
            # People/Célébrités
            'people': 'People',
            'célébrités': 'People',
            'celebrites': 'People',
            'senenews people': 'People',
            
            # Société
            'société': 'Société',
            'societe': 'Société',
            'justice': 'Société',
            
            # International
            'international': 'International',
            'afrique': 'International',
            'afrique - actualité senenews people': 'International',
            
            # Multimedia/Divertissement
            'multimedia': 'Multimedia',
            'multimédia': 'Multimedia',
            'clip vidéo': 'Multimedia',
            'senenews tv': 'Multimedia',
            
            # Contributions/Opinion
            'contributions': 'Opinion',
            'contribution': 'Opinion',
            
            # Météo
            'meteo': 'Météo',
            'météo': 'Météo',
            
            # Premium/Spécial
            'articles premium': 'Premium',
            'premium': 'Premium',
            
            # Live/Direct
            'en direct': 'Live',
            'live': 'Live',
            'en direct / live': 'Live'
        }
        
        # Cas spéciaux pour les thèmes commençant par "Sénégal - Actualités >"
        if theme.startswith("Sénégal - Actualités"):
            # Cas spéciaux pour "Actualité"
            if (theme == "Sénégal - Actualités" or 
                "A-La-Une" in theme or 
                "Notification" in theme):
                return "Actualité"
            
            # Extraire le terme après "Sénégal - Actualités >"
            if ">" in theme:
                parts = theme.split(">")
                if len(parts) >= 2:
                    main_theme = parts[1].strip()
                    # Si il y a encore des sous-catégories, prendre la première
                    if ">" in main_theme:
                        main_theme = main_theme.split(">")[0].strip()
                    
                    # Appliquer le mapping
                    main_theme_lower = main_theme.lower()
                    if main_theme_lower in theme_mapping:
                        return theme_mapping[main_theme_lower]
                    else:
                        # Capitaliser proprement
                        return main_theme.capitalize()
        
        # Vérifier le mapping direct
        if theme_lower in theme_mapping:
            return theme_mapping[theme_lower]
        
        # Recherche de mots-clés dans le thème
        for keyword, mapped_theme in theme_mapping.items():
            if keyword in theme_lower:
                return mapped_theme
        
        # Cas par défaut
        if theme_lower in ['actualités', 'actualites', 'actualité', 'actualite']:
            return "Actualité"
        
        # Si aucune règle ne s'applique, capitaliser le premier mot
        first_word = theme.split()[0] if theme.split() else theme
        if len(first_word) > 2:
            return first_word.capitalize()
        
        return "Autre"
    
    def parse_french_date(self, date_str):
        """Convertit une date française en format datetime"""
        months_fr = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
            'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }
        
        try:
            date_str = date_str.strip().lower()
            pattern = r'(\d{1,2})\s+(\w+)\s+(\d{4})'
            match = re.search(pattern, date_str)
            
            if match:
                day = int(match.group(1))
                month_name = match.group(2)
                year = int(match.group(3))
                
                if month_name in months_fr:
                    month = months_fr[month_name]
                    return datetime(year, month, day)
        except Exception as e:
            print(f"⚠ Erreur parsing date française '{date_str}': {e}")
        
        return None
    
    def parse_senenews_date(self, date_string):
        """Parse date from SeneNews format '12/06/2025 à 13:05'"""
        try:
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})\s+à\s+(\d{2}:\d{2})', date_string)
            if date_match:
                date_part = date_match.group(1)
                time_part = date_match.group(2)
                return datetime.strptime(f"{date_part} {time_part}", "%d/%m/%Y %H:%M")
        except Exception as e:
            print(f"⚠ Erreur parsing date SeneNews '{date_string}': {e}")
        return None
    
    def is_date_in_range(self, article_date, start_date, end_date):
        """Vérifier si la date de l'article est dans l'intervalle spécifié"""
        if not article_date:
            return False
        return start_date <= article_date <= end_date
    
    def get_soup(self, url):
        """Récupérer et parser une page web"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ Erreur récupération {url}: {e}")
            return None
    
    def scrape_senenews(self, start_date, end_date, max_pages=10):
        """Scraper SeneNews"""
        print("\n🔥 SCRAPING SENENEWS 🔥")
        base_url = "https://www.senenews.com"
        articles_found = 0
        
        for page in range(1, max_pages + 1):
            print(f"\n📄 SeneNews - Page {page}")
            
            if page == 1:
                page_url = f"{base_url}/category/actualites"
            else:
                page_url = f"{base_url}/category/actualites/page/{page}"
            
            soup = self.get_soup(page_url)
            if not soup:
                continue
            
            # Récupérer les liens d'articles
            article_links = []
            selectors = [
                'h2 a[href*="senenews.com"]',
                'h3 a[href*="senenews.com"]',
                '.entry-title a',
                'article a[href*="senenews.com"]',
                'a[href*="/20"]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and 'senenews.com' in href:
                        full_url = urljoin(base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
            
            if not article_links:
                print(f"❌ Aucun article trouvé sur la page {page}")
                break
            
            print(f"🔍 {len(article_links)} articles trouvés")
            
            page_articles_in_range = 0
            articles_too_old = 0
            articles_skipped_duplicate = 0
            
            for article_url in article_links:
                # Vérifier si l'article existe déjà
                if self.is_duplicate_url(article_url):
                    articles_skipped_duplicate += 1
                    continue
                
                article_data = self.extract_senenews_article(article_url)
                
                if article_data and article_data['date']:
                    article_date = self.parse_senenews_date(article_data['date'])
                    
                    if article_date:
                        if self.is_date_in_range(article_date, start_date, end_date):
                            article_data['source'] = 'SeneNews'
                            article_data['theme_original'] = article_data.get('rubrique', 'Actualités')
                            article_data['date_parsed'] = article_date.strftime('%Y-%m-%d %H:%M')
                            self.all_articles.append(article_data)
                            self.existing_urls.add(article_url)  # Ajouter à la liste des URLs existantes
                            page_articles_in_range += 1
                            articles_found += 1
                            print(f"✅ Nouvel article ajouté: {article_data['titre'][:50]}...")
                        elif article_date < start_date:
                            articles_too_old += 1
                
                time.sleep(1)
            
            print(f"📊 Page {page}: {page_articles_in_range} nouveaux, {articles_skipped_duplicate} doublons, {articles_too_old} trop anciens")
            
            if articles_too_old > page_articles_in_range and page_articles_in_range == 0:
                print("🛑 Articles trop anciens, arrêt du scraping SeneNews")
                break
            
            time.sleep(2)
        
        print(f"✅ SeneNews terminé: {articles_found} nouveaux articles récupérés")
        return articles_found
    
    def extract_senenews_article(self, article_url):
        """Extraire les données d'un article SeneNews"""
        try:
            soup = self.get_soup(article_url)
            if not soup:
                return None
            
            data = {
                'url': article_url,
                'titre': '',
                'auteur': '',
                'date': '',
                'rubrique': '',
                'contenu': ''
            }
            
            # Titre
            title_elem = soup.find('h1', class_='entry-title')
            if title_elem:
                data['titre'] = title_elem.get_text(strip=True)
            
            # Auteur
            author_elem = soup.find('a', class_='aSingle')
            if author_elem:
                data['auteur'] = author_elem.get_text(strip=True)
            
            # Date
            time_elem = soup.find('time')
            if time_elem:
                date_span = time_elem.find('span', class_='date updated')
                if date_span:
                    data['date'] = date_span.get_text(strip=True)
            
            # Rubrique
            breadcrumb = []
            nav_links = soup.select('p a[href*="category"]')
            for link in nav_links:
                breadcrumb.append(link.get_text(strip=True))
            data['rubrique'] = ' > '.join(breadcrumb) if breadcrumb else 'Actualités'
            
            # Contenu
            content_paragraphs = []
            content_area = soup.find('div', id='articleBody') or soup.find('div', class_='content-single-full')
            
            if content_area:
                paragraphs = content_area.find_all('p')
                for p in paragraphs:
                    if p.find_parent('div', class_='responsiveinpost'):
                        continue
                    if p.find_parent('ins', class_='adsbygoogle'):
                        continue
                    
                    text = p.get_text(strip=True)
                    if (text and len(text) > 30 and 
                        not any(skip in text.lower() for skip in ['partager', 'suivez', 'lire aussi', 'tags:', 'par ', 'source:', 'facebook', 'twitter', 'whatsapp', 'advertisement'])):
                        content_paragraphs.append(text)
            
            data['contenu'] = '\n\n'.join(content_paragraphs)
            return data
            
        except Exception as e:
            print(f"❌ Erreur extraction SeneNews {article_url}: {e}")
            return None
    
    def scrape_senego(self, start_date, end_date, max_pages=10):
        """Scraper Senego"""
        print("\n🌟 SCRAPING SENEGO 🌟")
        base_url = "https://senego.com"
        articles_found = 0
        
        # Récupérer les thèmes
        try:
            soup = self.get_soup(base_url)
            if not soup:
                return 0
            
            menu_items = soup.select("header nav.nav .top-menu-content-wrapper .menuItemWrapper a.navItem")
            navigation = [{'theme': a.text.strip(), 'url': base_url + a['href'] if a['href'].startswith('/') else a['href']}
                         for a in menu_items]
            themes_dict = {item['theme'].lower(): item['url'] for item in navigation if '/rubrique/' in item['url']}
            
            if themes_dict:
                first_key = next(iter(themes_dict))
                themes_dict.pop(first_key)
                
        except Exception as e:
            print(f"❌ Erreur récupération menu Senego: {e}")
            return 0
        
        # Scraper chaque thème
        for theme, base_link in themes_dict.items():
            print(f"\n📚 Senego - Thème: {theme}")
            theme_articles_found = 0
            should_continue_theme = True
            
            for page_num in range(1, max_pages + 1):
                if not should_continue_theme:
                    break
                    
                url = f"{base_link}/page/{page_num}" if page_num > 1 else base_link
                print(f"📄 Page {page_num}")
                
                soup = self.get_soup(url)
                if not soup:
                    break
                
                articles = soup.select("section.sectionWithSidebar section.postsSectionCenter article")
                if not articles:
                    break
                
                page_articles_in_range = 0
                page_articles_too_old = 0
                articles_skipped_duplicate = 0
                
                for article in articles:
                    try:
                        title_tag = article.select_one("h2.archive-post-title a")
                        if not title_tag:
                            continue
                            
                        titre = title_tag.get_text(strip=True)
                        article_url = title_tag['href']
                        
                        # Vérifier si l'article existe déjà
                        if self.is_duplicate_url(article_url):
                            articles_skipped_duplicate += 1
                            continue
                        
                        auteur_elem = article.select_one("span.archive-post-author")
                        date_elem = article.select_one("span.archive-post-date")
                        
                        auteur = auteur_elem.get_text(strip=True) if auteur_elem else "Auteur inconnu"
                        date_str = date_elem.get_text(strip=True) if date_elem else "Date inconnue"
                        
                        # Parser la date
                        article_date = self.parse_french_date(date_str)
                        
                        # Vérifier si dans la période
                        if article_date:
                            if self.is_date_in_range(article_date, start_date, end_date):
                                # Récupérer le contenu
                                article_soup = self.get_soup(article_url)
                                if article_soup:
                                    content_tag = article_soup.select_one("div.articleLeftContainer article div.article-detail-content123")
                                    contenu = content_tag.get_text(separator="\n", strip=True) if content_tag else "Contenu vide"
                                    
                                    self.all_articles.append({
                                        "source": "Senego",
                                        "theme_original": theme,
                                        "titre": titre,
                                        "date": date_str,
                                        "date_parsed": article_date.strftime('%Y-%m-%d'),
                                        "auteur": auteur,
                                        "contenu": contenu,
                                        "url": article_url,
                                        "rubrique": theme
                                    })
                                    
                                    self.existing_urls.add(article_url)  # Ajouter à la liste des URLs existantes
                                    page_articles_in_range += 1
                                    theme_articles_found += 1
                                    articles_found += 1
                                    print(f"✅ Nouvel article ajouté: {titre[:50]}...")
                            elif article_date < start_date:
                                page_articles_too_old += 1
                        
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"❌ Erreur article Senego: {e}")
                
                print(f"📊 Page {page_num}: {page_articles_in_range} nouveaux, {articles_skipped_duplicate} doublons")
                
                # Arrêter si tous les articles sont trop anciens
                if page_articles_too_old > 0 and page_articles_in_range == 0:
                    print(f"🛑 Arrêt thème {theme}: articles trop anciens")
                    should_continue_theme = False
                
                time.sleep(1)
            
            print(f"📊 Thème {theme}: {theme_articles_found} nouveaux articles")
        
        print(f"✅ Senego terminé: {articles_found} nouveaux articles récupérés")
        return articles_found
    
    def process_themes(self):
        """Traite et harmonise tous les thèmes après collecte"""
        print("\n🔄 HARMONISATION DES THÈMES")
        
        if not self.all_articles:
            print("❌ Aucun nouvel article à traiter")
            return
        
        # Créer le DataFrame
        df = pd.DataFrame(self.all_articles)
        
        # Afficher les thèmes originaux pour debug
        print("\n📊 Thèmes originaux trouvés:")
        if 'theme_original' in df.columns:
            theme_counts = df['theme_original'].value_counts()
            for theme, count in theme_counts.items():
                print(f"   • {theme}: {count} articles")
        
        # Harmoniser les thèmes
        if 'theme_original' in df.columns:
            df['theme'] = df['theme_original'].apply(self.harmonize_theme)
        elif 'theme' in df.columns:
            df['theme'] = df['theme'].apply(self.harmonize_theme)
        else:
            df['theme'] = 'Autre'
        
        # Afficher les thèmes harmonisés
        print("\n✨ Thèmes harmonisés:")
        theme_counts_harmonized = df['theme'].value_counts()
        for theme, count in theme_counts_harmonized.items():
            print(f"   • {theme}: {count} articles")
        
        # Supprimer les colonnes temporaires
        columns_to_remove = ['theme_original', 'rubrique']
        for col in columns_to_remove:
            if col in df.columns:
                df = df.drop(columns=[col])
        
        # Mettre à jour all_articles
        self.all_articles = df.to_dict('records')
        
        print(f"✅ Harmonisation terminée: {len(df['theme'].unique())} thèmes uniques")
    
    def merge_and_save_data(self):
        """Fusionne les nouvelles données avec le fichier principal et sauvegarde"""
        if not self.all_articles:
            print("❌ Aucune nouvelle donnée à fusionner")
            return False
        
        print(f"\n🔄 FUSION DES DONNÉES")
        
        # Créer DataFrame des nouvelles données
        new_df = pd.DataFrame(self.all_articles)
        print(f"📥 Nouvelles données: {len(new_df)} articles")
        
        # Charger les données existantes si le fichier existe
        if os.path.exists(self.main_csv_file):
            try:
                existing_df = pd.read_csv(self.main_csv_file)
                print(f"📂 Données existantes: {len(existing_df)} articles")
                
                # Combiner les données
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # Dédupliquer par URL (garder la version la plus récente)
                combined_df = combined_df.drop_duplicates(subset=['url'], keep='last')
                print(f"🔧 Après déduplication: {len(combined_df)} articles")
                
            except Exception as e:
                print(f"⚠️ Erreur lecture fichier existant: {e}")
                combined_df = new_df
        else:
            print("📄 Création du fichier principal")
            combined_df = new_df
        
        # Trier par date si possible
        if 'date_parsed' in combined_df.columns:
            combined_df = combined_df.sort_values('date_parsed', ascending=False)
        
        # Réorganiser les colonnes
        columns_order = ['source', 'theme', 'titre', 'date', 'date_parsed', 'auteur', 'contenu', 'url']
        existing_columns = [col for col in columns_order if col in combined_df.columns]
        combined_df = combined_df[existing_columns]
        
        # Sauvegarder
        try:
            combined_df.to_csv(self.main_csv_file, index=False, encoding='utf-8')
            print(f"💾 Fichier principal mis à jour: {self.main_csv_file}")
            print(f"📊 Total articles: {len(combined_df)}")
            
            # Afficher la répartition des thèmes
            if 'theme' in combined_df.columns:
                print(f"\n📊 Répartition des thèmes (top 10):")
                theme_distribution = combined_df['theme'].value_counts().head(10)
                for theme, count in theme_distribution.items():
                    percentage = (count / len(combined_df)) * 100
                    print(f"   • {theme}: {count} articles ({percentage:.1f}%)")
            
            # Afficher les nouvelles données par source
            if len(new_df) > 0:
                print(f"\n📈 Nouveaux articles par source:")
                source_counts = new_df['source'].value_counts()
                for source, count in source_counts.items():
                    print(f"   • {source}: {count} nouveaux articles")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def scrape_all(self, days_back=1, max_pages=10):
        """Scraper les deux sites et fusionner avec les données existantes"""
        print(f"🚀 SCRAPER UNIFIÉ - Récupération des {days_back} derniers jours")
        
        # Calculer les dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        print(f"📅 Période: {start_date.strftime('%d/%m/%Y %H:%M')} - {end_date.strftime('%d/%m/%Y %H:%M')}")
        print(f"📂 URLs existantes chargées: {len(self.existing_urls)}")
        
        # Scraper les deux sites
        senenews_count = self.scrape_senenews(start_date, end_date, max_pages)
        senego_count = self.scrape_senego(start_date, end_date, max_pages)
        
        # Traiter les thèmes après collecte
        self.process_themes()
        
        total_new_articles = len(self.all_articles)
        
        print(f"\n🎉 RÉSUMÉ FINAL:")
        print(f"   📰 SeneNews: {senenews_count} nouveaux articles")
        print(f"   📰 Senego: {senego_count} nouveaux articles")
        print(f"   📰 Total nouveaux: {total_new_articles} articles")
        
        # Fusionner et sauvegarder
        if total_new_articles > 0:
            success = self.merge_and_save_data()
            return success
        else:
            print("ℹ️ Aucun nouvel article trouvé")
            return False

def main():
    scraper = UnifiedNewsScraper()
    
    try:
        # Scraper les deux sites et fusionner
        success = scraper.scrape_all(days_back=1, max_pages=15)
        
        if success:
            print(f"\n🎯 SCRAPING ET FUSION TERMINÉS AVEC SUCCÈS!")
            print(f"📄 Fichier principal mis à jour: {scraper.main_csv_file}")
            print(f"🔗 Sources scrapées: SeneNews + Senego")
            print(f"🏷️ Thèmes harmonisés automatiquement")
            print(f"🔄 Données fusionnées avec déduplication")
        else:
            print(f"\n📊 SCRAPING TERMINÉ - Aucune nouvelle donnée")
            print(f"📄 Fichier principal: {scraper.main_csv_file}")
    
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur pendant le scraping: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()