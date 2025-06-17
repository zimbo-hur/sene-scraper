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

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI/CD-GitHub%20Actions-orange.svg)](https://github.com/features/actions)

## 🎯 Description

Ce projet automatise la collecte d'articles de presse sénégalais depuis **SeneWeb** et **Senego**, puis utilise des techniques de **Topic Modeling** avec l'algorithme **LDA (Latent Dirichlet Allocation)** pour identifier les sujets d'actualité les plus populaires.

### ✨ Fonctionnalités principales
- 🕷️ **Web scraping automatisé** des sites d'actualités sénégalais
- 🧠 **Topic Modeling** avec LDA pour identifier les tendances
- ⚙️ **Automatisation complète** via GitHub Actions
- 📊 **Interface interactive** avec Dash (voir dépôt séparé)
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
│   └── Liens.txt             # Liens utiles
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
Ouvrez `Notebook_NLP.ipynb` dans Jupyter pour explorer les données et visualiser les résultats du Topic Modeling.

## 🤖 Automatisation

Le projet utilise **GitHub Actions** pour automatiser les tâches :

### Scraping Quotidien
- **Déclencheur** : Tous les jours à 6h UTC
- **Action** : Exécute `scraper.py` et commit les nouvelles données
- **Fichier** : `.github/workflows/scrape.yml`

### Réentraînement Hebdomadaire
- **Déclencheur** : Tous les dimanches
- **Action** : Réentraîne le modèle LDA avec les nouvelles données
- **Fichier** : `.github/workflows/lda.yml`

## 🛠️ Technologies Utilisées

### Backend
- **Python 3.12** - Langage principal
- **Scikit-learn** - Algorithme LDA
- **NLTK** - Traitement du langage naturel
- **Pandas** - Manipulation des données
- **BeautifulSoup** - Web scraping

### Infrastructure
- **GitHub Actions** - CI/CD et automatisation
- **Joblib** - Sérialisation des modèles
- **CSV** - Stockage des données

## 📊 Données Collectées

Pour chaque article, les informations suivantes sont extraites :
- **Titre** - Titre de l'article
- **Date** - Date de publication
- **Contenu** - Texte complet de l'article
- **Source** - Site web source (SeneWeb/Senego)
- **URL** - Lien vers l'article original

## 🧠 Topic Modeling

### Processus LDA
1. **Préprocessing** : Nettoyage du texte, suppression des mots vides
2. **Vectorisation** : Transformation du texte en vecteurs TF-IDF
3. **Modélisation** : Application de l'algorithme LDA
4. **Évaluation** : Calcul du Coherence Score
5. **Sauvegarde** : Stockage du meilleur modèle

### Métriques d'évaluation
- **Coherence Score** : Mesure la cohérence sémantique des topics
- **Perplexity** : Évalue la qualité prédictive du modèle

## 📈 Monitoring et Performance

### Métriques suivies
- Nombre d'articles collectés par jour
- Performance du scraping (taux de succès)
- Qualité des topics identifiés
- Temps d'exécution des processus

## 🔧 Configuration

### Variables d'environnement
Aucune variable d'environnement requise pour l'utilisation de base.

### Personnalisation
- **Sources** : Modifiez `scraper.py` pour ajouter d'autres sites
- **Modèle** : Ajustez les paramètres LDA dans `lda.py`
- **Fréquence** : Modifiez les cron dans les workflows GitHub Actions

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📝 Roadmap

- [ ] Extension à d'autres sources (Le Soleil, BBC Afrique)
- [ ] Analyse de sentiment
- [ ] Support multilingue (français/wolof)
- [ ] API REST pour accès externe
- [ ] Détection automatique d'événements

## 🐛 Problèmes Connus

- Le scraping peut échouer si les sites changent leur structure HTML
- Les modèles peuvent nécessiter un réajustement avec l'évolution du vocabulaire

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteurs

- **Ahmed Firhoun OUMAROU SOULEYE** - *Étudiant AS3 Data Science* - [@ahmed-github](https://github.com/ahmed-username)
- **Mamadou Saïdou DIALLO** - *Étudiant AS3 Data Science* - [@mamadou-github](https://github.com/mamadou-username)

## 🏫 Contexte Académique

Ce projet s'inscrit dans le cadre du cours de Web Scraping dispensé par **M. Baye Demba DIACK**, Chef du Bureau des Données et des Solutions informatique (BDSI) à l'École nationale de la statistique et de l'analyse économique (ENSAE) - Pierre NDIAYE.

## 🙏 Remerciements

- **M. Baye Demba DIACK** pour son encadrement et ses conseils précieux
- L'**ENSAE Pierre NDIAYE** pour le cadre académique et les ressources mises à disposition
- **SeneWeb** et **Senego** pour les données d'actualités accessibles
- La communauté open-source pour les outils utilisés
- Les contributeurs du projet

---

⭐ N'oubliez pas de mettre une étoile si ce projet vous a été utile !
