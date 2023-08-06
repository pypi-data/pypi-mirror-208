from math import isclose

import pytest

from retriv.reranker.cross_encoder import CrossEncoder


# FIXTURES =====================================================================
@pytest.fixture
def cross_encoder():
    return CrossEncoder(model="cross-encoder/ms-marco-MiniLM-L-6-v2")


@pytest.fixture
def queries():
    return [
        "How many people live in Berlin?",
        "How many people live in Berlin?",
    ]


@pytest.fixture
def docs():
    return [
        "Berlin has a population of 3,520,031 registered inhabitants in an area of 891.82 square kilometers.",
        "New York City is famous for the Metropolitan Museum of Art.",
    ]


# TESTS ========================================================================
def test_call(cross_encoder, queries, docs):
    scores = cross_encoder(
        queries=queries,
        docs=docs,
    )
    assert isclose(scores[0], 8.8459, abs_tol=0.0001)
    assert isclose(scores[1], -11.2456, abs_tol=0.0001)
