from typing import List, Union

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class CrossEncoder:
    def __init__(
        self,
        model_path: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        max_length: int = 512,
        device: str = "cpu",
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = (
            AutoModelForSequenceClassification.from_pretrained(model_path)
            .to(device)
            .eval()
        )
        self.max_length = max_length
        self.device = device
        self.tokenizer_kwargs = {
            "padding": True,
            "truncation": True,
            "max_length": self.max_length,
            "return_tensors": "pt",
        }

    def change_device(self, device: str = "cpu"):
        self.device = device
        self.model.to(device)

    def tokenize(self, queries: List[str], docs: List[str]):
        tokens = self.tokenizer(queries, docs, **self.tokenizer_kwargs)
        return {k: v.to(self.device) for k, v in tokens.items()}

    def __call__(
        self,
        queries: Union[str, List[str]],
        docs: Union[str, List[str]],
    ):
        if type(queries) == str:
            return self.score(queries, docs)
        else:
            return self.bscore(queries, docs)

    def score(self, query: str, doc: str):
        return self.bscore([[query, doc]], batch_size=1, show_progress=False)[0]

    def bscore(self, queries: List[str], docs: List[str]) -> List[float]:
        tokens = self.tokenize(queries, docs)

        with torch.no_grad():
            scores = self.model(**tokens).logits

        return scores.cpu().numpy().reshape(-1).tolist()
