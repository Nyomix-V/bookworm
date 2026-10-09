# config.py — Configuration et dictionnaires de mots vides pour bookworm.py

# Dictionnaire de mots narratifs omniprésents dans la fiction victorienne (exclus de la classification de genre)
DOMAIN_STOPWORDS = {
    # Pronoms, prépositions, articles, verbes auxiliaires et mots très fréquents
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
    # Narrative and common Victorian fiction terms additionnels
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
    # Nouveaux ajouts de mots génériques identifiés
    'yet', 'yard', 'company', 'cast', 'bury', 'beneath', 'accidentally',
    'encounter', 'everyone', 'discovers', 'chemical', 'alternate', 'complex',
    'connection', 'destroys', 'contrast', 'desire', 'trial', 'strike',
    'pressure', 'retire', 'miss', 'spot', 'ago', 'locate', 'original',
    'sign', 'plan', 'reason', 'achieves', 'adapt', 'waste', 'basement',
    'central', 'van', 'decide', 'totalitarian', 'conqueror', 'connect'
}

# Verbes génériques exclus du topic modeling (Etape 7)
GENERIC_VERBS = {
    'say', 'says', 'said', 'ask', 'asks', 'asked', 'reply', 'replies', 'replied',
    'answer', 'answers', 'answered', 'tell', 'tells', 'told', 'speak', 'speaks', 'spoke',
    'spoken', 'talk', 'talks', 'talked', 'cry', 'cries', 'cried', 'shout', 'shouted',
    'whisper', 'whispered', 'exclaim', 'exclaimed', 'call', 'called', 'calling',
    'go', 'goes', 'went', 'going', 'gone', 'come', 'comes', 'came', 'coming',
    'take', 'takes', 'took', 'taking', 'taken', 'give', 'gives', 'gave', 'giving', 'given',
    'make', 'makes', 'made', 'making', 'do', 'does', 'did', 'done', 'doing',
    'find', 'finds', 'found', 'finding', 'get', 'gets', 'got', 'getting', 'gotten',
    'look', 'looks', 'looked', 'looking', 'see', 'sees', 'saw', 'seen', 'seeing',
    'hear', 'hears', 'heard', 'hearing', 'listen', 'listened', 'turn', 'turned',
    'think', 'thinks', 'thought', 'thinking', 'know', 'knows', 'knew', 'knowing', 'known',
    'want', 'wants', 'wanted', 'wanting', 'seem', 'seems', 'seemed', 'seeming',
    'feel', 'feels', 'felt', 'feeling', 'believe', 'believed', 'remember', 'remembered',
    'forget', 'forgot', 'hope', 'hoped', 'wish', 'wished', 'wonder', 'wondered',
    'would', 'could', 'should', 'shall', 'will', 'must', 'might', 'ought', 'may',
    'begin', 'began', 'beginning', 'start', 'started', 'starting', 'stop', 'stopped',
    'keep', 'kept', 'keeping', 'hold', 'held', 'bring', 'brought', 'carry', 'carried',
    'put', 'leave', 'left', 'leaving', 'run', 'ran', 'stand', 'stood', 'sit', 'sat',
    'become', 'became', 'happen', 'happened', 'mean', 'meant', 'meaning', 'try', 'tried',
    'trying', 'need', 'needs', 'needed', 'let', 'use', 'uses', 'used'
}

# Mots narratifs généraux exclus du topic modeling (Etape 7)
GENERIC_WORDS = {
    'little', 'well', 'like', 'must', 'much', 'many', 'good', 'great', 'poor', 'dear',
    'upon', 'first', 'last', 'next', 'course', 'thing', 'things', 'people', 'person',
    'time', 'way', 'day', 'night', 'room', 'house', 'door', 'window', 'hand', 'eyes',
    'head', 'face', 'voice', 'chapter', 'back', 'away', 'never', 'always', 'almost',
    'quite', 'rather', 'still', 'even', 'something', 'nothing', 'anything', 'someone',
    'everyone', 'another', 'other', 'others', 'without', 'long', 'short', 'old', 'young',
    'place', 'world', 'year', 'years', 'life', 'death', 'here', 'there', 'now', 'then',
    'project', 'gutenberg', 'ebook', 'license', 'online', 'author', 'translator',
    'publisher', 'published', 'illustration', 'illustrations', 'illustrator',
    'volume', 'book', 'works', 'complete', 'part', 'chapter', 'section',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'right', 'left', 'sure', 'certain', 'minute', 'minutes', 'second', 'seconds',
    'moment', 'moments', 'hour', 'hours', 'however', 'perhaps', 'maybe', 'indeed',
    'though', 'either', 'neither', 'enough', 'also', 'yet', 'ready', 'ever', 'never',
    'yer', 'ye', 'thy', 'thee', 'thou'
}

# --- Constantes pour la reconnaissance d'entités nommées (NER) ---

CHAR_INDICATOR_WORDS = {
    'rabbit', 'hatter', 'turtle', 'mouse', 'dormouse', 'gryphon', 'caterpillar', 
    'hare', 'dodo', 'queen', 'king', 'duchess', 'prince', 'princess', 'captain', 
    'doctor', 'sir', 'lord', 'lady', 'mr', 'mrs', 'miss', 'cook', 'baby', 
    'soldier', 'dracula', 'harker', 'mina', 'jonathan', 'van helsing', 'helsing', 
    'lucy', 'seward', 'renfield', 'sherlock', 'holmes', 'watson', 'poirot', 'jack', 
    'dorothy', 'wizard', 'alice', 'peter', 'pan', 'wendy', 'hook', 'john', 'michael',
    'cinderella', 'snow', 'white', 'beast', 'beauty', 'pinocchio', 'mowgli', 'bagheera',
    'baloo', 'shere', 'khan', 'kaa', 'akela', 'tarzan', 'jane',
    'clown', 'clowns', 'stork', 'storks', 'eaglet', 'eaglets', 'monkey', 'monkeys', 'beasts',
    'dodo', 'pigeon', 'lizard', 'pat',
    'goat', 'beetle', 'gnat', 'walrus', 'unicorn', 'lion', 'panther', 'leopard', 'tiger', 'peacock',
    'otter', 'badger', 'mole', 'rat', 'toad', 'camel', 'elephant', 'bear', 'wolf', 'fox', 'sheep',
    'pig', 'cow', 'bull', 'calf', 'dog', 'cat', 'mouse', 'bird', 'eagle', 'hawk', 'owl', 'crow',
    'raven', 'sparrow', 'robin', 'pigeon', 'dove', 'swan', 'duck', 'goose', 'hen', 'rooster',
    'chicken', 'frog', 'toad', 'fish', 'shark', 'whale', 'crab', 'lobster', 'seal', 'seals'
}

SPEECH_ACTION_VERBS = {
    'said', 'thought', 'cried', 'replied', 'asked', 'whispered', 'exclaimed', 
    'sighed', 'began', 'told', 'went', 'came', 'looked', 'saw', 'heard', 
    'took', 'gave', 'made', 'called', 'cries', 'says', 'sat', 'stood', 
    'walked', 'ran', 'jumped', 'smiled', 'laughed', 'shouted', 'ordered'
}

LOC_INDICATOR_WORDS = {
    'wonderland', 'england', 'london', 'transylvania', 'bistritz', 'galatz', 
    'whitby', 'munich', 'exeter', 'europe', 'america', 'france', 'paris', 
    'rome', 'castle', 'street', 'road', 'lake', 'river', 'sea', 'ocean', 
    'country', 'city', 'town', 'village', 'island',
    'united', 'states', 'kingdom', 'republic', 'empire', 'netherlands', 'bulgaria', 'germany', 'austria',
    'hungary', 'romania', 'russia', 'switzerland', 'italy', 'spain', 'mountains', 'mountain', 'mount',
    'mt', 'mt.', 'valley', 'pass', 'gulf', 'bay', 'port', 'harbour', 'harbor', 'cape', 'peninsula',
    'islands', 'continent', 'county', 'district', 'province', 'border', 'frontier', 'creek', 'canal',
    'channel', 'forest', 'wood', 'woods', 'desert', 'park', 'square', 'garden', 'gardens', 'palace',
    'manor', 'abbey', 'cathedral', 'church', 'temple', 'house', 'hall', 'villa', 'cottage', 'station',
    'hotel', 'inn', 'tavern', 'museum', 'university', 'college', 'school', 'hospital', 'asylum',
    'prison', 'jail', 'cemetery', 'grave', 'tomb', 'carfax', 'piccadilly', 'varna', 'purfleet',
    'mediterranean', 'pacific', 'atlantic', 'indian', 'arctic', 'antarctic', 'vanikoro', 'danube',
    'thames', 'rhine', 'seine', 'kansas', 'derbyshire', 'windsor', 'ealing', 'montagu', 'pole', 'south pole', 'north pole',
    'india', 'yorkshire', 'china', 'woking', 'weybridge', 'richmond', 'leatherhead', 'canada', 'egypt',
    'turkey', 'greece', 'japan', 'holland', 'amsterdam', 'budapest', 'surrey', 'hampshire', 'kent', 'sussex'
}

TITLE_PREFIXES = {
    'poor', 'dear', 'young', 'old', 'little', 'great', 'good',
    'mr', 'mrs', 'dr', 'sir', 'lord', 'lady', 'miss', 'madam',
    'mr.', 'mrs.', 'dr.', 'sir.', 'ms.', 'ms'
}

TITLES = {
    'mr', 'mrs', 'miss', 'sir', 'dr', 'lord', 'lady', 'queen', 'king', 'captain', 'uncle', 'aunt', 'poor', 'dear',
    'earl', 'duke', 'baron', 'knight', 'count', 'emperor'
}

GUTENBERG_NOISE = {
    'project', 'gutenberg', 'license', 'online', 'ebook', 'author', 'translator', 
    'editor', 'published', 'publisher', 'illustrator', 'illustrated', 'chapter', 
    'credits', 'release', 'date', 'language', 'character', 'set', 'utf', 
    'copying', 'distribution', 'work', 'title', 'see', 'read', 'first', 'last', 'new'
}

CONTRACTION_FRAGMENTS = {'ll', 've', 're', 'd', 's', 'm', 't', 'nt', 'il', "n't"}

EXTRA_STOP = {
    'even', 'then', 'thus', 'here', 'there', 'some', 'many', 'both', 'each', 
    'every', 'very', 'only', 'just', 'also', 'well', 'soon', 'good', 'dear', 
    'oh', 'ah', 'shall', 'would', 'could', 'should', 'cannot', 'things', 
    'something', 'nothing', 'anything', 'someone', 'everyone', 'chapter', 
    'page', 'english', 'french', 'german', 'spanish', 'italian', 'latin', 
    'american', 'british', 'russian', 'west', 'east', 'north', 'south', 'yes', 'no',
    'god', 'lord', 'lady', 'majesty', 'coroner', 'sir', 'doctor', 'professor',
    'city', 'place', 'world', 'earth', 'street', 'road', 'lane', 'avenue', 'town',
    'whilst', 'always', 'almost', 'never', 'ever', 'began', 'came', 'went', 'asked',
    'said', 'thought', 'looked', 'seemed', 'heard', 'saw', 'took', 'gave', 'made',
    'done', 'did', 'does', 'do', 'go', 'goes', 'going', 'come', 'find', 'found',
    'tell', 'told', 'see', 'read', 'write', 'wrote', 'written', 'speak', 'spoke',
    'spoken', 'laugh', 'laughed', 'cried', 'cry', 'think', 'thinks', 'thinking',
    'feel', 'felt', 'feeling', 'know', 'knew', 'known', 'knows', 'outside', 'inside',
    'indeed', 'perhaps', 'probably', 'possibly', 'truly', 'really', 'surely',
    'already', 'yet', 'still', 'now', 'where', 'when', 'why', 'how', 'who', 'whom',
    'whose', 'which', 'what', 'whatever', 'whoever', 'whichever', 'whenever',
    'wherever', 'poor', 'time', 'miss', 'mr', 'mrs', 'ms', 'dr', 'madam'
}

ENTITY_BLACKLIST = {
    # Concepts abstraits / états
    'death', 'life', 'time', 'nature', 'fate', 'truth', 'justice', 'freedom',
    'love', 'hate', 'fear', 'hope', 'faith', 'soul', 'spirit', 'mind', 'heart',
    'power', 'force', 'light', 'dark', 'darkness', 'evil', 'good',
    # Rôles/titres sans nom propre
    'captain', 'count', 'king', 'queen', 'prince', 'princess', 'duke', 'master',
    'servant', 'guard', 'soldier', 'officer', 'chief', 'head', 'leader', 'general',
    # Formats narratifs
    'diary', 'journal', 'letter', 'chapter', 'note', 'record', 'memorandum',
    'narrative', 'story', 'tale', 'account', 'report', 'entry', 'excerpt',
    # Mots relationnels
    'friend', 'mother', 'father', 'sister', 'brother', 'uncle', 'aunt',
    'husband', 'wife', 'son', 'daughter', 'family', 'child', 'baby',
    # Directions / positions génériques
    'east', 'west', 'north', 'south', 'centre', 'center', 'middle',
    # Adjectifs nominalisés courants
    'great', 'young', 'old', 'poor', 'little', 'big', 'high', 'low', 'long',
    'strong', 'weak', 'rich', 'true', 'false', 'real', 'last', 'first', 'next',
    # Divers génériques
    'art', 'work', 'end', 'day', 'night', 'morning', 'evening', 'year', 'month',
    'man', 'woman', 'men', 'women', 'boy', 'girl', 'person', 'people', 'folk',
    'hand', 'face', 'eyes', 'voice', 'words', 'word', 'thing', 'things', 'way',
    'place', 'room', 'house', 'home', 'door', 'window', 'wall', 'floor', 'table',
    # Exclamations / interjections fréquemment capitalisées en milieu de phrase
    'alas', 'sacred', 'cross', 'holy', 'blessed', 'curse', 'devil', 'god',
    'thank', 'pray', 'glad', 'sorry', 'indeed', 'surely', 'certainly', 'perhaps',
    # Structures / lieux génériques (sans nom propre associé)
    'castle', 'gate', 'bridge', 'tower', 'garden', 'park', 'square', 'port',
    'shore', 'cliff', 'field', 'forest', 'hill', 'valley', 'coast', 'river',
    # Ethnies / groupes / nationalités (souvent mal taggés comme PERSON)
    'slovaks', 'gypsies', 'romani', 'peasants', 'villagers', 'natives',
    'soldiers', 'guards', 'sailors', 'crew', 'servants', 'men', 'women',
    'english', 'french', 'german', 'spanish', 'dutch', 'hungarian', 'transylvanian',
    # Noms géographiques génériques sans nom propre
    'exeter', 'galatz', 'budapest', 'munich',
    # --- AJOUTS DE MOIS, JOURS, NATIONALITÉS ET BRUIT D'OBJETS ---
    'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'egyptian', 'japanese', 'chinese', 'indian', 'belgian', 'greek', 'turkish', 'swiss', 'austrian', 'canadian', 'american', 'russian', 'british', 'scottish', 'irish',
    'balloon', 'spectacles', 'apron', 'ribbon', 'throne', 'straw', 'key', 'gates', 'guardian', 'guardians',
    'beast', 'beasts', 'clown', 'clowns', 'stork', 'storks', 'eaglet', 'eaglets', 'opalsens',
    'emerald', 'emeralds', 'star', 'stars', 'wish', 'wishes', 'diamond', 'diamonds', 'pearl', 'pearls',
    'stone', 'stones', 'opals', 'opal', 'gold', 'silver', 'wood', 'tin', 'iron', 'cap',
    'western', 'eastern', 'northern', 'southern',
    # --- NOUVEAUX RETAILS DE NETTOYAGE ---
    'magic', 'woods', 'sea', 'lake', 'river', 'mountain', 'hill', 'valley', 'palace', 'machine',
    'silent', 'upper', 'lower', 'christian', 'christians', 'frenchman', 'frenchwoman', 'chinaman',
    'hindustani', 'eskimo', 'eskimos', 'norwegian', 'hullo', 'whip', 'law', 'fish', 'pain', 'swine',
    'yellow', 'jasmine', 'golden', 'age', 'porcelain', 'liberty', 'bonds', 'morcar', 'children', 'nights'
}

MULTIWORD_EXCLAMATIONS = {
    'thank god', 'oh dear', 'good lord', 'good heavens', 'my god',
    'dear god', 'good god', 'oh god', 'holy god', 'bless me',
    'dear me', 'alas poor', 'so help',
}

