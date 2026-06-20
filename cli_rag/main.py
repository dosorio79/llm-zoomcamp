import os
from collections.abc import Callable
from pathlib import Path

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Prompt

from src.agent import ask_agent
from src.display import console, print_answer, print_cost, print_menu, print_token_usage
from src.ingestion import (
    COMMIT_ID,
    REPO_NAME,
    REPO_OWNER,
    build_index,
    chunk_documents_for_indexing,
    load_documents_from_repo,
)
from src.rag import ask_rag


DB_PATH = "storage/chunk.db"
APP_DIR = Path(__file__).resolve().parent
ENV_PATHS = [
    APP_DIR / ".env",
    APP_DIR.parent / ".env",
    APP_DIR.parent / "Lessons" / ".env",
]
MENU_CHOICES = {
    "1": "Build / rebuild index",
    "2": "Clean index",
    "3": "Plain RAG",
    "4": "Agentic RAG",
    "5": "Exit",
}
ChatHistory = object | None
ChatResult = tuple[dict, ChatHistory]
TurnFunction = Callable[[str, ChatHistory], ChatResult]


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


def ensure_index(rebuild: bool = False) -> None:
    if rebuild and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    if os.path.exists(DB_PATH):
        console.print("[green]Index found.[/green]")
        return

    console.print(
        "[yellow]"
        "Index not found. "
        f"Building index from {REPO_OWNER}/{REPO_NAME} lessons at commit {COMMIT_ID}..."
        "[/yellow]"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        load_task = progress.add_task("Loading lesson files from GitHub", total=None)
        documents = load_documents_from_repo()
        progress.update(
            load_task,
            description=f"Loaded {len(documents)} lesson files",
            total=1,
            completed=1,
        )

        chunk_task = progress.add_task("Chunking lesson files", total=None)
        chunks = chunk_documents_for_indexing(documents)
        progress.update(
            chunk_task,
            description=f"Created {len(chunks)} chunks",
            total=1,
            completed=1,
        )

        index_task = progress.add_task("Indexing chunks", total=len(chunks))
        build_index(
            chunks,
            db_path=DB_PATH,
            progress_callback=lambda: progress.advance(index_task),
        )

    console.print("[green]Index built.[/green]")


def clean_index() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        console.print(f"[green]Removed index at {DB_PATH}.[/green]")
        return

    console.print(f"[yellow]No index found at {DB_PATH}.[/yellow]")


def run_rag_turn(question: str, history: ChatHistory) -> ChatResult:
    return ask_rag(question), history


def run_agent_turn(question: str, history: ChatHistory) -> ChatResult:
    result = ask_agent(
        question=question,
        previous_messages=history if isinstance(history, list) else None,
    )
    return result, result.get("messages")


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


def run_index_setup(rebuild: bool) -> bool:
    try:
        ensure_index(rebuild=rebuild)
    except Exception as e:
        console.print(f"[bold red]Error during index setup:[/bold red] {e}")
        return False

    return True


def main() -> None:
    load_env_files()

    while True:
        print_menu(MENU_CHOICES)
        choice = Prompt.ask(
            "[bold]Choose an option[/bold]",
            choices=list(MENU_CHOICES),
            default="3",
            show_choices=False,
        )

        if choice == "1":
            run_index_setup(rebuild=True)
        elif choice == "2":
            clean_index()
        elif choice == "3":
            if run_index_setup(rebuild=False):
                run_chat_loop("plain RAG", run_rag_turn, token_key="usage")
        elif choice == "4":
            if run_index_setup(rebuild=False):
                run_chat_loop("agentic RAG", run_agent_turn, token_key="tokens")
        else:
            break


if __name__ == "__main__":
    main()
