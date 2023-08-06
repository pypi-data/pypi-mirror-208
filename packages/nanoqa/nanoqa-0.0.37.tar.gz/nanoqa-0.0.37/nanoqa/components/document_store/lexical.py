import json
import time
from string import Template
from typing import Any, Dict, Generator, List, Optional, Union

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from elasticsearch.helpers import bulk, scan

from ...schemas import Document

TITLE_FIELD_NAME = "title"
CONTENT_FIELD_NAME = "content"
NAME_FIELD_NAME = "name"


def compose_es_mapping(k1=0.9, b=0.4, analyzer="english"):
    # elasticsearch setting
    mapping = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                # configure our default similarity algorithm explicitly to use bm25
                "similarity": {"default": {"type": "BM25", "k1": str(k1), "b": str(b)}},
            },
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": analyzer,
                    }
                }
            },
        },
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "name": {"type": "keyword"},
            },
            "dynamic_templates": [
                {
                    "strings": {
                        "path_match": "*",
                        "match_mapping_type": "string",
                        "mapping": {"type": "keyword"},
                    }
                }
            ],
        },
    }
    return mapping


class DuplicateDocumentError(ValueError):
    """Exception for Duplicate document"""

    pass


class ElasticsearchDocumentStore:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 9200,
        index: str = "open",
        mapping: Optional[dict] = None,
        username: str = None,
        password: str = None,
        ca_certs: Optional[str] = None,
        http_auth: Optional[str] = None,
        verify_certs: bool = None,
        create_index: bool = True,
        analyzer: str = "english",
    ):
        self.host: str = host
        self.port: int = port
        self.index: str = index
        self.username: str = username
        self.password: str = password
        self.ca_certs: Optional[str] = ca_certs
        self.http_auth: Optional[str] = http_auth
        self.verify_certs: bool = verify_certs
        self.client: Elasticsearch = self._init_elastic_client(
            host, port, username, password, ca_certs, http_auth, verify_certs
        )
        self.mapping = mapping
        self.analyzer = analyzer

        self.duplicate_documents_options: tuple = ("skip", "overwrite", "fail")
        self.refresh_type = "wait_for"

        if create_index:
            self._create_document_index(index)

    @staticmethod
    def _init_elastic_client(
        host: str,
        port: int,
        username: str,
        password: str,
        ca_certs: Optional[str] = None,
        http_auth: Optional[str] = None,
        verify_certs: bool = None,
        scheme="http",
        timeout=30,
    ):
        hosts = [{"host": host, "port": port}]
        if scheme == "https":
            hosts = f"https://{host}:{port}"

        if username:
            client = Elasticsearch(
                hosts=hosts,
                username=username,
                password=password,
                ca_certs=ca_certs,
                http_auth=http_auth,
                verify_certs=verify_certs,
                timeout=timeout,
                scheme=scheme,
            )
        else:
            client = Elasticsearch(
                hosts=hosts,
                scheme=scheme,
                timeout=timeout,
            )

        return client

    def _create_document_index(self, index_name):
        if self.mapping:
            mapping = self.mapping
        else:
            mapping = compose_es_mapping(analyzer=self.analyzer)

        try:
            self.client.indices.create(
                index=index_name,
                settings=mapping["settings"],
                mappings=mapping["mappings"],
            )
        except RequestError as e:
            # With multiple workers we need to avoid race conditions, where:
            # - there's no index in the beginning
            # - both want to create one
            # - one fails as the other one already created it
            if not self.client.indices.exists(index=index_name):
                raise e

    def get_document_by_id(
        self, id: str, index: Optional[str] = None
    ) -> Optional[Document]:
        index = index or self.index
        documents = self.get_documents_by_id([id], index=index)
        if documents:
            return documents[0]
        else:
            return None

    def get_documents_by_id(
        self, ids: List[str], index: Optional[str] = None
    ) -> List[Document]:
        index = index or self.index
        query = {"query": {"ids": {"values": ids}}}
        result = self.client.search(index=index, body=query)["hits"]["hits"]
        documents = [self._convert_es_hit_to_document(hit) for hit in result]
        return documents

    @staticmethod
    def _convert_es_hit_to_document(hit: dict) -> Document:
        meta_data = {
            k: v for k, v in hit["_source"].items() if k not in [CONTENT_FIELD_NAME]
        }
        if "highlight" in hit:
            meta_data["highlight"] = " ".join(hit["highlight"]["content"])
        score = hit["_score"] if hit["_score"] else None
        doc_dict = {
            "id": hit["_id"],
            "content": hit["_source"].get(CONTENT_FIELD_NAME),
            "score": score,
            "meta": meta_data,
        }
        document = Document.from_dict(doc_dict)
        return document

    def _handle_duplicate_documents(
        self,
        documents: List[Document],
        index: Optional[str] = None,
        duplicate_documents: Optional[str] = None,
    ):
        index = index or self.index
        if duplicate_documents in ("skip", "fail"):
            # drop duplicates by id
            _hash_ids: list = []
            _documents: list = []
            for document in documents:
                if document.id in _hash_ids:
                    continue
                _documents.append(document)
                _hash_ids.append(document.id)
            documents = _documents
            documents_in_index = self.get_documents_by_id(
                [doc.id for doc in documents], index=index
            )
            ids_exist_in_index = [doc.id for doc in documents_in_index]

            if len(ids_exist_in_index) > 0 and duplicate_documents == "fail":
                raise DuplicateDocumentError(
                    f"Duplicate documents found in index {index}: {ids_exist_in_index}"
                )
            documents = list(
                filter(lambda doc: doc.id not in ids_exist_in_index, documents)
            )

        return documents

    def write_documents(
        self,
        documents: Union[List[dict], List[Document]],
        index: Optional[str] = None,
        batch_size: int = 10_000,
        duplicate_documents: Optional[str] = None,
    ):
        if index and not self.client.indices.exists(index=index):
            self._create_document_index(index)

        if index is None:
            index = self.index

        assert (
            duplicate_documents in self.duplicate_documents_options
        ), f"duplicate_documents parameter must be {', '.join(self.duplicate_documents_options)}"

        document_objects = [
            Document.from_dict(d) if isinstance(d, dict) else d for d in documents
        ]
        document_objects = self._handle_duplicate_documents(
            document_objects, index, duplicate_documents
        )

        documents_to_index = []
        for doc in document_objects:
            _doc = {
                "_op_type": "index" if duplicate_documents == "overwrite" else "create",
                "_index": index,
                **doc.to_dict(),
            }

            # rename the id to _id
            _doc["_id"] = _doc.pop("id")

            # avoid score field and empty fields
            _ = _doc.pop("score", None)
            _doc = {k: v for k, v in _doc.items() if v is not None}

            # un-nest meta data field
            if "meta" in _doc:
                for k, v in _doc["meta"].items():
                    _doc[k] = v
                _doc.pop("meta")
            documents_to_index.append(_doc)

            if len(documents_to_index) % batch_size == 0:
                bulk(
                    self.client,
                    documents_to_index,
                    request_timeout=300,
                    refresh=self.refresh_type,
                )
                documents_to_index = []

        if documents_to_index:
            bulk(
                self.client,
                documents_to_index,
                request_timeout=300,
                refresh=self.refresh_type,
            )

    def update_document_meta(self, id: str, meta: Dict[str, str]):
        body = {"doc": meta}
        self.client.update(
            index=self.index, id=id, body=body, refresh=self.refresh_type
        )

    def get_document_count(
        self,
        filters: Optional[Dict[str, List[str]]] = None,
        index: Optional[str] = None,
    ) -> int:
        index = index or self.index

        body: dict = {"query": {"bool": {}}}

        if filters:
            filter_clause = []
            for key, values in filters.items():
                if type(values) != list:
                    raise ValueError(
                        f'Wrong filter format for key "{key}": Please provide a list of allowed values for each key. '
                        'Example: {"name": ["some", "more"], "category": ["only_one"]} '
                    )
                filter_clause.append({"terms": {key: values}})
            body["query"]["bool"]["filter"] = filter_clause

        result = self.client.count(index=index, body=body)
        count = result["count"]

        return count

    def get_all_documents(
        self,
        index: Optional[str] = None,
        filters: Optional[Dict[str, List[str]]] = None,
        batch_size: int = 10_000,
    ) -> List[Document]:
        result = self.get_all_documents_generator(
            index=index, filters=filters, batch_size=batch_size
        )
        documents = list(result)
        return documents

    def get_all_documents_generator(
        self,
        index: Optional[str] = None,
        filters: Optional[Dict[str, List[str]]] = None,
        batch_size: int = 10_000,
    ) -> Generator[Document, None, None]:
        if index is None:
            index = self.index

        result = self._get_all_documents_in_index(
            index=index, filters=filters, batch_size=batch_size
        )
        for hit in result:
            document = self._convert_es_hit_to_document(hit)
            yield document

    def _get_all_documents_in_index(
        self,
        index: str,
        filters: Optional[Dict[str, List[str]]] = None,
        batch_size: int = 10_000,
    ) -> Generator[dict, None, None]:
        body: dict = {"query": {"bool": {}}}

        if filters:
            filter_clause = []
            for key, values in filters.items():
                filter_clause.append({"terms": {key: values}})
            body["query"]["bool"]["filter"] = filter_clause

        result = scan(self.client, query=body, index=index, size=batch_size)
        yield from result

    def delete_documents(
        self,
        index: Optional[str] = None,
        ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, List[str]]] = None,
    ):
        index = index or self.index
        query: Dict[str, Any] = {"query": {}}
        if filters:
            filter_clause = []
            for key, values in filters.items():
                filter_clause.append({"terms": {key: values}})
                query["query"]["bool"] = {"filter": filter_clause}

            if ids:
                query["query"]["bool"]["must"] = {"ids": {"values": ids}}

        elif ids:
            query["query"]["ids"] = {"values": ids}
        else:
            query["query"] = {"match_all": {}}
        self.client.delete_by_query(index=index, body=query, ignore=[404])
        # We want to be sure that all docs are deleted before continuing (delete_by_query doesn't support wait_for)
        if self.refresh_type == "wait_for":
            time.sleep(2)

    def query(
        self,
        query: str,
        filters: Optional[Dict[str, List[str]]] = None,
        top_k: int = 10,
        custom_query: Optional[str] = None,
        index: Optional[str] = None,
    ) -> List[Document]:
        if index is None:
            index = self.index

        if custom_query:
            template = Template(custom_query)
            substitutions = {"query": f'"{query}"'}
            if filters:
                for key, values in filters.items():
                    values_str = json.dumps(values)
                    substitutions[key] = values_str

            custom_query_json = template.substitute(**substitutions)
            body = json.loads(custom_query_json)
            # add top_k
            body["size"] = str(top_k)
        else:
            if not isinstance(query, str):
                raise ValueError(
                    "The query provided seems to be not a string, but an object of type {type(query)}. This can cause Elasticsearch to fail."
                )
            body = {
                "size": str(top_k),
                "query": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "type": "most_fields",
                                    "fields": ["content"],
                                }
                            }
                        ]
                    }
                },
            }

            if filters:
                filter_clause = []
                for key, values in filters.items():
                    if type(values) != list:
                        raise ValueError(
                            f'Wrong filter format: "{key}": {values}. Provide a list of values for each key. '
                            'Example: {"name": ["some", "more"], "category": ["only_one"]} '
                        )
                    filter_clause.append({"terms": {key: values}})
                body["query"]["bool"]["filter"] = filter_clause
        result = self.client.search(
            index=index,
            query=body["query"],
            size=top_k,
            highlight=None if "highlight" not in body else body["highlight"],
        )["hits"]["hits"]
        documents = [self._convert_es_hit_to_document(hit) for hit in result]

        return documents

    @staticmethod
    def delete_es_index(
        index: str,
        host: str = "localhost",
        port: int = 9200,
        scheme: str = "http",
        timeout: int = 30,
    ):
        hosts = [{"host": host, "port": port}]
        client = Elasticsearch(hosts=hosts, timeout=timeout, scheme=scheme)
        client.indices.delete(index=index, ignore=[400, 404])
        client.close()

    def ping(self):
        return self.client.ping()
