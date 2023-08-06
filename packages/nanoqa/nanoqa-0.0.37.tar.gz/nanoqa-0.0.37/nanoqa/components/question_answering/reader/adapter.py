import os
from pathlib import Path
from typing import List, Union

import torch

from ....schemas import AdapterTrainingArguments
from ..handlers.train import handle_adapter_training
from ..reader.base import BaseReader


class ReaderWithAdapter(BaseReader):
    def __init__(
        self,
        model_name_or_path: str,
        max_seq_len: int = 384,
        doc_stride: int = 128,
        max_ans_len: int = 30,
        use_gpu: bool = True,
        nbest_from_chunk: int = 3,
        nbest_from_document: int = 1,
        return_no_answer: bool = False,
        no_ans_boost: float = 0.0,
        skip_detailed_features: bool = True,
        display_progress_bar: bool = True,
    ):
        """
        :param model_name_or_path: name of the model to load or path to a directory containing model files
        :param max_seq_len: maximum length of the sequence to be considered by the model
        :param doc_stride: stride to be used while splitting the document into chunks
        :param max_ans_len: maximum length of the answer to be considered by the model
        :param use_gpu: whether to use GPU or not
        :param nbest_from_chunk: number of best answers to be considered from each chunk
        :param nbest_from_document: number of best answers to be considered from the whole document
        :param return_no_answer:  whether to return no answer or not
        :param no_ans_boost: boost to be applied to the score of no answer
        :param skip_detailed_features: whether to skip detailed features or not
        :param display_progress_bar: whether to display progress bar or not
        """
        super().__init__(
            model_name_or_path,
            max_seq_len,
            doc_stride,
            max_ans_len,
            use_gpu,
            nbest_from_chunk,
            nbest_from_document,
            return_no_answer,
            no_ans_boost,
            skip_detailed_features,
            display_progress_bar,
        )

    def load_adapter(self, adapter_location: Union[str, Path]):
        if isinstance(adapter_location, Path):
            adapter_location = str(adapter_location)
        adapter_name = self.model.load_adapter(adapter_location, with_head=False)
        self.model.qa_outputs.load_state_dict(
            torch.load(os.path.join(adapter_location, "qa_outputs.bin"))
        )
        self.model.set_active_adapters([adapter_name])
        if self.use_gpu and torch.cuda.is_available():
            self.model.cuda()

    def delete_all_adapters(self, adapter_names: List[str]):
        if adapter_names:
            for adapter_name in adapter_names:
                self.model.delete_adapter(adapter_name)
        self.model.set_active_adapters(None)

    def train(self, training_args: AdapterTrainingArguments):
        # delete adapter name if exists
        self.delete_all_adapters([training_args.adapter_name])
        # add fresh adapter layers, and set it as active
        self.model.add_adapter(training_args.adapter_name)
        self.model.train_adapter(training_args.adapter_name)
        self.model.set_active_adapters([training_args.adapter_name])

        handle_adapter_training(
            model=self.model,
            tokenizer=self.tokenizer,
            data_dir=training_args.data_dir,
            train_filename=training_args.train_filename,
            max_seq_len=training_args.max_seq_len,
            doc_stride=training_args.doc_stride,
            learning_rate=training_args.learning_rate,
            batch_size=training_args.batch_size,
            n_epochs=training_args.n_epochs,
        )

        # save the adapter layers and prediction head.
        self.model.save_adapter(
            save_directory=training_args.save_dir,
            adapter_name=training_args.adapter_name,
            with_head=False,
        )
        prediction_head = self.model.qa_outputs
        torch.save(
            prediction_head.state_dict(),
            os.path.join(training_args.save_dir, "qa_outputs.bin"),
        )
