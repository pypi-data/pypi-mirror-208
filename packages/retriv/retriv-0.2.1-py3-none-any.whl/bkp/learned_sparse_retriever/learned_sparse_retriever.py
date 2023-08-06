import os
from pathlib import Path
from typing import Dict, Iterable, List, Set, Union

import numba as nb
import numpy as np
import orjson
from indxr import Indxr
from numba.typed import List as TypedList
from oneliner_utils import create_path, read_jsonl
from tqdm import tqdm
from transformers import AutoTokenizer

from ..base_retriever import BaseRetriever
from ..utils.paths import docs_path, sr_state_path
from .build_inverted_index import build_inverted_index
from .sparse_retrieval_models.sum_impacts import sum_impacts, sum_impacts_multi


def home_path():
    p = Path(Path.home() / ".retriv" / "collections")
    p.mkdir(parents=True, exist_ok=True)
    return p


class LearnedSparseRetriever(BaseRetriever):
    def __init__(
        self,
        index_name: str = "new-index",
        tokenizer_path: str = None,
        hyperparams: dict = None,
    ):
        self.init_args = {
            "index_name": index_name,
            "tokenizer": AutoTokenizer.from_pretrained(tokenizer_path),
        }

        self.index_name = index_name

        self.id_mapping = None
        self.inverted_index = None
        self.vocabulary = None
        self.doc_count = None
        self.doc_lens = None
        self.relative_doc_lens = None
        self.doc_index = None

        self.preprocessing_args = {"tokenizer": self.tokenizer}

        self.hyperparams = {} if hyperparams is None else hyperparams

    def save(self):
        print(f"Saving {self.index_name} index on disk...")

        state = {
            "init_args": self.init_args,
            "id_mapping": self.id_mapping,
            "doc_count": self.doc_count,
            "inverted_index": self.inverted_index,
            "vocabulary": self.vocabulary,
            "doc_lens": self.doc_lens,
            "relative_doc_lens": self.relative_doc_lens,
            "hyperparams": self.hyperparams,
        }

        np.savez_compressed(sr_state_path(self.index_name), state=state)

    @staticmethod
    def load(index_name: str = "new-index"):
        print(f"Loading {index_name} from disk...")

        state = np.load(sr_state_path(index_name), allow_pickle=True)["state"][
            ()
        ]

        se = LearnedSparseRetriever(**state["init_args"])
        se.doc_index = Indxr(docs_path(index_name))
        se.id_mapping = state["id_mapping"]
        se.doc_count = state["doc_count"]
        se.inverted_index = state["inverted_index"]
        se.vocabulary = set(se.inverted_index)
        se.doc_lens = state["doc_lens"]
        se.relative_doc_lens = state["relative_doc_lens"]
        se.hyperparams = state["hyperparams"]

        state = {
            "init_args": se.init_args,
            "id_mapping": se.id_mapping,
            "doc_count": se.doc_count,
            "inverted_index": se.inverted_index,
            "vocabulary": se.vocabulary,
            "doc_lens": se.doc_lens,
            "relative_doc_lens": se.relative_doc_lens,
            "hyperparams": se.hyperparams,
        }

        return se

    def index_aux(self, show_progress: bool = True):
        collection = read_jsonl(
            docs_path(self.index_name),
            generator=True,
            callback=lambda x: x["text"],
        )

        # Preprocessing --------------------------------------------------------
        collection = multi_preprocessing(
            collection=collection,
            **self.preprocessing_args,
            n_threads=os.cpu_count(),
        )  # This is a generator

        # Inverted index -------------------------------------------------------
        self.inverted_index, self.relative_doc_lens = build_inverted_index(
            collection=collection,
            n_docs=self.doc_count,
            min_df=self.min_df,
            show_progress=show_progress,
        )
        self.vocabulary = set(self.inverted_index)

    def index(
        self,
        collection: Iterable,
        callback: callable = None,
        show_progress: bool = True,
    ):
        self.save_collection(collection, callback, show_progress)
        self.initialize_doc_index()
        self.initialize_id_mapping()
        self.doc_count = len(self.id_mapping)
        self.index_aux(show_progress)
        self.save()
        return self

    def index_file(
        self, path: str, callback: callable = None, show_progress: bool = True
    ) -> None:
        collection = self.collection_generator(path=path, callback=callback)
        return self.index(collection=collection, show_progress=show_progress)

    # SEARCH ===================================================================
    def query_preprocessing(self, query: str) -> List[str]:
        return preprocessing(query, **self.preprocessing_args)

    def get_term_doc_impacts(self, query_terms: List[str]) -> nb.types.List:
        return TypedList([self.inverted_index[t]["tfs"] for t in query_terms])

    def get_doc_ids(self, query_terms: List[str]) -> nb.types.List:
        return TypedList(
            [self.inverted_index[t]["doc_ids"] for t in query_terms]
        )

    def search(self, query: str, return_docs: bool = True, cutoff: int = 100):
        query_terms = self.query_preprocessing(query)
        if not query_terms:
            return {}
        query_terms = [t for t in query_terms if t in self.vocabulary]
        if not query_terms:
            return {}

        doc_ids = self.get_doc_ids(query_terms)
        term_doc_impacts = self.get_term_doc_impacts(query_terms)

        unique_doc_ids, scores = sum_impacts(
            term_doc_impacts=term_doc_impacts,
            doc_ids=doc_ids,
            relative_doc_lens=self.relative_doc_lens,
            cutoff=cutoff,
            **self.hyperparams,
        )

        unique_doc_ids = self.map_internal_ids_to_original_ids(unique_doc_ids)

        if not return_docs:
            return dict(zip(unique_doc_ids, scores))

        return self.prepare_results(unique_doc_ids, scores)

    def msearch(self, queries: List[Dict[str, str]], cutoff: int = 100):
        term_doc_impacts = TypedList()
        doc_ids = TypedList()
        q_ids = []
        no_results_q_ids = []

        for q in queries:
            q_id, query = q["id"], q["text"]
            query_terms = self.query_preprocessing(query)
            query_terms = [t for t in query_terms if t in self.vocabulary]
            if not query_terms:
                no_results_q_ids.append(q_id)
                continue

            if all(t not in self.inverted_index for t in query_terms):
                no_results_q_ids.append(q_id)
                continue

            q_ids.append(q_id)
            term_doc_impacts.append(self.get_term_doc_impacts(query_terms))
            doc_ids.append(self.get_doc_ids(query_terms))

        if not q_ids:
            return {q_id: {} for q_id in [q["id"] for q in queries]}

        unique_doc_ids, scores = sum_impacts_multi(
            term_doc_impacts=term_doc_impacts,
            doc_ids=doc_ids,
            relative_doc_lens=self.relative_doc_lens,
            cutoff=cutoff,
            **self.hyperparams,
        )

        unique_doc_ids = [
            self.map_internal_ids_to_original_ids(_unique_doc_ids)
            for _unique_doc_ids in unique_doc_ids
        ]

        results = {
            q: dict(zip(unique_doc_ids[i], scores[i]))
            for i, q in enumerate(q_ids)
        }

        for q_id in no_results_q_ids:
            results[q_id] = {}

        # Order as queries
        return {q_id: results[q_id] for q_id in [q["id"] for q in queries]}

    def bsearch(
        self,
        queries: List[Dict[str, str]],
        cutoff: int = 100,
        chunksize: int = 1_000,
        show_progress: bool = True,
        qrels: Dict[str, Dict[str, float]] = None,
        path: str = None,
    ):
        chunks = [
            queries[i : i + chunksize]
            for i in range(0, len(queries), chunksize)
        ]

        results = {}

        pbar = tqdm(
            total=len(queries),
            disable=not show_progress,
            desc="Batch search",
            dynamic_ncols=True,
            mininterval=0.5,
        )

        if path is None:
            for chunk in chunks:
                new_results = self.msearch(queries=chunk, cutoff=cutoff)
                results = {**results, **new_results}
                pbar.update(min(chunksize, len(chunk)))
        else:
            path = create_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "wb") as f:
                for chunk in chunks:
                    new_results = self.msearch(queries=chunk, cutoff=cutoff)

                    for i, (k, v) in enumerate(new_results.items()):
                        x = {
                            "id": k,
                            "text": chunk[i]["text"],
                            "lsr_doc_ids": list(v.keys()),
                            "lsr_scores": [float(s) for s in list(v.values())],
                        }
                        if qrels is not None:
                            x["rel_doc_ids"] = list(qrels[k].keys())
                            x["rel_scores"] = list(qrels[k].values())
                        f.write(orjson.dumps(x) + "\n".encode())

                    pbar.update(min(chunksize, len(chunk)))

        return results
