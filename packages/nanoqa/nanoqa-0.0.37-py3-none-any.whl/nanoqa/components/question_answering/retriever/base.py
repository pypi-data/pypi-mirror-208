import json
from typing import Dict, List, Optional

from ....schemas import Document
from ...document_store.lexical import ElasticsearchDocumentStore


def compose_es_query(
    query, weight_text=5, weight_title=2, factor=10000, modifier="ln2p"
):
    query_dict = {
        "query": {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": query,
                        "type": "most_fields",
                        "fields": [f"title^{weight_title}", f"content^{weight_text}"],
                    }
                },
                "field_value_factor": {
                    "field": "popularity_score",
                    "factor": factor,
                    "modifier": modifier,
                    "missing": 0,
                },
            }
        },
        "highlight": {"fields": {"content": {"fragment_size": 100000000}}},
    }

    return json.dumps(query_dict)


class Retriever:
    def __init__(self, document_store: ElasticsearchDocumentStore, top_k: int = 10):
        self.document_store = document_store
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        filters: dict = None,
        top_k: Optional[int] = None,
        index: Optional[str] = None,
        fields: Optional[Dict[str, float]] = None,
    ) -> List[Document]:
        if top_k is None:
            top_k = self.top_k
        if index is None:
            index = self.document_store.index
        if fields is None:
            fields = {"content": 1.0, "title": 0.0}

        return self.document_store.query(
            query,
            filters,
            top_k,
            custom_query=compose_es_query(
                query,
                weight_text=fields.get("content", 1.0),
                weight_title=fields.get("title", 0),
            ),
            index=index,
        )
