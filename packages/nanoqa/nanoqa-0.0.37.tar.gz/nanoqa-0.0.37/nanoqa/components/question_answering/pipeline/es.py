import logging
import re
import time
import unicodedata
from typing import Dict, List, Optional

import torch.cuda

from ....schemas import (
    Document,
    FinalPrediction,
    PipelineAnswer,
    PipelineResponse,
    ReaderArguments,
)
from ...document_store import ElasticsearchDocumentStore as DocumentStore
from ...question_answering import Ranker, Reader, Retriever
from ...rich_utils import (
    display_answers,
    display_json,
    display_retrieved_documents,
    display_time_taken,
)

logger = logging.getLogger(__name__)


class ElasticSearchPipeline:
    def __init__(
        self,
        model_name_or_path: str,
        index_name: str,
        username: str,
        password: str,
        index_hash: str,
        reader_args: ReaderArguments,
        ca_certs: str = Optional[str],
        http_auth: str = Optional[str],
        verify_certs: bool = True,
        use_ranker: bool = True,
        top_k_ranker: int = 50,
        use_gpu: bool = True,
        es_host: str = "localhost",
        es_port: int = 9200,
        skip_detailed_features: bool = True,
        display_progress_bar: bool = False,
    ):
        self.model_name_or_path = model_name_or_path
        self.index_name = index_name
        self.index_hash = index_hash
        self.username = username
        self.password = password
        self.ca_certs = ca_certs
        self.http_auth = http_auth
        self.verify_certs = verify_certs
        self.max_seq_len = reader_args.max_seq_len
        self.max_ans_len = reader_args.max_ans_len
        self.doc_stride = reader_args.doc_stride
        self.nbest_from_chunk = reader_args.nbest_from_chunk
        self.nbest_from_document = reader_args.nbest_from_document
        self.return_no_ans = reader_args.return_no_answer
        self.no_ans_boost = reader_args.no_ans_boost
        self.use_ranker = use_ranker
        self.top_k_ranker = top_k_ranker
        self.device = torch.device(
            "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        )
        self.skip_detailed_features = skip_detailed_features
        self.display_progress_bar = display_progress_bar
        self.es_host = es_host
        self.es_port = es_port

        self.document_store = self._init_document_store()
        self.retriever = self._init_retriever()
        self.reader = self._init_reader()
        self.ranker = self._init_ranker()

        self.display_pipeline_params()
        self.pad_token = self.reader.tokenizer.pad_token

    def _init_document_store(self) -> DocumentStore:
        index = self.index_name or self.index_hash
        return DocumentStore(
            username=self.username,
            password=self.password,
            ca_certs=self.ca_certs,
            http_auth=self.http_auth,
            verify_certs=self.verify_certs,
            host=self.es_host,
            port=self.es_port,
            index=index,
        )

    def display_pipeline_params(self):
        # display attributes of Pipeline class, if they are among string, int, float, bool
        display_json(
            data={
                k: v
                for k, v in self.__dict__.items()
                if isinstance(v, (str, int, float, bool))
            }
        )

    def _init_retriever(self) -> Retriever:
        return Retriever(document_store=self.document_store, top_k=10)

    def _init_reader(self) -> Reader:
        return Reader(
            model_name_or_path=self.model_name_or_path,
            max_seq_len=self.max_seq_len,
            max_ans_len=self.max_ans_len,
            doc_stride=self.doc_stride,
            use_gpu=self.device.type == "cuda",
            nbest_from_chunk=self.nbest_from_chunk,
            nbest_from_document=self.nbest_from_document,
            return_no_answer=self.return_no_ans,
            no_ans_boost=self.no_ans_boost,
            skip_detailed_features=self.skip_detailed_features,
            display_progress_bar=self.display_progress_bar,
        )

    def _init_ranker(self) -> Ranker:
        # by default we load cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
        # a multi-lingual cross-encoder to rank documents
        return Ranker(max_seq_len=self.max_seq_len, use_gpu=self.device.type == "cuda")

    def switch_retriever(self, username: str, index_name: str, index_hash: str):
        self.username = username
        self.index_name = index_name
        self.index_hash = index_hash
        self.document_store = self._init_document_store()
        self.retriever = self._init_retriever()

    @staticmethod
    def convert_highlights_to_positions(html_string: str) -> List[Dict[str, int]]:
        positions = []
        pattern_em = re.compile("<em>")
        pattern_slash_em = re.compile("</em>")
        for index, (p, q) in enumerate(
            zip(
                pattern_em.finditer(html_string), pattern_slash_em.finditer(html_string)
            )
        ):
            positions.append(
                {
                    "start": p.start() - index * 9,
                    "end": q.start() - ((index + 1) * 4 + index * 5),
                }
            )
        return positions

    def _aggregate_retriever(
        self,
        query: str,
        documents: List[Document],
        use_reader: bool = False,
        use_fallback: bool = False,
    ):
        pipeline_answers: List[PipelineAnswer] = []
        for ranking, document in enumerate(documents):
            offsets_in_context = self.convert_highlights_to_positions(
                document.meta.get("highlight", "")
            )
            offsets_in_document = document.meta.get(
                "offsets_in_document", {"start": 0, "end": 0}
            )
            context_start_pos = offsets_in_document["start"]
            pipeline_answers.append(
                PipelineAnswer(
                    **{
                        "ranking": ranking,
                        "document_id": document.id,
                        "answer": "",
                        "sum_of_logits": 0,
                        "score": document.score,
                        "context": document.content,
                        "document_index": -1,
                        "chunk_index": -1,
                        "offsets_in_context": offsets_in_context,
                        "offsets_in_document": [
                            {
                                "start": context_start_pos + d["start"],
                                "end": context_start_pos + d["end"],
                            }
                            for d in offsets_in_context
                        ],
                        "start_logits": [],
                        "end_logits": [],
                        "start_probability": 0.0,
                        "end_probability": 0.0,
                        "tokens": [],
                        "meta": {
                            "name": document.meta["name"],
                            "title": document.meta["title"],
                            "_split_id": document.meta.get("_split_id", -1),
                            "from_page": document.meta.get("from_page", -1),
                            "to_page": document.meta.get("to_page", -1),
                        },
                    }
                )
            )

        return PipelineResponse(
            query=query,
            answers=pipeline_answers,
            use_reader=use_reader,
            use_fallback=use_fallback,
        )

    def _aggregate_retriever_reader(
        self, query: str, documents: List[Document], predictions: List[FinalPrediction]
    ) -> PipelineResponse:
        pipeline_answers: List[PipelineAnswer] = []
        for ranking, prediction in enumerate(predictions):
            document = documents[prediction.document_index]
            offsets_in_document = document.meta.get(
                "offsets_in_document", {"start": 0, "end": 0}
            )
            context_start_pos = offsets_in_document["start"]

            if self.pad_token in prediction.tokens:
                first_pad_token_pos = prediction.tokens.index(self.pad_token)
            else:
                first_pad_token_pos = len(prediction.tokens)

            pipeline_answers.append(
                PipelineAnswer(
                    **{
                        "ranking": ranking,
                        "document_id": document.id,
                        "document_index": prediction.document_index,
                        "chunk_index": prediction.chunk_index,
                        "answer": prediction.text,
                        "sum_of_logits": prediction.sum_of_logits,
                        "score": prediction.score,
                        "context": prediction.context,
                        "offsets_in_context": prediction.offsets_in_context,
                        "offsets_in_document": [
                            {
                                "start": context_start_pos
                                + prediction.offsets_in_context[0]["start"],
                                "end": context_start_pos
                                + prediction.offsets_in_context[0]["end"],
                            }
                        ],
                        "start_logits": prediction.start_logits[:first_pad_token_pos],
                        "end_logits": prediction.end_logits[:first_pad_token_pos],
                        "start_probability": prediction.start_probability,
                        "end_probability": prediction.end_probability,
                        "tokens": prediction.tokens[:first_pad_token_pos],
                        "meta": {
                            "name": document.meta["name"],
                            "title": document.meta["title"],
                            "_split_id": document.meta.get("_split_id", -1),
                            "from_page": document.meta.get("from_page", -1),
                            "to_page": document.meta.get("to_page", -1),
                        },
                    }
                )
            )
        return PipelineResponse(
            query=query, answers=pipeline_answers, use_reader=True, use_fallback=False
        )

    def run(
        self,
        query: str,
        top_k_retriever: int = 10,
        top_k_reader: int = 10,
        weight_text: float = 1.0,
        weight_title: float = 0.0,
        use_reader: bool = True,
        use_fallback: bool = True,
    ):
        if self.use_ranker:
            top_k_retriever = max(self.top_k_ranker, top_k_retriever)

        # clean non-breaking spaces
        query = unicodedata.normalize("NFKD", query)
        # Retrieve documents
        timer_retriever = time.perf_counter()
        documents = self.retriever.retrieve(
            query=query,
            top_k=top_k_retriever,
            fields={"content": weight_text, "title": weight_title},
        )
        time_used_retrieval = round(time.perf_counter() - timer_retriever, 3)
        if len(documents) == 0:
            logger.error("No documents retrieved by this query.")
            return self._aggregate_retriever(
                query=query,
                documents=[],
                use_reader=use_reader,
                use_fallback=use_fallback,
            )

        if not use_reader:
            return self._aggregate_retriever(
                query, documents, use_reader=False, use_fallback=False
            )

        timer_ranker = time.perf_counter()
        if self.use_ranker:
            documents = self.ranker.rank(query, documents, top_k=top_k_reader)
        time_used_reranking = (
            round(time.perf_counter() - timer_ranker, 3) if self.use_ranker else 0
        )

        display_retrieved_documents(query, documents)

        timer_reader = time.perf_counter()
        # inference
        predictions: List[FinalPrediction] = self.reader.read(
            question=query,
            contexts=[doc.content for doc in documents],
            top_k=top_k_reader,
        )
        time_used_inference = round(time.perf_counter() - timer_reader, 3)

        if use_fallback and (not predictions or predictions[0].score < 0.5):
            return self._aggregate_retriever(
                query, documents, use_reader=False, use_fallback=True
            )

        response = self._aggregate_retriever_reader(query, documents, predictions)
        display_answers(response.answers)

        display_time_taken(
            {
                "time_used_retriever": time_used_retrieval,
                "time_used_reader": time_used_inference,
                "time_used_ranker": time_used_reranking,
            }
        )
        return response

    def run_on_documents(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 1,
        time_used_ir: float = 0.0,
    ):
        display_retrieved_documents(query, documents)
        # clean non-breaking spaces
        query = unicodedata.normalize("NFKD", query)
        # inference
        timer_reader = time.perf_counter()
        predictions: List[FinalPrediction] = self.reader.read(
            question=query, contexts=[doc.content for doc in documents], top_k=top_k
        )
        time_used_inference = round(time.perf_counter() - timer_reader, 3)
        response = self._aggregate_retriever_reader(query, documents, predictions)
        display_answers(response.answers)

        display_time_taken(
            {
                "time_used_retriever+ranker": time_used_ir,
                "time_used_reader": time_used_inference,
            }
        )

        return response

    def run_on_text(self, query: str, context: str, top_k: int = 1):
        query = unicodedata.normalize("NFKD", query)
        documents = [
            Document(
                content=context,
                meta={
                    "name": "playground-context",
                    "title": "playground-context",
                    "_split_id": -1,
                    "offsets_in_document": {"start": 0, "end": len(context)},
                },
            )
        ]
        timer_reader = time.perf_counter()
        predictions: List[FinalPrediction] = self.reader.read(
            question=query, contexts=[doc.content for doc in documents], top_k=top_k
        )
        time_used_inference = round(time.perf_counter() - timer_reader, 3)
        logger.info(f"[Playground] Time used for inference: {time_used_inference}s")

        response = self._aggregate_retriever_reader(query, documents, predictions)
        display_answers(response.answers)
        return response
