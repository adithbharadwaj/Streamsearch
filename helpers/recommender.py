import pickle

import pandas as pd

def load_similarity(filepath):
    return pd.read_pickle(filepath)

def topn_similar(similarity, id, n=10):
    try:
        return list(similarity[id].sort_values(ascending=False).index[1:(n+1)])
    except KeyError:
        return []
