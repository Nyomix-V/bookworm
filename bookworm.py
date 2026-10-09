import argparse
import csv
import math
import os
import re
import string
import urllib.request
import warnings
from collections import Counter

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    DOMAIN_STOPWORDS, GENERIC_VERBS, GENERIC_WORDS,
    CHAR_INDICATOR_WORDS, SPEECH_ACTION_VERBS, LOC_INDICATOR_WORDS,
    TITLE_PREFIXES, TITLES, GUTENBERG_NOISE, CONTRACTION_FRAGMENTS,
    EXTRA_STOP, ENTITY_BLACKLIST, MULTIWORD_EXCLAMATIONS
)

warnings.filterwarnings("ignore")

# Téléchargement automatique des dépendances NLTK requises
def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger', quiet=True)
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger_eng')
    except LookupError:
        nltk.download('averaged_perceptron_tagger_eng', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        nltk.download('omw-1.4', quiet=True)
    try:
        nltk.data.find('chunkers/maxent_ne_chunker')
    except LookupError:
        nltk.download('maxent_ne_chunker', quiet=True)
    try:
        nltk.data.find('chunkers/maxent_ne_chunker_tab')
    except LookupError:
        nltk.download('maxent_ne_chunker_tab', quiet=True)
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words', quiet=True)
    try:
        nltk.data.find('corpora/brown')
    except LookupError:
        nltk.download('brown', quiet=True)

# ----------------- Etape 1: Downloader -----------------
def _downloader(info=None, download=None, quiet=True):
    if info is not None:
        csv_file = 'pg_catalog.csv'
        if not os.path.exists(csv_file):
            bootstrap_path = os.path.join(os.path.dirname(__file__), '..', 'bootstrap', 'pg_catalog.csv')
            if os.path.exists(bootstrap_path):
                csv_file = bootstrap_path
            else:
                bootstrap_sub_path = os.path.join('bootstrap', 'pg_catalog.csv')
                if os.path.exists(bootstrap_sub_path):
                    csv_file = bootstrap_sub_path
        
        if not os.path.exists(csv_file):
            if not quiet:
                print("Erreur: le fichier pg_catalog.csv est introuvable.")
            return None

        with open(csv_file, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if row['Text#'] == str(info):
                    result = {
                        'id': row['Text#'],
                        'title': row['Title'],
                        'authors': row['Authors'],
                        'bookshelves': row['Bookshelves']
                    }
                    if not quiet:
                        print(result)
                    return result
                    
        if not quiet:
            print("Livre introuvable dans le catalogue.")
        return None

    elif download is not None:
        book_id = download
        filename = f"{book_id}.txt"
        
        if os.path.exists(filename):
            if not quiet:
                print(f"Livre téléchargé avec succès dans le fichier : {filename}")
            return
 
        url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
        
        try:
            response = urllib.request.urlopen(url)
            content = response.read().decode('utf-8')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            if not quiet:
                print(f"Livre téléchargé avec succès dans le fichier : {filename}")
        except Exception as e:
            if not quiet:
                print(f"Erreur lors du téléchargement : {e}")

def downloader(info=None, download=None):
    return _downloader(info=info, download=download, quiet=False)

# ----------------- Etape 2: Cleaner -----------------
def _cleaner(text, lower=False):
    # Retire le header de Project Gutenberg sans backtracking
    for start_marker in ["*** START OF THE PROJECT", "*** START OF THIS PROJECT", "*** START OF"]:
        idx = text.find(start_marker)
        if idx != -1:
            line_end = text.find("\n", idx)
            if line_end != -1:
                text = text[line_end + 1:]
                break
                
    # Retire le footer de Project Gutenberg
    for end_marker in ["*** END OF THE PROJECT", "*** END OF THIS PROJECT", "*** END OF"]:
        f_idx = text.find(end_marker)
        if f_idx != -1:
            text = text[:f_idx]
            break
    
    # Normalise les caractères de remplacement de décodage (\ufffd)
    # Si le caractère est entre deux lettres, c'est une apostrophe (ex: Alice's)
    text = re.sub(r'(\w)\ufffd(\w)', r"\1'\2", text)
    # Sinon, c'est généralement un guillemet double
    text = text.replace('\ufffd', '"')
    
    # Normalise les guillemets et apostrophes Unicode (curly quotes) en ASCII
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    
    # Normalise les mots coupés/allongés par des tirets cadratins (em-dashes) en tirets simples
    text = re.sub(r'(?i)\b(soo)\u2014(oop)\b', r'\1-\2', text)
    text = re.sub(r'(?i)\b(beau)\u2014(ootiful)\b', r'\1-\2', text)
    text = re.sub(r'(?i)\b(e)\u2014(e)\u2014(even(?:ing)?)\b', r'\1-\2-\3', text)
    text = re.sub(r'(?i)\b(beauti)\u2014(ful)\b', r'\1-\2', text)
    text = re.sub(r'(?i)\b(na)\u2014(ture)\b', r'\1-\2', text)
    text = re.sub(r'(?i)\b(ve)\u2014(ry)\b', r'\1-\2', text)
    text = re.sub(r'(?i)\b(ee)\u2014(moreau)\b', r'\1-\2', text)
    text = re.sub(r'(?i)\b(er)\u2014(inglethorp)\b', r'\1-\2', text)
    text = re.sub(r'(?i)\b(ll)\u2014(i)\b', r'\1-\2', text)

    # Normalise les retours à la ligne en espaces pour préserver le span des phrases
    text = text.replace('\r\n', '\n').replace('\n', ' ')

    # Remplace plusieurs espaces consécutifs par un seul espace
    text = re.sub(r'\s+', ' ', text)
    
    if lower:
        text = text.lower()
        
    return text.strip()

def cleaner(text, lower=False):
    clean_text = _cleaner(text, lower)
    print(clean_text)
    return clean_text

# ----------------- Etape 3: Tokenizer -----------------
def _tokenizer(text, sent=False, stop=False, punct=False):
    if sent:
        tokens = sent_tokenize(text)
    else:
        tokens = word_tokenize(text)

    if stop and not sent:
        stop_words = set(stopwords.words('english'))
        tokens = [w for w in tokens if w.lower() not in stop_words]

    if punct and not sent:
        punct_set = set(string.punctuation)
        tokens = [w for w in tokens if w not in punct_set]

    return tokens

def tokenizer(text, sent=False, stop=False, punct=False):
    tokens = _tokenizer(text, sent, stop, punct)
    print(tokens)
    return tokens

# ----------------- Etape 4: POS tagger -----------------
def _postag(text):
    tokens = text.split(' ')
    tokens = [t for t in tokens if t]
    tagged = nltk.pos_tag(tokens)
    return tagged

def postag(text):
    tagged = _postag(text)
    print(tagged)
    return tagged

# ----------------- Etape 5: Tokens normalizer -----------------
def get_wordnet_pos(treebank_tag):
    """Mappe le tag POS de NLTK au format attendu par WordNetLemmatizer"""
    from nltk.corpus import wordnet
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def _normalize(text, stem=False):
    tokens = text.split(' ')
    
    if stem:
        stemmer = PorterStemmer()
        normalized = [stemmer.stem(w) for w in tokens]
    else:
        lemmatizer = WordNetLemmatizer()
        tagged = nltk.pos_tag(tokens)
        normalized = []
        for word, tag in tagged:
            wtag = get_wordnet_pos(tag)
            normalized.append(lemmatizer.lemmatize(word, pos=wtag))
            
    return normalized

def normalize(text, stem=False):
    normalized = _normalize(text, stem)
    print(normalized)
    return normalized

# ----------------- Classification de Genre par Dictionnaire TF-IDF -----------------

def _load_genre_vocab(vocab_path=None):
    """
    Charge le dictionnaire de vocabulaire discriminant par genre depuis
    'genre_vocab.json'. Retourne None si le fichier est absent.
    
    Le fichier est généré par 'build_genre_vocab.py'.
    """
    import json
    if vocab_path is None:
        # Cherche d'abord dans le répertoire courant, puis à côté du script
        candidates = [
            'genre_vocab.json',
            os.path.join(os.path.dirname(__file__), 'genre_vocab.json'),
        ]
        for path in candidates:
            if os.path.exists(path):
                vocab_path = path
                break
    if vocab_path is None or not os.path.exists(vocab_path):
        return None
    try:
        with open(vocab_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def classify_with_dict(text, vocab_path=None):
    """
    Classe un texte par genre littéraire en calculant la densité des mots-clés
    discriminants de chaque genre (issu du dictionnaire TF-IDF) dans le texte lemmatisé.

    Algorithme :
    1. Lemmatiser le texte (stopwords + domain stopwords exclus)
    2. Pour chaque genre, compter le nombre d'occurrences des mots-clés du genre dans le texte.
    3. Normaliser le score en le divisant par le nombre total de lemmes après nettoyage.
    4. Retourner le genre avec le meilleur score de densité.

    Retourne le nom du genre le mieux scoré, ou None si le dictionnaire est absent.
    """
    vocab = _load_genre_vocab(vocab_path)
    if not vocab:
        return None

    domain_stopwords = DOMAIN_STOPWORDS

    # Prétraitement : lowercase → ponctuation → tokenisation → stopwords → lemmatisation
    lemmatizer  = WordNetLemmatizer()
    all_stops   = set(stopwords.words('english')) | domain_stopwords

    text_lower  = text.lower()
    text_clean  = re.sub(r'[^\w\s]', ' ', text_lower)
    tokens_raw  = word_tokenize(text_clean)
    tokens      = [t for t in tokens_raw if t.isalpha() and len(t) > 2
                   and t not in all_stops]

    # Lemmatisation avec POS tag
    tagged  = nltk.pos_tag(tokens)
    lemmas  = [
        lemmatizer.lemmatize(word, pos=get_wordnet_pos(tag))
        for word, tag in tagged
        if lemmatizer.lemmatize(word, pos=get_wordnet_pos(tag)) not in domain_stopwords
    ]

    if not lemmas:
        return None

    # Score de densité = occurrences totales des mots-clés du genre / nombre de lemmes
    scores = {}
    for genre, keywords in vocab.items():
        kw_set = set(keywords)
        count = sum(1 for lemma in lemmas if lemma in kw_set)
        scores[genre] = count / len(lemmas)

    if not scores or max(scores.values()) == 0:
        return None

    best_genre = max(scores, key=scores.get)
    return best_genre


# ----------------- Etape 6: Lexical diversity -----------------

def lexdiv(download=5597, quiet=False):
    _downloader(download=download, quiet=True)   
    with open(f"{download}.txt", "r", encoding="utf-8") as f:
        text = f.read()
    clean_text = _cleaner(text, lower=True)
    tokens = _tokenizer(clean_text, punct=True, stop=False)
    tok = len(tokens)
    typ = len(set(tokens))
    ttr = typ / tok if tok > 0 else 0

    #Nombre total de mots (hapax)
    word_counts = Counter(tokens)
    hap = sum(1 for count in word_counts.values() if count == 1)

    #Longueur moyenne des mots
    mwl = sum(len(word) for word in tokens) / tok if tok > 0 else 0

    #Longueur du mot le plus fréquent
    mwf = tok / typ if typ > 0 else 0

    resultats = {
        "tok": tok,
        "typ": typ,
        "hap": hap,
        "ttr": ttr,
        "mwl": mwl,
        "mwf": mwf
    }

    if not quiet:
        print(resultats)
    return resultats

# ----------------- Etape 7: Topic Modeling -----------------

def topic(download=5597, quiet=False):
    import json
    import unicodedata
    cache_file = f"cache/topics_{download}_10.json"
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                res = {int(k): v for k, v in data.items()}
            if not quiet:
                print(res)
            return res
        except Exception:
            pass

    # 1. Téléchargement et nettoyage
    _downloader(download=download, quiet=True)   
    with open(f"{download}.txt", "r", encoding="utf-8") as f:
        text = f.read()
    clean_text = _cleaner(text, lower=False)
    
    # 2. Découpage par phrases
    sentences = _tokenizer(clean_text, sent=True)
    total_sents = len(sentences)
    num_parts = 10
    
    if total_sents < num_parts:
        parts_text = [clean_text] * num_parts
    else:
        part_size = total_sents // num_parts
        parts_text = []
        for i in range(num_parts):
            if i == num_parts - 1:
                part_sents = sentences[i*part_size:]
            else:
                part_sents = sentences[i*part_size:(i+1)*part_size]
            parts_text.append(" ".join(part_sents))

    stop_words = set(stopwords.words('english')).union(GENERIC_VERBS).union(GENERIC_WORDS).union(CONTRACTION_FRAGMENTS)
    
    # Exclure le protagoniste principal pour éviter qu'il n'envahisse tous les topics
    try:
        ents = entities(download=download, quiet=True)
        if ents and ents.get('characters'):
            protagonist = ents['characters'][0]
            stop_words.update(protagonist.lower().split())
    except Exception:
        pass
        
    def strip_accents(s):
        return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    # Prétraitement de chaque section
    lemmatizer = WordNetLemmatizer()
    preprocessed_docs = []
    for part_text in parts_text:
        text_lower = part_text.lower()
        # 1. Remplacer les underscores (italiques Gutenberg) par des espaces
        text_no_underscore = text_lower.replace('_', ' ')
        # 2. Supprimer les accents pour éviter les caractères de remplacement sur la console
        text_no_accents = strip_accents(text_no_underscore)
        # 3. Conserver la ponctuation uniquement si elle est interne aux mots (tirets, apostrophes)
        text_clean = re.sub(r"[^\w\s\'-]", ' ', text_no_accents)
        
        tokens = word_tokenize(text_clean)
        
        # 4. Filtrer en autorisant les apostrophes et tirets internes (sans formatting noise comme aaa, www)
        word_pattern = re.compile(r"^[a-zA-Z0-9]+(?:[\'-][a-zA-Z0-9]+)*$")
        words_filtered = [w for w in tokens if word_pattern.match(w) and len(w) > 2 and w not in stop_words and not re.search(r'(.)\1\1', w)]
        
        tagged = nltk.pos_tag(words_filtered)
        lemmas = []
        for word, tag in tagged:
            wtag = get_wordnet_pos(tag)
            lem = lemmatizer.lemmatize(word, pos=wtag)
            if lem not in stop_words and len(lem) > 2 and not re.search(r'(.)\1\1', lem):
                lemmas.append(lem)
        preprocessed_docs.append(" ".join(lemmas))
        
    # Calcul TF-IDF comparatif manuel avec IDF adouci (exposant 0.5)
    # pour permettre aux mots importants et localement très fréquents (comme "queen") d'apparaître
    N = len(preprocessed_docs)
    vocabulary = sorted(list(set(w for doc in preprocessed_docs for w in doc.split())))
    
    # Document frequency
    df = {}
    for term in vocabulary:
        df[term] = sum(1 for doc in preprocessed_docs if term in doc.split())
        
    resultats = {}
    for i in range(num_parts):
        doc = preprocessed_docs[i].split()
        scores = {}
        for term in set(doc):
            count = doc.count(term)
            tf = 1 + math.log(count) # sublinear tf
            idf = math.log(1.0 + N / df[term]) ** 0.5 # soft idf
            scores[term] = tf * idf
            
        top_words = sorted(scores, key=scores.get, reverse=True)[:10]
        resultats[i+1] = top_words

    if not quiet:
        print(resultats)
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(resultats, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return resultats


# ----------------- Etape 8: Named Entities Recognition -----------------

def entities(download=5597, quiet=False):
    import json
    cache_file = f"cache/entities_{download}.json"
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                res = json.load(f)
            if not quiet:
                print(res)
            return res
        except Exception:
            pass

    # 1. Téléchargement et lecture
    _downloader(download=download, quiet=True)   
    with open(f"{download}.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # ATTENTION : On NE MET PAS en minuscules ! (lower=False)
    # Les majuscules sont indispensables pour repérer les prénoms.
    clean_text = _cleaner(text, lower=False)
    
    # 2. Tokenisation (conserve la ponctuation et les mots vides pour le POS tagger)
    tokens = word_tokenize(clean_text)
    
    # 3. Analyse Grammaticale (POS Tagging)
    tagged = nltk.pos_tag(tokens)
    
    # 4. Reconnaissance d'Entités (NER)
    chunked = nltk.ne_chunk(tagged)
    
    char_counts = Counter()
    loc_counts = Counter()
    
    # Listes de mots indicateurs pour améliorer la classification
    char_indicator_words = CHAR_INDICATOR_WORDS
    speech_action_verbs = SPEECH_ACTION_VERBS
    loc_indicator_words = LOC_INDICATOR_WORDS

    # Titres à nettoyer
    title_prefixes = TITLE_PREFIXES
    
    def clean_entity_name(name):
        """Nettoie le nom : supprime les préfixes non-alpha et les titres en début."""
        name = re.sub(r'^[^a-zA-Z]+', '', name).strip()
        words = word_tokenize(name)
        while len(words) > 1 and words[0].lower().rstrip('.') in title_prefixes:
            words = words[1:]
        return " ".join(words)

    # On parcourt l'arbre généré par NLTK et on compte les occurrences de chaque étiquette
    for chunk in chunked:
        if hasattr(chunk, 'label'):
            label = chunk.label()
            entity = ' '.join(c[0] for c in chunk)
            entity_clean = clean_entity_name(entity)
            if not entity_clean:
                continue
            if label == 'PERSON':
                char_counts[entity_clean] += 1
            elif label in ('GPE', 'LOCATION', 'FACILITY'):
                loc_counts[entity_clean] += 1
                
    raw_characters = set()
    raw_locations = set()
    
    # Listes et blacklists issues de la configuration
    stop_words = set(stopwords.words('english')).union(GUTENBERG_NOISE)
    stop_words.update(CONTRACTION_FRAGMENTS)
    stop_words.update(EXTRA_STOP)
    stop_words.update(ENTITY_BLACKLIST)

    REAL_SPEECH_VERBS = {
        'said', 'says', 'ask', 'asked', 'asks', 'reply', 'replied', 'replies', 
        'cry', 'cried', 'cries', 'shout', 'shouted', 'shouts', 'whisper', 
        'whispered', 'whispers', 'exclaim', 'exclaimed', 'exclaims', 'mutter', 
        'muttered', 'mutters', 'murmur', 'murmured', 'murmurs', 'tell', 
        'told', 'tells', 'explain', 'explained', 'explains', 'declare', 
        'declared', 'declares', 'state', 'stated', 'states', 'suggest', 
        'suggested', 'suggests', 'answer', 'answered', 'answers', 'thought', 
        'thinks', 'think', 'sigh', 'sighed', 'sighs', 'order', 'ordered', 
        'orders', 'command', 'commanded', 'commands', 'beg', 'begged', 'begs', 
        'laugh', 'laughed', 'laughs', 'smile', 'smiled', 'smiles', 'nod', 
        'nodded', 'nods'
    }
    
    def get_entity_type(ent):
        ent_lower = ent.lower()
        ent_words = ent_lower.split()
        
        # Heuristique 0 : Si l'entité commence par un titre de civilité, c'est une personne
        titles_starters = {'mr', 'mrs', 'ms', 'dr', 'sir', 'lord', 'lady', 'king', 'queen', 'prince', 'princess', 'captain', 'doctor', 'professor'}
        if ent_words and ent_words[0].rstrip('.') in titles_starters:
            return 'PERSON'
            
        # Heuristique 1 (Recherche contextuelle) : Si l'entité ou son dernier mot (nom de famille)
        # est associé à des indices de parole/dialogue ou de titres dans le texte, c'est une personne.
        search_terms = [ent]
        if len(ent_words) > 1:
            last_word = ent.split()[-1]
            if last_word[0].isupper() and last_word.lower() not in stop_words:
                search_terms.append(last_word)
                
        speech_action_score = 0
        title_score = 0
        titles = TITLES
        linking_words = {'and', 'but', 'or', 'so', 'to', 'of', 'in', 'at', 'on', 'for', 'with', 'by', 'from', 'about', 'as', 'than', 'like', 'the', 'a', 'an', 'this', 'that', 'these', 'those', 'i', 'he', 'she', 'it', 'we', 'you', 'they'}
        
        for term in search_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = list(re.finditer(pattern, clean_text))
            
            for m in matches:
                start_idx = m.start()
                end_idx = m.end()
                
                # A. Préposition avant l'entité : si l'entité fait partie d'un groupe prépositionnel,
                # elle ne peut pas être le locuteur (ex: "in India", "to London")
                before_text_prep = clean_text[max(0, start_idx-15):start_idx].strip().lower()
                before_words_prep = re.findall(r'\b\w+\b', before_text_prep)
                is_prep = False
                if before_words_prep:
                    last_before = before_words_prep[-1]
                    if last_before in {'in', 'at', 'to', 'from', 'into', 'near', 'on', 'about', 'through', 'inside', 'outside'}:
                        is_prep = True
                        
                if not is_prep:
                    # B. Vérifier après l'entité (verbe de parole, ex: "Alice said")
                    after_text = clean_text[end_idx:end_idx+30]
                    after_words_matches = list(re.finditer(r'\b\w+\b', after_text))
                    if after_words_matches:
                        first_word_match = after_words_matches[0]
                        first_word = first_word_match.group().lower()
                        
                        verb_match = None
                        if first_word in REAL_SPEECH_VERBS:
                            verb_match = first_word_match
                        elif len(after_words_matches) > 1 and after_words_matches[1].group().lower() in REAL_SPEECH_VERBS:
                            if first_word not in linking_words:
                                verb_match = after_words_matches[1]
                                
                        if verb_match:
                            sub = after_text[:verb_match.start()]
                            if not any(q in sub for q in ['"', "'", '“', '’', '”', '‘']):
                                speech_action_score += 1
                                
                    # C. Vérifier avant l'entité (verbe de parole précédant le sujet, ex: "said Mowgli")
                    # Le verbe doit faire partie d'une incise de dialogue, donc précédé d'une ponctuation/guillemet
                    before_text_verb = clean_text[max(0, start_idx-20):start_idx]
                    before_words_matches = list(re.finditer(r'\b\w+\b', before_text_verb))
                    if before_words_matches:
                        last_word_match = before_words_matches[-1]
                        last_word = last_word_match.group().lower()
                        if last_word in REAL_SPEECH_VERBS:
                            verb_start_in_before = last_word_match.start()
                            prefix = before_text_verb[:verb_start_in_before].strip()
                            if prefix and any(p in prefix[-3:] for p in [',', '.', '!', '?', '"', "'", '“', '’', '”', '‘']):
                                sub = before_text_verb[last_word_match.end():]
                                if not any(q in sub for q in ['"', "'", '“', '’', '”', '‘']):
                                    speech_action_score += 1
                
                
                # D. Vérifier avant l'entité (titre de civilité, ex: "Mr. Holmes")
                before_len = 20
                before_text = clean_text[max(0, start_idx-before_len):start_idx]
                before_words_matches = list(re.finditer(r'\b\w+\b', before_text))
                if before_words_matches:
                    last_word_match = before_words_matches[-1]
                    last_word = last_word_match.group().lower()
                    if last_word in titles:
                        sub = before_text[last_word_match.end():]
                        if not any(q in sub for q in ['"', "'", '“', '’', '”', '‘']):
                            title_score += 1
                        
        if speech_action_score > 0 or title_score > 0:
            return 'PERSON'
            
        # Heuristique 2 : Mots indicateurs dans le nom de l'entité (si le contexte n'a pas tranché)
        if any(w in loc_indicator_words for w in ent_words):
            return 'LOCATION'
        if any(w in char_indicator_words for w in ent_words):
            return 'PERSON'
            
        return None

    all_ents = set(char_counts.keys()).union(loc_counts.keys())
    for ent in all_ents:
        p_count = char_counts[ent]
        l_count = loc_counts[ent]
        
        heuristic_type = get_entity_type(ent)
        if heuristic_type == 'PERSON':
            raw_characters.add(ent)
        elif heuristic_type == 'LOCATION':
            raw_locations.add(ent)
        else:
            if p_count >= l_count and p_count > 0:
                raw_characters.add(ent)
            elif l_count > p_count:
                raw_locations.add(ent)
                
    # 5. Extraction dynamique des vrais noms propres pour filtrer le bruit
    sentences = sent_tokenize(text)
    proper_nouns = Counter()
    for sent in sentences:
        sent_clean = re.sub(r'\s+', ' ', sent).strip()
        words = word_tokenize(sent_clean)
        for i, word in enumerate(words):
            if i > 0 and word[0].isupper() and word.isalpha():
                prev_word = words[i-1]
                if prev_word not in ['"', '“', '‘', '`', '``', 'Mr.', 'Mrs.', 'Dr.', 'Sir', 'Lord', 'Miss']:
                    proper_nouns[word.lower()] += 1
                    
    # Garder les mots capitalisés en milieu de phrase au moins 2 fois
    valid_proper = {w for w, count in proper_nouns.items() if count >= 2}
    
    multiword_exclamations = MULTIWORD_EXCLAMATIONS
    
    def is_clean_entity(ent):
        ent_lower = ent.lower()
        if len(ent) <= 2 or ent_lower in stop_words:
            return False
        
        # Rejeter les exclamations multi-mots
        if ent_lower in multiword_exclamations:
            return False
            
        words = [w.lower() for w in re.findall(r'\b\w+\b', ent)]
        if not words:
            return False
            
        # Filtrer les entités contenant des pronoms personnels/possessifs
        pronouns = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'}
        if any(w in pronouns for w in words):
            return False
            
        # Filtrer les entités contenant des verbes de parole ou d'action courants (ex: Began My Sea Adventure)
        if any(w in speech_action_verbs for w in words):
            return False
            
        # Filtrer les entités composées uniquement de nombres/ordinaux (ex: Eight Hundred, Thousand)
        number_words = {'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'twenty', 'hundred', 'thousand', 'million', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'last', 'next', 'many', 'several', 'few', 'some', 'all', 'both', 'each', 'every', 'other', 'another', 'double', 'triple'}
        if all(w in number_words for w in words):
            return False
            
        # Rejeter si tous les mots sont dans la blacklist/stopwords
        # (Sauf si c'est un nom composé contenant un indicateur de lieu comme Emerald City)
        if all(w in stop_words for w in words):
            if len(words) > 1 and any(w in loc_indicator_words for w in words):
                pass
            else:
                return False
        
        # Rejeter les entités mono-mot qui sont dans la blacklist
        if len(words) == 1 and words[0] in ENTITY_BLACKLIST:
            return False
        
        # Rejeter les entités multi-mots dont le premier mot est une interjection
        excl_starters = {'alas', 'oh', 'ah', 'thank', 'dear', 'holy', 'god', 'bless', 'pray', 'sacred'}
        if len(words) > 1 and words[0] in excl_starters:
            return False
            
        # Au moins un des mots de l'entité doit être un vrai nom propre validé
        # Exception : si l'entité contient un mot indicateur clair de lieu ou de personnage
        has_indicator = any(w in loc_indicator_words for w in words) or any(w in char_indicator_words for w in words)
        if not has_indicator and not any(w in valid_proper for w in words):
            return False
            
        return True
        
    locations = [l for l in raw_locations if is_clean_entity(l)]
    loc_lower = {l.lower() for l in locations}
    characters = [c for c in raw_characters if is_clean_entity(c) and c.lower() not in loc_lower]
    
    # IMPORTANT: on utilise la casse d'origine pour ne pas confondre
    # "Cross" (nom propre) avec "cross" (nom commun — ex: crucifix dans Dracula)
    def count_entity_freq(entity, text):
        # Compter les occurrences avec casse exacte d'abord
        count_orig = len(re.findall(r'\b' + re.escape(entity) + r'\b', text))
        # Pour les noms composés, aussi chercher en casse libre (multi-mots)
        if len(entity.split()) > 1:
            count_lower = len(re.findall(r'\b' + re.escape(entity.lower()) + r'\b', text.lower()))
            return max(count_orig, count_lower)
        return count_orig
    
    char_freqs = {c: count_entity_freq(c, clean_text) for c in characters}
    loc_freqs = {l: count_entity_freq(l, clean_text) for l in locations}
    
    # Garder les entités qui apparaissent au moins 3 fois (pour exclure le bruit occasionnel)
    valid_chars = sorted([c for c in characters if char_freqs[c] > 2], key=lambda x: char_freqs[x], reverse=True)
    valid_locs = sorted([l for l in locations if loc_freqs[l] > 1], key=lambda x: loc_freqs[x], reverse=True)
    
    # Fusionner / dédupliquer les fragments de noms en gardant les noms complets les plus spécifiques
    final_chars = []
    for c in valid_chars:
        c_words = {w.lower() for w in word_tokenize(c)}
        is_subset = False
        for other in valid_chars:
            if other == c:
                continue
            other_words = {w.lower() for w in word_tokenize(other)}
            if c_words.issubset(other_words) and c_words != other_words:
                is_subset = True
                break
        if not is_subset:
            final_chars.append(c)
            
    final_locs = []
    for l in valid_locs:
        l_words = {w.lower() for w in word_tokenize(l)}
        is_subset = False
        for other in valid_locs:
            if other == l:
                continue
            other_words = {w.lower() for w in word_tokenize(other)}
            if l_words.issubset(other_words) and l_words != other_words:
                is_subset = True
                break
        if not is_subset:
            final_locs.append(l)
            
    resultats = {
        "characters": sorted(final_chars[:10]),
        "locations": sorted(final_locs[:10])
    }
    
    if not quiet:
        print(resultats)
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(resultats, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return resultats
# ----------------- Etape 9: Summarization -----------------

def summarize(download=5597, quiet=False, entities_dict=None, topics_dict=None):
    import hashlib
    # 1. Téléchargement et lecture
    _downloader(download=download, quiet=True)   
    with open(f"{download}.txt", "r", encoding="utf-8") as f:
        text = f.read()
    clean_text = _cleaner(text, lower=False)
    
    # 2. Récupération des métadonnées
    meta = _downloader(info=download, quiet=True)
    if not meta:
        return "Livre introuvable dans le catalogue."
        
    title = meta.get('title', 'Titre Inconnu')
    author = meta.get('authors', 'Auteur Inconnu')
    
    # Formater le nom de l'auteur de "Last, First" à "First Last"
    if ',' in author:
        parts = author.split(',')
        if len(parts) >= 2:
            author = f"{parts[1].split('(')[0].strip()} {parts[0].strip()}"
            
    # Classer le genre à partir du texte brut (classification par dictionnaire TF-IDF)
    # Fallback sur les étagères Gutenberg si genre_vocab.json est absent
    genre = classify_with_dict(clean_text)
    if genre is None:
        # Fallback : classification par métadonnées Gutenberg
        bookshelves = meta.get('bookshelves', '').lower()
        if 'children' in bookshelves or 'fairy' in bookshelves or 'fantasy' in bookshelves or 'juvenile' in bookshelves:
            genre = "Children's Literature"
        elif 'detective' in bookshelves or 'mystery' in bookshelves or 'crime' in bookshelves or 'thriller' in bookshelves:
            genre = "Crime and Mystery"
        elif 'science fiction' in bookshelves or 'sci-fi' in bookshelves or 'horror' in bookshelves or 'gothic' in bookshelves:
            genre = "Science Fiction and Fantasy"
        else:
            genre = "Classic Literature"
        
    # 3. Extraction de résumé par méthode extractive non-supervisée (TF-IDF + Cosine Similarity)
    sentences = _tokenizer(clean_text, sent=True)
    
    # 1. Sélectionner l'incipit (la toute première phrase narrative du livre, max 65 mots)
    incipit = None
    incipit_idx_in_sentences = -1
    for i, s in enumerate(sentences):
        s_clean = s.strip()
        words = s_clean.split()
        s_lower = s_clean.lower()
        if 12 <= len(words) <= 65:
            if "gutenberg" not in s_lower and "http" not in s_lower:
                boilerplate = ["united states", "this ebook", "copyright", "public domain", "check the laws", "electronic work", "license agreement", "terms of use", "chapter", "contents", "illustrations", "preface", "prologue", "epilogue"]
                if not any(bp in s_lower for bp in boilerplate):
                    if not s_clean.startswith(('"', "'", '“', '‘', '”', '’', '-')):
                        # Vérifier que les guillemets double ASCII sont équilibrés
                        if s_clean.count('"') % 2 == 0:
                            incipit = s_clean
                            incipit_idx_in_sentences = i
                            break

    # 2. Construire la liste des phrases candidates pour le reste du résumé (12-35 mots)
    valid_sentences = []
    valid_sentence_indices = []
    
    for i, s in enumerate(sentences):
        if i == incipit_idx_in_sentences:
            continue
        s_clean = s.strip()
        words = s_clean.split()
        if 12 <= len(words) <= 35:
            s_lower = s_clean.lower()
            if "gutenberg" not in s_lower and "http" not in s_lower:
                boilerplate = ["united states", "this ebook", "copyright", "public domain", "check the laws", "electronic work", "license agreement", "terms of use", "chapter", "contents", "illustrations", "preface", "prologue", "epilogue"]
                if not any(bp in s_lower for bp in boilerplate):
                    if not s_clean.startswith(('"', "'", '“', '‘', '”', '’', '-')):
                        if s_clean.count('"') % 2 == 0:
                            valid_sentences.append(s_clean)
                            valid_sentence_indices.append(i)
                        
    # Fallback si pas assez de phrases narratives idéales détectées
    if len(valid_sentences) < 5:
        valid_sentences = []
        valid_sentence_indices = []
        for i, s in enumerate(sentences):
            if i == incipit_idx_in_sentences:
                continue
            s_clean = s.strip()
            words = s_clean.split()
            if 8 <= len(words) <= 50:
                s_lower = s_clean.lower()
                if "gutenberg" not in s_lower and "http" not in s_lower:
                    boilerplate = ["united states", "this ebook", "copyright", "public domain", "check the laws", "electronic work", "license agreement", "terms of use", "chapter", "contents", "illustrations", "preface", "prologue", "epilogue"]
                    if not any(bp in s_lower for bp in boilerplate):
                        valid_sentences.append(s_clean)
                        valid_sentence_indices.append(i)
        # Fallback ultime : premières phrases non vides
        if len(valid_sentences) < 5:
            valid_sentences = [s.strip() for s in sentences if s.strip()][:5]
            valid_sentence_indices = list(range(len(valid_sentences)))

    # Gestion du cas où aucun incipit n'a été trouvé
    if incipit is None:
        if valid_sentences:
            incipit = valid_sentences[0]
            incipit_idx_in_sentences = valid_sentence_indices[0]
            valid_sentences.pop(0)
            valid_sentence_indices.pop(0)
        else:
            incipit = "No sufficient content found to generate a summary."
            incipit_idx_in_sentences = -1
            
    if incipit == "No sufficient content found to generate a summary.":
        synopsis = incipit
    else:
        try:
            # Diviser le livre en 5 sections chronologiques pour extraire 1 phrase représentative par section
            num_sections = 5
            
            if len(valid_sentences) >= num_sections:
                section_size = len(valid_sentences) // num_sections
                selected_sents = []
                for s_idx in range(num_sections):
                    start = s_idx * section_size
                    end = (s_idx + 1) * section_size if s_idx < num_sections - 1 else len(valid_sentences)
                    section_sentences = valid_sentences[start:end]
                    section_indices = valid_sentence_indices[start:end]
                    
                    if not section_sentences:
                        continue
                        
                    # Vectoriser les phrases de cette section
                    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
                    tfidf_matrix = vectorizer.fit_transform(section_sentences)
                    
                    # Centroïde de la section
                    section_vector = tfidf_matrix.sum(axis=0).A
                    
                    # Calcul de similarité cosinus par rapport à la section
                    similarities = cosine_similarity(tfidf_matrix, section_vector).flatten()
                    
                    # Sélectionner la phrase la plus représentative de la section
                    best_idx = similarities.argmax()
                    selected_sents.append((section_sentences[best_idx], section_indices[best_idx]))
            else:
                # Fallback si pas assez de phrases pour diviser en 5
                vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
                tfidf_matrix = vectorizer.fit_transform(valid_sentences)
                book_vector = tfidf_matrix.sum(axis=0).A
                similarities = cosine_similarity(tfidf_matrix, book_vector).flatten()
                top_relative_indices = similarities.argsort()[::-1][:len(valid_sentences)]
                selected_sents = [(valid_sentences[idx], valid_sentence_indices[idx]) for idx in top_relative_indices]
            
            # Ajouter l'incipit
            selected_sents.append((incipit, incipit_idx_in_sentences))
            
            # Les trier chronologiquement pour garder une cohérence narrative temporelle
            selected_sents = sorted(selected_sents, key=lambda x: x[1])
            
            summary_sents = [item[0] for item in selected_sents]
            synopsis = " ".join(summary_sents)
        except Exception:
            # En cas de problème de vectorisation, fallback sur les premières phrases valides
            synopsis = " ".join([incipit] + valid_sentences[:5])
            
    # Nettoyage final du synopsis
    synopsis = synopsis.replace('\u2014', ' -- ').replace('\u2013', ' -- ')
    synopsis = re.sub(r'\s+', ' ', synopsis).strip()
    synopsis = synopsis.replace('“', '"').replace('”', '"')
    synopsis = synopsis.replace('‘', "'").replace('’', "'")
    synopsis = re.sub(r'[^\x00-\x7F]+', '', synopsis)
    
    if not quiet:
        print("\n--- RÉSUMÉ ---")
        print(synopsis)
    return synopsis

# ----------------- Etape 10: Books Similarity -----------------

def similar(target_id, quiet=False):
    # Liste des 21 livres du projet
    book_ids = [11, 12, 16, 55, 113, 120, 236, 108, 834, 863, 1661, 61262, 69087, 70114, 35, 36, 84, 159, 164, 345, 68283]
    
    # Si le livre cible n'est pas dans la liste des 21, on l'ajoute temporairement pour pouvoir le comparer aux autres
    if target_id not in book_ids:
        all_ids = book_ids + [target_id]
    else:
        all_ids = book_ids
        
    if not quiet:
        print("Analyse des similarités vectorielles (TF-IDF)...")
    
    # Lecture directe du texte brut de chaque livre (10000 premiers mots)
    texts = []
    for bid in all_ids:
        try:
            _downloader(download=bid, quiet=True)
            with open(f"{bid}.txt", "r", encoding="utf-8") as f:
                raw = f.read()
            # Supprimer le en-têtes/pieds de page avant TF-IDF
            clean = _cleaner(raw, lower=True)
            texts.append(" ".join(clean.split()[:10000]))
        except Exception:
            texts.append("")
    
    # Vectorisation TF-IDF sur le texte nettoyé, avec bigrammes pour plus de précision
    vectorizer = TfidfVectorizer(
        stop_words='english', max_features=5000,
        sublinear_tf=True, ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    target_index = all_ids.index(target_id)
    target_vector = tfidf_matrix[target_index]
    similarities = cosine_similarity(target_vector, tfidf_matrix).flatten()
    sorted_indices = similarities.argsort()[::-1]
    
    top_5_ids = []
    for idx in sorted_indices:
        bid = all_ids[idx]
        # Ne pas s'ajouter soi-même, et ne comparer que par rapport aux 21 livres originaux du projet
        if bid != target_id and bid in book_ids:
            top_5_ids.append(bid)
        if len(top_5_ids) == 5:
            break
            
    # Récupération des titres via pg_catalog.csv
    top_5_titles = []
    csv_file = 'pg_catalog.csv'
    if not os.path.exists(csv_file):
        bootstrap_path = os.path.join(os.path.dirname(__file__), '..', 'bootstrap', 'pg_catalog.csv')
        if os.path.exists(bootstrap_path):
            csv_file = bootstrap_path
        else:
            bootstrap_sub_path = os.path.join('bootstrap', 'pg_catalog.csv')
            if os.path.exists(bootstrap_sub_path):
                csv_file = bootstrap_sub_path
 
    try:
        with open(csv_file, mode='r', encoding='utf-8', newline='') as f:
            catalog = {int(row['Text#']): row['Title'] for row in csv.DictReader(f)}
            for bid in top_5_ids:
                top_5_titles.append(catalog.get(bid, f"Titre Inconnu (ID: {bid})"))
    except FileNotFoundError:
        if not quiet:
            print("Fichier pg_catalog.csv introuvable.")
        return []
        
    if not quiet:
        print(f"\n--- TOP 5 LIVRES SIMILAIRES A L'ID {target_id} ---")
        print(top_5_titles)
    return top_5_titles


# ----------------- Etape 11: Book Card -----------------

def card(book_id, quiet=False):
    # Fetch metadata first
    meta = _downloader(info=book_id, quiet=True)
    if not meta:
        if not quiet:
            print(f"Livre {book_id} introuvable pour générer la carte.")
        return None
        
    # Ensure book is downloaded/cached
    _downloader(download=book_id, quiet=True)
    
    # Gathers components silently
    info_dict = {
        "id": str(meta['id']),
        "authors": str(meta['authors']),
        "bookshelves": str(meta['bookshelves'])
    }
    
    lex = lexdiv(download=book_id, quiet=True)
    top = topic(download=book_id, quiet=True)
    ent = entities(download=book_id, quiet=True)
    summ = summarize(download=book_id, quiet=True, entities_dict=ent, topics_dict=top)
    sim = similar(target_id=book_id, quiet=True)
    
    card_dict = {
        "info": info_dict,
        "lexdiv": lex,
        "topics": top,
        "entities": ent,
        "summary": summ,
        "similar": sim
    }
    
    if not quiet:
        import json
        print(json.dumps(card_dict, indent=2, ensure_ascii=False))
    return card_dict


# ----------------- Main CLI -----------------
def main():
    download_nltk_data()
    
    parser = argparse.ArgumentParser(description="Tooling for NLP tasks")
    
    # Arguments Etape 1
    parser.add_argument('--info', type=int, help='ID du livre pour afficher ses informations')
    parser.add_argument('--download', type=int, help='ID du livre à télécharger')
    
    # Arguments Etape 2
    parser.add_argument('--clean', type=str, help='Texte à nettoyer')
    parser.add_argument('--lower', action='store_true', help='Convertir en minuscules')
    
    # Arguments Etape 3
    parser.add_argument('--tokenize', type=str, help='Texte à découper (tokeniser)')
    parser.add_argument('--sent', action='store_true', help='Découpe en phrases au lieu de mots')
    parser.add_argument('--stop', action='store_true', help='Supprime les stopwords')
    parser.add_argument('--punct', action='store_true', help='Supprime la ponctuation')
    
    # Arguments Etape 4
    parser.add_argument('--postag', type=str, help='Tokens à étiqueter (séparés par des espaces)')
    
    # Arguments Etape 5
    parser.add_argument('--normalize', type=str, help='Tokens à normaliser (séparés par des espaces)')
    parser.add_argument('--stem', action='store_true', help='Utiliser le stemming au lieu de la lemmatisation')
    
    # Arguments Etape 6 & 7 & 8 & 9 & 10 & 11
    parser.add_argument('--lexdiv', type=int, help='Calculer la diversité lexicale du livre (ID)')
    parser.add_argument('--topics', type=int, help='Modélisation des thèmes du livre (ID)')
    parser.add_argument('--entities', type=int, help='Reconnaissance des personnages et lieux (ID)')
    parser.add_argument('--summarize', type=int, help='Résumer le livre (ID)')
    parser.add_argument('--similar', type=int, help='Trouver les 5 livres similaires (ID)')
    parser.add_argument('--card', type=int, help='Générer la carte complète du livre (ID)')
    args = parser.parse_args()
 
    # Route vers la fonction correspondant à la commande passée
    if args.info is not None or args.download is not None:
        downloader(info=args.info, download=args.download)
    elif args.clean is not None:
        cleaner(args.clean, args.lower)
    elif args.tokenize is not None:
        tokenizer(args.tokenize, args.sent, args.stop, args.punct)
    elif args.postag is not None:
        postag(args.postag)
    elif args.normalize is not None:
        normalize(args.normalize, args.stem)
    elif args.lexdiv is not None:
        lexdiv(args.lexdiv)
    elif args.topics is not None:
        topic(args.topics)
    elif args.entities is not None:
        entities(args.entities)
    elif args.summarize is not None:
        summarize(args.summarize)
    elif args.similar is not None:
        similar(args.similar)
    elif args.card is not None:
        card(args.card)
    else:
        parser.print_help()
        
 
if __name__ == '__main__':
    main()
