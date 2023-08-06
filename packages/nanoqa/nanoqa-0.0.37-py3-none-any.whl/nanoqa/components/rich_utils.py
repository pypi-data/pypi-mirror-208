from typing import List

from rich import print_json
from rich.console import Console
from rich.table import Table

from ..schemas import Document, PipelineAnswer

console = Console()


def display_time_taken(times: dict):
    console.log("")
    table = Table(
        title=f"Time Used (in seconds)",
        show_header=True,
        header_style="bold",
        expand=True,
    )

    if len(times) == 3:
        table.add_column("Retriever", style="blue", justify="center")
        table.add_column("Reader", style="blue", justify="center")
        table.add_column("Ranker", style="blue", justify="center")

        table.add_row(
            f"[bold]{times.get('time_used_retriever')}[/bold]",
            f"[bold]{times.get('time_used_reader')}[/bold]",
            f"[bold]{times.get('time_used_ranker')}[/bold]",
        )
    elif len(times) == 2:
        table.add_column("Retriever+Ranker", style="blue", justify="center")
        table.add_column("Reader", style="blue", justify="center")

        table.add_row(
            f"[bold]{times.get('time_used_retriever+ranker')}[/bold]",
            f"[bold]{times.get('time_used_reader')}[/bold]",
        )

    console.print(table)
    console.log("")


def display_retrieved_documents(query: str, documents: List[Document]):
    console.log("")
    console.log(f"For query: [bold green]{query}[/]")
    table = Table(
        title=f"Top-{len(documents)} documents (with re-ranking if ranker available)",
        show_header=True,
        header_style="bold",
        expand=True,
    )
    table.add_column("Rank", style="blue", justify="center")
    table.add_column("Title", style="blue", justify="center")
    table.add_column("Id", style="blue", justify="center")
    table.add_column("Score", style="green", justify="center")

    for ranking, document in enumerate(documents):
        table.add_row(
            str(ranking + 1),
            f"[bold]{'Unknown' if 'title' not in document.meta else document.meta['title']}[/bold]",
            f"[bold]{document.id}[/bold]",
            f"[bold]{document.score}[/bold]",
        )
    console.print(table)
    console.log("")


def display_answers(answers: List[PipelineAnswer]):
    console.log("")
    table = Table(
        title=f"Top-{len(answers)} answers inferred",
        show_header=True,
        header_style="bold",
        expand=True,
    )
    table.add_column("Rank", style="blue", justify="center")
    table.add_column("Answer", style="blue", justify="center")
    table.add_column("Meta.Name", style="blue", justify="center")
    table.add_column("D-Index", style="blue", justify="center")
    table.add_column("C-Index", style="blue", justify="center")
    table.add_column("Sum of logits", style="green", justify="center")
    table.add_column("Probability", style="green", justify="center")

    for index, ans in enumerate(answers):
        table.add_row(
            str(index + 1),
            f"[bold]{ans.answer}[/bold]",
            f"[bold]{'Unknown' if 'name' not in ans.meta else ans.meta['name']}[/bold]",
            f"[bold]{ans.document_index}[/bold]",
            f"[bold]{ans.chunk_index}[/bold]",
            f"[bold]{ans.sum_of_logits}[/bold]",
            f"[bold]{ans.score}[/bold]",
        )

    console.print(table)
    console.log("")


def display_json(data: dict):
    print_json(data=data)
