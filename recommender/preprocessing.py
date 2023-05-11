import json
import unicodedata
from functools import partial

from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

STOPWORDS = ENGLISH_STOP_WORDS.union(stopwords.words('english'))

def extract_genre_names(json_str):
    genres = map(lambda genre: genre['name'], json.loads(json_str))
    genres = map(lambda genre: genre.lower().replace(' ', '-'), genres)
    return set(genres)

def tokenize(raw_str):
    try:
        tokens = word_tokenize(raw_str)
    except LookupError:
        import nltk
        nltk.download('punkt')
    tokens = filter(lambda token: token.isalpha(), tokens)
    tokens = map(lambda token: token.lower(), tokens)
    tokens = map(partial(unicodedata.normalize, 'NFKC'), tokens)
    return list(tokens)

def to_wordnet_pos(penn_pos):
    if penn_pos.startswith('V'):
        return wordnet.VERB
    elif penn_pos.startswith('J'):
        return wordnet.ADJ
    elif penn_pos.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def lemmatize(tokens):
    lemmatizer = WordNetLemmatizer()

    try:
        poss = list(map(lambda tag: to_wordnet_pos(tag[1]), pos_tag(tokens)))
    except LookupError:
        import nltk
        nltk.download('averaged_perceptron_tagger')

    tokens = [
        lemmatizer.lemmatize(token, pos=poss[i])
        for i, token in enumerate(tokens)
    ]

    return tokens

def normalize(raw_str):
    tokens = tokenize(raw_str)
    tokens = lemmatize(tokens)
    tokens = list(filter(lambda token: token not in STOPWORDS, tokens))
    return tokens

def inject_keywords(media):
    media['overview'] = media['overview'] + media['keywords']
    media = media.drop(columns=['keywords'])
    return media
