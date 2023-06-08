import logging
import os
import pickle
from enum import Enum
from timeit import default_timer as timer

import numpy as np
from scipy.sparse import csr_matrix, hstack, vstack
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer

from .preprocessing import *

KEEP_COLUMNS = ['genres', 'overview']

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

    def train(self, medias, vocab_size=None, embedding_dim=None):
        self.pipeline(medias, EmbedderMode.TRAIN, vocab_size=vocab_size, embedding_dim=embedding_dim)

    def embed(self, medias, save_path=None):
        embeddings, ids = self.pipeline(medias, EmbedderMode.INFER)
        if save_path:
            logging.info(f'Saving embeddings to "{save_path}"')
            np.savez(save_path, embeddings=embeddings, ids=ids)
        return embeddings, ids

    def embed_batches(self, medias, batch_size, save_dir):
        assert (batch_size > 0) and (batch_size <= medias.shape[0])

        num_batches = int(np.ceil(medias.shape[0] / batch_size))

        batch_idx = 1
        lower = 0   # Lower row of batch

        while lower < medias.shape[0]:
            if lower + batch_size > medias.shape[0]:
                upper = medias.shape[0]     # Upper row of batch (exclusive)
            else:
                upper = lower + batch_size

            print(f'BATCH {batch_idx}/{num_batches}', end='\n\n')

            self.embed(medias.iloc[lower:upper, :], save_path=os.path.join(save_dir, f'embeddings-{batch_idx}.npz'))

            print('–' * 80)

            lower = upper
            batch_idx += 1

    def pipeline(self, medias, mode, vocab_size=None, embedding_dim=None):
        assert mode.value in EmbedderMode.values()

        logging.info(f'{self.__class__.__name__} in [{mode.value}] mode.')

        medias = medias.loc[:, KEEP_COLUMNS]
        ids = medias.index.to_numpy()

        logging.info('Preprocessing \'genres\'')
        medias['genres'] = medias['genres'].apply(extract_genre_names)

        logging.info('Encoding \'genres\'')
        if mode == EmbedderMode.TRAIN:
            self.encoder_genres = MultiLabelBinarizer()
            encoded_genres = self.encoder_genres.fit_transform(medias['genres'])
        else:
            encoded_genres = self.encoder_genres.transform(medias['genres'])

        logging.info('Preprocessing \'overview\'')
        medias['overview'] = medias['overview'].fillna('')

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
            vectorized_overview = self.vectorizer_overview.fit_transform(medias['overview'])
        else:
            vectorized_overview = self.vectorizer_overview.transform(medias['overview'])
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
                logging.info(f'Reducing dimension to {self.get_embedding_dim()}...')
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
        return self.svd.n_components

    def save(self, model_path):
        with open(os.path.join(model_path, FILENAME_ENCODER_GENRES), 'wb+') as f:
            pickle.dump(self.encoder_genres, f)
        with open(os.path.join(model_path, FILENAME_VECTORIZER_OVERVIEW), 'wb+') as f:
            pickle.dump(self.vectorizer_overview, f)
        if self.svd:
            with open(os.path.join(model_path, FILENAME_SVD), 'wb+') as f:
                pickle.dump(self.svd, f)

    @classmethod
    def load(cls, model_path):
        embedder = cls()
        with open(os.path.join(model_path, FILENAME_ENCODER_GENRES), 'rb') as f:
            embedder.encoder_genres = pickle.load(f)
        with open(os.path.join(model_path, FILENAME_VECTORIZER_OVERVIEW), 'rb') as f:
            embedder.vectorizer_overview = pickle.load(f)

        svd_path = os.path.join(model_path, FILENAME_SVD)
        if os.path.exists(svd_path):
            with open(svd_path, 'rb') as f:
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
    def __init__(self, embeddings, ids):
        self.embeddings = embeddings
        self.ids = ids

    @classmethod
    def from_dir(cls, embeddings_dir):
        embeddings, ids = Embedder.load_embeddings(embeddings_dir)
        return cls(embeddings, ids)

    def recommend(self, embedding, n=10):
        similarity = cosine_similarity(self.embeddings, embedding).flatten()

        most_similar_rows = np.argsort(-similarity)
        if most_similar_rows[0] == 1:
            most_similar_rows = most_similar_rows[1:(n+1)]
        else:
            most_similar_rows = most_similar_rows[:n]

        most_similar_ids = [
            int(self.ids[row])
            for row in most_similar_rows
        ]

        return most_similar_ids

    def recommend_by_id(self, id, n=10):
        assert id in self.ids

        row = list(self.ids).index(id)
        embedding = self.embeddings[row]

        return self.recommend(embedding, n=n+1)[1:]

    def recommend_pprint(self, id, titles, n=10):
        query_title = ids_to_titles(id, titles)
        print(f'Top {n} similar movies to "{query_title}":')
        for similar_id in self.recommend_by_id(id, n=n):
            print(f'* {ids_to_titles(similar_id, titles)}')

def ids_to_titles(ids, titles):
    if type(ids) == int:
        return titles[ids]
    return list(map(titles.__getitem__, ids))
