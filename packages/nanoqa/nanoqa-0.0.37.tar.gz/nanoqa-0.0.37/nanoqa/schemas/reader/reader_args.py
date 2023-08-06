from dataclasses import dataclass


@dataclass
class ReaderBaseArguments:
    max_seq_len: int
    doc_stride: int
    max_ans_len: int


@dataclass
class ReaderArguments(ReaderBaseArguments):
    nbest_from_chunk: int = 3
    nbest_from_document: int = 1
    no_ans_boost: float = 0.0
    return_no_answer: bool = False


@dataclass
class AdapterTrainingArguments:
    adapter_name: str

    data_dir: str
    train_filename: str
    save_dir: str

    max_seq_len: int
    doc_stride: int
    batch_size: int
    n_epochs: int
    learning_rate: float
