from time import time
from typing import Tuple

import numba as nb
import numpy as np
from numba import njit, prange
from numba.typed import List as TypedList

from ..utils.numba_utils import (  # intersect_sorted,
    arg_unsorted_top_k,
    get_indices,
    join_sorted_multi_recursive,
)

# @njit(cache=True)
# def sum_scores(
#     weights: nb.typed.List[np.ndarray],
#     # max_weights: nb.typed.List[float],
#     doc_ids: nb.typed.List[np.ndarray],
#     doc_count: int,
#     cutoff: int,
# ) -> Tuple[np.ndarray]:
#     unique_doc_ids = join_sorted_multi_recursive(doc_ids)
#     scores = np.empty(doc_count, dtype=np.float32)
#     scores[unique_doc_ids] = 0.0  # Initialize scores

#     # lens = np.array([x.size for x in doc_ids])
#     # sorted_i = np.argsort(lens)

#     # for i in sorted_i:
#     #     if i > 1 and len(unique_doc_ids) > cutoff:
#     #         st = time()
#     #         _doc_ids, indices = intersect_sorted(unique_doc_ids, doc_ids[i])
#     #         scores[_doc_ids] += weights[i][indices]
#     #         print(time() - st)
#     #     else:
#     #         _doc_ids = doc_ids[i]
#     #         scores[_doc_ids] += weights[i]

#     # if (
#     #     len(weights) > 1
#     #     and i < len(weights) - 1
#     #     and len(unique_doc_ids) > cutoff
#     # ):
#     # unique_doc_ids_scores = scores[unique_doc_ids]
#     # cutoff_score = -np.partition(-unique_doc_ids_scores, cutoff)[cutoff - 1]
#     # max_sum = sum(max_weights[sorted_i[i + 1 :]])
#     # unique_doc_ids = unique_doc_ids[
#     #     unique_doc_ids_scores >= cutoff_score - max_sum
#     # ]

#     for i in range(len(doc_ids)):
#         _doc_ids = doc_ids[i]
#         scores[_doc_ids] += weights[i]

#     scores = scores[unique_doc_ids]

#     if cutoff < len(scores):
#         top_scores = -np.partition(-scores, cutoff)[:cutoff]
#         indices = get_indices(scores, top_scores)
#         unique_doc_ids = unique_doc_ids[indices]
#         scores = scores[indices]

#     indices = np.argsort(scores)[::-1]

#     return unique_doc_ids[indices], scores[indices]


@njit(cache=True)
def sum_scores(
    weights: nb.typed.List[np.ndarray],
    doc_ids: nb.typed.List[np.ndarray],
    doc_count: int,
    cutoff: int,
) -> Tuple[np.ndarray]:
    unique_doc_ids = join_sorted_multi_recursive(doc_ids)
    scores = np.empty(doc_count, dtype=np.float32)
    scores[unique_doc_ids] = 0.0  # Initialize scores

    for i in range(len(weights)):
        indices = doc_ids[i]
        scores[indices] += weights[i]

    scores = scores[unique_doc_ids]

    if cutoff < len(scores):
        indices = arg_unsorted_top_k(scores, cutoff)
        unique_doc_ids = unique_doc_ids[indices]
        scores = scores[indices]

    indices = np.argsort(scores)[::-1]

    return unique_doc_ids[indices], scores[indices]


@njit(parallel=True, cache=True)
def sum_scores_multi(
    weights: nb.typed.List[nb.typed.List[np.ndarray]],
    doc_ids: nb.typed.List[nb.typed.List[np.ndarray]],
    doc_count: int,
    cutoff: int,
) -> Tuple[nb.typed.List[np.ndarray]]:
    unique_doc_ids = TypedList([np.empty(1, dtype=np.int32) for _ in doc_ids])
    scores = TypedList([np.empty(1, dtype=np.float32) for _ in doc_ids])

    for i in prange(len(weights)):
        _weights = weights[i]
        _doc_ids = doc_ids[i]

        _unique_doc_ids = join_sorted_multi_recursive(_doc_ids)
        _scores = np.empty(doc_count, dtype=np.float32)
        _scores[_unique_doc_ids] = 0.0  # Initialize scores

        for j in range(len(_weights)):
            _indices = _doc_ids[j]
            _scores[_indices] += _weights[j]

        # max_weights = np.array([max(__weights) for __weights in _weights])

        # for j in range(len(_weights)):
        #     if j > 1:
        #         unique_doc_ids_scores = _scores[_unique_doc_ids]
        #         cutoff_score = -np.partition(-unique_doc_ids_scores, cutoff)[
        #             cutoff - 1
        #         ]
        #         max_sum = sum(max_weights[j:])
        #         _unique_doc_ids = _unique_doc_ids[
        #             unique_doc_ids_scores + max_sum >= cutoff_score
        #         ]
        #         __doc_ids, _indices = intersect_sorted(
        #             _unique_doc_ids, _doc_ids[j]
        #         )
        #         _scores[__doc_ids] += _weights[j][_indices]
        #     else:
        #         __doc_ids = _doc_ids[j]
        #         _scores[__doc_ids] += _weights[j]

        _scores = _scores[_unique_doc_ids]

        if cutoff < len(_scores):
            indices = arg_unsorted_top_k(_scores, cutoff)
            _unique_doc_ids = _unique_doc_ids[indices]
            _scores = _scores[indices]

        _indices = np.argsort(_scores)[::-1]

        unique_doc_ids[i] = _unique_doc_ids[_indices]
        scores[i] = _scores[_indices]

    return unique_doc_ids, scores
