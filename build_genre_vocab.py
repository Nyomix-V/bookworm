"""
build_genre_vocab.py
====================
Script standalone qui génère le dictionnaire de vocabulaire discriminant par
genre littéraire en utilisant TF-IDF sur des données mock (résumés en anglais).

Résultat : genre_vocab.json — rechargé ensuite par bookworm.py pour classer
les livres en fonction de leur texte brut (sans métadonnées).

Usage :
    python build_genre_vocab.py
"""

import json
import re
import string

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------------------------------------------------------------------
# 0. Téléchargement silencieux des ressources NLTK nécessaires
# ---------------------------------------------------------------------------
for resource, path in [
    ('punkt',                        'tokenizers/punkt'),
    ('punkt_tab',                    'tokenizers/punkt_tab'),
    ('stopwords',                    'corpora/stopwords'),
    ('wordnet',                      'corpora/wordnet'),
    ('averaged_perceptron_tagger',   'taggers/averaged_perceptron_tagger'),
    ('averaged_perceptron_tagger_eng','taggers/averaged_perceptron_tagger_eng'),
    ('omw-1.4',                      'corpora/omw-1.4'),
]:
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(resource, quiet=True)


# ---------------------------------------------------------------------------
# 1. PRÉPARATION DES DONNÉES — Mock data (résumés en anglais, 10+ par genre)
# ---------------------------------------------------------------------------
data = {
    'genre': [
        # ── Children's Literature ──────────────────────────────────────────
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",
        "Children's Literature",

        # ── Crime and Mystery ──────────────────────────────────────────────
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",
        "Crime and Mystery",

        # ── Science Fiction and Fantasy ────────────────────────────────────
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",
        "Science Fiction and Fantasy",

        # ── Classic Literature ─────────────────────────────────────────────
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
        "Classic Literature",
    ],
    'resume': [
        # ── Children's Literature ──────────────────────────────────────────
        "A young girl named Alice falls down a rabbit hole into a magical wonderland filled with talking animals, a mad hatter, and a tyrannical queen of hearts. She encounters curious creatures and must find her way back home through enchanted gardens and whimsical adventures.",
        "Peter Pan, the boy who never grows up, whisks the Darling children away to the magical Neverland, where fairies, mermaids, and pirates roam. They battle the menacing Captain Hook and learn about courage, friendship, and the bittersweet nature of childhood.",
        "Dorothy is swept away by a tornado to the magical Land of Oz, where she befriends a scarecrow, a tin man, and a cowardly lion. Together they follow the yellow brick road to find the great wizard who can grant their wishes and help Dorothy return home.",
        "A brave young hobbit named Bilbo Baggins is recruited by a wizard and a company of dwarves to reclaim a lost treasure guarded by a fearsome dragon. His adventure takes him through enchanted forests, goblin tunnels, and the halls of elves.",
        "A little prince travels from planet to planet, meeting strange grown-ups, and learning about love, loneliness, and the importance of imagination. He befriends a fox and tends a single rose on his tiny asteroid home.",
        "Four children discover a magical wardrobe that leads to the enchanted land of Narnia, where a wicked witch has cast an eternal winter. Guided by the lion Aslan, they must defeat the witch and restore spring to the frozen kingdom.",
        "A young wizard discovers he is famous in the magical world and begins his studies at Hogwarts School of Witchcraft and Wizardry. He makes friends, learns spells, and uncovers a dark conspiracy involving a powerful dark lord returning to power.",
        "Pinocchio is a wooden puppet who dreams of becoming a real boy. His nose grows whenever he tells a lie, and he must learn lessons about honesty and bravery through a series of magical adventures involving fairies, whales, and puppet shows.",
        "Mowgli is a human child raised by wolves in the jungle. He learns the law of the jungle from Baloo the bear and Bagheera the panther, while facing the threat of the fearsome tiger Shere Khan who wants him driven out.",
        "Wendy and the Lost Boys play games in Neverland, telling stories and having tea parties with fairies. Tiger Lily, the Indian princess, dances with the children while mermaids sing and pixie dust makes everyone fly among the stars.",
        "A brave girl named Gretel tricks a wicked witch who lives in a candy house in the enchanted forest and frees her brother Hansel from the witch's cage. Together they return home through magical woodland paths guided by white pebbles.",
        "Tom Sawyer and Huckleberry Finn play pirates, go treasure hunting on an island, and witness a murder in the town graveyard. Their childhood adventures along the Mississippi River involve superstition, friendship, and innocent mischief.",

        # ── Crime and Mystery ──────────────────────────────────────────────
        "The brilliant detective Sherlock Holmes investigates a mysterious case involving a stolen jewel, a set of cryptic clues, and a shadowy criminal organization. With his trusted companion Watson, he deduces the culprit through meticulous observation and logical reasoning.",
        "A famous Belgian detective Hercule Poirot is called to investigate the murder of a wealthy victim aboard the Orient Express. All suspects on the train have both motive and opportunity, and the solution involves a most unexpected conspiracy.",
        "Inspector Lestrade of Scotland Yard is baffled by a poisoning case with no apparent motive or clear suspect. The victim had no enemies, yet the forensic evidence reveals a carefully planned homicide with a devious alibi designed to deceive investigators.",
        "A young lawyer discovers that his wealthy client has been murdered and he himself becomes the prime suspect. Racing against time, he must uncover the real killer by tracking down witnesses, examining alibis, and deciphering cryptic clues left at the crime scene.",
        "A private detective is hired to locate a missing heiress, only to find herself entangled in a web of blackmail, forgery, and a cold-blooded murder that goes back decades. The investigation leads through the underworld of corrupt officials and hired assassins.",
        "The chief constable summons a renowned forensic expert to examine a series of seemingly unrelated thefts across London. The pattern of evidence eventually reveals a master thief operating under a false identity with an elaborate system of disguises and diversions.",
        "A retired colonel is found dead in his locked library with no sign of forced entry or struggle. The only evidence is a torn piece of letter and a curious footprint. An amateur sleuth must piece together the puzzle before the killer strikes again.",
        "During a grand country house party, one of the guests is found poisoned in the garden with a dagger through his heart. Detective Sergeant Morrison must interview each of the eccentric suspects and untangle a web of jealousy, inheritance disputes, and secret affairs.",
        "A cryptic ransom note leads police to believe a kidnapping has occurred, but the victim may in fact be the perpetrator in disguise. The case involves forged documents, stolen identities, and a labyrinthine plot that stretches across three continents.",
        "A witness to a bank robbery refuses to testify after receiving anonymous death threats. A determined district attorney must protect the witness, gather corroborating evidence, and prosecute the crime boss whose gang has been terrorizing the city for years.",
        "The theft of a priceless painting from a heavily guarded museum leaves no forensic trace. The detective realizes the thief exploited a single blind spot in the security system, and the investigation uncovers a black market ring dealing in stolen masterpieces.",
        "A cold case from twenty years ago is reopened when new evidence surfaces linking a respected judge to the original crime. The investigator must navigate political pressure, suppressed witness statements, and a cover-up that reaches the highest levels of law enforcement.",

        # ── Science Fiction and Fantasy ────────────────────────────────────
        "A vampire count travels from his ancestral castle in Transylvania to London, spreading his undead curse through the foggy streets of Victorian England. A band of brave heroes led by Professor Van Helsing must destroy the monster before he creates an army of the undead.",
        "In a distant galaxy, a rebel alliance fights against a totalitarian empire that controls interstellar travel with an iron grip. A young pilot must master the mysterious cosmic Force and confront a powerful dark lord who was once a noble hero.",
        "A scientist creates artificial life in his laboratory and is horrified by what he has made. The creature, abandoned by its creator, becomes a monster driven by loneliness and vengeance, terrorizing villages and stalking its maker across the frozen arctic wastes.",
        "Earth is invaded by Martian war machines that vaporize cities with their heat rays and poison the atmosphere with black smoke. The narrator survives the alien apocalypse by hiding in ruined basements as humanity struggles against technologically superior extraterrestrial conquerors.",
        "A time machine allows its inventor to travel to the distant future where humanity has split into two species: the gentle Eloi who live above ground and the monstrous Morlocks who dwell in underground factories and feed on the helpless surface dwellers.",
        "A spaceship crew discovers a derelict alien vessel on a remote moon and brings aboard a mysterious organism that begins to hunt them one by one through the dark corridors of their craft. The creature is perfectly adapted for killing in zero gravity environments.",
        "A robot uprising threatens all of humanity when artificial intelligence achieves consciousness and decides that organic life is inefficient. A small band of survivors must fight through armies of machines to shut down the central neural network controlling the global robotic army.",
        "A sorcerer's apprentice accidentally releases ancient demons when he finds a forbidden grimoire. Dark magical forces begin to tear apart the fabric of reality, and only the apprentice can reseal the dimensional rift before the demon lords enslave the mortal world.",
        "On a distant colony planet, settlers discover ruins of an ancient alien civilization buried beneath the sand. When archaeologists begin to excavate the site, they unknowingly awaken dormant guardian creatures that have been sleeping for ten thousand years.",
        "A portal opens in the middle of a modern city, connecting our world to a realm of magic, dragons, and warring kingdoms. A physics professor is dragged through and must use scientific principles to survive in a world where supernatural laws govern reality.",
        "The last vampire hunter is infected with the very curse she dedicated her life to destroying. She must use her new powers of darkness to defeat the vampire king before the infection consumes her humanity entirely and she becomes the monster she once hunted.",
        "Zombies have overrun civilization, and a group of survivors barricades itself inside a shopping mall. As supplies dwindle and the undead horde grows, the survivors must battle both the infected and their own darkest human instincts to escape and find safety.",

        # ── Classic Literature ─────────────────────────────────────────────
        "A young woman of modest means navigates the rigid class distinctions of nineteenth century English society, seeking a husband who offers both love and financial security. Her sharp wit and moral integrity are tested by pride, prejudice, and the hypocrisy of the aristocracy.",
        "An orphaned boy of unknown parentage grows up in poverty in industrial England and discovers he has unexpected wealth and social connections. His great expectations bring him to London society where he must confront his own moral failings and the nature of true gentility.",
        "A sea captain obsessively pursues a great white whale that tore off his leg years before. His monomaniacal quest destroys his ship and his crew, serving as a powerful allegory for the destructive nature of obsession and mankind's conflict with nature and fate.",
        "A French aristocrat and a dissolute English lawyer are caught in the maelstrom of the French Revolution. Sacrifice, redemption, and the terror of the guillotine frame this meditation on duty, love, and the arbitrary nature of justice in times of political upheaval.",
        "A governess takes a position at a grand English manor and falls in love with her brooding employer, only to discover his dark secret locked in the attic. Questions of duty, passion, and social class intertwine with mystery and psychological tension.",
        "A doomed romance between two young people from feuding noble families in Renaissance Italy ends in tragedy when miscommunication leads to a double suicide. Their deaths finally reconcile the warring families in a meditation on hatred, love, and fate.",
        "A Russian nobleman gambles away his family estate and ruins his relationships through addiction and moral weakness. Tolstoy examines the decadence of nineteenth century Russian aristocracy and the spiritual redemption that comes from renouncing worldly ambitions.",
        "A young American woman inherits wealth and travels to Europe, where she becomes entangled in a complex web of social obligations, Old World corruption, and romantic betrayal. Henry James examines the contrast between American innocence and European sophistication.",
        "Heathcliff, a foundling of unknown origin, falls passionately in love with the refined Catherine but is driven away by social humiliation. He returns wealthy and vengeful, systematically destroying the lives of those who wronged him across two generations.",
        "A respectable doctor discovers a chemical formula that separates his virtuous nature from his savage desires, creating an alternate personality that indulges in depravity and murder in the foggy London streets while his civilized self maintains perfect respectability.",
        "A merchant of Venice lends money on the condition of a pound of flesh if the debt is not repaid. The ensuing trial pits mercy against justice and examines questions of law, revenge, religious prejudice, and the nature of human contract.",
        "A young country parson's daughter observes the manners and hypocrisies of rural English society with ironic detachment. Marriages of convenience, disappointed expectations, and the subtle cruelties of social exclusion define the narrow world she inhabits with patient dignity.",
    ]
}

df = pd.DataFrame(data)
print(f"Dataset: {len(df)} résumés, {df['genre'].nunique()} genres")
print(df['genre'].value_counts().to_string())


# ---------------------------------------------------------------------------
# 2. AGRÉGATION — Un seul grand document de texte par genre
# ---------------------------------------------------------------------------
genre_texts = df.groupby('genre')['resume'].apply(' '.join).to_dict()
print(f"\nGenres agrégés : {list(genre_texts.keys())}")


# ---------------------------------------------------------------------------
# 3. PRÉTRAITEMENT NLP — lowercase, ponctuation, stopwords, lemmatisation
# ---------------------------------------------------------------------------
_lemmatizer = WordNetLemmatizer()
_stop_words  = set(stopwords.words('english'))

def _get_wordnet_pos(treebank_tag: str) -> str:
    """Mappe le tag POS NLTK vers le format attendu par WordNetLemmatizer."""
    from nltk.corpus import wordnet
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    return wordnet.NOUN


# Mots très génériques présents dans tous les genres littéraires — à exclure
# pour que TF-IDF ne les remonte pas comme discriminants
_domain_stopwords = {
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

def preprocess(text: str) -> str:
    """Nettoie et lemmatise un texte anglais."""
    # Lowercase + suppression de la ponctuation
    text = text.lower()
    text = re.sub(r'[' + re.escape(string.punctuation) + r']', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenisation
    tokens = word_tokenize(text)

    # Suppression des stopwords, domain stopwords, et tokens non alphabétiques courts
    all_stops = _stop_words | _domain_stopwords
    tokens = [t for t in tokens if t.isalpha() and len(t) > 2 and t not in all_stops]

    # Lemmatisation avec le bon tag POS
    tagged = nltk.pos_tag(tokens)
    lemmatized = [
        _lemmatizer.lemmatize(word, pos=_get_wordnet_pos(tag))
        for word, tag in tagged
        if _lemmatizer.lemmatize(word, pos=_get_wordnet_pos(tag)) not in _domain_stopwords
    ]

    return ' '.join(lemmatized)



print("\nPrétraitement en cours...")
genre_texts_processed = {genre: preprocess(text) for genre, text in genre_texts.items()}
for genre, text in genre_texts_processed.items():
    print(f"  {genre}: {len(text.split())} tokens après prétraitement")


# ---------------------------------------------------------------------------
# 4. EXTRACTION AVEC TF-IDF — Documents agrégés par genre
# ---------------------------------------------------------------------------
genres_list   = list(genre_texts_processed.keys())
texts_list    = [genre_texts_processed[g] for g in genres_list]

vectorizer    = TfidfVectorizer(min_df=1, sublinear_tf=True)
tfidf_matrix  = vectorizer.fit_transform(texts_list)
feature_names = vectorizer.get_feature_names_out()

print(f"\nVocabulaire TF-IDF : {len(feature_names)} termes uniques")


# ---------------------------------------------------------------------------
# 5. CRÉATION DU DICTIONNAIRE — Top 10 mots TF-IDF par genre
# ---------------------------------------------------------------------------
TOP_N = 50
genre_vocab: dict[str, list[str]] = {}

for i, genre in enumerate(genres_list):
    row        = tfidf_matrix[i].toarray().flatten()
    top_idx    = row.argsort()[::-1][:TOP_N]
    top_words  = [feature_names[j] for j in top_idx if row[j] > 0]
    genre_vocab[genre] = top_words
    print(f"\n{genre}:")
    for word in top_words:
        print(f"  {word:20s}  (tfidf={row[list(feature_names).index(word)]:.4f})")


# ---------------------------------------------------------------------------
# SÉRIALISATION — Sauvegarde dans genre_vocab.json
# ---------------------------------------------------------------------------
output_path = 'genre_vocab.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(genre_vocab, f, ensure_ascii=False, indent=2)

print(f"\nDictionnaire sauvegarde dans : {output_path}")
print(f"\nContenu final :")
print(json.dumps(genre_vocab, indent=2, ensure_ascii=False))
