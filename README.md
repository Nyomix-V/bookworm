# Through the Looking-Glass : bookworm.py

Ce dépôt contient le moteur de traitement automatique du langage naturel (NLP) `bookworm.py` développé pour le projet **Through the Looking-Glass**. C'est un outil léger conçu pour aider les éditeurs et correcteurs à générer instantanément des fiches de lecture structurées ("book cards") au format JSON à partir d'e-books du Projet Gutenberg.

---

## 🎯 Objectifs & Contraintes d'Architecture

Contrairement aux solutions modernes basées sur de gros modèles de langage (LLMs) ou des modèles de Deep Learning massifs (Transformers), `bookworm.py` a été développé sous des contraintes strictes :
1. **Exécution ultra-rapide** : Analyse complète d'un livre (même volumineux comme *Dracula*) et génération de la fiche en moins de 3 secondes (bien en dessous de la limite de 15 secondes).
2. **Fonctionnement 100% hors-ligne & léger** : Pas de GPU nécessaire, pas de dépendances lourdes (pas de PyTorch, TensorFlow ou de modèles spaCy de plusieurs centaines de Mo).
3. **Zéro boîte noire** : Les décisions algorithmiques (classification de genre, résumés, détection d'entités) reposent sur des modèles explicables et des règles linguistiques déterministes.

---

## 🛠️ Installation & Configuration

### Prérequis
Le script fonctionne avec Python 3.8+ et nécessite les bibliothèques suivantes :
* `nltk` (Tokenisation, POS Tagging, NER de base)
* `numpy` (Calculs vectoriels)
* `pandas` (Lecture du catalogue)
* `scikit-learn` (Vectorisation TF-IDF et similarité cosinus)

### Installation
Installez les dépendances avec pip :
```bash
pip install -r requirements.txt
```

### Catalogue Project Gutenberg
Les commandes `--info` et `--download` lisent le catalogue officiel du Projet Gutenberg, non inclus dans ce dépôt (fichier volumineux). Téléchargez-le à côté de `bookworm.py` :
```bash
curl -L -o pg_catalog.csv https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv
```

Au tout premier démarrage, le script télécharge automatiquement en tâche de fond les ressources NLTK nécessaires (`punkt`, `stopwords`, `wordnet`, `maxent_ne_chunker`, etc.).

---

## 📖 Tutoriel d'Utilisation (Étape par Étape)

Le script propose 11 commandes CLI correspondant aux étapes de traitement. Voici un parcours type d'analyse.

### Étape 1 : Obtenir les métadonnées et télécharger un livre
Pour afficher les informations d'un livre du catalogue (ex: ID 11 pour *Alice in Wonderland*) :
```bash
python bookworm.py --info 11
```
Pour télécharger le livre au format texte brut localement :
```bash
python bookworm.py --download 11
```

### Étape 2 : Nettoyer le texte
Pour nettoyer les en-têtes et pieds de page légaux du Projet Gutenberg :
```bash
python bookworm.py --clean "TEXTE_BRUT_ICI"
```

### Étape 3 : Découper le texte (Tokenisation)
Découper une phrase en mots (ou en phrases avec `--sent`), en retirant optionnellement la ponctuation (`--punct`) ou les mots vides (`--stop`) :
```bash
python bookworm.py --tokenize "Alice was beginning to get very tired." --punct --stop
```

### Étape 4 : Étiquetage grammatical (POS Tagging)
Assigner une catégorie grammaticale (Nom, Verbe, Adjectif...) à chaque mot :
```bash
python bookworm.py --postag "The Caterpillar was the first to speak"
```

### Étape 5 : Normaliser les mots
Réduire les mots à leur forme de base (lemmatisation par défaut, ou racinisation avec `--stem`) :
```bash
python bookworm.py --normalize "The games are going on better now"
```

### Étape 6 : Calculer la diversité lexicale
Calculer le nombre de mots uniques, le ratio Type-Token (TTR), les mots uniques n'apparaissant qu'une fois (Hapax), ainsi que la longueur moyenne des mots :
```bash
python bookworm.py --lexdiv 11
```

### Étape 7 : Modélisation thématique (Topic Modeling)
Extraire les 10 mots-clés thématiques les plus importants pour chacune des 10 sections chronologiques du livre :
```bash
python bookworm.py --topics 11
```

### Étape 8 : Reconnaissance d'Entités (NER)
Extraire les 10 personnages principaux et les 10 lieux les plus cités :
```bash
python bookworm.py --entities 11
```

### Étape 9 : Générer un résumé narratif
Générer un synopsis représentatif et chronologique du livre :
```bash
python bookworm.py --summarize 11
```

### Étape 10 : Calculer la similarité entre livres
Trouver les 5 livres les plus similaires au livre cible parmi la collection locale :
```bash
python bookworm.py --similar 11
```

### Étape 11 : Générer la fiche livre complète ("Book Card")
Exécuter l'ensemble du pipeline et renvoyer une fiche structurée complète au format JSON :
```bash
python bookworm.py --card 11
```

---

## 🧠 Explications Détaillées du Code

Voici le fonctionnement interne des briques NLP de `bookworm.py` :

### 1. Nettoyage de texte robuste (`_cleaner`)
* **Retrait des métadonnées** : Localise précisément le début et la fin de l'œuvre à l'aide de marqueurs comme `*** START OF THE PROJECT` et coupe la chaîne sans expressions régulières complexes. Cela évite le *catastrophic backtracking* qui figeait auparavant le programme sur les gros volumes.
* **Normalisation des guillemets et apostrophes** : Remplace les guillemets curly unicode (`“`, `”`, `‘`, `’`) et les caractères corrompus de conversion (`\ufffd`) par des guillemets simples (`'`) ou doubles (`"`) ASCII standard. Cela permet à NLTK de segmenter correctement les fins de phrases en présence de dialogues.
* **Linéarisation** : Remplace les retours à la ligne (`\n`) par des espaces simples pour éviter que le découpage de phrases ne soit interrompu au milieu d'une proposition.

### 2. Modélisation thématique par Section (`topic`)
* Le livre est découpé en 10 blocs temporels égaux.
* Un prétraitement lourd élimine les stopwords (anglais standards), les verbes narratifs omniprésents (`said`, `looked`), les mots vides propres à Gutenberg et les résidus de contractions grammaticales (`n't`, `ll`, `ve`, `re`).
* L'extraction thématique utilise une formule **TF-IDF avec IDF adouci** (exposant 0.5) appliquée à chaque bloc. Cette méthode algébrique est déterministe (contrairement à LDA qui est stochastique) et s'exécute en quelques millisecondes.

### 3. NER Hybride Heuristique (`entities`)
Pour éviter d'importer des modèles de Deep Learning géants, nous utilisons le chunker de base de NLTK couplé à des règles contextuelles robustes :
* **Détection du locuteur** : Si un mot capitalisé est immédiatement suivi ou précédé d'un verbe de parole (`said`, `thought`, `cried`) en dehors des guillemets de dialogue, il est classé comme personnage.
* **Indicateurs de civilité** : Les préfixes comme `Mr.`, `Dr.`, `Lady`, `Queen` forcent la classification en personnage.
* **Exclusion prépositionnelle** : Si l'entité est précédée de prépositions de lieu (`in`, `at`, `to`), elle est classée en lieu.
* **Filtrage** : Les entités vides, les pronoms, les nombres écrits en toutes lettres (ex: *Eight Hundred*) et une blacklist personnalisée de concepts abstraits (*death*, *nature*) sont éliminés.

### 4. Résumé Chronologique par Section (`summarize`)
* **L'Incipit** : L'algorithme cherche d'abord la première vraie phrase narrative du livre (taille comprise entre 12 et 65 mots, sans en-tête Gutenberg, et avec des guillemets équilibrés) pour servir d'accroche.
* **Segmentation et Sélection** : Le reste du livre est divisé en 5 segments chronologiques égaux. Pour chaque segment, nous calculons le profil TF-IDF et extrayons **l'unique phrase la plus centrale** (similarité cosinus maximale avec le centroïde du segment).
* Les 5 phrases extraites et l'incipit sont ensuite triés chronologiquement pour former un résumé de 6 phrases retraçant tout l'arc narratif du roman de manière fluide et logique, sans aucun risque d'hallucination.

### 5. Similarité Vectorielle (`similar`)
* Vectorise les 10 000 premiers mots de chaque livre du catalogue.
* Applique un modèle TF-IDF avec bigrammes pour capturer le style et les associations de mots.
* Calcule la **similarité cosinus** entre le vecteur du livre cible et les autres livres pour retourner les 5 plus proches.
