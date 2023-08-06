import json
import os

import torch.cuda
from datasets import Dataset
from transformers import (
    AdapterTrainer,
    IntervalStrategy,
    TrainingArguments,
    default_data_collator,
)


def load_squad_like_dataset(filepath: str, include_ids: bool = False):
    f = open(filepath, "r")
    squad_dict = json.load(f)
    contexts, questions, answers, ids = [], [], [], []
    for example in squad_dict["data"]:
        for paragraph in example["paragraphs"]:
            context = paragraph["context"]
            for qa in paragraph["qas"]:
                question = qa["question"]
                example_id = qa["id"]
                texts = [ans["text"] for ans in qa["answers"]]
                starts = [ans["answer_start"] for ans in qa["answers"]]
                contexts.append(context)
                questions.append(question)
                answers.append({"text": texts, "answer_start": starts})
                ids.append(example_id)
    questions = [question.strip() for question in questions]
    squad = {"context": contexts, "question": questions, "answers": answers}
    if include_ids:
        squad["id"] = ids
    f.close()

    return Dataset.from_dict(squad)


def squad_to_train_features(examples, tokenizer, max_seq_len, doc_stride):
    pad_on_right = tokenizer.padding_side == "right"
    tokenized_examples = tokenizer(
        examples["question" if pad_on_right else "context"],
        examples["context" if pad_on_right else "question"],
        truncation="only_second" if pad_on_right else "only_first",
        max_length=max_seq_len,
        stride=doc_stride,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
    )

    sample_mapping = tokenized_examples.pop("overflow_to_sample_mapping")
    offset_mapping = tokenized_examples.pop("offset_mapping")

    # compute labels for training
    tokenized_examples["start_positions"] = []
    tokenized_examples["end_positions"] = []

    for i, offsets in enumerate(offset_mapping):
        input_ids = tokenized_examples["input_ids"][i]
        # Find [CLS] example
        cls_index = input_ids.index(tokenizer.cls_token_id)

        sequence_ids = tokenized_examples.sequence_ids(i)

        sample_index = sample_mapping[i]
        answers = examples["answers"][sample_index]
        if len(answers["answer_start"]) == 0:
            # negative example, put [CLS]
            tokenized_examples["start_positions"].append(cls_index)
            tokenized_examples["end_positions"].append(cls_index)
        else:
            # start character of the answer in the context
            start_char = answers["answer_start"][0]
            end_char = start_char + len(answers["text"][0])

            token_start_index = 0
            # skip the question tokens and special tokens
            while sequence_ids[token_start_index] != (1 if pad_on_right else 0):
                token_start_index += 1

            # put end_index at the end of sequence
            token_end_index = len(input_ids) - 1
            # skip the [PAD] and [EOS] tokens at the end
            while sequence_ids[token_end_index] != (1 if pad_on_right else 0):
                token_end_index -= 1

            # find exact positions of start and end tokens in sequence
            # if answer is out of the context, then this chunk doesn't contain the answer, put [CLS]
            if not (
                offsets[token_start_index][0] <= start_char
                and offsets[token_end_index][1] >= end_char
            ):
                tokenized_examples["start_positions"].append(cls_index)
                tokenized_examples["end_positions"].append(cls_index)
            else:
                # Iterate the tokens in the sequence to find two ends of the answer
                while (
                    token_start_index < len(offsets)
                    and offsets[token_start_index][0] <= start_char
                ):
                    token_start_index += 1
                while offsets[token_end_index][1] >= end_char:
                    token_end_index -= 1
                start_position = token_start_index - 1
                end_position = token_end_index + 1
                # Edge Case: the answer is the last word of the context
                if start_position == len(sequence_ids) - 1:
                    start_position = end_position
                # Edge Case
                if start_position > end_position:
                    start_position, end_position = end_position, start_position

                tokenized_examples["start_positions"].append(start_position)
                tokenized_examples["end_positions"].append(end_position)

    return tokenized_examples


def handle_adapter_training(
    model,
    tokenizer,
    data_dir,
    train_filename,
    max_seq_len,
    doc_stride,
    learning_rate,
    batch_size,
    n_epochs,
):
    train_filename = os.path.join(data_dir, train_filename)
    train_examples = load_squad_like_dataset(filepath=train_filename)
    train_features = train_examples.map(
        lambda examples: squad_to_train_features(
            examples, tokenizer, max_seq_len, doc_stride
        ),
        batched=True,
        remove_columns=train_examples.column_names,
        desc="Tokenization",
    )

    args = TrainingArguments(
        output_dir="/tmp/temporary_output_dir",
        overwrite_output_dir=True,
        do_train=True,
        do_eval=False,
        do_predict=False,
        evaluation_strategy=IntervalStrategy.NO,
        logging_strategy=IntervalStrategy.NO,
        save_strategy=IntervalStrategy.NO,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=1,
        fp16=True if torch.cuda.is_available() else False,
        learning_rate=learning_rate,
        num_train_epochs=n_epochs,
        weight_decay=0.01,
    )

    trainer = AdapterTrainer(
        model,
        args,
        train_dataset=train_features,
        eval_dataset=None,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )
    trainer.train()
    trainer.model.eval()
