"""debug_classify.py — Affiche les scores détaillés de classify_with_dict"""
import re
from bookworm import (
    _cleaner, _load_genre_vocab, WordNetLemmatizer, stopwords,
    word_tokenize, get_wordnet_pos, nltk
)

vocab = _load_genre_vocab()
lemmatizer = WordNetLemmatizer()

# Copie conforme des domain_stopwords de bookworm.py
domain_stopwords = {
    # Pronouns, prepositions, articles, auxiliary verbs, and highly frequent words
    'use', 'begin', 'learn', 'tell', 'name', 'home', 'land', 'leave',
    'find', 'come', 'take', 'make', 'give', 'keep', 'bring', 'turn',
    'help', 'lead', 'face', 'become', 'return', 'discover', 'life',
    'world', 'story', 'people', 'place', 'year', 'time', 'way', 'day',
    'thing', 'end', 'hand', 'man', 'woman', 'young', 'old', 'dark',
    'great', 'long', 'high', 'new', 'good', 'true', 'able', 'know',
    'seek', 'live', 'let', 'set', 'run', 'look', 'feel', 'call', 'hold',
    'small', 'large', 'start', 'stop', 'try', 'form', 'create', 'reach',
    'escape', 'battle', 'fight', 'power', 'force', 'control', 'band',
    'hero', 'piece', 'system', 'cold', 'distant', 'guide', 'group',
    'survive', 'member', 'strange', 'finally', 'hide', 'free',
    'lose', 'allow', 'remain', 'attack', 'move',
    'must', 'one', 'war', 'hunt', 'travel', 'ruin', 'destroy',
    'ancient', 'creature', 'machine', 'reality', 'army',
    'involve', 'brave',
    'send', 'save', 'protect', 'carry', 'serve', 'stand', 'open',
    'close', 'break', 'follow', 'watch', 'drive',
    # Quantités et nombres
    'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'eleven', 'twelve', 'twenty', 'hundred', 'thousand', 'million', 'double',
    'triple', 'once', 'twice', 'half', 'third', 'quarter',
    # Prépositions et adverbes de mouvement/direction
    'across', 'along', 'around', 'behind', 'between', 'through', 'under',
    'above', 'below', 'near', 'far', 'beside', 'within', 'without',
    # Nationalités, pays et villes (non discriminants pour le genre)
    'london', 'england', 'english', 'french', 'france', 'paris', 'american',
    'america', 'russian', 'russia', 'europe', 'european', 'german', 'germany',
    'venice', 'transylvania', 'rome', 'italian', 'italy', 'londoner', 'britain',
    'british', 'scotland', 'irish', 'ireland',
    # Noms de personnages du mock-data (ne doivent pas servir de features de classification)
    'alice', 'dorothy', 'sherlock', 'holmes', 'watson', 'poirot', 'lestrade',
    'morrison', 'wendy', 'peter', 'pan', 'mowgli', 'baloo', 'bagheera',
    'shere', 'khan', 'gretel', 'hansel', 'tom', 'sawyer', 'huck',
    'huckleberry', 'finn', 'aslan', 'hook', 'darling', 'dracula', 'helsing',
    'harker', 'mina', 'lucy', 'tolstoy', 'henry', 'james', 'heathcliff',
    'catherine', 'scarecrow', 'oz', 'captain',
    # Mots grammaticaux ou de communication très fréquents
    'want', 'wanted', 'whenever', 'companion', 'condition', 'catch', 'whose',
    'shall', 'would', 'could', 'should', 'might', 'must', 'ought', 'may',
    'unto', 'upon', 'towards', 'meanwhile', 'whose', 'whom', 'whosoever',
    # Additional generic narrative and common Victorian fiction terms
    'adventure', 'child', 'play', 'girl', 'boy', 'away', 'together', 'forest',
    'friendship', 'brother', 'sister', 'parent', 'father', 'mother', 'son',
    'daughter', 'case', 'hire', 'examine', 'web', 'wealthy', 'identity',
    'secret', 'mysterious', 'mystery', 'shadowy', 'black', 'white', 'red',
    'blue', 'green', 'yellow', 'color', 'colour', 'humanity', 'survivor',
    'city', 'lord', 'abandon', 'apart', 'first', 'second', 'third', 'nature',
    'family', 'society', 'moral', 'love', 'class', 'duty', 'wealth',
    'fate', 'question', 'unknown', 'century', 'history', 'narrator', 'novel',
    'book', 'write', 'author', 'read', 'gentle', 'simple', 'common', 'general',
    'special', 'particular', 'various', 'different', 'several', 'many',
    'much', 'little', 'few', 'bad', 'hear', 'speak', 'think', 'believe',
    'understand', 'remember', 'forget', 'seem', 'see', 'show', 'appear',
    'disappear', 'walk', 'fly', 'arrive', 'stay', 'sit', 'lie', 'rose', 'rise', 'fall',
    'get', 'do', 'have', 'receive', 'search', 'last', 'next', 'past', 'future',
    'present', 'night', 'morning', 'evening', 'afternoon', 'week', 'month',
    'hour', 'minute', 'second', 'house', 'room', 'door', 'window', 'wall',
    'street', 'road', 'town', 'country', 'earth', 'sky', 'sun', 'moon', 'star',
    'baby', 'kid', 'friend', 'enemy', 'host', 'guest', 'tell', 'say', 'go',
    'work', 'die', 'death', 'kill', 'killer', 'live', 'living', 'dead',
    'happen', 'occur', 'exist', 'seem', 'appear', 'become', 'grow', 'fall',
    'feel', 'wish', 'hope', 'fear', 'dread', 'happy', 'sad', 'angry', 'silent',
    'silence', 'voice', 'sound', 'light', 'shadow', 'mind', 'heart', 'soul',
    'body', 'head', 'face', 'eye', 'ear', 'nose', 'mouth', 'hair', 'arm', 'leg',
    'foot', 'step', 'walk', 'path', 'road', 'way', 'direction', 'side', 'part',
    'half', 'whole', 'full', 'empty', 'clear', 'obscure', 'heavy', 'light',
    'hot', 'cold', 'warm', 'cool', 'wet', 'dry', 'soft', 'hard', 'strong',
    'weak', 'fast', 'slow', 'quick', 'sudden', 'gradual', 'near', 'far', 'close',
    'distant', 'high', 'low', 'deep', 'shallow', 'wide', 'narrow', 'thick',
    'thin', 'fat', 'lean', 'rich', 'poor', 'young', 'old', 'new', 'ancient',
    'modern', 'future', 'past', 'early', 'late', 'soon', 'long', 'short',
    'big', 'small', 'tiny', 'huge', 'vast', 'broad', 'large', 'little',
    # New additions of generic words identified from analysis
    'yet', 'yard', 'company', 'cast', 'bury', 'beneath', 'accidentally',
    'encounter', 'everyone', 'discovers', 'chemical', 'alternate', 'complex',
    'connection', 'destroys', 'contrast', 'desire', 'trial', 'strike',
    'pressure', 'retire', 'miss', 'spot', 'ago', 'locate', 'original',
    'sign', 'plan', 'reason', 'achieves', 'adapt', 'waste', 'basement',
    'central', 'van', 'decide', 'totalitarian', 'conqueror', 'connect'
}

books = [
    (11,   "Alice's Adventures in Wonderland"),
    (345,  "Dracula"),
    (1661, "Sherlock Holmes"),
    (84,   "Frankenstein"),
    (164,  "Twenty Thousand Leagues"),
    (113,  "Treasure Island"),
]

for bid, name in books:
    with open(f"{bid}.txt", "r", encoding="utf-8") as f:
        raw = f.read()
    text = _cleaner(raw, lower=False)
    
    text_lower = text.lower()
    text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
    tokens_raw = word_tokenize(text_clean)
    tokens = [t for t in tokens_raw if t.isalpha() and len(t) > 2 and t not in (set(stopwords.words('english')) | domain_stopwords)]
    tagged = nltk.pos_tag(tokens)
    lemmas = [
        lemmatizer.lemmatize(w, pos=get_wordnet_pos(tag)) 
        for w, tag in tagged
        if lemmatizer.lemmatize(w, pos=get_wordnet_pos(tag)) not in domain_stopwords
    ]
    
    total = len(lemmas)
    print(f"\n{'='*60}")
    print(f"[{name}] - {total} tokens lemmatisés")
    for genre, keywords in vocab.items():
        kw_set = set(keywords)
        hits = [(kw, lemmas.count(kw)) for kw in keywords if kw in lemmas]
        hit_count = sum(c for _, c in hits)
        score = hit_count / total if total > 0 else 0
        print(f"  {genre:<35} score={score:.6f}  hits={hit_count}  keywords_found={hits}")
