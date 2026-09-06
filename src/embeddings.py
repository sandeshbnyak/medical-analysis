import numpy as np
from sentence_transformers import SentenceTransformer


@staticmethod
def _sentence_transformer_static(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    return SentenceTransformer(model_name)


def load_embedder(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    return SentenceTransformer(model_name)


def embed_texts(embedder, texts):
    embeddings = embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return np.asarray(embeddings, dtype="float32")
