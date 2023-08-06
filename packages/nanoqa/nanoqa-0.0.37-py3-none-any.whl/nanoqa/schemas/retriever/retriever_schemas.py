from dataclasses import dataclass
from typing import Any, Dict, Optional

import mmh3


@dataclass
class Document:
    id: str
    content: str
    meta: Dict[str, Any]
    score: float

    def __init__(
        self,
        content: str,
        id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        score: Optional[float] = None,
    ):
        if not content:
            raise ValueError("Document content cannot be empty")
        self.content = content
        self.meta = meta or {}
        self.score = score or 0.0
        if id:
            self.id = id
        else:
            # use the content to create hash_key used as id
            self.id = "{:02x}".format(mmh3.hash128(str(content), signed=False))

    @classmethod
    def from_dict(cls, d: dict):
        _doc = d.copy()
        init_args = ["content", "meta", "score"]
        if "meta" not in _doc:
            _doc["meta"] = {}
        if "content" not in _doc:
            _doc["content"] = ""
        if "score" not in _doc:
            _doc["score"] = 0.0
        return cls(**{k: _doc[k] for k in init_args})

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "meta": self.meta,
            "score": self.score,
        }

    def __repr__(self):
        return f'Document(id={self.id}, content={self.content[:100] + "..."}, meta={self.meta}, score={self.score})'

    def __str__(self):
        return self.__repr__()


@dataclass
class SplitUnit:
    text: str
    offsets: Dict[str, int]
    split_id: int
    from_page: int
    to_page: int
