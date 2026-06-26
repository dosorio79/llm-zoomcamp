from collections.abc import Callable
import os
from pathlib import Path
from typing import Any, Literal, cast

from psycopg import sql
from rich.prompt import Confirm, Prompt

from src.config import (
    BM25_INDEX_NAME,
    CHUNKS_TABLE,
    COMMIT_ID,
    DATABASE_SCHEMA,
    REPO_NAME,
    REPO_OWNER,
    VECTOR_INDEX_NAME,
)
from src.display import console, print_answer, print_cost, print_menu, print_token_usage
from src.db.connection import fetch_all


APP_DIR = Path(__file__).resolve().parent
ENV_PATHS = [
    APP_DIR / ".env",
    APP_DIR.parent / ".env",
    APP_DIR.parent / "Lessons" / ".env",
]
MENU_CHOICES = {
    "1": "Reset knowledge store",
    "2": "Plain RAG",
    "3": "Agentic RAG",
    "4": "Exit",
}
RETRIEVER_CHOICES = {
    "1": "text",
    "2": "vector",
    "3": "hybrid",
}
RetrieverMode = Literal["text", "vector", "hybrid"]
ChatHistory = object | None
ChatResult = tuple[dict[str, Any], ChatHistory]
TurnFunction = Callable[[str, ChatHistory], ChatResult]
SOURCE_PATH_FILTER = "/lessons/"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")

        if key and key not in os.environ:
            os.environ[key] = value


def load_env_files(env_paths: list[Path] = ENV_PATHS) -> None:
    for env_path in env_paths:
        load_env_file(env_path)


def choose_retriever_mode() -> RetrieverMode:
    labels = {
        "1": "Text / BM25",
        "2": "Vector / embeddings",
        "3": "Hybrid / BM25 + vector",
    }
    print_menu(labels)
    choice = Prompt.ask(
        "[bold]Choose retrieval mode[/bold]",
        choices=list(RETRIEVER_CHOICES),
        default="3",
        show_choices=False,
    )
    return cast(RetrieverMode, RETRIEVER_CHOICES[choice])


def build_rag_turn(retriever_mode: RetrieverMode) -> TurnFunction:
    def run_rag_turn(question: str, history: ChatHistory) -> ChatResult:
        from src.rag_pipeline import ask_rag

        return ask_rag(question, retriever_mode=retriever_mode), history

    return run_rag_turn


def build_agent_turn(retriever_mode: RetrieverMode) -> TurnFunction:
    def run_agent_turn(question: str, history: ChatHistory) -> ChatResult:
        from src.agent import ask_agent

        result = ask_agent(
            question=question,
            previous_messages=history if isinstance(history, list) else None,
            retriever_mode=retriever_mode,
        )
        return result, result.get("messages")

    return run_agent_turn


def run_chat_loop(title: str, run_turn: TurnFunction, token_key: str) -> None:
    console.print(
        f"[bold cyan]Running {title}.[/bold cyan] Type 'exit' to return to the menu.\n"
    )

    history = None
    while True:
        question = Prompt.ask("[bold]Question[/bold]").strip()

        if question.lower() in {"exit", "quit", "stop"}:
            break

        if not question:
            continue

        result, history = run_turn(question, history)

        print_answer(result["answer"])

        if result.get(token_key):
            print_token_usage(result[token_key])

        if result.get("cost") is not None:
            print_cost(result["cost"])

        console.print()


def get_schema_status() -> dict[str, Any]:
    statement = sql.SQL(
        """
        SELECT
            to_regclass(%s) IS NOT NULL AS table_exists,
            to_regclass(%s) IS NOT NULL AS bm25_index_exists,
            to_regclass(%s) IS NOT NULL AS vector_index_exists,
            CASE
                WHEN to_regclass(%s) IS NULL THEN NULL
                ELSE (SELECT COUNT(*) FROM {}.{})
            END AS row_count
        """
    ).format(
        sql.Identifier(DATABASE_SCHEMA),
        sql.Identifier(CHUNKS_TABLE),
    )

    rows = fetch_all(
        statement,
        (
            f"{DATABASE_SCHEMA}.{CHUNKS_TABLE}",
            f"{DATABASE_SCHEMA}.{BM25_INDEX_NAME}",
            f"{DATABASE_SCHEMA}.{VECTOR_INDEX_NAME}",
            f"{DATABASE_SCHEMA}.{CHUNKS_TABLE}",
        ),
    )
    row = rows[0]

    return {
        "table_exists": row[0],
        "bm25_index_exists": row[1],
        "vector_index_exists": row[2],
        "row_count": row[3],
    }


def print_schema_status() -> None:
    status = get_schema_status()
    row_count = status["row_count"]
    row_count_text = "not available" if row_count is None else str(row_count)

    console.print(
        "[dim]Schema status:[/dim] "
        f"table={'yes' if status['table_exists'] else 'no'}, "
        f"bm25_index={'yes' if status['bm25_index_exists'] else 'no'}, "
        f"vector_index={'yes' if status['vector_index_exists'] else 'no'}, "
        f"rows={row_count_text}"
    )
    console.print(
        "[dim]Configured source:[/dim] "
        f"{REPO_OWNER}/{REPO_NAME}@{COMMIT_ID} "
        f"path filter={SOURCE_PATH_FILTER}"
    )


def run_schema_setup(reset: bool = False) -> bool:
    from src.db import reset_schema, setup_schema

    try:
        if reset:
            console.print("[cyan]Dropping and recreating database schema...[/cyan]")
            reset_schema()
            console.print("[green]Database schema reset complete.[/green]")
        else:
            console.print("[cyan]Creating database schema if needed...[/cyan]")
            setup_schema()
            console.print("[green]Database schema setup complete.[/green]")

        print_schema_status()
    except Exception as e:
        console.print(f"[bold red]Error during schema setup:[/bold red] {e}")
        return False

    return True


def run_ingestion(*, ensure_schema: bool = True) -> bool:
    from src.ingestion import ingest_repository

    try:
        if ensure_schema and not run_schema_setup():
            return False

        console.print(
            "[cyan]Loading, chunking, embedding, and indexing documents from "
            f"{REPO_OWNER}/{REPO_NAME}@{COMMIT_ID} ({SOURCE_PATH_FILTER})...[/cyan]"
        )
        inserted = ingest_repository()
        console.print(f"[green]Ingestion complete. Upserted {inserted} chunks.[/green]")
        print_schema_status()
    except Exception as e:
        console.print(f"[bold red]Error during ingestion:[/bold red] {e}")
        return False

    return True


def run_knowledge_store_reset() -> bool:
    from src.db import reset_schema

    if not Confirm.ask(
        "[bold red]This will erase indexed chunks and rebuild the store. Continue?[/bold red]",
        default=False,
    ):
        console.print("[yellow]Reset cancelled.[/yellow]")
        return False

    try:
        console.print("[cyan]Dropping and recreating database schema...[/cyan]")
        reset_schema()
        console.print("[green]Database schema reset complete.[/green]")
        print_schema_status()
    except Exception as e:
        console.print(f"[bold red]Error during schema reset:[/bold red] {e}")
        return False

    return run_ingestion(ensure_schema=False)


def main() -> None:
    load_env_files()

    while True:
        print_menu(MENU_CHOICES)
        choice = Prompt.ask(
            "[bold]Choose an option[/bold]",
            choices=list(MENU_CHOICES),
            default="2",
            show_choices=False,
        )

        if choice == "1":
            run_knowledge_store_reset()
        elif choice == "2":
            if run_schema_setup():
                retriever_mode = choose_retriever_mode()
                run_chat_loop(
                    f"plain RAG ({retriever_mode})",
                    build_rag_turn(retriever_mode),
                    token_key="usage",
                )
        elif choice == "3":
            if run_schema_setup():
                retriever_mode = choose_retriever_mode()
                run_chat_loop(
                    f"agentic RAG ({retriever_mode})",
                    build_agent_turn(retriever_mode),
                    token_key="tokens",
                )
        else:
            break


if __name__ == "__main__":
    main()
