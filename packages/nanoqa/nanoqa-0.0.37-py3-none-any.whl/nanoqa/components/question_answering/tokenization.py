import logging
from typing import List

import torch
from transformers import BatchEncoding, PreTrainedTokenizer

logger = logging.getLogger(__name__)


def tokenization_question_contexts(
    tokenizer: PreTrainedTokenizer,
    question: str,
    contexts: List[str],
    max_seq_len: int,
    doc_stride: int,
    device: torch.device,
) -> BatchEncoding:
    pad_on_right = tokenizer.padding_side == "right"
    encoded_inputs = tokenizer(
        [question] * len(contexts) if pad_on_right else contexts,
        contexts if pad_on_right else [question] * len(contexts),
        truncation="only_second" if pad_on_right else "only_first",
        max_length=max_seq_len,
        stride=doc_stride,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
        return_tensors="pt",
    ).to(device)
    logger.info(
        f"Tokenization => Got {len(encoded_inputs['offset_mapping'])} chunks from {len(contexts)} contexts"
    )
    return encoded_inputs
