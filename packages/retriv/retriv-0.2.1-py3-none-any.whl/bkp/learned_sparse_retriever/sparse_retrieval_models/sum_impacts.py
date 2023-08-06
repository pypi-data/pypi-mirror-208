from typing import Tuple

import numba as nb
import numpy as np
from numba import njit, prange
from numba.typed import List as TypedList

from ...utils.numba_utils import join_sorted_multi_recursive, unsorted_top_k


@njit(cache=True)
def sum_impacts(
    term_doc_impacts: nb.typed.List[np.ndarray],
    doc_ids: nb.typed.List[np.ndarray],
    relative_doc_lens: nb.typed.List[np.ndarray],
    cutoff: int,
) -> Tuple[np.ndarray]:
    unique_doc_ids = join_sorted_multi_recursive(doc_ids)

    doc_count = len(relative_doc_lens)
    scores = np.empty(doc_count, dtype=np.float32)
    scores[unique_doc_ids] = 0.0  # Initialize scores

    for i in range(len(term_doc_impacts)):
        indices = doc_ids[i]
        impacts = term_doc_impacts[i]
        scores[indices] += impacts

    scores = scores[unique_doc_ids]

    if cutoff < len(scores):
        scores, indices = unsorted_top_k(scores, cutoff)
        unique_doc_ids = unique_doc_ids[indices]

    indices = np.argsort(-scores)

    return unique_doc_ids[indices], scores[indices]


@njit(cache=True, parallel=True)
def sum_impacts_multi(
    term_doc_impacts: nb.typed.List[nb.typed.List[np.ndarray]],
    doc_ids: nb.typed.List[nb.typed.List[np.ndarray]],
    relative_doc_lens: nb.typed.List[nb.typed.List[np.ndarray]],
    cutoff: int,
) -> Tuple[nb.typed.List[np.ndarray]]:
    unique_doc_ids = TypedList([np.empty(1, dtype=np.int32) for _ in doc_ids])
    scores = TypedList([np.empty(1, dtype=np.float32) for _ in doc_ids])

    for i in prange(len(term_doc_impacts)):
        _term_doc_impacts = term_doc_impacts[i]
        _doc_ids = doc_ids[i]

        _unique_doc_ids = join_sorted_multi_recursive(_doc_ids)

        doc_count = len(relative_doc_lens)
        _scores = np.empty(doc_count, dtype=np.float32)
        _scores[_unique_doc_ids] = 0.0  # Initialize _scores

        for j in range(len(_term_doc_impacts)):
            indices = _doc_ids[j]
            impacts = _term_doc_impacts[j]
            _scores[indices] += impacts

        _scores = _scores[_unique_doc_ids]

        if cutoff < len(_scores):
            _scores, indices = unsorted_top_k(_scores, cutoff)
            _unique_doc_ids = _unique_doc_ids[indices]

        indices = np.argsort(_scores)[::-1]

        unique_doc_ids[i] = _unique_doc_ids[indices]
        scores[i] = _scores[indices]

    return unique_doc_ids, scores
