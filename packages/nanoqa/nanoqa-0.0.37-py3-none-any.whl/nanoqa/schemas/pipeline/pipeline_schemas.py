from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PipelineAnswer:
    ranking: int
    document_id: str
    answer: str
    sum_of_logits: float
    score: float
    context: str
    document_index: int
    chunk_index: int
    offsets_in_context: List[Dict[str, int]]
    offsets_in_document: List[Dict[str, int]]
    start_logits: List[float]
    end_logits: List[float]
    start_probability: float
    end_probability: float
    tokens: List[str]
    meta: Dict[str, str]


@dataclass
class PipelineResponse:
    query: str
    answers: List[PipelineAnswer]
    use_reader: bool
    use_fallback: bool
