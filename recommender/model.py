import logging
import os

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import *

KEEP_COLUMNS = ['genres', 'overview', 'keywords']

FILENAME_IDS = 'ids.npy'
FILENAME_EMBEDDINGS = 'embeddings.npy'
FILENAME_SIMILARITY = 'similarity.npy'
FILENAME_VOCAB = 'vocab.npy'

class Recommender:
    def __init__(self):
        self.ids = None
        self.similarity = None

        self.embeddings = None
        self.vocab = None

    def train(self, media, vocab_size=None, embedding_dim=None):
        media = media.loc[:, KEEP_COLUMNS]

        self.ids = media.index.to_numpy()   # Need this to index into `embeddings` and `similarity`.

        logging.info('Preprocessing \'genres\'')
        media['genres'] = media['genres'].apply(extract_genre_names)

        logging.info('Encoding \'genres\'')
        media, _, _ = encode_genres(media)

        logging.info('Preprocessing \'overview\'')
        media['overview'] = media['overview'].fillna('')

        logging.info('Injecting \'keywords\' into \'overview\'')
        media = inject_keywords(media)

        logging.info(f'Encoding \'overview\'...')
        time_start = timer()
        media, encoder_overview, _ = encode_overview(media, vocab_size=vocab_size)
        self.vocab = encoder_overview.get_feature_names_out()
        logging.info(f'Encoding \'overview\' took {round(timer() - time_start, 4)} s, for a vocabulary size of {len(self.vocab)}.')

        self.embeddings = media.values

        if embedding_dim:
            logging.info(f'Reducing embeddings to {embedding_dim}-length vectors...')
            time_start = timer()
            self.embeddings, _ = reduce_embedding_dim(self.embeddings, embedding_dim)
            logging.info(f'Reducing embedding dimension took {round(timer() - time_start)} s.')

        logging.info('Computing cosine similarity...')
        time_start = timer()
        self.similarity = cosine_similarity(media)
        logging.info(f'Computing cosine similarity took {round(timer() - time_start, 4)} s.')

    def recommend(self, id, n=10):
        row = list(self.ids).index(id)
        cols = (-self.similarity[row]).argsort()[1:(n+1)]
        similar_ids = [self.ids[col] for col in cols]
        return similar_ids

    def recommend_pprint(self, titles, id, n=10):
        print(f'Top {n} similar movies to \"{titles[id]}\":')
        for similar_id in self.recommend(id, n=n):
            print(f'* {titles[similar_id]}')

    def save(self, model_path, inference=False):
        os.makedirs(model_path, exist_ok=True)

        np.save(os.path.join(model_path, FILENAME_IDS), self.ids)
        np.save(os.path.join(model_path, FILENAME_SIMILARITY), self.similarity)

        # Optional fields not required for inference.
        if not inference:
            np.save(os.path.join(model_path, FILENAME_EMBEDDINGS), self.embeddings)
            np.save(os.path.join(model_path, FILENAME_VOCAB), self.similarity)

    @classmethod
    def load(cls, model_path, inference=True):
        rec = cls()

        rec.ids = np.load(os.path.join(model_path, FILENAME_IDS))
        rec.similarity = np.load(os.path.join(model_path, FILENAME_SIMILARITY))

        if not inference:
            rec.embeddings = np.load(os.path.join(model_path, FILENAME_EMBEDDINGS))
            rec.vocab = np.load(os.path.join(model_path, FILENAME_VOCAB))

        return rec
