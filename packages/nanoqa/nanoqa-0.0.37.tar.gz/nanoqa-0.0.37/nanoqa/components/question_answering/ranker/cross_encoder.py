from typing import List

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from ....schemas import Document


class Ranker:
    def __init__(
        self,
        model_name_or_path: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
        max_seq_len: int = 384,
        use_gpu: bool = False,
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name_or_path
        )
        self.max_seq_len = max_seq_len
        self.device = (
            torch.device("cuda")
            if use_gpu and torch.cuda.is_available()
            else torch.device("cpu")
        )
        self.model.to(self.device)

    def rank(
        self, query: str, documents: List[Document], top_k: int = 5
    ) -> List[Document]:
        id_doc_mapping = {doc.id: doc for doc in documents}
        contexts = [f"{doc.meta['name']}\n{doc.content}" for doc in documents]
        encoded_model_inputs = self.tokenizer(
            [query for _ in range(len(contexts))],
            contexts,
            padding="max_length",
            max_length=self.max_seq_len,
            truncation=True,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            model_outputs = self.model(**encoded_model_inputs)
            logits = model_outputs.logits.cpu().flatten().tolist()
            pairs = [
                {"id": doc_id, "ctx": ctx, "score": score}
                for doc_id, ctx, score in zip(id_doc_mapping.keys(), contexts, logits)
            ]
        ranked_pairs = sorted(pairs, key=lambda x: x["score"], reverse=True)[:top_k]

        del encoded_model_inputs
        torch.cuda.empty_cache()
        return [id_doc_mapping[pair["id"]] for pair in ranked_pairs]
