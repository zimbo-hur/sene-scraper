# Manipulation des données
import pandas as pd
import re
import os

# Traitement de texte
import nltk
from nltk.corpus import stopwords
from unidecode import unidecode

# Modélisation thématique
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS
from sklearn.decomposition import LatentDirichletAllocation

# Optimisation hyperparamètres
import optuna

# Sauvegarde de modèles
import joblib

# Utilitaires
from sklearn.model_selection import train_test_split
from wordcloud import STOPWORDS

# Charger les données (exemple)
df = pd.read_csv("articles_scraped.csv")
df = df.dropna(subset=['contenu'])
print(f"📊 {len(df)} articles avec contenu chargés")

# Initialisation de NLTK
# Télécharger les stopwords français de NLTK si nécessaire
try:
    nltk.download('stopwords', quiet=True)
    print("✅ Stopwords NLTK téléchargés")
except Exception as e:
    print(f"⚠️ Erreur téléchargement stopwords: {e}")

# Fusionner les stopwords : WordCloud + NLTK + tes mots perso
custom_stopwords = set(STOPWORDS)
try:
    custom_stopwords.update(stopwords.words('french'))
except:
    print("⚠️ Stopwords français non disponibles")
custom_stopwords.update(ENGLISH_STOP_WORDS)  # Parfois utile si mélange anglais/français

# Ajouter tes propres mots
custom_stopwords.update([
    'selon', 'ce', 'cet', 'cette', 'dont', 'ainsi', 'hgroupe', 'ete', 'aussi','field','plus',
    'dun', 'dune', 'cest', 'comme', 'juin', 'apres', 'deux', 'senegal','senegalais','juingroupe',
    'sest','lors','egalement','sans','notamment', 'quil', 'tout', 'tous', 'fait','entre',
    'titre','plusieurs','sous','faire','bien','meme','avant','toujours','cela','face','tres',
    'leur','leurs','toute','toutes','vers','quelle','jai','etait','etais','senegalaise',
    'alors','encore','avoir','nest', 'etre',
])

# Prétraitement du texte
def preprocess(text):
    if pd.isna(text):  # Gestion des valeurs NaN
        return ""
    text = str(text).lower()                      # minuscules
    text = unidecode(text)                        # enlever les accents
    text = re.sub(r'\d+', '', text)               # enlever les chiffres
    text = re.sub(r'[^\w\s]', '', text)           # enlever la ponctuation
    tokens = text.split()                         # tokenisation simple
    tokens = [word for word in tokens if word not in custom_stopwords and len(word) > 2]
    return ' '.join(tokens)

print("🔄 Prétraitement des textes...")
df['cleaned_content'] = df['contenu'].apply(preprocess)

# Filtrer les textes vides après prétraitement
df = df[df['cleaned_content'].str.len() > 10]
print(f"📝 {len(df)} articles après prétraitement")

# Vectorisation avec CountVectorizer
# Créer un vecteur de type Bag of Words
print("🔤 Vectorisation...")
vectorizer = CountVectorizer(max_df=0.95, min_df=2) 
X = vectorizer.fit_transform(df['cleaned_content'])

print(f"📊 Matrice: {X.shape[0]} documents, {X.shape[1]} mots")

X_train, X_val = train_test_split(X, test_size=0.2, random_state=42)

def objective(trial):
    n_components = trial.suggest_int('n_components', 3, 15)
    learning_decay = trial.suggest_float('learning_decay', 0.5, 0.9)
    learning_offset = trial.suggest_int('learning_offset', 10, 100)

    lda = LatentDirichletAllocation(
        n_components=n_components,
        learning_method='online',
        learning_decay=learning_decay,
        learning_offset=learning_offset,
        max_iter=10,
        random_state=42
    )
    
    try:
        lda.fit(X_train)
        # On évalue la perplexité sur validation
        perplexity = lda.perplexity(X_val)
        return perplexity  # objectif : minimiser la perplexité
    except Exception as e:
        print(f"⚠️ Erreur dans un trial: {e}")
        return float('inf')  # Retourner une valeur très élevée en cas d'erreur

print("🎯 Optimisation des hyperparamètres...")
study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=30)

print("Meilleurs paramètres : ", study.best_params)
print("Meilleure perplexité :", study.best_value)

best_params = study.best_params

print("🏋️ Entraînement final du modèle...")
best_lda = LatentDirichletAllocation(
    n_components=best_params['n_components'],
    learning_method='online',
    learning_decay=best_params['learning_decay'],
    learning_offset=best_params['learning_offset'],
    max_iter=20,   # ou plus, pour un entraînement complet
    random_state=42
)

best_lda.fit(X) 

# Créer le dossier models s'il n'existe pas
os.makedirs('./models', exist_ok=True)

# Sauvegarder le modèle
print("💾 Sauvegarde du modèle...")
joblib.dump(best_lda, './models/best_lda_model.joblib')

# Sauvegarder aussi le vectorizer pour pouvoir l'utiliser plus tard
joblib.dump(vectorizer, './models/vectorizer.joblib')

print("✅ Modèle sauvegardé avec succès!")

# Test de chargement
print("🔍 Test de chargement...")
try:
    best_lda_loaded = joblib.load('./models/best_lda_model.joblib')
    vectorizer_loaded = joblib.load('./models/vectorizer.joblib')
    print("✅ Test de chargement réussi!")
except Exception as e:
    print(f"❌ Erreur lors du test de chargement: {e}")