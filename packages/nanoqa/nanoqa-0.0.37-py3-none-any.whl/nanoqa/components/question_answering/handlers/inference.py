import collections
import logging
from typing import List, Optional, Tuple

import numpy as np
import torch
from torch import Tensor as T
from tqdm import trange
from transformers import BatchEncoding, PreTrainedTokenizer
from transformers.modeling_outputs import QuestionAnsweringModelOutput

from ....schemas import ChunkPrediction, DocumentPrediction, FinalPrediction

logger = logging.getLogger(__name__)


def model_inference(model, inputs: BatchEncoding, display_progress_bar: bool = True):
    offset_mappings = inputs.pop("offset_mapping")
    sample_mappings = inputs.pop("overflow_to_sample_mapping")
    all_starts, all_ends = [], []
    with torch.no_grad():
        for chunk_idx in trange(
            len(offset_mappings), desc="Inference", disable=not display_progress_bar
        ):
            chunk_model_inputs = {
                "input_ids": inputs["input_ids"][chunk_idx].unsqueeze(0),
                "attention_mask": inputs["attention_mask"][chunk_idx].unsqueeze(0),
            }
            if "token_type_ids" in inputs:
                chunk_model_inputs["token_type_ids"] = inputs["token_type_ids"][
                    chunk_idx
                ].unsqueeze(0)
            outputs: QuestionAnsweringModelOutput = model(**chunk_model_inputs)
            all_starts.append(outputs.start_logits)
            all_ends.append(outputs.end_logits)

    all_starts = torch.cat(all_starts, dim=0)
    all_ends = torch.cat(all_ends, dim=0)

    return all_starts, all_ends, offset_mappings, sample_mappings


def to_list(t: T):
    return t.detach().cpu().tolist()


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


def single_chunk_aggregation(
    starts,
    ends,
    offsets,
    current_noAns: Optional[dict],
    sample_index: int,
    chunk_index: int,
    document_index: int,
    nbest_from_chunk: int,
    max_ans_len: int,
    nbest_combination: int = 50,
) -> Tuple[List[ChunkPrediction], dict]:
    chunk_predictions = []
    chunk_noAns_score = starts[0] + ends[0]
    start_probs = softmax(starts)
    end_probs = softmax(ends)

    if current_noAns is None or current_noAns.get("sum_of_logits") > chunk_noAns_score:
        current_noAns = {
            "sum_of_logits": chunk_noAns_score,
            "sample_index": sample_index,
            "chunk_index": chunk_index,
            "document_index": document_index,
            "start_prob": start_probs[0],
            "end_prob": end_probs[0],
        }

    start_indexes = np.argsort(starts)[-1 : -nbest_combination - 1 : -1].tolist()
    end_indexes = np.argsort(ends)[-1 : -nbest_combination - 1 : -1].tolist()
    for start_index in start_indexes:
        for end_index in end_indexes:
            # exclude bad combinations
            if (
                start_index >= len(offsets)
                or end_index >= len(offsets)
                or offsets[start_index] is None
                or offsets[end_index] is None
            ):
                continue
            if end_index < start_index:
                continue
            if end_index - start_index + 1 > max_ans_len:
                continue

            chunk_predictions.append(
                ChunkPrediction(
                    offsets=(offsets[start_index][0], offsets[end_index][1]),
                    start_tok_pos=start_index,
                    end_tok_pos=end_index,
                    sample_index=sample_index,
                    chunk_index=chunk_index,
                    document_index=document_index,
                    start_prob=start_probs[start_index],
                    end_prob=end_probs[end_index],
                )
            )
    chunk_predictions = sorted(chunk_predictions, reverse=True)[:nbest_from_chunk]
    return chunk_predictions, current_noAns


def multi_documents_aggregation(
    inputs: BatchEncoding,
    tokenizer: PreTrainedTokenizer,
    all_starts: T,
    all_ends: T,
    offset_mappings: T,
    sample_mappings: T,
    documents: List[str],
    nbest_from_chunk: int = 3,
    nbest_from_document: int = 1,
    max_ans_len: int = 30,
    return_no_answer: bool = False,
    skip_detailed_features: bool = False,
):
    pad_on_right = tokenizer.padding_side == "right"
    all_input_ids = to_list(inputs.input_ids)
    # convert all tensors to lists
    all_starts = to_list(all_starts)
    all_ends = to_list(all_ends)
    offset_mappings = to_list(offset_mappings)
    sample_mappings = to_list(sample_mappings)

    # count the number of chunks that long text split into
    # examples: [0, 0, 1] => first long context split into 2 chunks, second context fits max_seq_len
    # convert into = {0: 2, 1: 1}
    sample_mappings = collections.Counter(sample_mappings)
    sample_mappings = sorted(sample_mappings.items())
    context_index = 1 if pad_on_right else 0

    all_document_predictions: List[DocumentPrediction] = []
    noAns_prediction: Optional[dict] = None

    sample_idx = 0
    for doc_idx in range(len(sample_mappings)):
        document = documents[doc_idx]
        n_chunks_in_context = sample_mappings[doc_idx][1]
        document_predictions = []
        for chunk_idx in range(n_chunks_in_context):
            sequence_ids = inputs.sequence_ids(sample_idx)
            offsets = [
                (o if sequence_ids[k] == context_index else None)
                for k, o in enumerate(offset_mappings[sample_idx])
            ]
            chunk_predictions, noAns_prediction = single_chunk_aggregation(
                all_starts[sample_idx],
                all_ends[sample_idx],
                offsets,
                current_noAns=noAns_prediction,
                sample_index=sample_idx,
                chunk_index=chunk_idx,
                document_index=doc_idx,
                nbest_from_chunk=nbest_from_chunk,
                max_ans_len=max_ans_len,
                nbest_combination=50,
            )
            for chunk_prediction in chunk_predictions:
                document_predictions.append(
                    DocumentPrediction(
                        text=document[
                            chunk_prediction.offsets[0] : chunk_prediction.offsets[1]
                        ],
                        sum_of_logits=all_starts[sample_idx][
                            chunk_prediction.start_tok_pos
                        ]
                        + all_ends[sample_idx][chunk_prediction.end_tok_pos],
                        chunk_prediction=chunk_prediction,
                    )
                )

            sample_idx += 1
        document_predictions = sorted(document_predictions, reverse=True)[
            :nbest_from_document
        ]
        all_document_predictions.extend(document_predictions)

    all_document_predictions = sorted(all_document_predictions, reverse=True)
    if return_no_answer:
        if all_document_predictions[0].sum_of_logits < noAns_prediction.get(
            "sum_of_logits"
        ):
            logger.info("NoAns Mechanism activated. Return empty list.")
            return []

    final_predictions: List[FinalPrediction] = []
    # aggregate final predictions
    for document_prediction in all_document_predictions:
        final_predictions.append(
            FinalPrediction(
                text=document_prediction.text,
                sum_of_logits=document_prediction.sum_of_logits,
                score=(document_prediction.start_prob + document_prediction.end_prob)
                / 2,
                context=documents[document_prediction.document_index],
                chunk_index=document_prediction.chunk_index,
                document_index=document_prediction.document_index,
                offsets_in_context=[
                    {
                        "start": document_prediction.offsets[0],
                        "end": document_prediction.offsets[1],
                    }
                ],
                start_probability=document_prediction.start_prob,
                end_probability=document_prediction.end_prob,
                start_logits=[]
                if skip_detailed_features
                else all_starts[document_prediction.sample_index],
                end_logits=[]
                if skip_detailed_features
                else all_ends[document_prediction.sample_index],
                tokens=[]
                if skip_detailed_features
                else [
                    token.replace("Ġ", "")
                    for token in tokenizer.convert_ids_to_tokens(
                        all_input_ids[document_prediction.sample_index]
                    )
                ],
            )
        )
    return final_predictions
