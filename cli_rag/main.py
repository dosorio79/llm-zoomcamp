from collections.abc import Callable
import os
from pathlib import Path

from rich.prompt import Prompt

from src.display import console, print_answer, print_cost, print_menu, print_token_usage


APP_DIR = Path(__file__).resolve().parent
ENV_PATHS = [
    APP_DIR / ".env",
    APP_DIR.parent / ".env",
    APP_DIR.parent / "Lessons" / ".env",
]
MENU_CHOICES = {
    "1": "Set up database schema",
    "2": "Reset database schema",
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


def run_rag_turn(question: str, history: ChatHistory) -> ChatResult:
    from src.rag_pipeline import ask_rag

    return ask_rag(question), history


def run_agent_turn(question: str, history: ChatHistory) -> ChatResult:
    from src.agent import ask_agent

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


def run_schema_setup(reset: bool = False) -> bool:
    from src.db import reset_schema, setup_schema

    try:
        if reset:
            reset_schema()
            console.print("[green]Database schema reset.[/green]")
        else:
            setup_schema()
            console.print("[green]Database schema ready.[/green]")
    except Exception as e:
        console.print(f"[bold red]Error during schema setup:[/bold red] {e}")
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
            run_schema_setup()
        elif choice == "2":
            run_schema_setup(reset=True)
        elif choice == "3":
            if run_schema_setup():
                run_chat_loop("plain RAG", run_rag_turn, token_key="usage")
        elif choice == "4":
            if run_schema_setup():
                run_chat_loop("agentic RAG", run_agent_turn, token_key="tokens")
        else:
            break


if __name__ == "__main__":
    main()
