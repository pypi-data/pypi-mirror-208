from typing import Callable

import h5py
import numpy as np
import scann


class ANNEngine:
    def __init__(self, path):
        self.path = path
        self.searcher = self.load_embeddings()

    def load_embeddings(self, path: str, name: str, callback: Callable = None):
        searcher = None

        with h5py.File(path, "r") as f:
            searcher = (
                scann.scann_ops_pybind.builder(f[name], 10, "dot_product")
                .tree(
                    num_leaves=2000,
                    num_leaves_to_search=100,
                    training_sample_size=250000,
                )
                .score_ah(2, anisotropic_quantization_threshold=0.2)
                .reorder(100)
                .build()
            )

        return searcher

    def search(
        self, query: np.ndarray, k: int
    ) -> tuple(np.ndarray, np.ndarray):
        return self.searcher.search(query, final_num_neighbors=k)

    def msearch(
        self, queries: np.ndarray, k: int
    ) -> tuple(np.ndarray, np.ndarray):
        return self.searcher.search_batched(queries, final_num_neighbors=k)

    def bsearch(
        self, queries: np.ndarray, k: int
    ) -> tuple(np.ndarray, np.ndarray):
        return self.searcher.search_batched(queries, final_num_neighbors=k)

    def autotune(self):
        raise NotImplementedError
