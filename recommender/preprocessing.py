import json
import unicodedata
from functools import partial
from timeit import default_timer as timer

import pandas as pd
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer

STOPWORDS = ENGLISH_STOP_WORDS.union(stopwords.words('english'))

def extract_genre_names(json_str):
    genres = map(lambda genre: genre['name'], json.loads(json_str))
    genres = map(lambda genre: genre.lower().replace(' ', '-'), genres)
    return set(genres)

def encode_genres(media):
    encoder_genres = MultiLabelBinarizer()
    genres_enc = encoder_genres.fit_transform(media['genres'])

    genre_columns = list(map(lambda genre: f'is_{genre}', encoder_genres.classes_))
    genres_enc = pd.DataFrame(genres_enc, columns=genre_columns, index=media.index)

    media = media.join(genres_enc)
    media = media.drop(columns=['genres'])

    return media, encoder_genres, genre_columns

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

def encode_overview(media, vocab_size=None):
    try:
        stopwords.words('english')
    except LookupError:
        import nltk
        nltk.download('stopwords')

    # IMP: Don't use the `stop_words` parameter as it doesn't work when using a custom `analyzer`.
    encoder_overview = TfidfVectorizer(
        strip_accents=False,
        lowercase=False,
        preprocessor=None,
        tokenizer=None,
        analyzer=normalize,
        norm='l2',
        max_features=vocab_size
    )
    overview_enc = encoder_overview.fit_transform(media['overview'])

    overview_columns = list(map(lambda token: f'tfidf_{token}', encoder_overview.get_feature_names_out()))
    overview_enc = pd.DataFrame(overview_enc.todense(), columns=overview_columns, index=media.index)

    media = media.join(overview_enc)
    media = media.drop(columns=['overview'])

    return media, encoder_overview, overview_columns

def reduce_embedding_dim(embeddings, new_embedding_dim):
    assert new_embedding_dim < embeddings.shape[1]

    pca = PCA(n_components=new_embedding_dim)
    embeddings = pca.fit_transform(embeddings)

    return embeddings, pca
