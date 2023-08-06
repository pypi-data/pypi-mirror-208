import logging
from typing import List, Optional, Set, Tuple

import nltk
from more_itertools import windowed

from ....schemas import SplitUnit
from ..utils import iso639_to_nltk

logger = logging.getLogger(__name__)


class PreProcessor:
    def __init__(
        self,
        split_by: str = "word",
        split_length: int = 200,
        split_overlap: int = 0,
        split_respect_sentence_boundary: bool = True,
        language: str = "en",
    ):
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

        self.split_by = split_by
        self.split_length = split_length
        self.split_overlap = split_overlap
        self.split_respect_sentence_boundary = split_respect_sentence_boundary
        self.language = iso639_to_nltk.get(language, language)
        self.print_log: Set[str] = set()

        self.sentence_tokenizer: nltk.tokenize.PunktSentenceTokenizer = nltk.data.load(
            f"tokenizers/punkt/{self.language}.pickle"
        )
        self.word_tokenizer = nltk.tokenize.WordPunctTokenizer()

    @staticmethod
    def _aggregate_offsets_to_splits(
        text: str,
        offsets: List[Tuple[int, int]],
        offsets_page_number: List[int],
        split_length: int,
        split_overlap: int,
    ) -> List[SplitUnit]:
        groups = windowed(
            seq=offsets, n=split_length, step=split_length - split_overlap
        )
        page_number_groups = windowed(
            seq=offsets_page_number, n=split_length, step=split_length - split_overlap
        )
        splits = []
        for group, page_number_group in zip(groups, page_number_groups):
            units_in_chunk = [unit for unit in group if unit is not None]
            page_nums = [unit for unit in page_number_group if unit is not None]

            from_page = page_nums[0]
            to_page = page_nums[-1]
            start = units_in_chunk[0][0]
            end = units_in_chunk[-1][1]
            splits.append(
                SplitUnit(
                    text=text[start:end],
                    offsets={"start": start, "end": end},
                    split_id=len(splits),
                    from_page=from_page,
                    to_page=to_page,
                )
            )
        return splits

    def process(
        self,
        pages: List[str],
        split_by: Optional[str] = None,
        split_length: Optional[int] = None,
        split_overlap: Optional[int] = None,
        split_respect_sentence_boundary: Optional[bool] = None,
    ) -> List[SplitUnit]:
        """
        Perform document cleaning and splitting. Can take a single document or a list of documents as input and returns a list of documents.
        """

        kwargs = {
            "split_by": split_by,
            "split_length": split_length,
            "split_overlap": split_overlap,
            "split_respect_sentence_boundary": split_respect_sentence_boundary,
        }

        return self.split(pages=pages, **kwargs)

    def _split_by_words(
        self, text: str, offsets_page_number, split_length: int, split_overlap: int
    ) -> List[SplitUnit]:
        offsets_generator = self.word_tokenizer.span_tokenize_sents([text])
        offsets = next(iter(offsets_generator))
        splits = self._aggregate_offsets_to_splits(
            text, offsets, offsets_page_number, split_length, split_overlap
        )
        return splits

    def _split_by_sentences(
        self, text: str, offsets_page_number, split_length: int, split_overlap: int
    ) -> List[SplitUnit]:
        offsets_generator = self.sentence_tokenizer.span_tokenize_sents([text])
        offsets = next(iter(offsets_generator))
        splits = self._aggregate_offsets_to_splits(
            text, offsets, offsets_page_number, split_length, split_overlap
        )
        return splits

    def _split_by_paragraphs(
        self, text: str, offsets_page_number, split_length: int, split_overlap: int
    ) -> List[SplitUnit]:
        def compute_offsets():
            subtexts = text.split("\n\n")
            _offsets = []
            for subtext in subtexts:
                start = text.find(subtext)
                end = start + len(subtext) + 1
                _offsets.append((start, end))
            return _offsets

        offsets = compute_offsets()
        splits = self._aggregate_offsets_to_splits(
            text, offsets, offsets_page_number, split_length, split_overlap
        )
        return splits

    def split(
        self,
        pages: List[str],
        split_by: Optional[str] = None,
        split_length: Optional[int] = None,
        split_overlap: Optional[int] = None,
        split_respect_sentence_boundary: Optional[bool] = None,
    ) -> List[SplitUnit]:
        if split_by is None:
            split_by = self.split_by
        if split_length is None:
            split_length = self.split_length
        if split_overlap is None:
            split_overlap = self.split_overlap
        if split_respect_sentence_boundary is None:
            split_respect_sentence_boundary = self.split_respect_sentence_boundary

        if split_by == "word" and split_respect_sentence_boundary:
            msg = (
                "Splitting by word and respecting sentence boundaries is not supported."
            )
            if msg not in self.print_log:
                self.print_log.add(msg)
                logger.warning(msg)
            split_respect_sentence_boundary = False

        if split_by == "word":
            split_func = self._split_by_words
        elif split_by == "sentence":
            split_func = self._split_by_sentences
        elif split_by == "paragraph":
            split_func = self._split_by_paragraphs
        else:
            raise ValueError(
                f"Unknown split_by value: {split_by}, choose from ['word', 'sentence', 'paragraph']"
            )

        offsets_page_number = []
        for idx, page in enumerate(pages):
            if split_by in ["word", "sentence"]:
                offsets_generator = self.word_tokenizer.span_tokenize_sents([page])
                offsets = next(iter(offsets_generator))
                offsets_page_number.extend([idx] * len(offsets))
            else:
                subtexts = page.split("\n\n")
                offsets_page_number.extend([idx] * len(subtexts))

        return split_func(
            text="\n".join(pages),
            offsets_page_number=offsets_page_number,
            split_length=split_length,
            split_overlap=split_overlap,
        )
