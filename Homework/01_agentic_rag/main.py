import os
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.pretty import Pretty
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
from src.ingestion import (
    build_index,
    chunk_documents_for_indexing,
    load_documents_from_repo,
)
from src.rag import ask_rag


DB_PATH = "storage/chunk.db"
ENV_PATH = Path(__file__).with_name(".env")
MENU_CHOICES = {
    "1": "Build / rebuild index",
    "2": "Plain RAG",
    "3": "Agentic RAG",
    "4": "Exit",
}
console = Console()


def load_env_file(env_path: Path = ENV_PATH) -> None:
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


def ensure_index(rebuild: bool = False) -> None:
    if rebuild and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    if os.path.exists(DB_PATH):
        console.print("[green]Index found.[/green]")
        return

    console.print("[yellow]Index not found. Building index...[/yellow]")

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


def print_metadata(title: str, data: object) -> None:
    console.print(Panel(Pretty(data), title=title, border_style="dim"))


def run_rag_loop() -> None:
    console.print("[bold cyan]Running plain RAG.[/bold cyan] Type 'exit' to return to the menu.\n")

    while True:
        question = Prompt.ask("[bold]Question[/bold]").strip()

        if question.lower() in {"exit", "quit", "stop"}:
            break

        if not question:
            continue

        result = ask_rag(question)

        print_answer(result["answer"])

        if result.get("usage"):
            print_metadata("Usage", result["usage"])

        console.print()


def run_agent_loop() -> None:
    console.print("[bold cyan]Running agentic RAG.[/bold cyan] Type 'exit' to return to the menu.\n")

    history = None

    while True:
        question = Prompt.ask("[bold]Question[/bold]").strip()

        if question.lower() in {"exit", "quit", "stop"}:
            break

        if not question:
            continue

        result = ask_agent(
            question=question,
            previous_messages=history,
        )

        history = result.get("messages")

        print_answer(result["answer"])

        if result.get("tokens"):
            print_metadata("Tokens", result["tokens"])

        if result.get("cost") is not None:
            console.print(Panel(str(result["cost"]), title="Cost", border_style="dim"))

        console.print()


def print_menu() -> None:
    menu = "\n".join(f"[bold]{key}[/bold]. {label}" for key, label in MENU_CHOICES.items())
    console.print(
        Panel(
            menu,
            title="LLM Zoomcamp RAG",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def run_index_setup(rebuild: bool) -> bool:
    try:
        ensure_index(rebuild=rebuild)
    except Exception as e:
        console.print(f"[bold red]Error during index setup:[/bold red] {e}")
        return False

    return True


def main() -> None:
    load_env_file()

    while True:
        print_menu()
        choice = Prompt.ask(
            "[bold]Choose an option[/bold]",
            choices=list(MENU_CHOICES),
            default="3",
            show_choices=False,
        )

        if choice == "1":
            run_index_setup(rebuild=True)
        elif choice == "2":
            if run_index_setup(rebuild=False):
                run_rag_loop()
        elif choice == "3":
            if run_index_setup(rebuild=False):
                run_agent_loop()
        else:
            break


if __name__ == "__main__":
    main()
