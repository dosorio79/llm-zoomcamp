from typing import Any

from .prompts import INSTRUCTIONS_AGENT

from openai import OpenAI
from toyaikit.llm import OpenAIClient
from toyaikit.chat.runners import OpenAIResponsesRunner

from .tools import get_tools
from .utils import calculate_openai_price


def build_agent_runner() -> OpenAIResponsesRunner:
    """
    Build and return an OpenAI agent runner with configured tools and prompts.

    Returns:
        OpenAIResponsesRunner: Configured runner instance for executing agent loops.
    """
    return OpenAIResponsesRunner(
        tools=get_tools(),
        developer_prompt=INSTRUCTIONS_AGENT,
        chat_interface=None,  # type: ignore
        llm_client=OpenAIClient(
            model="gpt-5.4-mini",
            client=OpenAI(),
        ),
    )


def run_agent(question: str, previous_messages: list[Any] | None = None) -> dict[str, Any]:
    """
    Execute the agent with a given question and return results.

    Args:
        question: The question or prompt to send to the agent.

    Returns:
        dict: Dictionary containing:
            - answer: The final message response
            - tokens: Token count for the session
            - cost: Cost of the API calls
            - messages: All messages in the conversation
    """
    runner = build_agent_runner()

    result = runner.loop(
        prompt=question,
        previous_messages=previous_messages or [],
        callback=None,  # type: ignore
    )

    return {
        "answer": result.last_message,
        "tokens": result.tokens,
        "cost": calculate_openai_price(
            model=result.tokens.model,
            input_tokens=result.tokens.input_tokens,
            output_tokens=result.tokens.output_tokens,
        ),
        "messages": result.all_messages,
    }


def ask_agent(question: str, previous_messages: list[Any] | None = None) -> dict[str, Any]:
    """
    Wrapper function to ask a question to the agent and get a response.

    Args:
        question: The question or prompt to send to the agent.

    Returns:
        dict: Dictionary containing the agent's response and metadata.
    """
    return run_agent(question, previous_messages=previous_messages)
