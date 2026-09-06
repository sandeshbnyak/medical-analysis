import os
from pathlib import Path

import faiss
import numpy as np


class FAISSVectorStore:
    def __init__(self, index, chunks):
        self.index = index
        self.chunks = chunks

    @classmethod
    def from_chunks(cls, chunks, embeddings):
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.asarray(embeddings, dtype="float32"))
        return cls(index=index, chunks=chunks)

    def search(self, query_embedding, k=5):
        distances, indices = self.index.search(np.asarray([query_embedding], dtype="float32"), k)
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            item = dict(self.chunks[int(idx)])
            item["distance"] = float(distance)
            results.append(item)
        return results

    def save(self, path):
        faiss.write_index(self.index, str(path))

    @classmethod
    def load(cls, path, chunks):
        index = faiss.read_index(str(path))
        return cls(index=index, chunks=chunks)
