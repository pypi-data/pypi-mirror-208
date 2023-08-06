from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ChunkPrediction:
    """
    Prediction from the chunk passed to the reader
    """

    offsets: Tuple[int, int]
    start_tok_pos: int
    end_tok_pos: int

    sample_index: int
    chunk_index: int
    document_index: int

    start_prob: float
    end_prob: float

    def __lt__(self, other):
        return (self.start_prob + self.end_prob) < (other.start_prob + other.end_prob)

    def __gt__(self, other):
        return (self.start_prob + self.end_prob) > (other.start_prob + other.end_prob)

    def __ge__(self, other):
        return (self.start_prob + self.end_prob) >= (other.start_prob + other.end_prob)

    def __le__(self, other):
        return (self.start_prob + self.end_prob) <= (other.start_prob + other.end_prob)


@dataclass
class DocumentPrediction(ChunkPrediction):
    """
    Prediction from a single document passed to the reader
    """

    text: str
    sum_of_logits: float

    def __init__(
        self, text: str, sum_of_logits: int, chunk_prediction: ChunkPrediction
    ):
        self.text = text
        self.sum_of_logits = sum_of_logits
        self.offsets = chunk_prediction.offsets
        self.start_tok_pos = chunk_prediction.start_tok_pos
        self.end_tok_pos = chunk_prediction.end_tok_pos
        self.sample_index = chunk_prediction.sample_index
        self.chunk_index = chunk_prediction.chunk_index
        self.document_index = chunk_prediction.document_index
        self.start_prob = chunk_prediction.start_prob
        self.end_prob = chunk_prediction.end_prob

    def __lt__(self, other):
        return self.sum_of_logits < other.sum_of_logits

    def __le__(self, other):
        return self.sum_of_logits <= other.sum_of_logits

    def __gt__(self, other):
        return self.sum_of_logits > other.sum_of_logits

    def __ge__(self, other):
        return self.sum_of_logits >= other.sum_of_logits


@dataclass
class FinalPrediction:
    """
    Prediction based a query and multiple documents (end-to-end)
    """

    text: str
    sum_of_logits: float
    score: float

    context: str
    chunk_index: int
    document_index: int
    offsets_in_context: List[Dict[str, int]]

    start_probability: float
    end_probability: float

    start_logits: List[float]
    end_logits: List[float]
    tokens: List[str]
