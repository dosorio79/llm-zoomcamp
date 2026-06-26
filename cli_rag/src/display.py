from decimal import Decimal, InvalidOperation
from typing import Callable

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


console = Console()

def print_answer(answer: str) -> None:
    console.print()
    console.print(
        Panel(
            Markdown(answer or "_No answer returned._"),
            title="Answer",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def print_menu(choices: dict[str, str]) -> None:
    menu = "\n".join(f"[bold]{key}[/bold]. {label}" for key, label in choices.items())
    console.print(
        Panel(
            menu,
            title="LLM Zoomcamp RAG",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def get_metadata_value(data: object, key: str) -> object | None:
    if isinstance(data, dict):
        return data.get(key)

    return getattr(data, key, None)


def print_rows_panel(
    title: str,
    rows: list[tuple[str, object | None]],
    formatter: Callable[[object], str] = str,
) -> None:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="green")
    table.add_column(style="cyan", justify="right")

    for label, value in rows:
        if value is not None:
            table.add_row(label, formatter(value))

    console.print(Panel(table, title=title, border_style="dim"))


def print_token_usage(data: object) -> None:
    input_tokens = get_metadata_value(data, "input_tokens")
    output_tokens = get_metadata_value(data, "output_tokens")
    total_tokens = get_metadata_value(data, "total_tokens")

    if total_tokens is None and isinstance(input_tokens, int) and isinstance(output_tokens, int):
        total_tokens = input_tokens + output_tokens

    print_rows_panel(
        title="Token Usage",
        rows=[
            ("Model", get_metadata_value(data, "model")),
            ("Input tokens", input_tokens),
            ("Cached tokens", get_metadata_value(data, "cached_tokens")),
            ("Output tokens", output_tokens),
            ("Reasoning tokens", get_metadata_value(data, "reasoning_tokens")),
            ("Total tokens", total_tokens),
        ],
    )


def format_cost(value: object) -> str:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return str(value)

    return f"${amount:.8f}"


def print_cost(data: object) -> None:
    print_rows_panel(
        title="Cost",
        rows=[
            ("Input cost", get_metadata_value(data, "input_cost")),
            ("Output cost", get_metadata_value(data, "output_cost")),
            ("Total cost", get_metadata_value(data, "total_cost")),
        ],
        formatter=format_cost,
    )
