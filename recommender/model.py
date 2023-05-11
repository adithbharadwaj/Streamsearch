import logging
import os
import pickle
from enum import Enum
from timeit import default_timer as timer

import numpy as np
from scipy.sparse import csr_matrix, hstack, vstack
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer

from .preprocessing import *

KEEP_COLUMNS = ['genres', 'overview', 'keywords']

FILENAME_ENCODER_GENRES = 'encoder_genres.pkl'
FILENAME_VECTORIZER_OVERVIEW = 'vectorizer_overview.pkl'
FILENAME_SVD = 'svd.pkl'

class EmbedderMode(Enum):
    TRAIN = 'train'
    INFER = 'infer'

    @classmethod
    def values(cls):
        return [e.value for e in cls]

class Embedder:
    def __init__(self):
        self.encoder_genres = None
        self.vectorizer_overview = None
        self.svd = None

    def train(self, media, vocab_size=None, embedding_dim=None):
        self.pipeline(media, EmbedderMode.TRAIN, vocab_size=vocab_size, embedding_dim=embedding_dim)

    def embed(self, media, save_path=None):
        embeddings, ids = self.pipeline(media, EmbedderMode.INFER)
        if save_path:
            logging.info(f'Saving embeddings to "{save_path}"')
            np.savez(save_path, embeddings=embeddings, ids=ids)
        return embeddings, ids

    def pipeline(self, media, mode, vocab_size=None, embedding_dim=None):
        assert mode.value in EmbedderMode.values()

        logging.info(f'{self.__class__.__name__} in [{mode.value}] mode.')

        media = media.loc[:, KEEP_COLUMNS]
        ids = media.index.to_numpy()

        logging.info('Preprocessing \'genres\'')
        media['genres'] = media['genres'].apply(extract_genre_names)

        logging.info('Encoding \'genres\'')
        if mode == EmbedderMode.TRAIN:
            self.encoder_genres = MultiLabelBinarizer()
            encoded_genres = self.encoder_genres.fit_transform(media['genres'])
        else:
            encoded_genres = self.encoder_genres.transform(media['genres'])

        logging.info('Preprocessing \'overview\'')
        media['overview'] = media['overview'].fillna('')

        logging.info('Injecting \'keywords\' into \'overview\'')
        media = inject_keywords(media)

        logging.info(f'Vectorizing \'overview\'...')
        time_start = timer()
        if mode == EmbedderMode.TRAIN:
            self.vectorizer_overview = TfidfVectorizer(
                strip_accents=False,
                lowercase=False,
                preprocessor=None,
                tokenizer=None,
                analyzer=normalize,
                norm='l2',
                max_features=vocab_size
            )
            vectorized_overview = self.vectorizer_overview.fit_transform(media['overview'])
        else:
            vectorized_overview = self.vectorizer_overview.transform(media['overview'])
        logging.info(f'Vectorizing \'overview\' took {round(timer() - time_start, 4)} s, for a vocabulary size of {len(self.get_vocab())}.')

        logging.info(f'Stacking vectorized overview onto encoded \'genres\'')
        embeddings = hstack([encoded_genres, vectorized_overview], format='csr')

        if mode == EmbedderMode.TRAIN:
            if embedding_dim:
                logging.info(f'Reducing dimension to {embedding_dim}...')
                time_start = timer()
                self.svd = TruncatedSVD(n_components=embedding_dim, algorithm='arpack')
                self.svd.fit(embeddings)
                logging.info(f'Dimensionality reduction took {round(timer() - time_start)} s.')
        else:
            if self.svd:
                logging.info(f'Reducing dimension to {embedding_dim}...')
                time_start = timer()
                embeddings = self.svd.transform(embeddings)
                logging.info(f'Dimensionality reduction took {round(timer() - time_start)} s.')

                logging.info('Sparsifying embeddings...')
                time_start = timer()
                embeddings = csr_matrix(embeddings)
                logging.info(f'Sparsifying embeddings took {round(timer() - time_start)} s.')

        if mode == EmbedderMode.INFER:
            return embeddings, ids

    def get_genres(self):
        return self.encoder_genres.classes_

    def get_vocab(self):
        return self.vectorizer_overview.get_feature_names_out()

    def get_embedding_dim(self):
        return self.svd.n_components_

    def save(self, model_path):
        with open(os.path.join(model_path, FILENAME_ENCODER_GENRES), 'w') as f:
            pickle.dump(self.encoder_genres, f)
        with open(os.path.join(model_path, FILENAME_VECTORIZER_OVERVIEW), 'w') as f:
            pickle.dump(self.vectorizer_overview, f)
        if self.svd:
            with open(os.path.join(model_path, FILENAME_SVD), 'w') as f:
                pickle.dump(self.svd, f)

    @classmethod
    def load(cls, model_path):
        embedder = cls()
        with open(os.path.join(model_path, FILENAME_ENCODER_GENRES), 'r') as f:
            embedder.encoder_genres = pickle.load(f)
        with open(os.path.join(model_path, FILENAME_VECTORIZER_OVERVIEW), 'r') as f:
            embedder.vectorizer_overview = pickle.dump(f)

        svd_path = os.path.join(model_path, FILENAME_SVD)
        if os.path.exists(svd_path):
            with open(svd_path, 'r'):
                embedder.svd = pickle.load(f)
        else:
            embedder.svd = None

        return embedder

    @staticmethod
    def load_embeddings(embeddings_dir):
        embeddings = None
        ids = np.array([])

        for filename in os.listdir(embeddings_dir):
            if os.path.splitext(filename)[1] == '.npz':
                contents = np.load(os.path.join(embeddings_dir, filename), allow_pickle=True)
                new_embeddings = contents['embeddings'].item()
                new_ids = contents['ids']

                if embeddings is None:
                    embeddings = new_embeddings
                else:
                    embeddings = vstack([embeddings, new_embeddings], format='csr')

                ids = np.append(ids, new_ids)

        return embeddings, ids

class Recommender:
    def __init__(self):
        pass
