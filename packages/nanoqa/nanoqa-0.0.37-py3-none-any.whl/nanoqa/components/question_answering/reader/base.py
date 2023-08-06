from dataclasses import replace
from typing import List, Optional

import torch
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, BatchEncoding

from ....schemas import FinalPrediction, ReaderArguments
from ..handlers.inference import model_inference, multi_documents_aggregation
from ..tokenization import tokenization_question_contexts


class BaseReader:
    def __init__(
        self,
        model_name_or_path: str,
        max_seq_len: int = 384,
        doc_stride: int = 128,
        max_ans_len: int = 30,
        use_gpu: bool = True,
        nbest_from_chunk: int = 3,
        nbest_from_document: int = 1,
        return_no_answer: bool = False,
        no_ans_boost: float = 0.0,
        skip_detailed_features: bool = True,
        display_progress_bar: bool = True,
    ):
        self.use_gpu = use_gpu
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() and use_gpu else "cpu"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name_or_path)
        self.reader_args = ReaderArguments(
            max_seq_len=max_seq_len,
            doc_stride=doc_stride,
            max_ans_len=max_ans_len,
            nbest_from_chunk=nbest_from_chunk,
            nbest_from_document=nbest_from_document,
            return_no_answer=return_no_answer,
            no_ans_boost=no_ans_boost,
        )
        self.skip_detailed_features = skip_detailed_features
        self.display_progress_bar = display_progress_bar
        self.model.to(self.device)

    def read(
        self, question: str, contexts: List[str], top_k: int = 5
    ) -> List[FinalPrediction]:
        # tokenization
        inputs: BatchEncoding = tokenization_question_contexts(
            self.tokenizer,
            question,
            contexts,
            self.reader_args.max_seq_len,
            self.reader_args.doc_stride,
            self.device,
        )
        # inference in a for-loop (otherwise we might get OOM errors)
        all_starts, all_ends, offset_mappings, sample_mappings = model_inference(
            self.model, inputs, self.display_progress_bar
        )
        # aggregation across multiple documents
        predictions: List[FinalPrediction] = multi_documents_aggregation(
            inputs,
            self.tokenizer,
            all_starts,
            all_ends,
            offset_mappings,
            sample_mappings,
            contexts,
            nbest_from_chunk=self.reader_args.nbest_from_chunk,
            nbest_from_document=self.reader_args.nbest_from_document,
            max_ans_len=self.reader_args.max_ans_len,
            skip_detailed_features=self.skip_detailed_features,
            return_no_answer=self.reader_args.return_no_answer,
        )
        return predictions[:top_k]

    def __call__(
        self, question: str, contexts: List[str], top_k: int = 5
    ) -> List[FinalPrediction]:
        return self.read(question, contexts, top_k)

    def update_reader_arguments(
        self,
        max_seq_len: Optional[int] = None,
        doc_stride: Optional[int] = None,
        max_ans_len: Optional[int] = None,
        return_no_answer: Optional[bool] = None,
        no_ans_boost: Optional[float] = None,
    ):
        if max_seq_len is not None:
            self.reader_args = replace(self.reader_args, max_seq_len=max_seq_len)
        if doc_stride is not None:
            self.reader_args = replace(self.reader_args, doc_stride=doc_stride)
        if max_ans_len is not None:
            self.reader_args = replace(self.reader_args, max_ans_len=max_ans_len)
        if return_no_answer is not None:
            self.reader_args = replace(
                self.reader_args, return_no_answer=return_no_answer
            )
        if no_ans_boost is not None:
            self.reader_args = replace(self.reader_args, no_ans_boost=no_ans_boost)
