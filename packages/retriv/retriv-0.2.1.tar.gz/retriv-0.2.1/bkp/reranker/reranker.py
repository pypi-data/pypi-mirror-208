from typing import Dict, List

from ..base_retriever import BaseRetriever
from .cross_encoder import CrossEncoder


class ReRanker(BaseRetriever):
    def __init__(
        self,
        index_name: str = "new-index",
        model_path: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        max_length: int = 512,
    ):
        self.index_name = index_name
        self.model_path = model_path

        self.max_length = max_length

        self.cross_encoder = CrossEncoder(
            model_path=model_path,
            max_length=max_length,
        )

        self.id_mapping = None
        self.reverse_id_mapping = None

    def rerank(
        self,
        query: str,
        results: Dict[str, float],
        return_docs: bool = True,
    ):
        # Get original doc texts
        doc_ids = self.map_internal_ids_to_original_ids(list(results))
        docs = [doc["text"] for doc in self.get_docs(doc_ids)]

        scores = self.cross_encoder([query] * len(docs), docs)

        if not return_docs:
            return dict(zip(doc_ids, scores))

        return self.prepare_results(doc_ids, scores)

    def mrerank(
        self, queries: List[Dict[str, str]], run: Dict[str, Dict[str, float]]
    ):
        return {
            query["id"]: self.rerank(query["text"], results, False)
            for query, results in zip(queries, run.values())
        }
