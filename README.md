# <center>École nationale de la statistique et de l'analyse économique (ENSAE) - Pierre NDIAYE</center>
## <center>Projet de Web Scraping</center>
### <center>📰 Analyse des tendances médiatiques, topic modeling</center>

<center>Réalisé par :</center>  
<center><strong>Ahmed Firhoun OUMAROU SOULEYE</strong></center>  
<center><strong>Mamadou Saïdou DIALLO</strong></center>  
<center><em>Étudiants en AS3 - Option Data Science</em></center>

<center>Cours tenu par :</center>  
<center><strong>M. Baye Demba DIACK</strong></center>  
<center><em>Chef du Bureau des Données et des Solutions informatique (BDSI)</em></center>  
<center>Année académique 2024-2025</center>

---

> Collecte automatisée et analyse des tendances d'actualités sénégalaises avec du Topic Modeling LDA

## 🎯 Description

Ce projet automatise la collecte d'articles de presse sénégalais depuis **SeneWeb** et **Senego**, puis utilise des techniques de **Topic Modeling** avec l'algorithme **LDA (Latent Dirichlet Allocation)** pour identifier les sujets d'actualité les plus populaires.

### ✨ Fonctionnalités principales
- 🕷️ **Web scraping automatisé** des sites d'actualités sénégalais
- 🧠 **Topic Modeling** avec LDA pour identifier les tendances
- ⚙️ **Automatisation complète** via GitHub Actions
- 📊 **Interface interactive** avec Dash (voir dépôt séparé: https://github.com/zimbo-hur/app_sene_scraper)
- 🔄 **Réentraînement périodique** des modèles

## 🏗️ Architecture du Projet

```
├── 📄 articles_scraped.csv      # Données collectées
├── 🐍 scraper.py               # Script de scraping
├── 🧠 lda.py                   # Modèle Topic Modeling
├── 📓 Notebook_NLP.ipynb       # Analyse exploratoire
├── 📋 requirements.txt         # Dépendances Python
├── .github/workflows/          # Automatisation CI/CD
│   ├── scrape.yml             # Scraping quotidien
│   └── lda.yml                # Réentraînement hebdomadaire
├── docs/                      # Documentation
│   ├── architecture.pptx      # Document d'architecture
│   ├── resume_projet.docx     # Résumé du projet
└── models/                    # Modèles sauvegardés
    ├── best_lda_model.joblib  # Modèle LDA optimisé
    └── vectorizer.joblib      # Vectoriseur de texte
```

## 🚀 Installation

### Prérequis
- Python 3.12+
- Git

### Installation des dépendances
```bash
git clone https://github.com/votre-username/actu-scraping-lda.git
cd actu-scraping-lda
pip install -r requirements.txt
```

## 📖 Utilisation

### 1. Scraping manuel
```bash
python scraper.py
```
Collecte les derniers articles depuis SeneWeb et Senego et les sauvegarde dans `articles_scraped.csv`.

### 2. Entraînement du modèle LDA
```bash
python lda.py
```
- Charge les données depuis le CSV
- Préprocesse le texte (nettoyage, tokenisation)
- Entraîne le modèle LDA
- Sauvegarde le meilleur modèle dans `/models/`

### 3. Analyse exploratoire
Ouvrez `Notebook_NLP.ipynb` dans Jupyter pour explorer les données et visualiser les résultats du Topic Modeling de manière rapide.

## 🤖 Automatisation

Le projet utilise **GitHub Actions** pour automatiser les tâches :

### Scraping Quotidien
- **Déclencheur** : Tous les jours à 1H GMT
- **Action** : Exécute `scraper.py` et commit les nouvelles données
- **Fichier** : `.github/workflows/scrape.yml`

### Réentraînement Hebdomadaire
- **Déclencheur** : Tous les lundi à 6h GMT
- **Action** : Réentraîne le modèle LDA avec les données actualisées
- **Fichier** : `.github/workflows/lda.yml`


## 📊 Données Collectées

Pour chaque article, les informations suivantes sont extraites :
- **Titre** - Titre de l'article
- **Auteur** - Auteur de l'article
- **Date** - Date de publication
- **Contenu** - Texte complet de l'article
- **Source** - Site web source (SeneWeb/Senego)
- **URL** - Lien vers l'article original


## 🧠 Topic Modeling

### Processus LDA
1. **Préprocessing** : Nettoyage du texte, suppression des mots vides
2. **Vectorisation** : Transformation du texte en vecteurs CountVectorizer
3. **Modélisation** : Application de l'algorithme LDA et optimisation des hyperparamètres
4. **Sauvegarde** : Stockage du meilleur modèle et du vectorizer


## 🏫 Contexte Académique

Ce projet s'inscrit dans le cadre du cours de Web Scraping dispensé par **M. Baye Demba DIACK**, Chef du Bureau des Données et des Solutions informatique (BDSI) à l'Agence nationale de la Statistique et de la Démographie (ANSD).

