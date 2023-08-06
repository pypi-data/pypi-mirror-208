__all__ = [
    "ANN_Searcher",
    "DenseRetriever",
    "Encoder",
    "SearchEngine",
    "SparseRetriever",
    "HybridRetriever",
    "Merger",
]

import os
import sys
from pathlib import Path

from loguru import logger

from .dense_retriever.ann_searcher import ANN_Searcher
from .dense_retriever.dense_retriever import DenseRetriever
from .dense_retriever.encoder import Encoder
from .hybrid_retriever import HybridRetriever
from .merger.merger import Merger
from .sparse_retriever.sparse_retriever import SparseRetriever
from .sparse_retriever.sparse_retriever import SparseRetriever as SearchEngine

# Set environment variables ----------------------------------------------------
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["RETRIV_BASE_PATH"] = str(Path.home() / ".retriv")


def set_base_path(path: str):
    os.environ["RETRIV_BASE_PATH"] = path


# Set logger -------------------------------------------------------------------
class LogFilter:
    def __init__(self, level: str):
        self.level = level

    def __call__(self, record):
        levelno = logger.level(self.level).no
        return record["level"].no >= levelno


log_filter = LogFilter("INFO")
logger.remove()
logger.add(sys.stderr, filter=log_filter, level=0)


def set_log_level(level: str):
    log_filter.level = level
